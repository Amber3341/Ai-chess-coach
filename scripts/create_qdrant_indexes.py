"""
One-time script to create payload indexes on the Qdrant chess-theory collection
for 'phase' and 'topic' fields, enabling fast filtered retrieval.

Run after ingest_theory.py:
    python scripts/create_qdrant_indexes.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

COLLECTION_NAME = "chess-theory"


def main() -> None:
    qdrant_url = os.environ.get("QDRANT_URL")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")

    if not qdrant_url:
        print("ERROR: QDRANT_URL not set in .env")
        sys.exit(1)

    print(f"Connecting to Qdrant at {qdrant_url}...")
    qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key or None)

    for field in ("phase", "topic"):
        print(f"  Creating keyword index on '{field}'...")
        qdrant.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=field,
            field_schema=PayloadSchemaType.KEYWORD,
        )
        print(f"  OK: Index created for '{field}'")

    print("\nDONE! Phase and topic payload indexes are ready.")
    print("Filtered RAG retrieval will now work correctly.")


if __name__ == "__main__":
    main()
