# Context Management Strategies for One-Shot End-to-End Coding Agents

> A comprehensive guide to managing large codebase context when building coding agents that operate on brownfield (existing) repositories.

---

## Table of Contents

- [1. The Core Problem](#1-the-core-problem)
- [2. Context Management Strategies](#2-context-management-strategies)
  - [2.1 Repo Map / Code Skeleton](#21-repo-map--code-skeleton)
  - [2.2 Keyword / Text Search](#22-keyword--text-search)
  - [2.3 Symbol Navigation](#23-symbol-navigation)
  - [2.4 Dependency / Import Graph](#24-dependency--import-graph)
  - [2.5 Vector Search / RAG](#25-vector-search--rag)
  - [2.6 Call Graph / Control Flow Analysis](#26-call-graph--control-flow-analysis)
  - [2.7 Type Information / Static Analysis](#27-type-information--static-analysis)
  - [2.8 Git History / Blame Analysis](#28-git-history--blame-analysis)
  - [2.9 Test Mapping](#29-test-mapping)
  - [2.10 Documentation / Comment Extraction](#210-documentation--comment-extraction)
  - [2.11 Context Window Management](#211-context-window-management)
- [3. Best Practice Workflow](#3-best-practice-workflow)
  - [3.1 Hierarchical Context Loading](#31-hierarchical-context-loading)
  - [3.2 Multi-Signal Retrieval](#32-multi-signal-retrieval)
  - [3.3 Token Budget Management](#33-token-budget-management)
  - [3.4 Iterative Deepening Pattern](#34-iterative-deepening-pattern)
  - [3.5 Context Freshness & Invalidation](#35-context-freshness--invalidation)
- [4. Strategy Comparison Matrix](#4-strategy-comparison-matrix)
- [5. Recommended Implementation Phases](#5-recommended-implementation-phases)
- [6. Anti-Patterns to Avoid](#6-anti-patterns-to-avoid)

---

## 1. The Core Problem

LLMs have finite context windows (128K–1M tokens). Real-world codebases have millions of lines of code. The challenge is **not** fitting the entire codebase into context — it's **selecting the right context** so the agent can make correct, convention-following changes.

```
Codebase: 500K LOC  ──►  Context Window: ~128K tokens (~40K LOC)
                          
                          You can only fit ~8% of the codebase.
                          The question: WHICH 8%?
```

### Why Pure RAG Falls Short for Code

| What RAG captures well | What RAG misses |
|------------------------|-----------------|
| Semantic similarity ("code about authentication") | Structural relationships (A imports B imports C) |
| Natural language descriptions in comments | Runtime call flow (A calls B calls C) |
| Similar code patterns | Type contracts and interfaces |
| | Co-change patterns (files that change together) |

**Key insight:** Code is a graph, not a document. Managing context requires **graph-aware strategies**, not just text retrieval.

---

## 2. Context Management Strategies

### 2.1 Repo Map / Code Skeleton

**Concept:** Summarize the entire repository as a list of file paths, class names, and function signatures — without implementation bodies. This gives the agent a "birds-eye view" of the codebase that fits in a small token budget.

**Why it matters:** This is the single most important strategy. It lets the agent know _what exists_ and _where to look deeper_, without consuming significant context.

#### Tools & Libraries

| Tool | Language | Description |
|------|----------|-------------|
| [Aider repo-map](https://github.com/paul-gauthier/aider) | Python | Gold standard. Uses ctags + PageRank to rank files by importance. Automatically manages token budget. |
| [tree-sitter](https://github.com/tree-sitter/tree-sitter) | C + bindings | Parse AST for 100+ languages. Extract function/class signatures programmatically. |
| [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter) | Python | Python bindings for tree-sitter. |
| [universal-ctags](https://github.com/universal-ctags/ctags) | CLI | Fast symbol indexing for 130+ languages. Outputs tag files with symbol locations. |
| Python `ast` module | Python | Built-in AST parsing specifically for Python source files. |

#### Example Output

```python
# Repo map — signatures only, ~2-4K tokens for a 100K LOC repo

# src/auth/routes.py
class AuthRouter:
    def login(request: LoginRequest) -> TokenResponse: ...
    def logout(request: Request) -> None: ...
    def refresh_token(token: str) -> TokenResponse: ...

# src/auth/service.py
class AuthService:
    def authenticate(email: str, password: str) -> User: ...
    def generate_token(user: User) -> str: ...
    def validate_token(token: str) -> Claims: ...

# src/models/user.py
class User(BaseModel):
    id: int
    email: str
    hashed_password: str
    is_active: bool
```

#### When to Use

- **Always.** This is Layer 0 — always present in context as the foundation.
- Token cost: ~2-8K tokens for a large repo.

---

### 2.2 Keyword / Text Search (Exact Match)

**Concept:** Search for exact strings in the codebase — function names, error messages, variable names, configuration keys.

**Why it matters:** When the task mentions specific identifiers (e.g., "fix `login_user` function" or "error: `INVALID_TOKEN`"), keyword search is the fastest and most precise way to locate relevant code.

#### Tools & Libraries

| Tool | Speed | Description |
|------|-------|-------------|
| [ripgrep (rg)](https://github.com/BurntSushi/ripgrep) | Fastest | Respects `.gitignore`, supports regex, parallel search. **Use this.** |
| [The Silver Searcher (ag)](https://github.com/ggreer/the_silver_searcher) | Very fast | Similar to ripgrep, slightly older. |
| `grep -r` | Fast | Available everywhere but slower than rg/ag. |

#### Usage Patterns

```bash
# Find function definition
rg "def login_user" --type py

# Find error message origin
rg "INVALID_TOKEN" --type-add 'code:*.{py,js,ts,rb}'

# Find all usages of a class
rg "AuthService" --type py -l    # -l = list files only

# Find TODO/FIXME comments
rg "TODO|FIXME|HACK" --type py
```

#### When to Use

- Task mentions specific identifiers, error messages, or strings.
- You know _what_ to search for but not _where_ it is.
- First-pass exploration before deeper analysis.

---

### 2.3 Symbol Navigation (Go-to-Definition, Find References)

**Concept:** Use language-aware tooling to navigate code structurally — find where a symbol is defined, find all references to it, find implementations of an interface.

**Why it matters:** Unlike text search, symbol navigation understands code semantics. Searching for `User` as text returns comments, strings, and variables — symbol navigation returns only the class definition and its usages.

#### Tools & Libraries

| Tool | Language Target | Description |
|------|----------------|-------------|
| [Pyright](https://github.com/microsoft/pyright) | Python | Microsoft's Python type checker. Provides go-to-def, find-refs, type inference. |
| [typescript-language-server](https://github.com/typescript-language-server/typescript-language-server) | TypeScript/JS | Full LSP server for TS/JS. |
| [rust-analyzer](https://github.com/rust-lang/rust-analyzer) | Rust | Excellent Rust LSP. |
| [jedi](https://github.com/davidhalter/jedi) | Python | Lightweight Python autocompletion and analysis. Easier to embed than Pyright. |
| [Sourcegraph SCIP](https://github.com/sourcegraph/scip) | Multi-language | Code intelligence indexing format used by Sourcegraph. |
| [stack-graphs](https://github.com/github/stack-graphs) | Multi-language | GitHub's name resolution engine. Precise cross-file navigation. |
| [universal-ctags](https://github.com/universal-ctags/ctags) | Multi-language | Lighter than LSP but less precise. Good for quick symbol lookups. |

#### When to Use

- Tracing code flow: "this function calls X — where is X defined?"
- Understanding impact: "what code uses this class/function?"
- Navigating inheritance: "what implements this interface?"

---

### 2.4 Dependency / Import Graph

**Concept:** Build a directed graph of file-level dependencies based on import statements. If `routes.py` imports `service.py` imports `models.py`, the agent knows that changing `models.py` may affect all three.

**Why it matters:** When modifying a file, the agent needs to understand the "blast radius" — which other files might be affected and need to be read or updated.

#### Tools & Libraries

| Tool | Language Target | Description |
|------|----------------|-------------|
| [madge](https://github.com/pahen/madge) | JS/TS | Visualize and analyze module dependencies. Detects circular deps. |
| [pydeps](https://github.com/thebjorn/pydeps) | Python | Python package dependency graphing. |
| [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) | JS/TS | Rule-based dependency validation and visualization. |
| [modulefinder](https://docs.python.org/3/library/modulefinder.html) | Python | Built-in Python module for finding imports. |
| [snakefood3](https://github.com/rmcgibbo/snakefood3) | Python | Generate Python dependency graphs. |
| Tree-sitter + custom queries | Any | Parse import/require/use statements from AST for any language. |

#### Usage Pattern

```
File being edited: auth/routes.py
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        auth/service.py  auth/middleware.py  auth/schemas.py
              │
              ▼
        models/user.py
              │
              ▼
        db/session.py

Agent should read: all files in this subgraph (6 files)
Agent should NOT read: payments/stripe.py (unrelated)
```

#### When to Use

- Determining which files to include in context when editing a specific file.
- Understanding ripple effects of changes.
- Detecting circular dependencies that complicate changes.

---

### 2.5 Vector Search / RAG (Semantic Search)

**Concept:** Convert code into vector embeddings, store in a vector database, and retrieve semantically similar code chunks when given a natural language query.

**Why it matters:** When the task is described in natural language ("fix the retry logic" or "add rate limiting to the API"), and you don't know the exact function names, vector search can find relevant code by meaning.

#### Embedding Models for Code

| Model | Provider | Type | Notes |
|-------|----------|------|-------|
| [voyage-code-3](https://www.voyageai.com/) | Voyage AI | API | **Best for code** as of 2025-2026. Purpose-built for code embeddings. |
| text-embedding-3-small | OpenAI | API | Good general-purpose, cost-effective. |
| text-embedding-3-large | OpenAI | API | Higher accuracy, higher cost. |
| [Nomic Embed Code](https://huggingface.co/nomic-ai/nomic-embed-code-v2-moe) | Nomic AI | Open source | Runs locally. No API cost. |
| [CodeBERT](https://github.com/microsoft/CodeBERT) | Microsoft | Open source | Older but fully free and local. |

#### Vector Databases

| Database | Deployment | Best for |
|----------|-----------|----------|
| [ChromaDB](https://github.com/chroma-core/chroma) | Embedded (in-process) | **Easiest to start.** Python-native, no server needed. |
| [LanceDB](https://github.com/lancedb/lancedb) | Embedded | Serverless, built on Lance columnar format. Very fast. |
| [Qdrant](https://github.com/qdrant/qdrant) | Server | Production-ready. Written in Rust. Rich filtering. |
| [FAISS](https://github.com/facebookresearch/faiss) | Library | Meta's similarity search. Fastest for pure vector ops. No persistence built-in. |
| [Milvus](https://github.com/milvus-io/milvus) | Server | Distributed, large-scale deployments. |

#### Code Chunking Strategies

This is **critical** — bad chunking ruins RAG quality.

| Strategy | Implementation | Quality | Notes |
|----------|---------------|---------|-------|
| **AST-based chunking** | Tree-sitter | ★★★★★ | Chunk at function/class boundaries. **Best approach.** Never splits a function in half. |
| **CodeSplitter** | [LlamaIndex CodeSplitter](https://docs.llamaindex.ai/en/stable/api_reference/node_parsers/code/) | ★★★★☆ | Uses tree-sitter under the hood. Easy to use. |
| **Recursive character** | LangChain RecursiveCharacterTextSplitter | ★★★☆☆ | Uses separator hierarchy (class → function → line). Decent fallback. |
| **Fixed-size sliding window** | Custom | ★★☆☆☆ | Simple but will cut functions in half. Avoid for code. |

#### When to Use

- Natural language queries: "where is the retry logic?"
- Finding code by behavior rather than name.
- **Complement to keyword/symbol search, not a replacement.**

---

### 2.6 Call Graph / Control Flow Analysis

**Concept:** Build a graph of function calls — which function calls which, and in what order. This reveals runtime flow that static imports don't show.

**Why it matters:** Import graphs show file dependencies, but call graphs show _behavioral_ dependencies. Function A and function B might be in the same file but have completely different callers and callees.

#### Tools & Libraries

| Tool | Language Target | Description |
|------|----------------|-------------|
| [PyCG](https://github.com/vitsalis/PyCG) | Python | Static call graph generator. |
| [pyan3](https://github.com/Technologicat/pyan) | Python | Call graph analysis + Graphviz visualization. |
| [java-callgraph](https://github.com/gousiosg/java-callgraph) | Java | Both static and dynamic call graph generation. |
| [ts-morph](https://github.com/dsherret/ts-morph) | TypeScript | Full TypeScript compiler API. Can build custom call graphs. |
| [joern](https://github.com/joernio/joern) | Multi-language | Code analysis platform using Code Property Graphs (CPG). Powerful but complex. |
| [CodeQL](https://codeql.github.com/) | Multi-language | GitHub's semantic code analysis. Query language for code. Very powerful for security analysis. |

#### When to Use

- Debugging complex flows: "what happens when a user calls POST /login?"
- Understanding side effects: "if I change this function, what other behavior changes?"
- Security analysis: "can user input reach this SQL query?"

---

### 2.7 Type Information / Static Analysis

**Concept:** Extract type annotations, interface definitions, and inferred types to understand function contracts without reading implementation details.

**Why it matters:** Types are a compact, high-signal summary of code. Knowing that `authenticate(email: str, password: str) -> User | None` tells you the contract without reading the 50-line implementation.

#### Tools & Libraries

| Tool | Language Target | Description |
|------|----------------|-------------|
| [Pyright](https://github.com/microsoft/pyright) | Python | Type inference even for untyped code. |
| [mypy](https://github.com/python/mypy) | Python | Standard type checker. Daemon mode for speed. |
| TypeScript compiler (`tsc`) | TypeScript | Built-in type system. |
| [Sorbet](https://sorbet.org/) | Ruby | Gradual type system for Ruby. Used by Stripe. |
| [semgrep](https://github.com/semgrep/semgrep) | Multi-language | Lightweight pattern matching and static analysis. |

#### When to Use

- Understanding function contracts before modifying callers.
- Verifying that changes maintain type compatibility.
- Extracting interface definitions without reading full implementations.

---

### 2.8 Git History / Blame Analysis

**Concept:** Use version control history to understand code evolution — which files change together, which code is stable vs. volatile, who owns what.

**Why it matters:** Files that frequently change together likely have hidden dependencies. Recently-changed code is more likely to have bugs. Stable, old code should be changed cautiously.

#### Tools & Commands

| Tool / Command | Purpose |
|---------------|---------|
| `git log --follow <file>` | History of a specific file (including renames). |
| `git blame <file>` | Who last modified each line, and when. |
| `git log --name-only --pretty=format:` | Find files that are committed together (co-change analysis). |
| `git log --since="1 month ago" --stat` | Recently active areas of the codebase. |
| [git-of-theseus](https://github.com/erikbern/git-of-theseus) | Analyze code age and survival over time. |
| [hercules](https://github.com/src-d/hercules) | Advanced git history analytics. |

#### Co-Change Analysis Example

```bash
# Find files that were committed together with auth/service.py
git log --pretty=format:"%H" -- auth/service.py | \
  xargs -I {} git show --name-only --pretty=format: {} | \
  sort | uniq -c | sort -rn | head -20

# Output:
#  47 auth/service.py
#  31 auth/routes.py          ← Almost always changes together
#  28 tests/test_auth.py      ← Test file for this module
#  12 models/user.py           ← Sometimes changes together
#   3 payments/billing.py     ← Rarely related
```

#### When to Use

- Suggesting additional files to review when changing a file.
- Gauging risk: old, stable code = be careful; new code = more likely to have bugs.
- Finding the right reviewer or domain expert.

---

### 2.9 Test Mapping (Test ↔ Source)

**Concept:** Maintain a mapping between source files and their corresponding test files, so when code is modified, only relevant tests are executed.

**Why it matters:** Running the full test suite after every change is too slow (minutes to hours). Test mapping enables fast, targeted validation — critical for the "shift-left" feedback loop.

#### Tools & Libraries

| Tool | Language Target | Description |
|------|----------------|-------------|
| [pytest-testmon](https://github.com/tarpas/pytest-testmon) | Python | Tracks which tests cover which source lines. Only re-runs affected tests. |
| [Jest --changedSince](https://jestjs.io/docs/cli#--changedsince) | JS/TS | Runs tests related to changed files based on dependency graph. |
| [Jest --findRelatedTests](https://jestjs.io/docs/cli#--findrelatedtests-spaceseparatedlistofsourcefiles) | JS/TS | Given source files, finds and runs related tests. |
| [Bazel](https://bazel.build/) | Multi-language | Hermetic build system with full dependency graph. Knows exactly which tests to run. |
| [Nx](https://nx.dev/) | JS/TS monorepo | Affected command runs only tests for changed projects. |
| Coverage diff analysis | Any | Compare coverage report with changed files to find relevant tests. |

#### Convention-Based Mapping (Fallback)

When no tool is available, use naming conventions:

```
src/auth/service.py     → tests/auth/test_service.py
src/auth/service.py     → tests/test_auth_service.py
src/components/Button.tsx → src/components/Button.test.tsx
src/components/Button.tsx → __tests__/components/Button.test.tsx
```

#### When to Use

- Phase 5 (Validation): only run tests affected by the agent's changes.
- Reduces feedback loop from minutes to seconds.

---

### 2.10 Documentation / Comment Extraction

**Concept:** Extract docstrings, inline comments, README files, and architecture decision records (ADRs) to understand the _intent_ behind code, not just the implementation.

**Why it matters:** Code tells you _how_ something works. Documentation tells you _why_ it was built that way and _what constraints_ exist. An agent that only reads code might violate unstated design decisions.

#### Tools & Sources

| Source | How to Extract |
|--------|---------------|
| Docstrings | Tree-sitter comment node queries, or language-specific tools (`pydoc`, `typedoc`, `javadoc`) |
| Inline comments | Tree-sitter or regex extraction |
| README.md | Direct file read |
| CONTRIBUTING.md | Direct file read — contains conventions |
| ARCHITECTURE.md / ADRs | Direct file read — design decisions |
| Agent rule files | `.cursorrules`, `.github/copilot-instructions.md`, `CLAUDE.md`, `AGENTS.md` |
| `.editorconfig` | Formatting conventions |
| `pyproject.toml` / `package.json` | Tool configurations, lint rules |

#### When to Use

- Always load agent rule files and contributing guides into context.
- Extract docstrings for functions/classes the agent plans to modify.
- Check ADRs before making architectural changes.

---

### 2.11 Context Window Management

**Concept:** Techniques for managing the finite token budget — deciding what goes in, what gets summarized, and what gets dropped.

#### Techniques & Tools

| Technique | Tool / Library | Description |
|-----------|---------------|-------------|
| **Token counting** | [tiktoken](https://github.com/openai/tiktoken) | Accurately count tokens for OpenAI models. Essential for budget management. |
| **Priority ranking** | Aider-style PageRank on file graph | Rank files by importance (how many other files depend on them). |
| **Summarization** | LLM (use a cheap/fast model like Claude Haiku) | Summarize long files into key signatures + behavior description. |
| **Hierarchical loading** | Custom | Skeleton → relevant chunks → full file (zoom-in pattern). |
| **Sliding window** | Custom | Keep recent + relevant context, drop stale context. |
| **Conversation compression** | [LangChain ConversationSummaryBufferMemory](https://python.langchain.com/docs/modules/memory/) | Automatically summarize older conversation turns. |
| **Multi-index retrieval** | [LlamaIndex](https://github.com/run-llama/llama_index) | Multiple retrieval strategies composed together. |

---

## 3. Best Practice Workflow

### 3.1 Hierarchical Context Loading

Load context in layers, from cheapest/broadest to most expensive/specific:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 0: Always Present (~2-8K tokens)                     │
│                                                             │
│  • Repo map / skeleton (file list + signatures)             │
│  • Agent rules (.cursorrules, CONTRIBUTING.md)              │
│  • Task description                                         │
│                                                             │
│  Purpose: Agent knows what exists and what conventions to   │
│           follow before reading any actual code.            │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: Targeted Search Results (~5-15K tokens)           │
│                                                             │
│  • Keyword search results (ripgrep)                         │
│  • Symbol navigation results (definitions, references)      │
│  • Dependency graph neighbors of target files               │
│  • Vector search results (if natural language query)        │
│                                                             │
│  Purpose: Identify the specific files and functions that    │
│           are relevant to the task.                          │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: Full File Contents (~20-60K tokens)               │
│                                                             │
│  • Full content of files to be modified                     │
│  • Full content of directly-dependent files                 │
│  • Relevant test files                                      │
│  • Type definitions / interfaces used by target files       │
│                                                             │
│  Purpose: Agent has complete understanding of code it       │
│           will modify and its immediate dependencies.       │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: Supplementary Context (remaining budget)          │
│                                                             │
│  • Git blame / recent changes for target files              │
│  • Co-changed files (git history analysis)                  │
│  • Documentation / docstrings for called functions          │
│  • Similar code examples from elsewhere in repo             │
│                                                             │
│  Purpose: Additional signal to improve code quality         │
│           and follow established patterns.                  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Multi-Signal Retrieval

Never rely on a single search strategy. Combine multiple signals and deduplicate:

```
         Task Description
              │
    ┌─────────┼──────────┬───────────┬────────────┐
    ▼         ▼          ▼           ▼            ▼
 Keyword   Symbol     Import     Vector       Git
 Search    Nav        Graph      Search      History
 (rg)      (LSP)     (AST)      (RAG)      (co-change)
    │         │          │           │            │
    │    file scores:    │      file scores:      │
    │    routes.py: 0.9  │      routes.py: 0.7    │
    │    service.py: 0.8 │      service.py: 0.8   │
    │         │          │           │            │
    └─────────┴──────────┴───────────┴────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Merge & Re-rank    │
              │                     │
              │  1. routes.py  (4/5 signals matched)
              │  2. service.py (4/5 signals matched)
              │  3. user.py    (3/5 signals matched)
              │  4. test_auth.py (2/5 signals matched)
              │  5. schemas.py (2/5 signals matched)
              └─────────────────────┘
```

**Ranking heuristic:**

```python
def rank_file(file, signals):
    score = 0
    score += 3.0 if signals.keyword_match      # High: exact match
    score += 2.5 if signals.symbol_reference    # High: structural
    score += 2.0 if signals.import_dependency   # Medium-high: structural
    score += 1.5 if signals.vector_similarity   # Medium: semantic
    score += 1.0 if signals.git_co_change       # Low-medium: historical
    score += 0.5 if signals.doc_mention         # Low: supplementary
    
    # Boost files closer to target in dependency graph
    score *= (1.0 / (1 + dependency_distance))
    
    return score
```

### 3.3 Token Budget Management

Allocate your token budget deliberately:

```
Total Context Budget: 128K tokens (example)
                │
                ├── System Prompt + Instructions:     ~3K  (2%)
                ├── Layer 0 (Repo Map + Rules):       ~8K  (6%)
                ├── Layer 1 (Search Results):         ~15K (12%)
                ├── Layer 2 (Full File Contents):     ~50K (39%)
                ├── Layer 3 (Supplementary):          ~12K (9%)
                ├── Planning + Reasoning:             ~20K (16%)
                └── Output (code generation):         ~20K (16%)
```

**Implementation:**

```python
class TokenBudget:
    def __init__(self, total: int = 128_000):
        self.total = total
        self.allocations = {
            "system":        int(total * 0.02),  # ~3K
            "repo_map":      int(total * 0.06),  # ~8K
            "search_results": int(total * 0.12), # ~15K
            "file_contents": int(total * 0.39),  # ~50K
            "supplementary": int(total * 0.09),  # ~12K
            "reasoning":     int(total * 0.16),  # ~20K
            "output":        int(total * 0.16),  # ~20K
        }
    
    def can_add(self, category: str, tokens: int) -> bool:
        return self.used[category] + tokens <= self.allocations[category]
    
    def add(self, category: str, content: str) -> bool:
        tokens = count_tokens(content)
        if self.can_add(category, tokens):
            self.used[category] += tokens
            self.context[category].append(content)
            return True
        return False  # Budget exceeded — skip or summarize
```

### 3.4 Iterative Deepening Pattern

This is how humans read code — and agents should too:

```
Round 1: DISCOVER
  ┌──────────────────────────────────┐
  │ Agent reads: Repo map (skeleton) │
  │ Agent decides: "I need to look   │
  │ at auth/routes.py and            │
  │ auth/service.py"                 │
  └──────────────────┬───────────────┘
                     │
Round 2: UNDERSTAND
  ┌──────────────────▼───────────────┐
  │ Agent reads: Full auth/routes.py │
  │ Agent reads: Full auth/service.py│
  │ Agent discovers: service.py calls│
  │ normalize_email() from utils/    │
  │ Agent decides: "I need utils/"   │
  └──────────────────┬───────────────┘
                     │
Round 3: PINPOINT
  ┌──────────────────▼───────────────┐
  │ Agent reads: utils/email.py      │
  │ Agent finds: normalize_email()   │
  │ doesn't call .lower()            │
  │ Agent: "Found the bug!"          │
  └──────────────────┬───────────────┘
                     │
Round 4: VERIFY CONVENTIONS
  ┌──────────────────▼───────────────┐
  │ Agent reads: tests/test_auth.py  │
  │ Agent checks: How are similar    │
  │ tests written in this repo?      │
  │ Agent: Ready to make changes.    │
  └──────────────────────────────────┘
```

**Key principle:** The agent requests more context as needed, rather than loading everything upfront. Each round narrows focus.

### 3.5 Context Freshness & Invalidation

Context can become stale during a long agent run:

```
┌──────────────────────────────────────────────────────────┐
│  CONTEXT INVALIDATION RULES                               │
│                                                           │
│  1. After editing a file:                                 │
│     → Re-read the file (agent's edit may have changed     │
│       the structure)                                      │
│     → Re-run lint (the file may now have errors)          │
│                                                           │
│  2. After a test failure:                                 │
│     → Re-read the test output (new error context)         │
│     → Re-read files mentioned in stack trace              │
│                                                           │
│  3. If the agent has been running for many steps:         │
│     → Summarize earlier context                           │
│     → Keep recent actions in full detail                  │
│     → Drop stale search results                           │
│                                                           │
│  4. After git operations (rebase, merge):                 │
│     → Invalidate ALL cached file contents                 │
│     → Re-index repo map (files may have moved)            │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Strategy Comparison Matrix

| # | Strategy | Precision | Recall | Speed | Token Cost | Best For |
|---|----------|-----------|--------|-------|------------|----------|
| 1 | Repo Map / Skeleton | ★★★★☆ | ★★★★★ | Very fast | Very low | Always — foundation layer |
| 2 | Keyword Search (ripgrep) | ★★★★★ | ★★☆☆☆ | Instant | None | Known identifiers, error messages |
| 3 | Symbol Navigation (LSP) | ★★★★★ | ★★★☆☆ | Fast | None | Tracing definitions and references |
| 4 | Dependency / Import Graph | ★★★★☆ | ★★★★☆ | Fast | None | Understanding blast radius |
| 5 | Vector Search / RAG | ★★★☆☆ | ★★★★☆ | Medium | Medium | Natural language queries |
| 6 | Call Graph | ★★★★★ | ★★★☆☆ | Slow | None | Runtime flow analysis |
| 7 | Type / Static Analysis | ★★★★★ | ★★☆☆☆ | Medium | None | Interface contracts |
| 8 | Git History / Blame | ★★★☆☆ | ★★☆☆☆ | Fast | None | Co-change patterns, code ownership |
| 9 | Test Mapping | ★★★★☆ | ★★★★☆ | Build once | None | Targeted test execution |
| 10 | Documentation Extraction | ★★★☆☆ | ★★☆☆☆ | Very fast | Very low | Understanding intent / constraints |
| 11 | Context Window Management | N/A | N/A | N/A | Reduces cost | Always — efficiency layer |

---

## 5. Recommended Implementation Phases

### Phase 1: Foundation (Start Here)

Build the minimum viable context pipeline.

```
Must-have:
  ✅ Repo Map          → tree-sitter + universal-ctags
  ✅ Keyword Search    → ripgrep
  ✅ Symbol Navigation → ctags (lightweight) or jedi (Python)
  ✅ Token Counting    → tiktoken
  ✅ Convention Loading → Read agent rule files

Outcome: Agent can find relevant code and understands repo structure.
```

### Phase 2: Intelligence

Add structural understanding and semantic search.

```
Should-have:
  ✅ Dependency Graph  → tree-sitter import parsing
  ✅ Vector/RAG Search → ChromaDB + voyage-code-3 (or text-embedding-3-small)
  ✅ AST-based Chunking → tree-sitter for chunk boundaries
  ✅ Token Budget Manager → Priority-based allocation

Outcome: Agent can find code by meaning AND structure. Context is managed efficiently.
```

### Phase 3: Advanced

Add deeper analysis for complex tasks.

```
Nice-to-have:
  ✅ Call Graph         → PyCG / pyan3
  ✅ Git Co-change      → git log analysis
  ✅ Test Mapping       → pytest-testmon / Jest --findRelatedTests
  ✅ Type Analysis      → Pyright / mypy
  ✅ Multi-signal Ranking → Weighted merge of all signals

Outcome: Agent has deep understanding comparable to a senior engineer.
```

### Phase 4: Optimization

Fine-tune for production use.

```
Optimization:
  ✅ Context Summarization → Use fast LLM for long file summaries
  ✅ Incremental Indexing   → Only re-index changed files
  ✅ Caching                → Cache embeddings, AST, symbol index
  ✅ Iterative Deepening    → Agent requests context on-demand

Outcome: Fast, cost-effective context loading at scale.
```

---

## 6. Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Do This Instead |
|-------------|-------------|----------------|
| **Stuff entire repo into context** | "Lost in the middle" — LLM ignores middle of long context | Hierarchical loading: skeleton → search → targeted read |
| **RAG-only approach** | Misses structural relationships | Combine RAG with keyword + symbol + dependency graph |
| **Fixed chunking for code** | Splits functions/classes in half, losing meaning | AST-based chunking (tree-sitter) |
| **No token budget** | Runs out of context or wastes tokens on irrelevant code | Explicit budget allocation per category |
| **Load all context upfront** | Wastes tokens on code that turns out to be irrelevant | Iterative deepening: discover → understand → pinpoint |
| **Ignore repo conventions** | Agent writes code that doesn't match project style | Always load agent rules, contributing guides, lint configs |
| **Run all tests after every change** | Too slow, wastes time/compute | Test mapping: run only affected tests |
| **No context invalidation** | Agent works with stale data after edits | Re-read edited files, re-run lint after changes |
| **Same strategy for all languages** | What works for Python may not work for Java | Adapt tools per language (LSP, type checker, etc.) |
| **Ignore git history** | Misses co-change patterns and code ownership | Use git log for co-change analysis and risk assessment |

---

## References

- [Aider — Repo Map Implementation](https://aider.chat/docs/repomap.html)
- [Stripe — Minions: One-Shot Coding Agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)
- [SWE-agent — Agent-Computer Interface](https://github.com/princeton-nlp/SWE-agent)
- [Tree-sitter — Incremental Parsing](https://tree-sitter.github.io/tree-sitter/)
- [Sourcegraph SCIP — Code Intelligence](https://github.com/sourcegraph/scip)
- [LlamaIndex — Code Retrieval](https://docs.llamaindex.ai/)
