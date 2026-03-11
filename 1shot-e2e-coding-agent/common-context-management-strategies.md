# Context Management Strategies for Large-Context AI Systems

> 5 universal strategies for managing large context — applicable to **code, documents, knowledge bases, legal corpora, research papers, and any large information system**.

---

## Table of Contents

- [1. The Core Problem](#1-the-core-problem)
- [2. The 5 Universal Strategies](#2-the-5-universal-strategies)
  - [Strategy 1: Structural Map (Skeleton / Index)](#strategy-1-structural-map-skeleton--index)
  - [Strategy 2: Keyword Search (Exact Match)](#strategy-2-keyword-search-exact-match)
  - [Strategy 3: Semantic Search (Vector / RAG)](#strategy-3-semantic-search-vector--rag)
  - [Strategy 4: Graph-Based Navigation (Relationships)](#strategy-4-graph-based-navigation-relationships)
  - [Strategy 5: Iterative Deepening with Token Budget](#strategy-5-iterative-deepening-with-token-budget)
- [3. Best Practice Workflow](#3-best-practice-workflow)
- [4. Strategy Comparison](#4-strategy-comparison)
- [5. Anti-Patterns](#5-anti-patterns)
- [6. Domain-Specific Extensions](#6-domain-specific-extensions)

---

## 1. The Core Problem

LLMs have finite context windows (128K–1M tokens). Real-world information systems are vastly larger. The challenge is **not** fitting everything into context — it's **selecting the right context**.

```
Your data:    10M+ tokens (codebase, doc corpus, knowledge base, etc.)
LLM context:  128K tokens

You can fit ~1%. The question: WHICH 1%?
```

| Scenario | Example Size | Context Challenge |
|----------|-------------|-------------------|
| Large codebase | 500K+ LOC (~2M tokens) | Find the 5-10 files that matter |
| Legal document corpus | 10K+ documents | Find the 3-5 clauses that apply |
| Research knowledge base | 50K+ papers | Find the 10-20 papers relevant to a question |
| Enterprise documentation | 5K+ pages | Find the specific policy/process needed |
| Customer support logs | 1M+ tickets | Find similar past resolutions |

**The same 5 strategies solve all of these.**

---

## 2. The 5 Universal Strategies

### Strategy 1: Structural Map (Skeleton / Index)

> **"Know what exists before diving deep."**

**Concept:** Create a lightweight, high-level summary of your entire corpus — a table of contents, skeleton, or index. This fits in minimal tokens and gives the LLM a "birds-eye view" to decide where to look deeper.

#### How It Applies Across Domains

| Domain | Structural Map Looks Like |
|--------|--------------------------|
| **Code** | File list + function/class signatures (no bodies). ~2-8K tokens for 100K LOC. |
| **Documents** | Document titles + section headings + first sentence of each section. |
| **Legal** | Contract index: clause titles + parties + dates. |
| **Research** | Paper titles + abstracts + keyword tags. |
| **Knowledge base** | Topic hierarchy + article titles + summaries. |

#### Tools & Libraries

| Tool | Domain | Description |
|------|--------|-------------|
| [tree-sitter](https://github.com/tree-sitter/tree-sitter) | Code | Parse AST → extract signatures for 100+ languages |
| [universal-ctags](https://github.com/universal-ctags/ctags) | Code | Fast symbol indexing for 130+ languages |
| [Aider repo-map](https://github.com/paul-gauthier/aider) | Code | Repo map with PageRank file ranking |
| [Unstructured](https://github.com/Unstructured-IO/unstructured) | Documents | Extract structure from PDFs, HTML, Docx, etc. |
| [docling](https://github.com/DS4SD/docling) | Documents | IBM's document parser — tables, figures, sections |
| Custom metadata index | Any | JSON/SQLite index of titles, tags, dates, relationships |

#### Example: Code Skeleton

```python
# ~3K tokens for an entire repo
# src/auth/routes.py
class AuthRouter:
    def login(request: LoginRequest) -> TokenResponse: ...
    def logout(request: Request) -> None: ...

# src/auth/service.py
class AuthService:
    def authenticate(email: str, password: str) -> User: ...
```

#### Example: Document Skeleton

```markdown
# Company Policies (127 documents)
├── HR/
│   ├── onboarding.md — "New employee onboarding process" (3 sections)
│   ├── pto-policy.md — "Paid time off policy" (5 sections)
│   └── remote-work.md — "Remote work guidelines" (4 sections)
├── Engineering/
│   ├── code-review.md — "Code review process and standards" (6 sections)
│   └── incident-response.md — "On-call and incident handling" (8 sections)
└── Legal/
    ├── privacy-policy.md — "User data privacy policy" (12 sections)
    └── terms-of-service.md — "Terms of service v3.2" (15 sections)
```

#### Key Principle

- **Always present in context** (Layer 0).
- Token cost: very low (~1-5% of budget).
- Purpose: let the LLM decide where to look next.

---

### Strategy 2: Keyword Search (Exact Match)

> **"When you know what word to look for, find it fast."**

**Concept:** Search for exact strings, names, identifiers, error messages, or specific terms. This is the highest-precision retrieval method — if the term exists, you'll find it.

#### How It Applies Across Domains

| Domain | What You Search For |
|--------|-------------------|
| **Code** | Function names, error messages, variable names, config keys |
| **Documents** | Policy names, product names, specific terms ("GDPR", "Section 4.2") |
| **Legal** | Clause references, party names, dates, legal terms ("indemnification") |
| **Research** | Author names, method names, dataset names, specific metrics |
| **Support logs** | Error codes, customer IDs, product SKUs |

#### Tools & Libraries

| Tool | Speed | Description |
|------|-------|-------------|
| [ripgrep (rg)](https://github.com/BurntSushi/ripgrep) | Fastest | File search. Respects `.gitignore`, regex support. Best for code/local files. |
| [Tantivy](https://github.com/quickwit-oss/tantivy) | Very fast | Rust full-text search engine (like Lucene). Good for building search indexes. |
| [Whoosh](https://github.com/mchaput/whoosh) | Fast | Pure Python full-text search. Easy to embed. |
| [SQLite FTS5](https://www.sqlite.org/fts5.html) | Fast | Full-text search built into SQLite. Zero dependencies. |
| [Elasticsearch](https://github.com/elastic/elasticsearch) | Fast (server) | Distributed search. Overkill for local, great for large-scale. |
| [Meilisearch](https://github.com/meilisearch/meilisearch) | Fast (server) | Lightweight alternative to Elasticsearch. Typo-tolerant. |

#### When to Use

- You know the **exact term** (function name, error code, clause title).
- Highest precision, lowest recall (won't find synonyms or paraphrases).
- Extremely fast, zero token cost for the search itself.

---

### Strategy 3: Semantic Search (Vector / RAG)

> **"When you know the meaning but not the exact words."**

**Concept:** Convert your content into vector embeddings, store in a vector database, and retrieve by semantic similarity. This finds content that's _about_ the same thing even if it uses different words.

#### How It Applies Across Domains

| Domain | Example Query → What It Finds |
|--------|------------------------------|
| **Code** | "retry logic with exponential backoff" → finds `_retry_with_delay()` function |
| **Documents** | "employee vacation rules" → finds "PTO Policy" document |
| **Legal** | "liability for data breach" → finds indemnification clause + privacy addendum |
| **Research** | "transformer models for time series" → finds relevant papers regardless of exact title |
| **Support** | "app crashes on login" → finds similar past tickets with resolutions |

#### Embedding Models

| Model | Provider | Best For |
|-------|----------|---------|
| [voyage-code-3](https://www.voyageai.com/) | Voyage AI (API) | Code-specific embeddings |
| text-embedding-3-small | OpenAI (API) | General purpose, cost-effective |
| text-embedding-3-large | OpenAI (API) | Higher accuracy, higher cost |
| [Nomic Embed](https://huggingface.co/nomic-ai) | Open source | Runs locally, no API cost |
| [BGE-M3](https://huggingface.co/BAAI/bge-m3) | Open source | Multi-lingual, multi-granularity |
| [Jina Embeddings v3](https://huggingface.co/jinaai/jina-embeddings-v3) | Open source | Strong general-purpose, local |

#### Vector Databases

| Database | Deployment | Best For |
|----------|-----------|----------|
| [ChromaDB](https://github.com/chroma-core/chroma) | Embedded | **Easiest to start.** Python-native, in-process. |
| [LanceDB](https://github.com/lancedb/lancedb) | Embedded | Serverless, fast, built on Lance format. |
| [Qdrant](https://github.com/qdrant/qdrant) | Server | Production-ready, Rust, rich filtering. |
| [FAISS](https://github.com/facebookresearch/faiss) | Library | Meta's lib. Fastest similarity search. No persistence. |
| [pgvector](https://github.com/pgvector/pgvector) | PostgreSQL extension | If you already use Postgres. |
| [Milvus](https://github.com/milvus-io/milvus) | Server | Large-scale distributed deployments. |

#### Chunking — The Make-or-Break Decision

Bad chunking ruins RAG quality. The key: **chunk at natural boundaries**.

| Domain | Natural Boundary | Tool |
|--------|-----------------|------|
| **Code** | Function / class / method | tree-sitter, [LlamaIndex CodeSplitter](https://docs.llamaindex.ai/) |
| **Documents** | Section / paragraph / heading | [Unstructured](https://github.com/Unstructured-IO/unstructured), [docling](https://github.com/DS4SD/docling) |
| **Legal** | Clause / article / section | Custom parser or Unstructured |
| **Research** | Abstract / section / figure caption | [GROBID](https://github.com/kermitt2/grobid) (parses papers) |
| **Generic** | Paragraph with overlap | [LangChain RecursiveCharacterTextSplitter](https://python.langchain.com/) |

**Rule:** Never split mid-sentence or mid-function. Always chunk at semantic boundaries.

#### When to Use

- Natural language queries without exact keywords.
- Finding "similar" content (code patterns, related documents, past cases).
- **Complement to keyword search, not a replacement.**

---

### Strategy 4: Graph-Based Navigation (Relationships)

> **"Content is connected. Follow the edges."**

**Concept:** Build a graph of relationships between content pieces: file imports file, document references document, clause depends on clause, paper cites paper. Navigate this graph to find related content that keyword and semantic search would miss.

**Why it matters:** Keyword search finds _matching_ content. RAG finds _similar_ content. Graph navigation finds _connected_ content — which is often the most important for making correct decisions.

#### How It Applies Across Domains

| Domain | Nodes | Edges (Relationships) |
|--------|-------|-----------------------|
| **Code** | Files, functions, classes | imports, calls, inherits, depends-on |
| **Documents** | Pages, sections | links-to, references, supersedes, is-child-of |
| **Legal** | Clauses, contracts | references, amends, depends-on, conflicts-with |
| **Research** | Papers | cites, is-cited-by, same-author, same-topic |
| **Support** | Tickets, articles | similar-to, resolved-by, caused-by |

#### Tools & Libraries

| Tool | Domain | Description |
|------|--------|-------------|
| [NetworkX](https://github.com/networkx/networkx) | Any | Python graph library. Build and query any relationship graph. |
| [Neo4j](https://github.com/neo4j/neo4j) | Any | Graph database. Best for complex, persistent relationship queries. |
| [LlamaIndex KnowledgeGraphIndex](https://docs.llamaindex.ai/) | Any | Build knowledge graphs from documents for LLM retrieval. |
| tree-sitter + import parsing | Code | Build file dependency graph by parsing imports. |
| [madge](https://github.com/pahen/madge) | JS/TS code | Module dependency graph visualization and analysis. |
| [Sourcegraph SCIP](https://github.com/sourcegraph/scip) | Code | Cross-repo code intelligence. |
| Link extraction (BeautifulSoup, regex) | Documents | Extract hyperlinks, cross-references between docs. |
| Citation parsing ([GROBID](https://github.com/kermitt2/grobid)) | Research | Extract citation graph from papers. |

#### Navigation Patterns

```
Pattern 1: EXPAND (find neighbors)
────────────────────────────────
  Starting node: auth/service.py
  → imported by: auth/routes.py, auth/middleware.py
  → imports: models/user.py, utils/crypto.py
  → frequently co-changed with: tests/test_auth.py
  
  Result: Read these 5 files to understand context.

Pattern 2: TRACE (follow a path)
────────────────────────────────
  "What happens when POST /login is called?"
  routes.py → service.py → user_model.py → db_session.py
  
  Result: Read along this call/reference chain.

Pattern 3: CLUSTER (find related groups)
────────────────────────────────────────
  "All documents related to GDPR compliance"
  privacy-policy.md → data-retention.md → user-consent.md
  ← referenced by: employee-handbook.md (Section 8)
  
  Result: These 4 documents form a topic cluster.
```

#### When to Use

- A change/query affects connected content (edit file A → need to check file B that imports A).
- Finding all content in a topic cluster.
- Tracing chains of causality, reference, or dependency.

---

### Strategy 5: Iterative Deepening with Token Budget

> **"Don't load everything. Zoom in progressively."**

**Concept:** Start broad and cheap, then progressively load more detail for the specific areas that matter. Manage a strict token budget to avoid wasting context on irrelevant content.

**Why it matters:** This is not a retrieval strategy — it's the **orchestration pattern** that ties the other 4 strategies together. Without it, you either waste context (load too much) or miss critical information (load too little).

#### The Pattern

```
Round 1: DISCOVER (use Strategy 1 — Structural Map)
  ┌──────────────────────────────────┐
  │ Agent reads: High-level skeleton │
  │ "I see 127 documents. The task   │
  │  is about PTO policy. I need     │
  │  HR/pto-policy.md and maybe      │
  │  HR/onboarding.md"               │
  └──────────────────┬───────────────┘
                     │
Round 2: LOCATE (use Strategy 2 + 3 — Keyword & Semantic Search)
  ┌──────────────────▼───────────────┐
  │ Keyword: search "PTO", "vacation"│
  │ Semantic: search "time off rules"│
  │ Found: pto-policy.md (Section 3) │
  │ and employee-handbook.md (Ch. 8) │
  └──────────────────┬───────────────┘
                     │
Round 3: EXPAND (use Strategy 4 — Graph Navigation)
  ┌──────────────────▼───────────────┐
  │ pto-policy.md references:        │
  │   → regional-addendum.md         │
  │   → hr-contact-list.md           │
  │ Load regional-addendum.md too    │
  └──────────────────┬───────────────┘
                     │
Round 4: DEEP READ (load full content)
  ┌──────────────────▼───────────────┐
  │ Read full text of:               │
  │   1. pto-policy.md (Section 3)   │
  │   2. regional-addendum.md        │
  │ Now have enough detail to answer │
  └──────────────────────────────────┘
```

#### Token Budget Management

```
Total Budget: 128K tokens
                │
                ├── System prompt / instructions:      ~3K   (2%)
                ├── Strategy 1: Structural map:        ~8K   (6%)
                ├── Strategy 2+3: Search results:      ~15K  (12%)
                ├── Strategy 4: Graph neighbors:       ~10K  (8%)
                ├── Full content of target items:      ~50K  (39%)
                ├── LLM reasoning / chain-of-thought:  ~22K  (17%)
                └── Output generation:                 ~20K  (16%)
```

**Implementation:**

```python
from dataclasses import dataclass, field

@dataclass
class TokenBudget:
    total: int = 128_000
    allocations: dict = field(default_factory=lambda: {
        "structural_map": 0.06,     # Always present
        "search_results": 0.12,     # Keyword + semantic results
        "graph_neighbors": 0.08,    # Related content via graph
        "full_content": 0.39,       # Deep reads
        "reasoning": 0.17,          # Chain of thought
        "output": 0.16,             # Generated response
        "system": 0.02,             # Instructions
    })
    used: dict = field(default_factory=lambda: {})

    def remaining(self, category: str) -> int:
        limit = int(self.total * self.allocations[category])
        return limit - self.used.get(category, 0)

    def can_add(self, category: str, tokens: int) -> bool:
        return self.remaining(category) >= tokens

    def try_add(self, category: str, content: str, count_fn) -> bool:
        tokens = count_fn(content)
        if self.can_add(category, tokens):
            self.used[category] = self.used.get(category, 0) + tokens
            return True
        return False  # Over budget — skip or summarize this content
```

#### Context Freshness (Invalidation)

During long-running tasks, context can become stale:

| Event | Action |
|-------|--------|
| Agent edits a file/document | Re-read the modified content |
| Test/validation fails | Load error details into context, re-read related files |
| Many steps have passed | Summarize old context, keep recent in full detail |
| External data changed (git pull, doc update) | Invalidate all cached content, rebuild structural map |

---

## 3. Best Practice Workflow

Combine all 5 strategies into a single pipeline:

```
┌──────────────────────────────────────────────────────────────┐
│  INPUT: Task / Query / Instruction                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 1: Load Structural Map (Strategy 1)                     │
│                                                               │
│  • Always loaded. Cheap. Gives overview.                      │
│  • Agent now knows WHAT exists and WHERE.                     │
│  Token cost: ~6% of budget                                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 2: Multi-Signal Search (Strategy 2 + 3)                 │
│                                                               │
│  • Keyword search: exact terms from the task                  │
│  • Semantic search: meaning-based retrieval                   │
│  • Merge results, deduplicate, rank by combined score         │
│  • Output: top 5-15 candidate items/files/sections            │
│  Token cost: ~12% of budget                                   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 3: Expand via Graph (Strategy 4)                        │
│                                                               │
│  • For each candidate, find connected content                 │
│  • dependencies, references, related items                    │
│  • Add high-relevance neighbors to context                    │
│  Token cost: ~8% of budget                                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 4: Deep Read + Execute (Strategy 5)                     │
│                                                               │
│  • Load full content of final selected items                  │
│  • Generate response / make changes                           │
│  • If needed: iterate (re-search, re-read, refine)            │
│  • Manage token budget throughout                             │
│  Token cost: ~39% of budget (full content)                    │
└──────────────────────────────────────────────────────────────┘
```

### Multi-Signal Ranking

When combining keyword + semantic search, rank by weighted score:

```python
def rank_item(item, signals):
    score = 0.0
    score += 3.0 * signals.keyword_match_strength   # Highest: exact match
    score += 2.0 * signals.semantic_similarity       # High: meaning match
    score += 1.5 * signals.graph_proximity           # Medium: connected
    score += 0.5 * signals.recency                   # Low: recently updated
    return score
```

---

## 4. Strategy Comparison

| # | Strategy | What It Finds | Precision | Recall | Speed | Token Cost |
|---|----------|--------------|-----------|--------|-------|------------|
| 1 | Structural Map | Everything (overview) | ★★★★☆ | ★★★★★ | Instant | Very low |
| 2 | Keyword Search | Exact matches | ★★★★★ | ★★☆☆☆ | Instant | Zero |
| 3 | Semantic / RAG | Meaning matches | ★★★☆☆ | ★★★★☆ | Medium | Medium |
| 4 | Graph Navigation | Connected content | ★★★★☆ | ★★★☆☆ | Fast | Low |
| 5 | Iterative Deepening | Right level of detail | N/A (orchestration) | N/A | N/A | Manages budget |

**Strategy 2 + 3 together cover most retrieval needs:**
- Keyword = high precision, low recall (finds exact, misses synonyms)
- Semantic = medium precision, high recall (finds related, may include noise)
- Combined = high precision + high recall

---

## 5. Anti-Patterns

| Anti-Pattern | Why It's Bad | Do This Instead |
|-------------|-------------|----------------|
| **Stuff everything into context** | LLM ignores middle of long context ("lost in the middle") | Hierarchical: map → search → targeted read |
| **RAG only** | Misses structural relationships and exact matches | Combine keyword + semantic + graph |
| **No structural map** | Agent doesn't know what exists, searches blindly | Always load skeleton/index first |
| **Bad chunking** | Splits content mid-sentence/mid-function, losing meaning | Chunk at natural boundaries (section, function, clause) |
| **No token budget** | Wastes context on low-value content, runs out of space | Explicit budget per category |
| **Load all upfront** | Wastes tokens on content that turns out irrelevant | Iterative deepening: discover → locate → expand → read |
| **Same retrieval for all queries** | Keyword queries don't need RAG; vague queries don't need keyword | Route to appropriate strategy based on query type |

---

## 6. Domain-Specific Extensions

The 5 core strategies are universal. For specific domains, add specialized layers:

### For Code

| Extension | Tool |
|-----------|------|
| Symbol Navigation (go-to-def, find-refs) | LSP servers (Pyright, rust-analyzer, typescript-language-server) |
| Call Graph | PyCG, pyan3, CodeQL, joern |
| Type Analysis | mypy, Pyright, TypeScript compiler |
| Test Mapping | pytest-testmon, Jest --findRelatedTests |
| Git Co-change Analysis | git log + custom scripts |

### For Legal / Compliance

| Extension | Tool |
|-----------|------|
| Clause cross-referencing | Custom parser + Neo4j |
| Regulatory mapping | Knowledge graph (regulation → affected clauses) |
| Version tracking | Document diff (which clauses changed between versions) |

### For Research / Academic

| Extension | Tool |
|-----------|------|
| Citation graph | GROBID, Semantic Scholar API |
| Author network | Co-authorship graph |
| Method lineage | Track which papers build on which methods |

### For Customer Support

| Extension | Tool |
|-----------|------|
| Ticket similarity clustering | Vector search + category tags |
| Resolution linking | Graph: ticket → resolution → knowledge article |
| Escalation pattern analysis | Temporal analysis of ticket chains |

---

## Summary

```
┌───────────────────────────────────────────────────────────┐
│                   5 UNIVERSAL STRATEGIES                    │
│                                                            │
│  1. Structural Map    — Know what exists (birds-eye view)  │
│  2. Keyword Search    — Find exact matches (high precision)│
│  3. Semantic Search   — Find by meaning (high recall)      │
│  4. Graph Navigation  — Find connected content (relations) │
│  5. Iterative Deepen  — Zoom in progressively (budget)     │
│                                                            │
│  These 5 cover ANY large-context scenario.                 │
│  Add domain-specific extensions only when needed.          │
└───────────────────────────────────────────────────────────┘
```

## References

- [Aider — Repo Map](https://aider.chat/docs/repomap.html)
- [Stripe — Minions: One-Shot Coding Agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)
- [LlamaIndex — Retrieval Strategies](https://docs.llamaindex.ai/)
- [LangChain — RAG](https://python.langchain.com/)
- [Tree-sitter — Incremental Parsing](https://tree-sitter.github.io/tree-sitter/)
- [ChromaDB — Vector Store](https://docs.trychroma.com/)
