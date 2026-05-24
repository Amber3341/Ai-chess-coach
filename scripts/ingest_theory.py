"""
One-time script to embed chess theory passages and upload them to Qdrant.
Run this once: python scripts/ingest_theory.py

Optimization #13: each passage is tagged with 'phase' and 'topic' metadata
so the RAG retriever can do filtered searches (e.g., only endgame passages
when the critical moment occurred in the endgame).
"""
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from google import genai
from google.genai.errors import ClientError, ServerError

from scripts.chess_theory import CHESS_THEORY

COLLECTION_NAME = "chess-theory"
VECTOR_SIZE = 3072  # gemini-embedding-001 actual dimension
BATCH_SIZE = 20
UPLOAD_BATCH = 10
RATE_LIMIT_WINDOW = 90  # passages per minute (free tier ≈ 100/min, keep headroom)


# ---------------------------------------------------------------------------
# Optimization #13 — Phase/topic auto-tagging
# ---------------------------------------------------------------------------

_PHASE_KEYWORDS: dict[str, list[str]] = {
    "opening": [
        "opening", "develop", "centre", "center", "castl", "ruy lopez",
        "sicilian", "italian", "french", "caro-kann", "queen's gambit",
        "king's indian", "dutch", "hypermodern",
    ],
    "endgame": [
        "endgame", "end game", "king activ", "pawn endgame", "rook endgame",
        "bishop endgame", "knight endgame", "queen endgame", "lucena",
        "philidor", "opposition", "triangulat", "zugzwang", "passed pawn",
        "promotion", "pawn majority",
    ],
    "middlegame": [
        "middlegame", "middle game", "attack", "outpost", "piece activ",
        "pawn structure", "weak", "two weakness", "space advantage",
        "opposite-side castling", "prophylax", "transform", "isolat",
        "backward pawn", "pawn break",
    ],
}

_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "tactics": [
        "fork", "pin", "skewer", "discovered", "overload", "deflect",
        "zwischenzug", "back-rank", "sacrifice", "greek gift", "decoy",
        "tactic", "combination",
    ],
    "pawn_structure": [
        "isolated pawn", "doubled pawn", "backward pawn", "passed pawn",
        "pawn majority", "pawn break", "pawn structure", "fixed pawn",
        "fianchet",
    ],
    "king_safety": [
        "king safety", "castl", "pawn shield", "king shelter", "h2-h3",
        "open file", "opposite-side castling", "pawn storm", "back-rank",
        "dragon diagonal",
    ],
    "endgame_technique": [
        "lucena", "philidor", "opposition", "triangulat", "zugzwang",
        "rook behind", "seventh rank", "opposite-colou", "opposite-color",
    ],
    "piece_activity": [
        "outpost", "bishop pair", "bad bishop", "rook on open", "double rook",
        "connected rook", "piece activ", "piece activ",
    ],
    "strategy": [
        "prophylax", "two weakness", "space advantage", "transform",
        "blockade", "plan", "regroup", "manoeuvr", "maneuvr",
    ],
    "opening_theory": [
        "ruy lopez", "sicilian", "italian", "french", "caro-kann",
        "queen's gambit", "king's indian", "dutch", "develop", "centre control",
        "center control",
    ],
}


def _detect_phase(text: str) -> str:
    lower = text.lower()
    scores: dict[str, int] = {phase: 0 for phase in _PHASE_KEYWORDS}
    for phase, keywords in _PHASE_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                scores[phase] += 1
    best = max(scores, key=lambda p: scores[p])
    return best if scores[best] > 0 else "general"


def _detect_topic(text: str) -> str:
    lower = text.lower()
    scores: dict[str, int] = {topic: 0 for topic in _TOPIC_KEYWORDS}
    for topic, keywords in _TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                scores[topic] += 1
    best = max(scores, key=lambda t: scores[t])
    return best if scores[best] > 0 else "general"


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------

