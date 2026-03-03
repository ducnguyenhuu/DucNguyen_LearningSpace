"""FastAPI dependency injection utilities.

Provides singleton-scoped dependencies for:
- Database session (per-request)
- VectorStore (singleton)
- EmbeddingProvider (singleton)
- LLMProvider (singleton)
- ModelManager (singleton)
- Business services (created from singletons)

All singletons are initialised on first request after startup.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.vector_store import VectorStore
from app.providers.base import EmbeddingProvider, LLMProvider
from app.providers.factory import create_embedding_provider, create_llm_provider

# ---------------------------------------------------------------------------
# Singleton instances (module-level — initialised once at startup)
# ---------------------------------------------------------------------------
_vector_store: VectorStore | None = None
_embedding_provider: EmbeddingProvider | None = None
_llm_provider: LLMProvider | None = None


def init_singletons() -> None:
    """Create all singleton instances.  Call once in FastAPI lifespan."""
    global _vector_store, _embedding_provider, _llm_provider  # noqa: PLW0603
    _vector_store = VectorStore()
    _embedding_provider = create_embedding_provider()
    _llm_provider = create_llm_provider()


def get_singleton_vector_store() -> VectorStore:
    """Return the singleton VectorStore (must call init_singletons first)."""
    if _vector_store is None:
        raise RuntimeError("VectorStore not initialised — call init_singletons()")
    return _vector_store


def get_singleton_embedding_provider() -> EmbeddingProvider:
    if _embedding_provider is None:
        raise RuntimeError("EmbeddingProvider not initialised — call init_singletons()")
    return _embedding_provider


def get_singleton_llm_provider() -> LLMProvider:
    if _llm_provider is None:
        raise RuntimeError("LLMProvider not initialised — call init_singletons()")
    return _llm_provider


# ---------------------------------------------------------------------------
# FastAPI Depends factories
# ---------------------------------------------------------------------------


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a per-request async database session."""
    async with get_async_session() as session:  # type: ignore[attr-defined]
        yield session


def get_vector_store() -> VectorStore:
    """Return the singleton VectorStore for use as a FastAPI dependency."""
    return get_singleton_vector_store()


def get_embedding_provider() -> EmbeddingProvider:
    """Return the singleton EmbeddingProvider for use as a FastAPI dependency."""
    return get_singleton_embedding_provider()


def get_llm_provider() -> LLMProvider:
    """Return the singleton LLMProvider for use as a FastAPI dependency."""
    return get_singleton_llm_provider()


# ---------------------------------------------------------------------------
# Annotated type aliases for clean route signatures
# ---------------------------------------------------------------------------

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
EmbProvider = Annotated[EmbeddingProvider, Depends(get_embedding_provider)]
LlmProv = Annotated[LLMProvider, Depends(get_llm_provider)]
VStore = Annotated[VectorStore, Depends(get_vector_store)]
