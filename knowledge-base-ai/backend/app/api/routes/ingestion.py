"""Ingestion REST routes — POST /ingestion/start, GET /ingestion/status/{job_id}.

WebSocket /ingestion/progress/{job_id} is implemented in T038.

Route contracts: api-contracts.md §1.1, §1.2
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession, EmbProvider, VStore
from app.config import settings
from app.core.exceptions import IngestionJobNotFoundError, PathValidationError
from app.core.logging import get_logger
from app.models.ingestion_job import IngestionJob
from app.parsers import Chunker
from app.services.embedding import EmbeddingService
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class StartIngestionRequest(BaseModel):
    """Body for POST /ingestion/start."""

    source_folder: Optional[str] = Field(
        default=None,
        description="Absolute path to the documents folder. "
        "Defaults to the configured knowledge_folder if omitted.",
    )


class StartIngestionResponse(BaseModel):
    """202 response body for POST /ingestion/start."""

    job_id: str
    status: str
    total_files: int
    source_folder: str
    started_at: datetime


class IngestionStatusResponse(BaseModel):
    """200 response body for GET /ingestion/status/{job_id}."""

    job_id: str
    status: str
    total_files: int
    processed_files: int
    new_files: int
    modified_files: int
    deleted_files: int
    skipped_files: int
    source_folder: str
    started_at: datetime
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Background task runner (owns its own DB session)
# ---------------------------------------------------------------------------


async def _run_pipeline_in_background(job_id: str) -> None:
    """Background task: fetch the job and run the full ingestion pipeline.

    Creates its own DB session so it is not bound to the HTTP request
    session (which closes when the 202 response is sent).
    """
    from app.api.deps import get_singleton_embedding_provider, get_singleton_vector_store
    from app.db.database import get_session

    async with get_session() as db:
        result = await db.execute(
            select(IngestionJob).where(IngestionJob.id == job_id)
        )
        job = result.scalars().first()
        if job is None:
            log.error("background_job_not_found", job_id=job_id)
            return

        embed_svc = EmbeddingService(get_singleton_embedding_provider())
        chunker = Chunker.from_settings(settings)
        svc = IngestionService(
            db=db,
            vector_store=get_singleton_vector_store(),
            embedding_service=embed_svc,
            chunker=chunker,
        )
        try:
            await svc.run_pipeline(job)
        except Exception:
            # run_pipeline already committed the failure status and logged the error
            pass


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post(
    "/start",
    status_code=202,
    summary="Start document ingestion (FR-005, FR-022, FR-023)",
    response_model=StartIngestionResponse,
)
async def start_ingestion(
    body: StartIngestionRequest,
    background_tasks: BackgroundTasks,
    db: DbSession,
    vector_store: VStore,
    embedding_provider: EmbProvider,
) -> StartIngestionResponse:
    """Trigger ingestion from the knowledge folder.

    Pre-flight checks performed synchronously before returning 202:
    - Disk space validation (400 if insufficient)
    - Path validation — existence, directory, readable, symlink resolved (400)
    - Single-job enforcement — 409 if a job is already running

    The actual parse → chunk → embed → store pipeline runs as a background
    task after the 202 is returned to the client.
    """
    source_folder = body.source_folder or settings.knowledge_folder
    if not source_folder:
        raise PathValidationError(
            path="",
            reason="no source_folder provided and knowledge_folder is not configured",
        )

    embed_svc = EmbeddingService(embedding_provider)
    chunker = Chunker.from_settings(settings)

    svc = IngestionService(
        db=db,
        vector_store=vector_store,
        embedding_service=embed_svc,
        chunker=chunker,
    )

    job = await svc.start_ingestion(source_folder)
    await db.commit()

    background_tasks.add_task(_run_pipeline_in_background, job.id)

    log.info(
        "ingestion_start_accepted",
        job_id=job.id,
        source_folder=job.source_folder,
    )

    return StartIngestionResponse(
        job_id=job.id,
        status=job.status,
        total_files=job.total_files,
        source_folder=job.source_folder,
        started_at=job.started_at,
    )


@router.get(
    "/status/{job_id}",
    summary="Get ingestion job status",
    response_model=IngestionStatusResponse,
)
async def get_ingestion_status(
    job_id: str,
    db: DbSession,
) -> IngestionStatusResponse:
    """Return the current status of an ingestion job.

    Raises 404 if the job_id does not exist.
    """
    result = await db.execute(
        select(IngestionJob).where(IngestionJob.id == job_id)
    )
    job = result.scalars().first()

    if job is None:
        raise IngestionJobNotFoundError(job_id=job_id)

    return IngestionStatusResponse(
        job_id=job.id,
        status=job.status,
        total_files=job.total_files,
        processed_files=job.processed_files,
        new_files=job.new_files,
        modified_files=job.modified_files,
        deleted_files=job.deleted_files,
        skipped_files=job.skipped_files,
        source_folder=job.source_folder,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )
