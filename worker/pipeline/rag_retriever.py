"""
RAG retriever module.
Connects to Qdrant and retrieves relevant chess theory passages
based on a query (e.g., game phase + critical move description).
"""
from __future__ import annotations

import logging
from api.config import get_settings
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

logger = logging.getLogger(__name__)


COLLECTION_NAME = "chess-theory"
_client: QdrantClient | None = None
_genai_client: genai.Client | None = None


def _get_qdrant() -> QdrantClient | None:
    global _client
    if _client is not None:
        return _client
    settings = get_settings()
    if not settings.qdrant_url:
        return None
    _client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )
    return _client


def _get_genai() -> genai.Client | None:
    global _genai_client
    if _genai_client is not None:
        return _genai_client
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    _genai_client = genai.Client(api_key=settings.gemini_api_key)
    return _genai_client


def _embed(text: str) -> list[float] | None:
    client = _get_genai()
    if not client:
        return None
    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )
        return result.embeddings[0].values
    except Exception as e:
        logger.error(f"[RAG] Embedding error: {e}")
        return None


def retrieve(query: str, top_k: int = 3) -> list[str]:
    """
    Retrieve top_k relevant chess theory passages for the given query.
    Returns empty list if Qdrant/Gemini is not configured or any error occurs.
    """
    qdrant = _get_qdrant()
    if not qdrant:
        return []

    settings = get_settings()
    collection = settings.qdrant_collection

    # Check collection exists
    try:
        existing = [c.name for c in qdrant.get_collections().collections]
        if collection not in existing:
            logger.warning(f"[RAG] Collection '{collection}' not found. Run scripts/ingest_theory.py first.")
            return []
    except Exception as e:
        logger.error(f"[RAG] Qdrant connection error: {e}")
        return []

    # Embed query
    vector = _embed(query)
    if not vector:
        return []

    # Search
    try:
        results: list[ScoredPoint] = qdrant.query_points(
            collection_name=collection,
            query=vector,
            limit=top_k,
        ).points
        return [r.payload["text"] for r in results if r.payload and "text" in r.payload]
    except Exception as e:
        logger.error(f"[RAG] Search error: {e}")
        return []
