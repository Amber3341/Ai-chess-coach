"""
Generate high-quality chess theory passages using Gemini and save them to
scripts/generated_theory.py for ingestion into Qdrant.

Run once:
    python scripts/generate_theory.py

This script will:
  1. Call Gemini for each topic in TOPICS with a coaching-focused prompt
  2. Validate the returned passage (length, chess coherence)
  3. Write all passages to scripts/generated_theory.py as a Python list
  4. You then re-run scripts/ingest_theory.py to push everything to Qdrant

Design goals for generated passages:
  - 80-130 words each (sweet spot for RAG coaching context)
  - Direct coaching voice ("When you see X, do Y")
  - Covers gaps in existing corpus: defensive technique, piece trading,
    stalemate, opening→middlegame transition, clock management, etc.
  - Includes concrete move examples where relevant
"""
import os
import sys
import time
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai.errors import ClientError

# ── Output file ─────────────────────────────────────────────────────────────
OUTPUT_FILE = Path(__file__).parent / "generated_theory.py"

# ── Gemini model ─────────────────────────────────────────────────────────────
GENERATION_MODEL = "gemini-2.5-flash"  # confirmed working model in this project

# ── Rate limiting (free tier: ~15 RPM for generation) ────────────────────────
REQUESTS_PER_MINUTE = 12   # conservative headroom
SLEEP_BETWEEN = 60 / REQUESTS_PER_MINUTE   # ~5 s per request

# ── Topic list ───────────────────────────────────────────────────────────────
# Each entry: (topic_string, phase_hint, category_hint)
# phase_hint  → "opening" | "middlegame" | "endgame" | "general"
# category_hint → used only for the prompt, not stored

