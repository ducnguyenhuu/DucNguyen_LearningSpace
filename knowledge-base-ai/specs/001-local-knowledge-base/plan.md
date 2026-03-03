# Implementation Plan: Local Knowledge Base Application

**Branch**: `001-local-knowledge-base` | **Date**: 2026-03-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-local-knowledge-base/spec.md`

## Summary

Build a local knowledge base application (similar to NotebookLM) with two phases: (1) document ingestion — parsing Word/MD/PDF files, chunking, embedding via a distilled model, and storing in a vector database; (2) conversational querying — a React web chatbot that retrieves relevant context via similarity search and generates answers using a local distilled LLM. The architecture uses a provider abstraction layer to enable future migration to commercial embedding/LLM APIs (Claude, Copilot).

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript + React 18 (frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy, ChromaDB, sentence-transformers, Ollama, React, Vite  
**Storage**: ChromaDB (vector embeddings), SQLite via SQLAlchemy (documents, conversations, messages) — PostgreSQL for server deployment  
**Testing**: pytest + React Testing Library + Vitest  
**Target Platform**: Local desktop (macOS/Linux/Windows); server deployment via Docker Compose  
**Project Type**: Web application (React frontend + FastAPI backend)  
**Performance Goals**: Ingest 50 docs (500 pages) in <30 min; answer queries in <30s; summaries in <60s  
**Constraints**: <6.5GB peak RAM, offline-capable after initial model download, 8GB minimum system  
**Scale/Scope**: Single-user local deployment; ~50-200 documents; ~1000 conversations  
**Network Binding**: `127.0.0.1` by default (FR-020); configurable via `HOST` env var for LAN/server access  
**Concurrency**: Single ingestion job at a time (FR-022); concurrent requests return `409 Conflict`  
**Path Safety**: Source folder paths validated for existence, directory type, and symlink resolution (FR-023)  
**Model Versioning**: On startup, compare stored embedding model version with configured model; auto re-embed if mismatch (FR-021)

## Constitution Check

Constitution v1.0.0 ratified 2026-03-02. The following gates
apply to every implementation task:

| # | Gate | Constitution Principle | Verification |
|---|------|----------------------|--------------|
| 1 | Layer separation | I. Production-Grade Architecture | Each module has single responsibility; parsers/services/providers/routes are independent |
| 2 | REST boundary | II. REST API Contract Boundary | All frontend↔backend communication via `/api/v1/` endpoints |
| 3 | Provider abstraction | III. Provider Abstraction | Embedding + LLM behind ABC interfaces; factory resolves from config |
| 4 | Structured logging | IV. Structured Observability | All logs JSON via structlog; request_id on every request |
| 5 | UI performance | V. Lightweight & User-Friendly UI | Pages interactive < 2s; feedback on all long-running ops |
| 6 | Incremental delivery | VI. Incremental Delivery | Each user story independently testable and deployable |
| 7 | Type safety | Development Workflow | mypy (Python) + tsc --noEmit (TypeScript) pass before merge |
| 8 | Test coverage | Development Workflow | Coverage MUST NOT decrease; integration test covers full RAG pipeline |

## Project Structure

### Documentation (this feature)

```text
specs/001-local-knowledge-base/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Technology research & model selection
├── data-model.md        # Phase 1: Entity models & relationships
├── quickstart.md        # Phase 1: Setup & deployment guide
├── contracts/
│   ├── api-contracts.md      # Phase 1: REST + WebSocket API contracts
│   └── frontend-contract.md  # Phase 1: UI component & routing contracts
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
knowledge-base-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point + CORS + lifespan
│   │   ├── config.py                # Pydantic Settings from .env
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── ingestion.py     # POST /ingestion/start, GET/WS progress
│   │   │   │   ├── documents.py     # CRUD /documents
│   │   │   │   ├── conversations.py # CRUD /conversations
│   │   │   │   ├── chat.py          # POST messages, WS streaming
│   │   │   │   ├── summary.py       # POST/GET /documents/{id}/summary
│   │   │   │   └── system.py        # GET /health, /config
│   │   │   └── deps.py              # FastAPI Depends (DB session, services)
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── document.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   ├── document_summary.py
│   │   │   └── ingestion_job.py
│   │   ├── services/                # Business logic
│   │   │   ├── ingestion.py         # Parse → chunk → embed → store pipeline
│   │   │   ├── embedding.py         # Embedding generation (delegates to provider)
│   │   │   ├── retrieval.py         # Top-K + threshold similarity search
│   │   │   ├── chat.py              # RAG orchestration with sliding window
│   │   │   ├── summary.py           # Iterative document summarization
│   │   │   └── model_manager.py     # Model download, health, warm-up
│   │   ├── providers/               # Abstraction layer (FR-013)
│   │   │   ├── base.py              # ABC: EmbeddingProvider, LLMProvider
│   │   │   ├── local_embedding.py   # sentence-transformers implementation
│   │   │   ├── local_llm.py         # Ollama HTTP client implementation
│   │   │   ├── openai_embedding.py  # Future: OpenAI API adapter
│   │   │   ├── claude_llm.py        # Future: Claude API adapter
│   │   │   └── factory.py           # Config → provider instance resolver
│   │   ├── parsers/                 # Document format extractors
│   │   │   ├── base.py              # ABC: DocumentParser
│   │   │   ├── pdf_parser.py        # PyMuPDF extraction
│   │   │   ├── docx_parser.py       # python-docx extraction
│   │   │   ├── markdown_parser.py   # Markdown text extraction
│   │   │   └── chunker.py           # Text splitter (size + overlap + boundaries)
│   │   ├── db/
│   │   │   ├── database.py          # SQLAlchemy engine, session factory
│   │   │   └── vector_store.py      # ChromaDB collection manager
│   │   └── core/
│   │       ├── logging.py           # Structured JSON logging (structlog)
│   │       └── exceptions.py        # Domain exception hierarchy
│   ├── alembic/                     # DB migrations
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_parsers.py
│   │   │   ├── test_chunker.py
│   │   │   ├── test_services.py
│   │   │   └── test_providers.py
│   │   ├── integration/
│   │   │   ├── test_ingestion.py
│   │   │   ├── test_chat.py
│   │   │   └── test_api.py
│   │   └── conftest.py
│   ├── requirements.txt
│   ├── .env.example
│   └── alembic.ini
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ChatView.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentDetail.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   ├── SourcePanel.tsx
│   │   │   │   └── ConversationSidebar.tsx
│   │   │   ├── documents/
│   │   │   │   ├── DocumentTable.tsx
│   │   │   │   ├── IngestionProgress.tsx
│   │   │   │   └── SummaryView.tsx
│   │   │   └── common/
│   │   │       ├── Layout.tsx
│   │   │       ├── Navbar.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── websocket.ts
│   │   │   └── types.ts
│   │   └── hooks/
│   │       ├── useChat.ts
│   │       ├── useDocuments.ts
│   │       └── useIngestion.ts
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── data/                            # gitignored
│   ├── chromadb/
│   └── knowledge_base.db
│
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

