"""
RAG retriever module.
Connects to Qdrant and retrieves relevant chess theory passages
based on a query (e.g., game phase + critical move description).

Optimizations applied:
  #3  - Collection-exists check cached at module level (no network round-trip per call)
  #6  - Embedding results cached with functools.lru_cache (avoids re-embedding identical queries)
  #13 - Filtered retrieval by phase tag when metadata is available
"""
from __future__ import annotations

import logging
from functools import lru_cache
from api.config import get_settings
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint, Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)

COLLECTION_NAME = "chess-theory"

# Module-level singletons
_client: QdrantClient | None = None
_genai_client: genai.Client | None = None
_collection_verified: bool = False

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

def _ensure_collection_exists(qdrant: QdrantClient, collection: str) -> bool:
    global _collection_verified
    if _collection_verified:
        return True
    try:
        collections = qdrant.get_collections().collections
        if not any(c.name == collection for c in collections):
            logger.warning("[RAG] Qdrant collection '%s' does not exist.", collection)
            return False
        _collection_verified = True
        return True
    except Exception as e:
        logger.error("[RAG] Failed to connect to Qdrant: %s", e)
        return False

@lru_cache(maxsize=256)
def _embed_cached(text: str) -> tuple[float, ...] | None:
    client = _get_genai()
    if client is None:
        return None
    try:
        response = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=text,
        )
        if not response.embeddings:
            return None
        vector = response.embeddings[0].values
        return tuple(vector)
    except Exception as e:
        logger.error("[RAG] Embedding error: %s", e)
        return None

def retrieve(query: str, top_k: int = 3, phase: str | None = None) -> list[str]:
    qdrant = _get_qdrant()
    if qdrant is None:
        return []

    if not _ensure_collection_exists(qdrant, COLLECTION_NAME):
        return []

    vector_tuple = _embed_cached(query)
    if not vector_tuple:
        return []
    vector = list(vector_tuple)

    query_filter: Filter | None = None
    if phase in ("opening", "middlegame", "endgame"):
        query_filter = Filter(
            must=[FieldCondition(key="phase", match=MatchValue(value=phase))]
        )

    if query_filter is not None:
        try:
            results: list[ScoredPoint] = qdrant.query_points(
                collection_name=COLLECTION_NAME,
                query=vector,
                query_filter=query_filter,
                limit=top_k,
            ).points
            passages = [r.payload["text"] for r in results if r.payload and "text" in r.payload]
            if passages:
                return passages
            logger.debug("[RAG] Phase-filtered search returned 0 results; falling back to unfiltered.")
        except Exception as e:
            logger.warning("[RAG] Phase-filtered search failed (%s); falling back to unfiltered.", e)

    try:
        results = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=top_k,
        ).points
        return [r.payload["text"] for r in results if r.payload and "text" in r.payload]
    except Exception as e:
        logger.error("[RAG] Search error: %s", e)
        return []