TOPICS: list[tuple[str, str, str]] = [

    # ── DEFENSIVE TECHNIQUE ───────────────────────────────────────────────────
    ("how to build a fortress draw in the endgame when you are a piece down",
     "endgame", "defensive technique"),
    ("using perpetual check as a saving resource when losing",
     "endgame", "defensive technique"),
    ("defending against a pawn storm when the opponent has castled on the opposite side",
     "middlegame", "defensive technique"),
    ("how to set up a stalemate trap when you are losing to win a draw",
     "endgame", "defensive technique"),
    ("defending passively with a rook — when to check and when to sit tight",
     "endgame", "defensive technique"),
    ("the principle of active defense — counterattacking instead of just defending",
     "middlegame", "defensive technique"),
    ("defending a bad bishop endgame — how to hold a draw with the wrong-colored bishop",
     "endgame", "defensive technique"),

    # ── PIECE TRADING DECISIONS ───────────────────────────────────────────────
    ("when to trade pieces and when to keep them on the board",
     "middlegame", "piece trading"),
    ("why trading your bad bishop for the opponent's good knight is winning",
     "middlegame", "piece trading"),
    ("when NOT to trade queens even if material is equal — keeping the queen for attack",
     "middlegame", "piece trading"),
    ("trading rooks to enter a won pawn endgame — knowing when the rook trade wins",
     "endgame", "piece trading"),
    ("the danger of trading into an opposite-colored bishop endgame when you are ahead",
     "endgame", "piece trading"),
    ("why simplifying into an endgame is wrong when you have the initiative",
     "middlegame", "piece trading"),

    # ── OPENING TO MIDDLEGAME TRANSITION ─────────────────────────────────────
    ("how to transition from the opening to the middlegame — what to do after development is complete",
     "opening", "transition"),
    ("identifying your middlegame plan based on the pawn structure in the opening",
     "opening", "transition"),
    ("what to do when your opponent deviates from opening theory",
     "opening", "transition"),
    ("completing development before attacking — why premature attacks fail",
     "opening", "transition"),
    ("how to handle a gambit correctly — accepting or declining and what comes next",
     "opening", "transition"),

    # ── MIDDLEGAME PLANNING FOR BEGINNERS ────────────────────────────────────
    ("how to make a plan in the middlegame when you do not know what to do",
     "middlegame", "planning"),
    ("the principle of improving your worst piece in the middlegame",
     "middlegame", "planning"),
    ("how to create a target to attack in the middlegame",
     "middlegame", "planning"),
    ("when to open the position and when to keep it closed in the middlegame",
     "middlegame", "planning"),
    ("how to use space advantage in the middlegame practically",
     "middlegame", "planning"),
    ("dealing with a cramped position — how to relieve pressure and free your pieces",
     "middlegame", "planning"),

    # ── STALEMATE TRAPS (FROM THE WINNING SIDE) ──────────────────────────────
    ("how to avoid giving stalemate in queen vs pawn endgames",
     "endgame", "stalemate avoidance"),
    ("stalemate trap in rook endgames — how the losing side sets it and how to avoid it",
     "endgame", "stalemate avoidance"),
    ("why advancing pawns too quickly can stalemate the opponent's king accidentally",
     "endgame", "stalemate avoidance"),
    ("the bishop-pawn stalemate trick — when a7 or a2 pawn promotes to stalemate",
     "endgame", "stalemate avoidance"),

    # ── COMMON BLUNDER PATTERNS ───────────────────────────────────────────────
    ("why hanging pieces happen and how to check for them before every move",
     "general", "blunder prevention"),
    ("back-rank weakness — how to create luft and avoid back-rank checkmates",
     "middlegame", "blunder prevention"),
    ("the danger of moving your king too early in the middlegame — why it gets attacked",
     "middlegame", "blunder prevention"),
    ("why moving a pinned piece can lose immediately — respecting absolute pins",
     "middlegame", "blunder prevention"),
    ("how to avoid blunders under time pressure — a practical checklist before moving",
     "general", "blunder prevention"),
    ("why counting defenders and attackers before every capture prevents material loss",
     "general", "blunder prevention"),

    # ── TACTICAL VISION ────────────────────────────────────────────────────────
    ("how to scan for tactical shots before making a move — a systematic approach",
     "general", "tactical vision"),
    ("recognizing when you should calculate deeply versus trust a positional move",
     "middlegame", "tactical vision"),
    ("how to spot a combination — recognizing forcing moves, checks, captures and threats",
     "middlegame", "tactical vision"),
    ("when sacrifices are correct — judging whether a piece sacrifice leads to checkmate or compensation",
     "middlegame", "tactical vision"),

    # ── ENDGAME: KING AND PAWN SPECIFICS ──────────────────────────────────────
    ("the concept of key squares in pawn endgames — how to reach them with the king",
     "endgame", "king and pawn"),
    ("pawn races — using the square of the pawn to judge if you can catch a passed pawn",
     "endgame", "king and pawn"),
    ("rook pawn endgames — why the defending king runs to the corner and draws",
     "endgame", "king and pawn"),
    ("how to convert a king and two pawns versus king — avoiding stalemate while promoting",
     "endgame", "king and pawn"),
    ("the wrong-rook-pawn and wrong-colored bishop endgame — why it is always a draw",
     "endgame", "king and pawn"),

    # ── ENDGAME: ROOK SPECIFICS ────────────────────────────────────────────────
    ("cutting off the king with the rook — how to restrict king mobility in rook endgames",
     "endgame", "rook endgame"),
    ("the seventh rank rook — how to get there and why it is so powerful",
     "endgame", "rook endgame"),
    ("rook vs two pawns — when the rook wins and when the pawns hold",
     "endgame", "rook endgame"),

    # ── ADVANCED STRATEGY ──────────────────────────────────────────────────────
    ("how to exploit a good knight vs bad bishop advantage step by step",
     "middlegame", "advanced strategy"),
    ("the concept of prophylaxis — stopping the opponent's plan proactively",
     "middlegame", "advanced strategy"),
    ("how to use the initiative — keeping pressure so the opponent can never consolidate",
     "middlegame", "advanced strategy"),
    ("when to push and when to consolidate — reading the position before committing",
     "middlegame", "advanced strategy"),
    ("converting small advantages — the technique of creating and exploiting a second weakness",
     "endgame", "advanced strategy"),
    ("strategic piece exchange — trading your passive piece for the opponent's active one",
     "middlegame", "advanced strategy"),

    # ── OPENING SPECIFIC TRAPS AND ERRORS ─────────────────────────────────────
    ("the most common opening mistake — developing the knight to the rim (Na3 or Nh3)",
     "opening", "opening error"),
    ("why pushing the f-pawn early (f4 or f5) can weaken the king fatally",
     "opening", "opening error"),
    ("the danger of early queen moves — how the opponent gains tempo attacking your queen",
     "opening", "opening error"),
    ("why not castling by move 12 is dangerous — the risk of a king stuck in the center",
     "opening", "opening error"),
    ("how to punish early h6 or a6 moves by the opponent — using the tempo advantage",
     "opening", "opening error"),
]


# ── Prompt factory ────────────────────────────────────────────────────────────

