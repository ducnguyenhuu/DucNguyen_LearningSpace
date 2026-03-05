"""Unit tests for backend service layer.

Coverage includes (per Constitution §VII):
- EmbeddingService: single embed, batch embed, model_version tagging, validation,
  error wrapping, property delegation.
- IngestionService helpers: validate_folder_path, check_disk_space, scan_folder,
  compute_sha256.
- IngestionService: single-job enforcement, start_ingestion pre-flight,
  run_pipeline (new/modified/deleted/unchanged/crash-resume detection).

Additional service tests (chat, retrieval, summary) will be added
here as the corresponding service modules are implemented (T037–T041).
"""
from __future__ import annotations

import pytest

from app.core.exceptions import AppError, ModelUnavailableError
from app.providers.base import EmbeddingProvider
from app.services.embedding import EmbeddingResult, EmbeddingService


# ---------------------------------------------------------------------------
# Mock provider helpers
# ---------------------------------------------------------------------------

DIM = 4  # small dimension for fast tests
_MODEL = "test-embed-v1"


class _StubEmbeddingProvider(EmbeddingProvider):
    """Minimal EmbeddingProvider that returns predictable fake vectors."""

    def __init__(
        self,
        model_version: str = _MODEL,
        dimensions: int = DIM,
        raise_on_embed: Exception | None = None,
    ) -> None:
        self._model_version = model_version
        self._dimensions = dimensions
        self._raise_on_embed = raise_on_embed

    async def embed(self, text: str) -> list[float]:
        if self._raise_on_embed is not None:
            raise self._raise_on_embed
        # vector length equals text length, clipped to DIM
        return [float(ord(c) % 10) for c in text[:self._dimensions]][:self._dimensions] + [0.0] * max(0, self._dimensions - len(text))

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if self._raise_on_embed is not None:
            raise self._raise_on_embed
        return [await self.embed(t) for t in texts]

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def dimensions(self) -> int:
        return self._dimensions


def _make_service(**kwargs: object) -> EmbeddingService:
    return EmbeddingService(_StubEmbeddingProvider(**kwargs))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# EmbeddingResult dataclass
# ---------------------------------------------------------------------------


class TestEmbeddingResult:
    def test_fields_stored(self) -> None:
        r = EmbeddingResult(vector=[1.0, 0.0], model_version="v1", text_length=5)
        assert r.vector == [1.0, 0.0]
        assert r.model_version == "v1"
        assert r.text_length == 5

    def test_frozen(self) -> None:
        r = EmbeddingResult(vector=[1.0], model_version="v1", text_length=1)
        with pytest.raises((AttributeError, TypeError)):
            r.model_version = "v2"  # type: ignore[misc]

    def test_equality(self) -> None:
        r1 = EmbeddingResult(vector=[1.0, 2.0], model_version="v1", text_length=3)
        r2 = EmbeddingResult(vector=[1.0, 2.0], model_version="v1", text_length=3)
        assert r1 == r2

    def test_inequality_different_vector(self) -> None:
        r1 = EmbeddingResult(vector=[1.0], model_version="v1", text_length=1)
        r2 = EmbeddingResult(vector=[2.0], model_version="v1", text_length=1)
        assert r1 != r2


# ---------------------------------------------------------------------------
# EmbeddingService construction
# ---------------------------------------------------------------------------


class TestEmbeddingServiceConstruction:
    def test_init_stores_provider(self) -> None:
        provider = _StubEmbeddingProvider()
        svc = EmbeddingService(provider)
        assert svc._provider is provider

    def test_model_version_delegates(self) -> None:
        svc = _make_service(model_version="custom-model-v2")
        assert svc.model_version == "custom-model-v2"

    def test_dimensions_delegates(self) -> None:
        svc = _make_service(dimensions=768)
        assert svc.dimensions == 768


# ---------------------------------------------------------------------------
# EmbeddingService.embed
# ---------------------------------------------------------------------------


