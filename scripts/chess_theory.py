"""
Chess theory corpus for RAG — full combined list.

Sources:
  - CHESS_THEORY_PART1  : openings and tactical motifs (~130 passages)
  - CHESS_THEORY_PART2  : pawn structure, endgames, advanced strategy (~104 passages)
  - CHESS_THEORY_GENERATED : LLM-generated coaching passages covering gap topics
                             (empty until you run scripts/generate_theory.py)

Note: _ORIGINAL has been retired — it was a strict near-duplicate subset of
Part 1 + Part 2 but with shorter, lower-quality passages. Removing it reduces
vector-space noise and frees Qdrant slots for the richer generated passages.

To grow the corpus:
  1.  python scripts/generate_theory.py     # generates scripts/generated_theory.py
  2.  python scripts/ingest_theory.py       # embeds + uploads everything to Qdrant
"""
from scripts.chess_theory_part1 import CHESS_THEORY_PART1
from scripts.chess_theory_part2 import CHESS_THEORY_PART2
from scripts.generated_theory import CHESS_THEORY_GENERATED

# Full combined corpus — dict-trick deduplicates exact-string duplicates while
# preserving insertion order (Part1 → Part2 → Generated).
CHESS_THEORY = list(
    {p: None for p in (CHESS_THEORY_PART1 + CHESS_THEORY_PART2 + CHESS_THEORY_GENERATED)}.keys()
)

