"""
One-time script to embed chess theory passages and upload them to Qdrant.
Run this once: python scripts/ingest_theory.py
"""
import os
import sys
import uuid
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from google import genai

from scripts.chess_theory import CHESS_THEORY

COLLECTION_NAME = "chess-theory"
VECTOR_SIZE = 3072  # gemini-embedding-001 actual dimension

def get_embedding(client: genai.Client, text: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return result.embeddings[0].values

def main():
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
    qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key or None)
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

    # Batch embed all passages in one API call (much faster, avoids rate limits)
    print(f"Embedding {len(CHESS_THEORY)} passages in batches...")
    BATCH_SIZE = 20
    all_embeddings = []
    
    import time
    from google.genai.errors import ClientError
    
    passages_embedded_in_window = 0
    
    for i in range(0, len(CHESS_THEORY), BATCH_SIZE):
        batch = CHESS_THEORY[i : i + BATCH_SIZE]
        print(f"  Batch {i//BATCH_SIZE + 1}: embedding passages {i+1}-{min(i+len(batch), len(CHESS_THEORY))}...")
        
        # Free tier is ~100 requests (passages) per minute. 
        if passages_embedded_in_window + len(batch) >= 90:
            print("    Approaching rate limit (100/min). Sleeping for 65 seconds...")
            time.sleep(65)
            passages_embedded_in_window = 0
            
        success = False
        while not success:
            try:
                result = gemini.models.embed_content(
                    model="gemini-embedding-001",
                    contents=batch,
                )
                all_embeddings.extend([e.values for e in result.embeddings])
                print(f"    OK: Got {len(result.embeddings)} embeddings")
                passages_embedded_in_window += len(batch)
                success = True
            except ClientError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("    Rate limit hit unexpectedly. Sleeping for 45 seconds before retry...")
                    time.sleep(45)
                else:
                    raise

    # Upload all vectors using integer IDs (Qdrant prefers these)
    points = [
        PointStruct(
            id=i,  # Use integer IDs — simpler and reliable
            vector=emb,
            payload={"text": text, "index": i},
        )
        for i, (text, emb) in enumerate(zip(CHESS_THEORY, all_embeddings))
    ]

    print(f"Uploading {len(points)} vectors to Qdrant...")
    # Upload in smaller batches to avoid timeout
    UPLOAD_BATCH = 10
    for start in range(0, len(points), UPLOAD_BATCH):
        batch = points[start : start + UPLOAD_BATCH]
        qdrant.upsert(collection_name=COLLECTION_NAME, points=batch)
        print(f"  Uploaded points {start}–{start + len(batch) - 1}")

    count = qdrant.count(collection_name=COLLECTION_NAME).count
    print(f"\nDONE! {count} theory passages now in Qdrant collection '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    main()