class TestEmbeddingServiceEmbed:
    async def test_returns_embedding_result(self) -> None:
        svc = _make_service()
        result = await svc.embed("hello")
        assert isinstance(result, EmbeddingResult)

    async def test_vector_has_correct_dimensions(self) -> None:
        svc = _make_service(dimensions=DIM)
        result = await svc.embed("hi")
        assert len(result.vector) == DIM

    async def test_model_version_tagged(self) -> None:
        svc = _make_service(model_version="nomic-embed-text-v1.5")
        result = await svc.embed("some text")
        assert result.model_version == "nomic-embed-text-v1.5"

    async def test_text_length_recorded(self) -> None:
        svc = _make_service()
        text = "hello world"
        result = await svc.embed(text)
        assert result.text_length == len(text)

    async def test_empty_string_raises_value_error(self) -> None:
        svc = _make_service()
        with pytest.raises(ValueError, match="non-empty"):
            await svc.embed("")

    async def test_whitespace_only_raises_value_error(self) -> None:
        svc = _make_service()
        with pytest.raises(ValueError, match="non-empty"):
            await svc.embed("   ")

    async def test_app_error_re_raised_unchanged(self) -> None:
        """ModelUnavailableError (AppError subclass) must propagate as-is."""
        exc = ModelUnavailableError(model="test-model", reason="offline")
        svc = _make_service(raise_on_embed=exc)
        with pytest.raises(ModelUnavailableError):
            await svc.embed("test")

    async def test_generic_exception_wrapped_as_app_error(self) -> None:
        svc = _make_service(raise_on_embed=RuntimeError("crash"))
        with pytest.raises(AppError, match="Embedding failed"):
            await svc.embed("test")

    async def test_vector_elements_are_floats(self) -> None:
        svc = _make_service()
        result = await svc.embed("abc")
        assert all(isinstance(v, float) for v in result.vector)


# ---------------------------------------------------------------------------
# EmbeddingService.embed_batch
# ---------------------------------------------------------------------------


class TestEmbeddingServiceEmbedBatch:
    async def test_returns_list_of_embedding_results(self) -> None:
        svc = _make_service()
        results = await svc.embed_batch(["foo", "bar", "baz"])
        assert len(results) == 3
        assert all(isinstance(r, EmbeddingResult) for r in results)

    async def test_order_preserved(self) -> None:
        """Each result's text_length must correspond to its input."""
        svc = _make_service()
        texts = ["a", "hello", "world!"]
        results = await svc.embed_batch(texts)
        for r, t in zip(results, texts):
            assert r.text_length == len(t)

    async def test_all_tagged_with_same_model_version(self) -> None:
        svc = _make_service(model_version="model-x")
        results = await svc.embed_batch(["alpha", "beta"])
        assert all(r.model_version == "model-x" for r in results)

    async def test_empty_list_raises_value_error(self) -> None:
        svc = _make_service()
        with pytest.raises(ValueError, match="must not be empty"):
            await svc.embed_batch([])

    async def test_element_empty_string_raises_value_error(self) -> None:
        svc = _make_service()
        with pytest.raises(ValueError, match="texts\\[1\\]"):
            await svc.embed_batch(["valid", ""])

    async def test_element_whitespace_only_raises_value_error(self) -> None:
        svc = _make_service()
        with pytest.raises(ValueError, match="texts\\[0\\]"):
            await svc.embed_batch(["   ", "valid"])

    async def test_app_error_re_raised_unchanged(self) -> None:
        exc = ModelUnavailableError(model="x", reason="down")
        svc = _make_service(raise_on_embed=exc)
        with pytest.raises(ModelUnavailableError):
            await svc.embed_batch(["text"])

    async def test_generic_exception_wrapped_as_app_error(self) -> None:
        svc = _make_service(raise_on_embed=OSError("io"))
        with pytest.raises(AppError, match="Batch embedding failed"):
            await svc.embed_batch(["text"])

    async def test_single_text_batch(self) -> None:
        svc = _make_service()
        results = await svc.embed_batch(["only one"])
        assert len(results) == 1
        assert results[0].text_length == len("only one")

    async def test_vectors_have_correct_dimension(self) -> None:
        svc = _make_service(dimensions=DIM)
        results = await svc.embed_batch(["a", "b"])
        assert all(len(r.vector) == DIM for r in results)


# ===========================================================================
# Ingestion service — helper functions (pure / near-pure, no DB needed)
# ===========================================================================

import hashlib
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.exceptions import IngestionConflictError, PathValidationError
from app.models.document import Document
from app.models.ingestion_job import IngestionJob
from app.services.ingestion import (
    IngestionService,
    _ScannedFile,
    check_disk_space,
    compute_sha256,
    scan_folder,
    validate_folder_path,
)