def build_prompt(topic: str, phase: str, category: str) -> str:
    return textwrap.dedent(f"""
        You are an expert chess coach writing a knowledge-base entry for a chess coaching AI.

        Topic: {topic}
        Game phase: {phase}
        Category: {category}

        Write a single chess coaching passage following these rules:
        - Length: exactly 80 to 130 words (count carefully).
        - Voice: direct coaching advice addressed to the player ("When you...", "Your job is...").
        - Structure: (1) briefly explain the concept, (2) say when it applies, (3) give a concrete action or example move.
        - Include at least one specific chess move or position example (e.g., "Rook to d1", "Nd5 blockade", "h3 prophylaxis").
        - No bullet points, no headers. One flowing paragraph only.
        - Do NOT start with "In chess" or "Chess is". Start with the concept or a direct coaching statement.
        - Do NOT repeat the topic word-for-word as the first sentence.

        Return ONLY the passage text. No title, no label, no quotes around it.
    """).strip()


# ── Validation ────────────────────────────────────────────────────────────────

def validate_passage(text: str) -> tuple[bool, str]:
    """Return (is_valid, reason). Passage must be 60-180 words."""
    words = len(text.split())
    if words < 60:
        return False, f"too short ({words} words)"
    if words > 180:
        return False, f"too long ({words} words)"
    if text.startswith('"') or text.startswith("'"):
        return False, "starts with a quote character"
    return True, "ok"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set in .env")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    passages: list[str] = []
    failed: list[tuple[str, str]] = []   # (topic, reason)

    total = len(TOPICS)
    print(f"Generating {total} passages using {GENERATION_MODEL}...\n")

    for idx, (topic, phase, category) in enumerate(TOPICS, 1):
        label = f"[{idx:02d}/{total}]"
        print(f"{label} {category.upper()} — {topic[:65]}...")

        prompt = build_prompt(topic, phase, category)

        retries = 3
        passage_text: str | None = None

        for attempt in range(1, retries + 1):
            try:
                response = client.models.generate_content(
                    model=GENERATION_MODEL,
                    contents=prompt,
                )
                raw = response.text.strip()
                # Strip surrounding quotes if model added them
                if raw.startswith('"') and raw.endswith('"'):
                    raw = raw[1:-1].strip()
                elif raw.startswith("'") and raw.endswith("'"):
                    raw = raw[1:-1].strip()

                valid, reason = validate_passage(raw)
                if valid:
                    passage_text = raw
                    word_count = len(raw.split())
                    print(f"         [OK] {word_count} words")
                    break
                else:
                    print(f"         [invalid] attempt {attempt}: {reason}")
                    if attempt < retries:
                        time.sleep(2)

            except ClientError as e:
                msg = str(e)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    wait = 30 * attempt
                    print(f"         [wait] rate limit -- sleeping {wait}s (attempt {attempt})")
                    time.sleep(wait)
                else:
                    print(f"         [error] ClientError: {e}")
                    break
            except Exception as e:
                print(f"         [error] unexpected: {e}")
                break

        if passage_text:
            passages.append(passage_text)
        else:
            failed.append((topic, "all attempts failed"))
            print(f"         [SKIPPED] could not generate a valid passage")

        # Rate-limit sleep between requests
        if idx < total:
            time.sleep(SLEEP_BETWEEN)

    # ── Write output file ──────────────────────────────────────────────────────
    print(f"\nWriting {len(passages)} passages to {OUTPUT_FILE} ...")

    header = textwrap.dedent(f"""\
        \"\"\"
        Auto-generated chess theory passages for RAG.
        Created by: scripts/generate_theory.py
        Model used: {GENERATION_MODEL}
        Total passages: {len(passages)}

        DO NOT EDIT MANUALLY — re-run scripts/generate_theory.py to regenerate.
        After updating this file, re-run scripts/ingest_theory.py to push to Qdrant.
        \"\"\"

        CHESS_THEORY_GENERATED: list[str] = [
    """)

    lines = [header]
    for p in passages:
        # Escape internal quotes and wrap in triple-quoted string for readability
        escaped = p.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'    "{escaped}",\n')
    lines.append("]\n")

    OUTPUT_FILE.write_text("".join(lines), encoding="utf-8")

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"DONE — {len(passages)}/{total} passages generated successfully.")
    if failed:
        print(f"\nFailed topics ({len(failed)}):")
        for topic, reason in failed:
            print(f"  - {topic[:70]} ({reason})")
    print(f"\nNext step: run  python scripts/ingest_theory.py  to push to Qdrant.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
