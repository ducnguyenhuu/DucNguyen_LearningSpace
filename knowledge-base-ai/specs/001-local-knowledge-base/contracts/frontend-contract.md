# Frontend Interface Contract: React Web Application

**Feature**: 001-local-knowledge-base  
**Date**: 2026-03-02

---

## 1. Pages / Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `Dashboard` | Landing page — quick stats, recent conversations, ingestion status |
| `/chat` | `ChatView` | Main conversational interface |
| `/chat/:conversationId` | `ChatView` | Continue existing conversation |
| `/documents` | `DocumentList` | Browse ingested documents, trigger ingestion |
| `/documents/:documentId` | `DocumentDetail` | Document details + summary |
| `/settings` | `Settings` | Configuration (model provider, chunk size, etc.) |

---

## 2. Core UI Components

### 2.1 Chat Interface

```
┌─────────────────────────────────────────────┐
│  ┌──────────┐                    ┌────────┐ │
│  │Sidebar   │  Chat Area         │ Sources│ │
│  │          │                    │ Panel  │ │
│  │ + New    │  ┌───────────────┐ │        │ │
│  │ 🗑 Clear  │  │ Message #1    │ │ doc1   │ │
│  │ Conv 1 ◄─│  │ (user)        │ │ p.12   │ │
│  │ Conv 2   │  └───────────────┘ │        │ │
│  │ Conv 3   │  ┌───────────────┐ │ doc2   │ │
│  │          │  │ Message #2    │ │ p.5    │ │
│  │          │  │ (assistant)   │ │        │ │
│  │          │  │ [citations]   │ │        │ │
│  │          │  └───────────────┘ │        │ │
│  │          │                    │        │ │
│  │          │  ┌───────────────┐ │        │ │
│  │          │  │ Input box   ▶ │ │        │ │
│  │          │  └───────────────┘ │        │ │
│  └──────────┘                    └────────┘ │
└─────────────────────────────────────────────┘
```

**Behaviors**:
- Conversation sidebar: scrollable list sorted by `updated_at` DESC
- "New Chat" button at top of sidebar
- "Clear All" button in sidebar: shows confirmation dialog before calling DELETE /conversations (FR-024)
- Individual conversation: swipe-to-delete or context menu with "Delete" option; shows confirmation
- After clearing all or deleting the active conversation: redirect to a new empty chat session
- Message area: auto-scrolls to latest message
- Assistant messages: render markdown, show clickable source citations
- Source panel: shows relevant documents when a citation is clicked
- Input box: submit on Enter, Shift+Enter for newline
- Streaming: tokens appear incrementally via WebSocket

### 2.2 Document Management

```
┌─────────────────────────────────────────────┐
│ Documents                    [▶ Run Ingest ] │
│ ─────────────────────────────────────────── │
│ ┌─────────────────────────────────────────┐ │
│ │ Progress Bar (if ingesting)             │ │
│ │ █████████░░░░░░░░ 12/25 files          │ │
│ │ Current: architecture-guide.pdf         │ │
│ │ Est. remaining: 3 min                   │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌──────────┬──────┬────────┬─────────────┐ │
│ │ Name     │ Type │ Chunks │ Actions     │ │
│ ├──────────┼──────┼────────┼─────────────┤ │
│ │ arch.pdf │ PDF  │ 42     │ 📄 Summary  │ │
│ │ api.md   │ MD   │ 15     │ 📄 Summary  │ │
│ │ spec.docx│ DOCX │ 28     │ 📄 Summary  │ │
│ └──────────┴──────┴────────┴─────────────┘ │
└─────────────────────────────────────────────┘
```

**Behaviors**:
- "Run Ingest" button triggers POST /ingestion/start
- Progress bar appears during ingestion via WebSocket
- Each document row shows summary button
- Click document name → DocumentDetail page
- Summary button → triggers POST /documents/{id}/summary

### 2.3 Dashboard

```
┌─────────────────────────────────────────────┐
│ Knowledge Base                              │
│ ─────────────────────────────────────────── │
│ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│ │ 25 Docs  │ │ 5 Chats  │ │ Models: OK ✓│ │
│ └──────────┘ └──────────┘ └──────────────┘ │
│                                             │
│ Recent Conversations          Quick Actions │
│ ├─ Architecture Q&A (2h ago)  [+ New Chat]  │
│ ├─ API Design (1d ago)        [Ingest Docs] │
│ └─ Setup Guide (3d ago)       [Settings]    │
└─────────────────────────────────────────────┘
```

---

## 3. State Management

| State Slice | Contents | Persistence |
|-------------|----------|-------------|
| `conversations` | List of conversations, current conversation messages | Server (API calls) |
| `documents` | List of documents, ingestion status | Server (API calls) |
| `chat` | Current input, streaming state, pending message | In-memory |
| `ingestion` | Active job status, progress | WebSocket + polling |
| `ui` | Sidebar open/closed, active panel, theme | localStorage |

---

## 4. Real-Time Communication

| Channel | Type | Purpose |
|---------|------|---------|
| `/api/v1/ingestion/progress/{job_id}` | WebSocket | Ingestion progress updates |
| `/api/v1/conversations/{id}/stream` | WebSocket | Streaming LLM responses |

---

## 5. Responsive Breakpoints

| Breakpoint | Layout |
|------------|--------|
| Desktop (≥1024px) | 3-column: sidebar + chat + sources |
| Tablet (768-1023px) | 2-column: sidebar collapses to icons + chat |
| Mobile (<768px) | 1-column: tabs for sidebar/chat/sources |

---

## 6. Error Handling & Boundaries

Per Constitution Principle I (Production-Grade Architecture), every error MUST be surfaced appropriately:

| Scenario | UI Behavior |
|----------|-------------|
| API request fails (network) | Toast notification with retry option; no silent failures |
| API returns 4xx/5xx | Display error message from `error.message` field; include `request_id` for support |
| WebSocket disconnects | Auto-reconnect with exponential backoff; show "Reconnecting..." banner |
| LLM unavailable (503) | Disable chat input; show "Model unavailable" status with retry |
| Ingestion file error | Show inline error in progress list; continue processing remaining files |
| Auto re-embedding (FR-021) | Show persistent info banner: "Re-embedding documents due to model update..." with progress; link to ingestion progress page |
| Unhandled exception | React Error Boundary catches and renders fallback UI with "Report Issue" option |

**React Error Boundary**: Wrap each route-level component in an Error Boundary. Log caught errors to console with `request_id` context when available.