# ---------------------------------------------------------------------------
# validate_folder_path
# ---------------------------------------------------------------------------


class TestValidateFolderPath:
    def test_empty_string_raises(self) -> None:
        with pytest.raises(PathValidationError, match="must not be empty"):
            validate_folder_path("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(PathValidationError, match="must not be empty"):
            validate_folder_path("   ")

    def test_nonexistent_path_raises(self, tmp_path: Path) -> None:
        with pytest.raises(PathValidationError, match="does not exist"):
            validate_folder_path(str(tmp_path / "ghost"))

    def test_file_path_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("hello")
        with pytest.raises(PathValidationError, match="not a directory"):
            validate_folder_path(str(f))

    def test_valid_directory_returns_resolved(self, tmp_path: Path) -> None:
        result = validate_folder_path(str(tmp_path))
        assert result == str(tmp_path.resolve())

    def test_symlink_resolved(self, tmp_path: Path) -> None:
        real_dir = tmp_path / "real"
        real_dir.mkdir()
        link = tmp_path / "link"
        link.symlink_to(real_dir)
        result = validate_folder_path(str(link))
        assert result == str(real_dir.resolve())


# ---------------------------------------------------------------------------
# check_disk_space
# ---------------------------------------------------------------------------


class TestCheckDiskSpace:
    def test_enough_space_does_not_raise(self, tmp_path: Path) -> None:
        # Require 1 MB — virtually always available
        check_disk_space(str(tmp_path), min_mb=1)

    def test_insufficient_space_raises_app_error(self, tmp_path: Path) -> None:
        from app.core.exceptions import AppError

        # Require an absurdly large amount to guarantee failure
        with pytest.raises(AppError, match="Insufficient disk space"):
            check_disk_space(str(tmp_path), min_mb=999_999_999)

    def test_insufficient_space_raises_400(self, tmp_path: Path) -> None:
        from app.core.exceptions import AppError

        with pytest.raises(AppError) as exc_info:
            check_disk_space(str(tmp_path), min_mb=999_999_999)
        assert exc_info.value.status_code == 400

    def test_oserror_is_non_fatal(self, tmp_path: Path) -> None:
        """If disk_usage raises OSError, check_disk_space should not raise."""
        with patch("shutil.disk_usage", side_effect=OSError("no device")):
            check_disk_space(str(tmp_path), min_mb=500)  # must NOT raise


# ---------------------------------------------------------------------------
# compute_sha256
# ---------------------------------------------------------------------------


class TestComputeSha256:
    def test_returns_64_char_hex(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_bytes(b"hello")
        digest = compute_sha256(str(f))
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_deterministic(self, tmp_path: Path) -> None:
        f = tmp_path / "b.txt"
        f.write_bytes(b"constant content")
        assert compute_sha256(str(f)) == compute_sha256(str(f))

    def test_different_content_different_hash(self, tmp_path: Path) -> None:
        f1 = tmp_path / "c1.txt"
        f2 = tmp_path / "c2.txt"
        f1.write_bytes(b"aaa")
        f2.write_bytes(b"bbb")
        assert compute_sha256(str(f1)) != compute_sha256(str(f2))

    def test_matches_stdlib(self, tmp_path: Path) -> None:
        content = b"test content for sha256"
        f = tmp_path / "d.txt"
        f.write_bytes(content)
        expected = hashlib.sha256(content).hexdigest()
        assert compute_sha256(str(f)) == expected


# ---------------------------------------------------------------------------
# scan_folder
# ---------------------------------------------------------------------------


class TestScanFolder:
    def test_empty_folder_returns_empty(self, tmp_path: Path) -> None:
        assert scan_folder(str(tmp_path)) == []

    def test_returns_supported_files(self, tmp_path: Path) -> None:
        (tmp_path / "doc.pdf").write_bytes(b"%PDF")
        (tmp_path / "note.md").write_text("# Hello")
        results = scan_folder(str(tmp_path))
        names = {r.file_name for r in results}
        assert "doc.pdf" in names
        assert "note.md" in names

    def test_skips_unsupported_extensions(self, tmp_path: Path) -> None:
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        (tmp_path / "data.csv").write_text("a,b,c")
        (tmp_path / "doc.pdf").write_bytes(b"%PDF")
        results = scan_folder(str(tmp_path))
        names = {r.file_name for r in results}
        assert "image.png" not in names
        assert "data.csv" not in names
        assert "doc.pdf" in names

    def test_scans_subdirectories(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.md").write_text("# Nested")
        results = scan_folder(str(tmp_path))
        names = {r.file_name for r in results}
        assert "nested.md" in names

    def test_result_has_correct_extension(self, tmp_path: Path) -> None:
        (tmp_path / "doc.docx").write_bytes(b"PK\x03\x04")
        results = scan_folder(str(tmp_path))
        assert results[0].extension == ".docx"

    def test_result_has_file_hash(self, tmp_path: Path) -> None:
        f = tmp_path / "note.md"
        f.write_text("content")
        results = scan_folder(str(tmp_path))
        assert len(results[0].file_hash) == 64

    def test_result_has_file_size(self, tmp_path: Path) -> None:
        f = tmp_path / "small.md"
        f.write_bytes(b"abc")
        results = scan_folder(str(tmp_path))
        assert results[0].file_size_bytes == 3

    def test_xlsx_included(self, tmp_path: Path) -> None:
        (tmp_path / "sheet.xlsx").write_bytes(b"PK\x03\x04")
        results = scan_folder(str(tmp_path))
        assert any(r.extension == ".xlsx" for r in results)


# ---------------------------------------------------------------------------
# IngestionService (mocked DB + dependencies)
# ---------------------------------------------------------------------------


def _make_ingestion_service(
    *,
    running_job: IngestionJob | None = None,
    existing_docs: list[Document] | None = None,
    min_disk_space_mb: int = 1,
) -> tuple[IngestionService, AsyncMock, MagicMock, MagicMock]:
    """Return (service, mock_db, mock_vector_store, mock_embed_service)."""
    db = AsyncMock()

    # Simulate db.execute returning a scalars().all() result
    scalar_result = MagicMock()
    scalar_result.scalars.return_value.first.return_value = running_job
    scalar_result.scalars.return_value.all.return_value = existing_docs or []
    db.execute = AsyncMock(return_value=scalar_result)
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.add = MagicMock()
    db.delete = MagicMock()

    vector_store = MagicMock()
    vector_store.delete_by_document_id = AsyncMock()
    vector_store.add_chunks = AsyncMock()

    embed_svc = MagicMock()
    embed_svc.embed_batch = AsyncMock(return_value=[])

    chunker = MagicMock()
    chunker.chunk = MagicMock(return_value=[])

    svc = IngestionService(
        db=db,
        vector_store=vector_store,
        embedding_service=embed_svc,
        chunker=chunker,
        min_disk_space_mb=min_disk_space_mb,
    )
    return svc, db, vector_store, embed_svc


class TestIngestionServiceConflictCheck:
    async def test_no_running_job_passes(self, tmp_path: Path) -> None:
        svc, *_ = _make_ingestion_service(running_job=None)
        # Should not raise — creates job
        job = await svc.start_ingestion(str(tmp_path))
        assert job.status == "running"

    async def test_running_job_raises_conflict(self, tmp_path: Path) -> None:
        running = IngestionJob(
            id="existing-job",
            source_folder=str(tmp_path),
            trigger_reason="user",
            status="running",
        )
        from datetime import UTC, datetime
        running.started_at = datetime.now(UTC)
        svc, *_ = _make_ingestion_service(running_job=running)
        with pytest.raises(IngestionConflictError):
            await svc.start_ingestion(str(tmp_path))


class TestIngestionServiceStartIngestion:
    async def test_invalid_path_raises_path_validation_error(self) -> None:
        svc, *_ = _make_ingestion_service(running_job=None)
        with pytest.raises(PathValidationError):
            await svc.start_ingestion("/nonexistent/ghost/folder")

    async def test_returns_running_job(self, tmp_path: Path) -> None:
        svc, db, *_ = _make_ingestion_service(running_job=None)
        job = await svc.start_ingestion(str(tmp_path))
        assert job.status == "running"
        assert job.source_folder == str(tmp_path.resolve())
        db.add.assert_called_once_with(job)
        db.flush.assert_called()

    async def test_trigger_reason_stored(self, tmp_path: Path) -> None:
        svc, *_ = _make_ingestion_service(running_job=None)
        job = await svc.start_ingestion(str(tmp_path), trigger_reason="reembed")
        assert job.trigger_reason == "reembed"

    async def test_low_disk_space_raises(self, tmp_path: Path) -> None:
        from app.core.exceptions import AppError

        svc, *_ = _make_ingestion_service(running_job=None, min_disk_space_mb=999_999_999)
        with pytest.raises(AppError, match="Insufficient disk space"):
            await svc.start_ingestion(str(tmp_path))


class TestIngestionPipelineFileDetection:
    """Tests for new / modified / deleted / unchanged detection in run_pipeline."""

    def _make_doc(
        self,
        *,
        file_path: str,
        file_hash: str = "aaa",
        status: str = "completed",
        tmp_path: Path | None = None,
    ) -> Document:
        from datetime import UTC, datetime

        d = Document(
            file_path=file_path,
            file_name=Path(file_path).name,
            file_type="md",
            file_hash=file_hash,
            file_size_bytes=10,
            status=status,
        )
        d.ingested_at = datetime.now(UTC)
        return d

    async def test_new_file_is_added_to_db(self, tmp_path: Path) -> None:
        (tmp_path / "new.md").write_text("# Hello")

        db = AsyncMock()
        scalar_result = MagicMock()
        # First call: check no running job → None; second call: load existing docs → []
        scalar_result.scalars.return_value.first.return_value = None
        scalar_result.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=scalar_result)
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.add = MagicMock()
        db.delete = MagicMock()

        vector_store = MagicMock()
        vector_store.delete_by_document_id = AsyncMock()
        vector_store.add_chunks = AsyncMock()

        from app.services.embedding import EmbeddingResult

        embed_svc = MagicMock()
        embed_svc.embed_batch = AsyncMock(return_value=[
            EmbeddingResult(vector=[0.1, 0.2], model_version="v1", text_length=5)
        ])

        from app.parsers import Chunker, TextChunk

        chunker = MagicMock()
        fake_chunk = MagicMock(spec=TextChunk)
        fake_chunk.text = "Hello"
        fake_chunk.chunk_index = 0
        fake_chunk.page_number = None
        chunker.chunk = MagicMock(return_value=[fake_chunk])

        svc = IngestionService(
            db=db,
            vector_store=vector_store,
            embedding_service=embed_svc,
            chunker=chunker,
            min_disk_space_mb=1,
        )

        job = IngestionJob(
            id="job-1",
            source_folder=str(tmp_path),
            trigger_reason="user",
            status="running",
        )
        from datetime import UTC, datetime
        job.started_at = datetime.now(UTC)
        job.processed_files = 0
        job.new_files = 0
        job.modified_files = 0
        job.deleted_files = 0
        job.skipped_files = 0
        job.total_files = 0

        await svc.run_pipeline(job)

        # new Document was added to the session
        db.add.assert_called()
        # vectors were stored
        vector_store.add_chunks.assert_called_once()
        assert job.processed_files == 1
        assert job.status == "completed"

    async def test_deleted_file_removes_doc_and_vectors(self, tmp_path: Path) -> None:
        """A document in DB whose file_path is NOT on disk should be deleted."""
        ghost_path = str(tmp_path / "ghost.md")  # file does NOT exist on disk

        existing_doc = self._make_doc(file_path=ghost_path, file_hash="old")

        db = AsyncMock()
        scalar_result = MagicMock()
        scalar_result.scalars.return_value.first.return_value = None
        scalar_result.scalars.return_value.all.return_value = [existing_doc]
        db.execute = AsyncMock(return_value=scalar_result)
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.add = MagicMock()
        db.delete = MagicMock()

        vector_store = MagicMock()
        vector_store.delete_by_document_id = AsyncMock()
        vector_store.add_chunks = AsyncMock()

        embed_svc = MagicMock()
        embed_svc.embed_batch = AsyncMock(return_value=[])

        chunker = MagicMock()
        chunker.chunk = MagicMock(return_value=[])

        svc = IngestionService(
            db=db,
            vector_store=vector_store,
            embedding_service=embed_svc,
            chunker=chunker,
            min_disk_space_mb=1,
        )

        job = IngestionJob(
            id="job-2",
            source_folder=str(tmp_path),
            trigger_reason="user",
            status="running",
        )
        from datetime import UTC, datetime
        job.started_at = datetime.now(UTC)
        job.processed_files = 0
        job.new_files = 0
        job.modified_files = 0
        job.deleted_files = 0
        job.skipped_files = 0
        job.total_files = 0

        await svc.run_pipeline(job)

        # ghost document was deleted from DB and its vectors removed
        db.delete.assert_called_once_with(existing_doc)
        vector_store.delete_by_document_id.assert_called_once_with(existing_doc.id)
        assert job.deleted_files == 1

    async def test_unchanged_file_skipped(self, tmp_path: Path) -> None:
        """A completed doc with matching hash must not be re-processed."""
        md_file = tmp_path / "same.md"
        md_file.write_text("# Same")
        real_hash = compute_sha256(str(md_file))

        existing_doc = self._make_doc(
            file_path=str(md_file.resolve()),
            file_hash=real_hash,
            status="completed",
        )

        db = AsyncMock()
        scalar_result = MagicMock()
        scalar_result.scalars.return_value.first.return_value = None
        scalar_result.scalars.return_value.all.return_value = [existing_doc]
        db.execute = AsyncMock(return_value=scalar_result)
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.add = MagicMock()
        db.delete = MagicMock()

        vector_store = MagicMock()
        vector_store.delete_by_document_id = AsyncMock()
        vector_store.add_chunks = AsyncMock()

        embed_svc = MagicMock()
        embed_svc.embed_batch = AsyncMock(return_value=[])

        chunker = MagicMock()

        svc = IngestionService(
            db=db,
            vector_store=vector_store,
            embedding_service=embed_svc,
            chunker=chunker,
            min_disk_space_mb=1,
        )

        job = IngestionJob(
            id="job-3",
            source_folder=str(tmp_path),
            trigger_reason="user",
            status="running",
        )
        from datetime import UTC, datetime
        job.started_at = datetime.now(UTC)
        job.processed_files = 0
        job.new_files = 0
        job.modified_files = 0
        job.deleted_files = 0
        job.skipped_files = 0
        job.total_files = 0

        await svc.run_pipeline(job)

        # Nothing was added, deleted, or embedded
        db.add.assert_not_called()
        db.delete.assert_not_called()
        vector_store.add_chunks.assert_not_called()
        assert job.processed_files == 0
        assert job.total_files == 0

    async def test_crash_resume_reprocesses_processing_doc(self, tmp_path: Path) -> None:
        """A doc stuck in 'processing' (crash) must be re-processed."""
        md_file = tmp_path / "resume.md"
        md_file.write_text("# Resume")
        real_hash = compute_sha256(str(md_file))

        # Simulate doc left in processing state from a previous crash
        existing_doc = self._make_doc(
            file_path=str(md_file.resolve()),
            file_hash=real_hash,  # same hash, not modified — it's a resume
            status="processing",
        )

        db = AsyncMock()
        scalar_result = MagicMock()
        scalar_result.scalars.return_value.first.return_value = None
        scalar_result.scalars.return_value.all.return_value = [existing_doc]
        db.execute = AsyncMock(return_value=scalar_result)
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.add = MagicMock()
        db.delete = MagicMock()

        vector_store = MagicMock()
        vector_store.delete_by_document_id = AsyncMock()
        vector_store.add_chunks = AsyncMock()

        from app.services.embedding import EmbeddingResult

        embed_svc = MagicMock()
        embed_svc.embed_batch = AsyncMock(return_value=[
            EmbeddingResult(vector=[0.1], model_version="v1", text_length=6)
        ])

        from app.parsers import Chunker, TextChunk

        chunker = MagicMock()
        fake_chunk = MagicMock(spec=TextChunk)
        fake_chunk.text = "Resume"
        fake_chunk.chunk_index = 0
        fake_chunk.page_number = None
        chunker.chunk = MagicMock(return_value=[fake_chunk])

        svc = IngestionService(
            db=db,
            vector_store=vector_store,
            embedding_service=embed_svc,
            chunker=chunker,
            min_disk_space_mb=1,
        )

        job = IngestionJob(
            id="job-4",
            source_folder=str(tmp_path),
            trigger_reason="user",
            status="running",
        )
        from datetime import UTC, datetime
        job.started_at = datetime.now(UTC)
        job.processed_files = 0
        job.new_files = 0
        job.modified_files = 0
        job.deleted_files = 0
        job.skipped_files = 0
        job.total_files = 0

        await svc.run_pipeline(job)

        # Old stale vectors deleted and new ones added
        vector_store.delete_by_document_id.assert_called_once()
        vector_store.add_chunks.assert_called_once()
        assert job.processed_files == 1
        assert existing_doc.status == "completed"