**Structure Decision**: Web application with separate `backend/` (Python/FastAPI) and `frontend/` (React/TypeScript) directories. This cleanly separates concerns, allows independent deployment, and matches the user's explicit preference for React frontend + Python backend.

## Key Design Decisions

### 1. Provider Abstraction Pattern

The `providers/` directory implements the Strategy pattern:

```
EmbeddingProvider (ABC)          LLMProvider (ABC)
  ├── embed(text) → vector         ├── generate(prompt, context) → str
  └── embed_batch(texts) → list    └── stream(prompt, context) → AsyncIterator[str]

LocalEmbeddingProvider            LocalLLMProvider
  (sentence-transformers)           (Ollama HTTP API)

OpenAIEmbeddingProvider           ClaudeLLMProvider
  (future)                          (future)
```

`factory.py` reads `EMBEDDING_PROVIDER` and `LLM_PROVIDER` from config and instantiates the correct class. Adding a new provider = 1 new file + 1 factory mapping.

### 2. RAG Pipeline Flow

```
User Question
     │
     ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Embed Query │───▶│ Vector Search │───▶│ Build Prompt│
│  (Provider)  │    │ (ChromaDB)   │    │ + Context   │
└─────────────┘    └──────────────┘    └──────┬──────┘
                                               │
                   ┌──────────────┐    ┌───────▼──────┐
                   │ Store + Send │◀───│ LLM Generate │
                   │  (DB + WS)  │    │  (Provider)  │
                   └──────────────┘    └──────────────┘
```

### 3. Logging Strategy

- **Library**: `structlog` with JSON output for machine-parseable logs
- **Levels**: INFO (normal ops), WARNING (skipped files, low disk), ERROR (parse failures, model errors)
- **Context fields**: `job_id`, `document_id`, `conversation_id`, `file_name`, `duration_ms`
- **Output**: stdout (for Docker/server) + rotating file (for local development)
- **Correlation**: Each request gets a `request_id` propagated through all log entries

### 4. Deployment Strategy

**Local Development**:
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev` (Vite dev server with proxy)
- Ollama: Running as local service
- SQLite for database

**Server Deployment (Docker Compose)**:
- Backend container: FastAPI + Uvicorn + Gunicorn
- Frontend container: Nginx serving React production build
- Ollama container: GPU-optional inference
- PostgreSQL container: Production database
- Shared volumes: ChromaDB data, model cache

### 5. Startup Model Version Check (FR-021)

On application startup, `model_manager.py` performs:

```
App Startup
    │
    ▼
┌──────────────────────┐
│ Read EMBEDDING_MODEL  │
│ from config (.env)    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐     ┌─────────────────┐
│ Query any ChromaDB   │────▶│ Compare versions │
│ vector's model_version│     └────────┬────────┘
└──────────────────────┘              │
                              ┌───────┴───────┐
                              │  Match?        │
                         Yes  │               │ No
                              ▼               ▼
                         [No action]    [Create IngestionJob
                                         trigger_reason='reembed'
                                         Re-embed all docs
                                         in background]
```

- **IngestionJob** has `trigger_reason` field: `user` (manual) or `reembed` (auto)
- Frontend notified via WebSocket `reembed_started` message + polling `/health` endpoint `reembedding` field
- Re-embedding runs at normal ingestion priority — user can still chat while it runs
- Search results may return mixed old/new embeddings during re-embed; acceptable for single-user local use

### 6. Security & Operational Defaults

- **Network binding** (FR-020): `HOST=127.0.0.1` prevents accidental LAN exposure; override for Docker/server
- **Single ingestion job** (FR-022): In-memory lock or DB status check; returns `409 Conflict` if busy
- **Path validation** (FR-023): `os.path.realpath()` resolves symlinks → validate `os.path.isdir()` → validate readable
- **Crash recovery** (FR-005): Documents with `status='processing'` or `status='pending'` are re-processed on next ingestion run
- **Conversation clear** (FR-024): Individual delete (CASCADE to messages) + bulk "clear all" with confirmation; permanent deletion, no soft-delete

## Complexity Tracking

No constitutional violations — no complexity justifications needed.
