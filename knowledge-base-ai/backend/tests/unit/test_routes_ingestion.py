"""Unit tests for ingestion REST routes.

Tests HTTP contracts per api-contracts.md §1.1 and §1.2:
- POST /api/v1/ingestion/start → 202 / 400 / 409 / 422
- GET  /api/v1/ingestion/status/{job_id} → 200 / 404

All database, vector store, and embedding provider dependencies are
replaced with lightweight mocks via FastAPI dependency overrides so
these tests run without a real DB or model infrastructure.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db_session, get_embedding_provider, get_vector_store
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.main import app
from app.models.ingestion_job import IngestionJob
from app.providers.base import EmbeddingProvider

# Configure structlog once so the lifespan log.info() calls don't hit
# the default PrintLogger (which has no .name attribute).
configure_logging(level="WARNING", fmt="console")


# ---------------------------------------------------------------------------
# Helpers / stubs
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 3, 4, 12, 0, 0, tzinfo=UTC)


def _make_job(
    *,
    id: str = "job-abc",
    status: str = "running",
    source_folder: str = "/tmp/docs",
    total_files: int = 0,
    processed_files: int = 0,
    new_files: int = 0,
    modified_files: int = 0,
    deleted_files: int = 0,
    skipped_files: int = 0,
    completed_at: datetime | None = None,
) -> IngestionJob:
    job = IngestionJob(
        id=id,
        source_folder=source_folder,
        trigger_reason="user",
        status=status,
        total_files=total_files,
        processed_files=processed_files,
        new_files=new_files,
        modified_files=modified_files,
        deleted_files=deleted_files,
        skipped_files=skipped_files,
        started_at=_NOW,
    )
    job.completed_at = completed_at
    return job


class _StubProvider(EmbeddingProvider):
    async def embed(self, text: str) -> list[float]:
        return [0.0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] for _ in texts]

    @property
    def model_version(self) -> str:
        return "test-model"

    @property
    def dimensions(self) -> int:
        return 1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_db() -> AsyncMock:
    """A mock AsyncSession with no running jobs and no existing documents."""
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result)
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.add = MagicMock()
    db.delete = MagicMock()
    return db


@pytest.fixture
def client(mock_db: AsyncMock) -> TestClient:
    """TestClient with all external dependencies overridden.

    Patches out the lifespan's heavy startup calls (init_db, init_singletons,
    ModelManager.startup) so tests run without a real DB or model infra.
    """

    async def _override_db() -> AsyncGenerator:
        yield mock_db

    def _override_vs() -> MagicMock:
        vs = MagicMock()
        vs.delete_by_document_id = AsyncMock()
        vs.add_chunks = AsyncMock()
        return vs

    def _override_embed() -> _StubProvider:
        return _StubProvider()

    app.dependency_overrides[get_db_session] = _override_db
    app.dependency_overrides[get_vector_store] = _override_vs
    app.dependency_overrides[get_embedding_provider] = _override_embed

    with (
        patch("app.main.init_db", return_value=AsyncMock()),
        patch("app.main.init_singletons"),
        patch("app.main.close_db", return_value=AsyncMock()),
        patch("app.main.get_singleton_vector_store", return_value=MagicMock()),
        patch("app.main.get_singleton_embedding_provider", return_value=MagicMock()),
        patch("app.main.get_singleton_llm_provider", return_value=MagicMock()),
        patch("app.services.model_manager.ModelManager.startup", new_callable=AsyncMock),
        patch("app.api.routes.ingestion._run_pipeline_in_background"),
    ):
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/v1/ingestion/start — happy path
# ---------------------------------------------------------------------------


class TestStartIngestionHappyPath:
    def test_returns_202(self, client: TestClient, tmp_path: object) -> None:
        resp = client.post(
            "/api/v1/ingestion/start",
            json={"source_folder": str(tmp_path)},
        )
        assert resp.status_code == 202

    def test_response_has_job_id(self, client: TestClient, tmp_path: object) -> None:
        resp = client.post(
            "/api/v1/ingestion/start",
            json={"source_folder": str(tmp_path)},
        )
        body = resp.json()
        assert "job_id" in body
        assert isinstance(body["job_id"], str)

    def test_response_status_is_running(self, client: TestClient, tmp_path: object) -> None:
        resp = client.post(
            "/api/v1/ingestion/start",
            json={"source_folder": str(tmp_path)},
        )
        assert resp.json()["status"] == "running"

    def test_response_source_folder_is_resolved(
        self, client: TestClient, tmp_path: object
    ) -> None:
        import os

        resp = client.post(
            "/api/v1/ingestion/start",
            json={"source_folder": str(tmp_path)},
        )
        expected = os.path.realpath(str(tmp_path))
        assert resp.json()["source_folder"] == expected

    def test_response_has_started_at(self, client: TestClient, tmp_path: object) -> None:
        resp = client.post(
            "/api/v1/ingestion/start",
            json={"source_folder": str(tmp_path)},
        )
        assert "started_at" in resp.json()

    def test_request_id_header_present(self, client: TestClient, tmp_path: object) -> None:
        resp = client.post(
            "/api/v1/ingestion/start",
            json={"source_folder": str(tmp_path)},
        )
        assert "x-request-id" in resp.headers


# ---------------------------------------------------------------------------
# POST /api/v1/ingestion/start — error cases
# ---------------------------------------------------------------------------


class TestStartIngestionErrors:
    def test_nonexistent_path_returns_422(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/ingestion/start",
            json={"source_folder": "/nonexistent/ghost/folder"},
        )
        assert resp.status_code == 422

    def test_nonexistent_path_error_code(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/ingestion/start",
            json={"source_folder": "/nonexistent/ghost/folder"},
        )
        assert resp.json()["error"]["code"] == "path_validation_error"

    def test_file_path_returns_422(self, client: TestClient, tmp_path: object) -> None:
        f = tmp_path / "file.txt"
        f.write_text("hello")
        resp = client.post(
            "/api/v1/ingestion/start",
            json={"source_folder": str(f)},
        )
        assert resp.status_code == 422

    def test_conflict_returns_409(
        self, tmp_path: object, mock_db: AsyncMock
    ) -> None:
        """Returns 409 when a running job already exists."""
        running_job = _make_job(id="existing", status="running")
        # Override execute to return the running job for conflict check
        conflict_result = MagicMock()
        conflict_result.scalars.return_value.first.return_value = running_job
        mock_db.execute = AsyncMock(return_value=conflict_result)

        async def _override_db() -> AsyncGenerator:
            yield mock_db

        def _override_vs() -> MagicMock:
            return MagicMock()

        def _override_embed() -> _StubProvider:
            return _StubProvider()

        app.dependency_overrides[get_db_session] = _override_db
        app.dependency_overrides[get_vector_store] = _override_vs
        app.dependency_overrides[get_embedding_provider] = _override_embed

        try:
            with (
                patch("app.main.init_db", return_value=AsyncMock()),
                patch("app.main.init_singletons"),
                patch("app.main.close_db", return_value=AsyncMock()),
                patch("app.main.get_singleton_vector_store", return_value=MagicMock()),
                patch("app.main.get_singleton_embedding_provider", return_value=MagicMock()),
                patch("app.main.get_singleton_llm_provider", return_value=MagicMock()),
                patch("app.services.model_manager.ModelManager.startup", new_callable=AsyncMock),
                patch("app.api.routes.ingestion._run_pipeline_in_background"),
            ):
                with TestClient(app, raise_server_exceptions=False) as c:
                    resp = c.post(
                        "/api/v1/ingestion/start",
                        json={"source_folder": str(tmp_path)},
                    )
            assert resp.status_code == 409
            assert resp.json()["error"]["code"] == "ingestion_conflict"
        finally:
            app.dependency_overrides.clear()

    def test_no_folder_configured_returns_422(self, client: TestClient) -> None:
        """Returns 422 when source_folder omitted and knowledge_folder is not set."""
        with patch("app.api.routes.ingestion.settings") as mock_settings:
            mock_settings.knowledge_folder = ""
            resp = client.post("/api/v1/ingestion/start", json={})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/ingestion/status/{job_id}
# ---------------------------------------------------------------------------


class TestGetIngestionStatus:
    def _build_client_with_job(self, job: IngestionJob | None) -> TestClient:
        """Build a TestClient whose DB mock returns *job* for every execute call."""
        db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.first.return_value = job
        db.execute = AsyncMock(return_value=result)

        async def _override_db() -> AsyncGenerator:
            yield db

        app.dependency_overrides[get_db_session] = _override_db
        app.dependency_overrides[get_vector_store] = lambda: MagicMock()
        app.dependency_overrides[get_embedding_provider] = lambda: _StubProvider()

        patches = [
            patch("app.main.init_db", return_value=AsyncMock()),
            patch("app.main.init_singletons"),
            patch("app.main.close_db", return_value=AsyncMock()),
            patch("app.main.get_singleton_vector_store", return_value=MagicMock()),
            patch("app.main.get_singleton_embedding_provider", return_value=MagicMock()),
            patch("app.main.get_singleton_llm_provider", return_value=MagicMock()),
            patch(
                "app.services.model_manager.ModelManager.startup",
                new_callable=AsyncMock,
            ),
        ]
        for p in patches:
            p.start()
        self._active_patches = patches
        return TestClient(app, raise_server_exceptions=False)

    def teardown_method(self) -> None:  # noqa: D102
        for p in getattr(self, "_active_patches", []):
            p.stop()

    def test_existing_job_returns_200(self) -> None:
        job = _make_job(id="job-1", status="completed", total_files=5, processed_files=5)
        with self._build_client_with_job(job) as c:
            resp = c.get("/api/v1/ingestion/status/job-1")
        app.dependency_overrides.clear()
        assert resp.status_code == 200

    def test_response_contains_all_fields(self) -> None:
        job = _make_job(
            id="job-1",
            status="running",
            total_files=10,
            processed_files=3,
            new_files=2,
            modified_files=1,
            deleted_files=0,
            skipped_files=0,
        )
        with self._build_client_with_job(job) as c:
            resp = c.get("/api/v1/ingestion/status/job-1")
        app.dependency_overrides.clear()
        body = resp.json()
        assert body["job_id"] == "job-1"
        assert body["status"] == "running"
        assert body["total_files"] == 10
        assert body["processed_files"] == 3
        assert body["new_files"] == 2
        assert body["modified_files"] == 1
        assert body["deleted_files"] == 0
        assert body["skipped_files"] == 0
        assert body["completed_at"] is None

    def test_completed_job_has_completed_at(self) -> None:
        job = _make_job(
            id="job-2",
            status="completed",
            completed_at=_NOW,
        )
        with self._build_client_with_job(job) as c:
            resp = c.get("/api/v1/ingestion/status/job-2")
        app.dependency_overrides.clear()
        assert resp.json()["completed_at"] is not None

    def test_missing_job_returns_404(self) -> None:
        with self._build_client_with_job(None) as c:
            resp = c.get("/api/v1/ingestion/status/ghost-job")
        app.dependency_overrides.clear()
        assert resp.status_code == 404

    def test_missing_job_error_code(self) -> None:
        with self._build_client_with_job(None) as c:
            resp = c.get("/api/v1/ingestion/status/ghost-job")
        app.dependency_overrides.clear()
        assert resp.json()["error"]["code"] == "ingestion_job_not_found"

    def test_request_id_header_present(self) -> None:
        job = _make_job(id="job-x")
        with self._build_client_with_job(job) as c:
            resp = c.get("/api/v1/ingestion/status/job-x")
        app.dependency_overrides.clear()
        assert "x-request-id" in resp.headers