def get_embedding_batch(client: genai.Client, texts: list[str]) -> list[list[float]]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
    )
    return [e.values for e in result.embeddings]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    qdrant_url = os.environ.get("QDRANT_URL")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if not qdrant_url:
        print("ERROR: QDRANT_URL not set in .env")
        sys.exit(1)
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY not set in .env")
        sys.exit(1)

    print(f"Connecting to Qdrant at {qdrant_url}...")
    qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key or None, timeout=60)
    gemini = genai.Client(api_key=gemini_api_key)

    # Create or recreate collection
    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists. Recreating...")
        qdrant.delete_collection(COLLECTION_NAME)

    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Collection '{COLLECTION_NAME}' created.")

    # Pre-compute phase/topic tags (fast, no API calls)
    print("Tagging passages with phase and topic metadata...")
    tags = [
        {"phase": _detect_phase(text), "topic": _detect_topic(text)}
        for text in CHESS_THEORY
    ]
    phase_distribution: dict[str, int] = {}
    topic_distribution: dict[str, int] = {}
    for t in tags:
        phase_distribution[t["phase"]] = phase_distribution.get(t["phase"], 0) + 1
        topic_distribution[t["topic"]] = topic_distribution.get(t["topic"], 0) + 1
    print(f"  Phase distribution: {phase_distribution}")
    print(f"  Topic distribution: {topic_distribution}")

    # Batch embed all passages
    print(f"\nEmbedding {len(CHESS_THEORY)} passages in batches of {BATCH_SIZE}...")
    all_embeddings: list[list[float]] = []
    passages_in_window = 0

    for i in range(0, len(CHESS_THEORY), BATCH_SIZE):
        batch = CHESS_THEORY[i: i + BATCH_SIZE]
        print(f"  Batch {i // BATCH_SIZE + 1}: passages {i + 1}–{min(i + len(batch), len(CHESS_THEORY))}...")

        if passages_in_window + len(batch) >= RATE_LIMIT_WINDOW:
            print("    Approaching rate limit. Sleeping 65 seconds...")
            time.sleep(65)
            passages_in_window = 0

        success = False
        while not success:
            try:
                embeddings = get_embedding_batch(gemini, batch)
                all_embeddings.extend(embeddings)
                print(f"    OK: {len(embeddings)} embeddings received.")
                passages_in_window += len(batch)
                success = True
            except (ClientError, ServerError) as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    print("    Rate limit hit. Sleeping 45 seconds before retry...")
                    time.sleep(45)
                elif "503" in err or "UNAVAILABLE" in err or "502" in err:
                    print("    Transient server error (503/502). Sleeping 20 seconds before retry...")
                    time.sleep(20)
                else:
                    raise

    # Build Qdrant points with Optimization #13 metadata
    points = [
        PointStruct(
            id=i,
            vector=emb,
            payload={
                "text": text,
                "index": i,
                "phase": tags[i]["phase"],   # Optimization #13
                "topic": tags[i]["topic"],   # Optimization #13
            },
        )
        for i, (text, emb) in enumerate(zip(CHESS_THEORY, all_embeddings))
    ]

    # Upload in small batches with retry on network timeouts
    print(f"\nUploading {len(points)} vectors to Qdrant...")
    for start in range(0, len(points), UPLOAD_BATCH):
        batch = points[start: start + UPLOAD_BATCH]
        for attempt in range(1, 5):   # up to 4 attempts
            try:
                qdrant.upsert(collection_name=COLLECTION_NAME, points=batch)
                print(f"  Uploaded points {start}-{start + len(batch) - 1}")
                break
            except Exception as e:
                wait = attempt * 10
                print(f"  Upload error (attempt {attempt}): {type(e).__name__}. Retrying in {wait}s...")
                time.sleep(wait)
                if attempt == 4:
                    raise

    count = qdrant.count(collection_name=COLLECTION_NAME).count
    print(
        f"\nDONE! {count} theory passages now in Qdrant collection '{COLLECTION_NAME}'.\n"
        f"Each passage has 'phase' and 'topic' metadata tags for filtered retrieval."
    )


if __name__ == "__main__":
    main()
