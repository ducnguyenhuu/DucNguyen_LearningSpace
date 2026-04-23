# AI Development Cost Estimation — Discovery & Workflow

---

## Problem Statement

Traditional estimation methods (COCOMO, Function Points, Planning Poker) were designed for
human-only development. They do not account for AI as a development factor, making them
unreliable for AI-assisted projects.

Teams need to answer:
- How much does it cost to build feature X using AI (tokens + human time)?
- How does that compare to pure human development?
- Can we predict AI cost before starting, based on feature characteristics?

Currently there is no established methodology for this. Teams either guess, ignore AI costs
entirely, or discover the true cost only after the project is done.

---

## Value

| Stakeholder | Value Delivered |
|-------------|----------------|
| Engineering manager | Accurate sprint cost forecasts; data to justify AI tooling investment |
| Developer | Clear expectation of how much human effort is still required when using AI |
| Finance / leadership | Real ROI numbers for AI tooling subscriptions and API spend |
| Product owner | Better-informed trade-off decisions between features |
| Organization | A self-improving cost model that gets more accurate over time with zero extra overhead |

---

## Acceptance Criteria

### In Scope

This project produces **two deliverables only**:
1. An estimation workflow — given a feature or project requirement as input, output a cost
   estimate (tokens + human hours) with a confidence band.
2. A data collection guideline — a detailed, step-by-step process for capturing actuals after
   each feature is built, so that historical data accumulates and estimates improve over time.

Actually building features, implementing projects, or running any development work is **not**
part of this project.

### Must Have

- [ ] A fixed task type taxonomy covering all common AI development work
- [ ] Greenfield estimation workflow: input feature → output cost estimate with confidence band
- [ ] Brownfield estimation workflow: same, with codebase context loading step and brownfield
      multiplier
- [ ] Project requirement support: decompose to features → estimate each → aggregate
- [ ] A detailed data collection guideline covering:
      - Exactly what data to collect after each completed feature
      - How to collect each data point (tool, method, timing)
      - How to attribute collected totals back to task types
      - How to feed collected data back into the Task Type Library
- [ ] Estimates include a confidence level and explicit range (not a point value)
- [ ] The Task Type Library starts with industry defaults and recalibrates from collected actuals

### Should Have

- [ ] Analogy-based estimation once 10+ features are collected
- [ ] Estimation accuracy (MMRE) below 0.25 once 30+ features are collected
- [ ] A parametric model (regression) calibrated from org data at the 30-feature threshold
- [ ] Efficiency ratio ($E = C_{Human} / C_{AI}$) reported per feature to show AI ROI

### Nice to Have

- [ ] Automated token collection via API log integration (no manual entry)
- [ ] Automated rework rate calculation via git diff script
- [ ] Dashboard showing estimation accuracy trends over time
- [ ] Per-task-type breakdown of where AI is most and least cost-effective

### Out of Scope

- Implementing, building, or executing any features or projects
- Estimating cost of AI infrastructure (GPU, fine-tuning, model training)
- Estimating non-development costs (PM time, design, QA manual testing)
- Real-time cost tracking during a session (focus is per-feature, not per-prompt)
- Building tooling or automation (this document is methodology and process only)

---

## Table of Contents

**Part I — Concepts**

1. [The Core Loop](#1-the-core-loop)
2. [Three Decision Layers](#2-three-decision-layers)
3. [Task Type Library — The Central Artifact](#3-task-type-library--the-central-artifact)

**Part II — Estimation Workflows**

4. [Input Routing — Scoping the Work](#4-input-routing--scoping-the-work)
5. [Greenfield Workflow](#5-greenfield-workflow)
6. [Brownfield Workflow](#6-brownfield-workflow)
   - [6.0 Context Loading Token Estimation](#60-context-loading-token-estimation)
   - [6.1 Brownfield Workflow Steps](#61-brownfield-workflow-steps)
7. [Cost Formulas](#7-cost-formulas)

**Part III — Maturity Phases**

8. [Phase 0: Bootstrap (0–9 features)](#8-phase-0-bootstrap-0-9-features)
9. [Phase 1: Calibration (10–29 features)](#9-phase-1-calibration-10-29-features)
10. [Phase 2: Parametric Model (30+ features)](#10-phase-2-parametric-model-30-features)

**Part IV — Data Collection**

11. [Data Collection Guideline](#11-data-collection-guideline)

**Part V — Operations**

12. [Configuration & File Layout](#12-configuration--file-layout)
13. [Model Version Handling](#13-model-version-handling)
14. [Known Limitations and Risks](#14-known-limitations-and-risks)
15. [Implementation Roadmap](#15-implementation-roadmap)

**Appendix**

A. [Estimation Agent — Automation Plan](#a-estimation-agent--automation-plan)
B. [Worked Example — End to End](#b-worked-example--end-to-end)
C. [Questionnaire-Based Context Estimation](#a-questionnaire-based-context-estimation)

---

# Part I — Concepts

## 1. The Core Loop

```
 INPUT (feature.md or project requirement)
   │
   ├─ Single Feature? ───────────────────────────────────────┐
   │                                                          │
   └─ Project Requirement? → [Decompose to Features] ───────→│
                                                              │
                                               Greenfield or  │
                                           ┌── Brownfield? ───┘
                                           │
                      ┌────────────────────┴──────────────────────────────────┐
                      │  GREENFIELD                │  BROWNFIELD              │
                      │  (no existing codebase)    │  (existing codebase)     │
                      │                            │  Step 0: Load context    │
                      └────────────────────────────┴──────────────────────────┘
                                           │
                                           ▼
                      ┌──────────────────────────────────────────────────────┐
                      │  STEP 1 — AI-HUMAN SOLUTION DIALOGUE                │
                      │  AI asks constraints → proposes 2–3 solutions       │
                      │  Human selects → AI maps to implementation tactic   │
                      │  saas / tooling / scratch / adapt                   │
                      └────────────────────────┬─────────────────────────────┘
                                               │
                                               ▼
                      ┌──────────────────────────────────────────────────────┐
                      │  STEP 2 — DECOMPOSE & ESTIMATE                      │
                      │  AI decomposes → map to task types → score per-task  │
                      │  complexity → lookup Task Type Library               │
                      │  → apply multipliers → sum → confidence band        │
                      └────────────────────────┬─────────────────────────────┘
                                               │
                                               ▼
                                          ESTIMATE OUTPUT
                                     (estimate.md + assumptions.md)
                                               │
                                    feature is built (later)
                                               │
                                               ▼
                      ┌──────────────────────────────────────────────────────┐
                      │  FEEDBACK LOOP — COLLECT ACTUALS                    │
                      │  auto + semi-auto + manual → attribute to tasks     │
                      │  → recalibrate Task Type Library                    │
                      │  → your org data replaces industry defaults         │
                      └──────────────────────────────────────────────────────┘
```

**Key insight:** The Task Type Library starts with industry-standard numbers and is
progressively replaced by your organization's actual numbers. Every completed feature makes
the next estimate more accurate.

---

## 2. Three Decision Layers

Estimation requires three layers of decisions. Each layer feeds the next and has a different
owner, frequency, and persistence.

```
┌──────────────────────────────────────────────────────────────────────┐
│ LAYER 1 — Architecture Pattern  (project-level, decided once)       │
│   Monolith / Microservices / Serverless / Event-driven              │
│   → Shapes which task types appear in the decomposition             │
│   → Stored in: project-level assumptions.md                         │
│   → NOT a library key                                               │
└──────────────────────────────────────────────────────────────────────┘
                              ↓ influences
┌──────────────────────────────────────────────────────────────────────┐
│ LAYER 2 — Solution Approach  (feature-level, via AI-Human dialogue) │
│   "Auth0" / "Passport.js" / "Custom OAuth2"                        │
│   → AI proposes 2–3 options, human selects                          │
│   → Determines WHICH TACTIC applies                                 │
│   → Stored in: feature-level assumptions.md                         │
│   → NOT a library key                                               │
└──────────────────────────────────────────────────────────────────────┘
                              ↓ maps to
┌──────────────────────────────────────────────────────────────────────┐
│ LAYER 3 — Implementation Tactic  (per-task, library lookup key)     │
│   saas / tooling / scratch / adapt                                  │
│   → Abstract cost behavior categories — NOT specific solutions      │
│   → IS the library key: (task_type, tactic)                         │
│   → Max 21 × 4 = 84 buckets — manageable data collection           │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.1 Why Tactics, Not Solutions

Specific solutions are infinite (Auth0, Clerk, Passport.js, python-jose, custom JWT...).
Tactics are **cost behavior categories** — solutions within the same tactic have similar
cost profiles:

| Tactic | Cost Behavior | Examples |
|--------|--------------|----------|
| `saas` | Low tokens, low human time — vendor handles logic | Auth0, Stripe, Twilio, SendGrid |
| `tooling` | Medium tokens, medium human time — wire library/framework | Passport.js, Rails scaffold, Django ORM |
| `scratch` | High tokens, high human time — generate everything | Custom OAuth2, bespoke algorithm |
| `adapt` | High input tokens (load existing code), very high human time (regression risk) | Bug fixes, refactors, performance tuning |

The specific solution (Auth0 vs Clerk) affects **complexity score**, not tactic category.

---

## 3. Task Type Library — The Central Artifact

A fixed taxonomy of AI task types, each with a cost entry. This is the lookup table used for
every estimate.

### 3.1 Taxonomy Design Principles

**The library is only as good as the taxonomy.** These rules must hold before collecting
any data — changing task type definitions later invalidates all historical records.

#### Granularity rule: building-block level

```
Too small (function-level):
  "write a function to hash password"
  → too granular, appears in isolation, no reusable cost pattern

Too large (feature-level):
  "build entire auth system"
  → equivalent to a feature; misses the point of decomposition

Correct (building-block level):
  "implement OAuth2 callback handler"
  → 1–3 days of AI-assisted work
  → 300–5,000 tokens typically
  → 0.2–4 hrs human review/rework
  → single coherent AI prompting pattern
  → appears in 3+ different features → enough data to calibrate
```

**Tests to validate a task type:**
- A developer immediately understands what to build from the type name alone
- It has a distinct AI prompting pattern (different prompt structure from other types)
- It will appear at least 3–4 times across different features within 6 months
- Token and human time profile is meaningfully different from adjacent types

#### Stability rule: add-only

```
Allowed   : add new task types (start with industry defaults; data accumulates over time)
Forbidden : rename existing types (breaks historical records)
Forbidden : split a type into two (old records become ambiguous)
Forbidden : merge two types (combined cost profile is meaningless)
```

If a new pattern emerges that doesn't fit existing types → add a new type.
If an existing type seems too broad → do NOT split it; use tactic + complexity
multipliers to differentiate within the type instead.

### 3.2 Taxonomy — 21 Task Types

```
TASK_TYPES = {

  # --- API & Backend Logic ---
  "crud_endpoint",            # REST/GraphQL endpoint with standard CRUD logic
  "auth_flow",                # Authentication/authorization: login, OAuth, JWT, sessions
  "service_class",            # Business logic service layer, use-case handler
  "integration_adapter",      # Connecting to external API / third-party service
  "realtime_feature",         # WebSocket, SSE, pub/sub, event-driven endpoint

  # --- Data ---
  "data_model",               # DB schema, ORM model class, migration
  "data_migration",           # Data transformation / migration script
  "data_pipeline",            # ETL / batch processing / streaming pipeline

  # --- Frontend ---
  "ui_component",             # Web frontend component (form, table, modal, chart)
  "mobile_component",         # Mobile component (React Native, Swift, Kotlin)

  # --- Testing ---
  "unit_test_suite",          # Unit tests for a class/module
  "integration_test",         # Integration, e2e, or contract tests

  # --- Maintenance & Quality ---
  "bug_fix_simple",           # Bug with clear, localized root cause
  "bug_fix_complex",          # Bug requiring investigation across multiple layers
  "refactor",                 # Code restructuring without behavior change
  "performance_optimization", # Profiling, caching, query tuning, memory optimization
  "security_hardening",       # Vulnerability fix, input validation, audit, dependency update

  # --- Infrastructure & Ops ---
  "infra_config",             # CI/CD pipeline, Docker, Terraform, cloud config
  "observability",            # Logging, distributed tracing, metrics, alerting setup

  # --- Documentation ---
  "documentation",            # README, API docs, ADRs, inline docs

  # --- Algorithms ---
  "algorithm",                # Non-trivial algorithm, ML inference, computation logic
}
```

Groupings are informational only — they do not affect library indexing.
The key is always `(task_type, tactic)`.

### 3.3 Valid Tactics per Task Type

Not every tactic is valid for every task type. `adapt` is the **only** valid tactic for
pure maintenance work. Generative tactics (`saas`, `tooling`, `scratch`) apply when building
new code.

| Task Type | saas | tooling | scratch | adapt |
|-----------|:----:|:-------:|:-------:|:-----:|
| `crud_endpoint` | — | ✓ | ✓ | — |
| `auth_flow` | ✓ | ✓ | ✓ | — |
| `service_class` | — | ✓ | ✓ | — |
| `integration_adapter` | ✓ | ✓ | ✓ | — |
| `realtime_feature` | ✓ | ✓ | ✓ | — |
| `data_model` | — | ✓ | ✓ | — |
| `data_migration` | — | ✓ | ✓ | ✓ |
| `data_pipeline` | ✓ | ✓ | ✓ | — |
| `ui_component` | — | ✓ | ✓ | — |
| `mobile_component` | — | ✓ | ✓ | — |
| `unit_test_suite` | — | ✓ | ✓ | — |
| `integration_test` | — | ✓ | ✓ | — |
| `bug_fix_simple` | — | — | — | ✓ only |
| `bug_fix_complex` | — | — | — | ✓ only |
| `refactor` | — | — | — | ✓ only |
| `performance_optimization` | — | — | — | ✓ only |
| `security_hardening` | ✓ | ✓ | — | ✓ |
| `infra_config` | ✓ | ✓ | ✓ | — |
| `observability` | ✓ | ✓ | ✓ | — |
| `documentation` | — | — | ✓ | — |
| `algorithm` | — | ✓ | ✓ | — |

**`security_hardening`** can be both generative (adding a new auth layer) and adapt (patching
an existing vulnerability). AI maps to the correct tactic during the solution dialogue.

**`data_migration`** allows adapt when migrating data in an existing system (reading existing
schema + transform logic), but tooling/scratch apply when building a migration pipeline fresh.

### 3.4 Library Schema

The library is indexed by **(task_type, tactic)** pairs.

**Key fields:**

| Field | Type | Values |
|-------|------|--------|
| `task_type` | string | One of the 21 TASK_TYPES |
| `implementation_tactic` | string | `saas` / `tooling` / `scratch` / `adapt` / `any` |

The `any` tactic holds industry defaults — the ultimate fallback when no tactic-specific
data is available.

**Per-entry stored values:**

| Field | Type | Description |
|-------|------|-------------|
| `industry_tokens_input` | int | Input tokens from published benchmarks |
| `industry_tokens_output` | int | Output tokens from published benchmarks |
| `industry_human_hr` | float | Human time (review + rework) — industry average |
| `org_tokens_input` | int | Actual avg from org records matching this key |
| `org_tokens_output` | int | Actual avg from org records matching this key |
| `org_human_hr` | float | Actual avg from org records matching this key |
| `data_points` | int | Number of actual samples for this (task_type, tactic) |
| `last_updated` | date | When org values were last recalibrated |

**Individual records** (raw data before aggregation) also store:

| Tag Field | Type | Purpose |
|-----------|------|---------|
| `tech_stack` | string | e.g. `"TypeScript + Express"`, `"Python + FastAPI"` |
| `ai_model_version` | string | e.g. `"gpt-4o-2024-11-20"` |
| `developer_level` | string | `junior` / `mid` / `senior` |

Tech stack is stored on individual records but **not used as a library key** to avoid
fragmenting data. Instead it becomes an Effort Factor in Phase 2 (Section 10).

### 3.5 Effective Value Formula

When estimating, blend industry and org values based on how much tactic-specific data exists:

$$V_{effective} = \frac{n}{n + k} \times V_{org} + \frac{k}{n + k} \times V_{industry}$$

Where:
- $n$ = data points for this specific **(task_type, tactic)** combination
- $k$ = prior strength = **5** (trust industry data until you have 5+ org samples)
- When $n = 0$: use pure industry defaults
- When $n = 10$: org data has 67% weight
- When $n \geq 30$: org data has 86%+ weight

### 3.6 Lookup Strategy & Fallback

Data accumulates per (task_type, tactic), so some combinations may have too few records
early on. Use a 3-level fallback:

```
Lookup order when estimating a task:

  Level 1: same task_type + same tactic
             → use if data_points ≥ 3
             → confidence: normal band

  Level 2: same task_type + any tactic (cross-tactic average)
             → use if Level 1 data_points < 3
             → widen confidence band by ×0.1 on each side
             → note in assumptions.md: "tactic-specific data insufficient"

  Level 3: industry defaults (tactic = "any")
             → use if 0 org records for this task_type
             → use bootstrap confidence band (×0.5 – ×2.0)
```

**When tech_stack matters enough to filter:**
If the org has 10+ records for a (task_type, tactic) combination and uses 2+ distinct
stacks, check whether stack splits the data significantly:
- If avg human_hr differs > 50% between stacks → filter by tech_stack at Level 1
- Otherwise → pool all stacks together (less fragmentation, more data)

### 3.7 Industry Defaults

These are the **`any` tactic entries** — used as fallback when no tactic-specific org data
exists. Tactic-specific entries will diverge once org data accumulates.

| Task Type | Input Tokens | Output Tokens | Human Hours | Notes |
|-----------|-------------|---------------|-------------|-------|
| `crud_endpoint` | 800 | 600 | 0.5 | Standard REST, one resource |
| `auth_flow` | 2,000 | 1,500 | 1.5 | Highly tactic-sensitive (0.5–4 hr range) |
| `service_class` | 1,200 | 1,000 | 0.8 | |
| `integration_adapter` | 1,800 | 1,200 | 1.2 | |
| `realtime_feature` | 2,200 | 1,600 | 2.0 | Complex async patterns |
| `data_model` | 500 | 400 | 0.3 | |
| `data_migration` | 1,500 | 1,000 | 2.0 | High human time — verification overhead |
| `data_pipeline` | 1,500 | 1,200 | 1.5 | |
| `ui_component` | 600 | 500 | 0.4 | Web-only |
| `mobile_component` | 900 | 700 | 0.7 | Platform quirks, less AI training data |
| `unit_test_suite` | 500 | 600 | 0.3 | Output > input — generation-heavy |
| `integration_test` | 800 | 900 | 0.5 | |
| `bug_fix_simple` | 1,500 | 400 | 0.8 | `adapt` only — input high (load existing code) |
| `bug_fix_complex` | 3,500 | 800 | 3.5 | `adapt` only — debugging is human-heavy |
| `refactor` | 2,500 | 1,200 | 1.5 | `adapt` only — AI reads to restructure |
| `performance_optimization` | 3,000 | 800 | 3.0 | `adapt` only — profiling is human-heavy |
| `security_hardening` | 2,500 | 800 | 2.0 | `adapt`/`tooling` — human review critical |
| `infra_config` | 800 | 600 | 0.6 | |
| `observability` | 900 | 700 | 0.8 | |
| `documentation` | 400 | 800 | 0.2 | Output-heavy — AI good at this |
| `algorithm` | 2,500 | 1,800 | 2.0 | High complexity, heavy iteration |

> **Source:** Aggregated from GitHub Copilot usage reports, SWE-bench benchmarks,
> and published AI productivity studies. Treat as rough starting points only.

### 3.8 Per-Task Complexity Scoring

Complexity is scored **per task, not per feature**. A single feature often contains tasks
of very different complexity — scoring at feature level over/underestimates individual tasks.

| Score | Meaning | Cost Multiplier |
|-------|---------|----------------|
| 1 | Trivial — pure boilerplate | ×0.6 |
| 2 | Simple — clear pattern exists | ×0.8 |
| 3 | Standard — typical task | ×1.0 |
| 5 | Complex — non-trivial logic | ×1.5 |
| 8 | Highly complex — novel / unknown territory | ×2.5 |

**How it's applied:**
$$tokens_{task} = library\_tokens \times complexity\_multiplier$$
$$human\_hr_{task} = library\_human\_hr \times complexity\_multiplier$$

**Feature-level complexity** (for reporting) = weighted average of per-task scores:
$$complexity_{feature} = \sum_{i} pct_i \times complexity_i$$

---

# Part II — Estimation Workflows

## 4. Input Routing — Scoping the Work

Two decisions before starting estimation:

### 4.1 Scope Decision

```
INPUT
  │
  ├─ Single scoped feature? (fits in 1–2 weeks, clear behavior)
  │     └─ YES → go directly to Section 5 or 6
  │
  └─ Project requirement? (multi-feature, high-level, or multi-week)
        └─ YES → decompose to features first, then apply Section 5 or 6 per feature
```

**Decomposing a project requirement:**

Prompt AI to clarify ambiguities first:
```
Given this project requirement, list:
1. Ambiguous terms or behaviors needing clarification
2. Implicit tasks not stated but almost certainly required
3. External dependencies or integrations to assume
```

Then decompose into independently estimable features (each ~1 sprint):
```
Project: "Build a user authentication system"
  Feature 1: Email/password registration and login
  Feature 2: OAuth2 login (Google)
  Feature 3: Password reset via email
  Feature 4: Session management and token refresh
  Feature 5: Account lockout after failed attempts
  Feature 6: Email verification on signup
```

Aggregate after estimating each feature:
$$C_{project} = \sum_{i=1}^{N} C_{feature_i}$$

Apply project-level uncertainty buffer:

| Input Type | Confidence Band |
|---|---|
| Single well-defined feature | ×0.7 – ×1.5 |
| Single vague feature | ×0.5 – ×2.0 |
| Multi-feature project | ×0.4 – ×2.5 (compounds with N and ambiguity) |

**Signs a feature needs further splitting:**
- Decomposes into more than 10 atomic tasks
- Touches more than 3 separate services or layers
- Estimate range exceeds ×3

### 4.2 Context Decision

```
FEATURE
  │
  ├─ No existing codebase to integrate with? → GREENFIELD → Section 5
  │
  └─ Must fit into an existing codebase?     → BROWNFIELD → Section 6
```

### 4.3 Architecture Pattern (project-level)

For project-level estimation, capture architecture pattern once. This shapes which task
types appear during decomposition:

| Architecture | Impact on Task Distribution |
|-------------|---------------------------|
| Monolith | Fewer `infra_config`/`integration_adapter`; more `service_class` |
| Microservices | More `infra_config`, `integration_adapter`, `observability`; API-heavy |
| Serverless | `infra_config` complexity high; unique deployment patterns |
| Event-driven | `realtime_feature`, `data_pipeline` appear; different from REST-heavy |

Stored in project-level `assumptions.md`. Not a library key — it influences decomposition,
not cost lookup.

---

## 5. Greenfield Workflow

A greenfield feature has **no existing codebase context** to load.

```
Feature description
        │
        ▼
[Step 1] AI–HUMAN SOLUTION DIALOGUE → LOCK TACTIC
        │
        │   AI asks targeted questions to understand constraints:
        │   - "What tech stack / frameworks does the team use?"
        │   - "Is vendor lock-in acceptable?"
        │   - "Performance, scale, or compliance requirements?"
        │   - "Budget constraints on recurring service costs?"
        │
        │   AI proposes 2–3 options with cost preview:
        │   Option A: Auth0 (saas)            → ~$23/mo, 0.5–1 hr work
        │   Option B: Passport.js (tooling)   → no recurring cost, ~1–2 hr
        │   Option C: Custom OAuth2 (scratch) → max control, ~4–5 hr
        │
        │   Human selects. AI maps selection → implementation tactic:
        │       saas    : delegate logic to a vendor API
        │       tooling : use a library or framework conventions
        │       scratch : build from first principles
        │
        │   Note: `adapt` does not apply in greenfield — there is no existing
        │   code to modify. If brownfield tasks arise during decomposition
        │   (e.g., migrating a shared module), route those tasks individually
        │   to the brownfield workflow.
        │
        │   → Tactic locked. Becomes library lookup key: (task_type, tactic).
        │
        ▼
[Step 2] AI decomposes feature into atomic tasks (tactic-aware)
        │
        ▼
[Step 3] Map each task → task type from taxonomy
        │
        ▼
[Step 4] Score complexity PER TASK (1 / 2 / 3 / 5 / 8)
        │
        ▼
[Step 5] Look up cost from Task Type Library
        │   Filter by: task_type AND tactic
        │   Apply fallback if needed (Section 3.6)
        │
        ▼
[Step 6] Per-task: cost = library_value × complexity_multiplier
        │   Sum across tasks → report estimate with confidence band
        │
        ▼
[Step 7] OUTPUT: estimate.md + decomposition.md + assumptions.md
```

**Token cost structure (greenfield):**
```
total_input_tokens  = task_description_tokens + iteration_context_tokens
total_output_tokens = generated_code_tokens
```

**Confidence band by data maturity:**

| Data Points in Library | Confidence Band |
|---|---|
| 0 (industry defaults only) | ×0.5 – ×2.0 |
| 1–9 org data points | ×0.6 – ×1.8 |
| 10–29 org data points | ×0.8 – ×1.3 |
| 30+ org data points | ×0.9 – ×1.1 |

---

## 6. Brownfield Workflow

A brownfield feature must integrate with an **existing codebase**. Context loading is a
distinct, measurable cost that recurs **every AI session** (not once per feature).

### 6.0 Context Loading Token Estimation

Before estimation begins, the estimator must determine how many tokens context loading will
consume across all tasks. This cost is **separate from** the Task Type Library and depends
on codebase size, not task type.

**How to collect codebase metadata (pre-access):**

If source code access is not yet available (e.g., commercial pre-sales), provide the client
with a lightweight CLI tool that outputs **metadata only** (no source code exposed):

```bash
$ npx context-estimator --scope src/auth src/routes src/middleware

{
  "total_files": 47,
  "total_loc": 12340,
  "total_bytes": 164533,
  "estimated_tokens": 41133,
  "modules": {
    "src/auth/":       { "files": 12, "loc": 3200, "tokens": 10667 },
    "src/routes/":     { "files": 20, "loc": 5800, "tokens": 19333 },
    "src/middleware/":  { "files": 15, "loc": 3340, "tokens": 11133 }
  }
}
```

Token estimate per file: `file_size_bytes / 4` (heuristic: ~4 bytes ≈ 1 token).

If the tool cannot be used, fall back to the questionnaire method (Appendix: Questionnaire-Based
Context Estimation).

**Two-tier context model:**

Every AI session loads context in two tiers:

| Tier | What | Loaded when | Estimate from metadata |
|------|------|-------------|------------------------|
| **Global context** ($T_{global}$) | README, architecture overview, coding conventions, dependency map | Every session | ~5–7% of total repo tokens |
| **Task-specific context** ($T_{task\_ctx_j}$) | Modules the task touches (full or partial) | Per task session | Sum of relevant module tokens × weight |

Weight ($W_m$):
- 1.0 — module is directly modified
- 0.3–0.5 — module is referenced / imported but not modified

**Session multiplier** ($S_j$):

Each task may require multiple AI sessions (context window resets, retries):

| Task complexity | Sessions ($S_j$) |
|-----------------|-------------------|
| Simple          | 1                 |
| Medium          | 1–2               |
| Complex         | 2–3               |

**Total context loading tokens for the entire feature:**

$$T_{context\_total} = \sum_{j=1}^{m} (T_{global} + T_{task\_ctx_j}) \times S_j$$

Where $m$ = number of tasks in the decomposition.

**Commercial safety buffer** (when estimating without source code access):

| Metadata source | Buffer |
|-----------------|--------|
| Client ran CLI tool | +20% |
| Questionnaire only | +50–100% |

---

### 6.1 Brownfield Workflow Steps

```
Feature description + existing codebase metadata
        │
        ▼
[Step 0] CONTEXT LOADING ESTIMATION — estimate T_context_total from metadata
        │   - Use client CLI tool output or questionnaire
        │   - Identify modules in scope per task
        │   - Calculate T_global + T_task_ctx per task × sessions
        │   - Apply safety buffer if no direct code access
        │   - Record in brownfield-context.md
        │
        ▼
[Step 1] CONTEXT LOADING — load relevant codebase into AI
        │   - Architecture overview / README
        │   - Module(s) being modified
        │   - Existing patterns (REST style, auth mechanism, ORM, test framework)
        │   - Key dependencies and their usage
        │
        │   Cost: T_context_total (estimated in Step 0, tracked as context_loading_tokens)
        │
        ▼
[Step 2] AI–HUMAN SOLUTION DIALOGUE (constrained by codebase context)
        │
        │   AI infers from loaded context:
        │   - Patterns already in use
        │   - Libraries/frameworks in the stack
        │   - Whether feature adds new code or modifies existing code
        │
        │   AI proposes options, flagging constraints:
        │   e.g. "Codebase uses Passport.js → extending existing auth is lowest risk.
        │         Switching to Auth0 requires session migration — estimate must include
        │         a refactor task with tactic = adapt."
        │
        │   Human selects. AI maps selection → implementation tactic:
        │       saas    : introduce a vendor integration
        │       tooling : add/use library or follow existing framework patterns
        │       scratch : extend existing custom code in the same style
        │       adapt   : modify existing code — fix, refactor, tune, migrate
        │
        │   Key rule: if selected tactic conflicts with existing patterns,
        │   decomposition MUST include an explicit migration/refactor task
        │   with tactic = adapt.
        │
        │   → Tactic locked. Document solution + tactic in assumptions.md.
        │
        ▼
[Step 3] AI decomposes into atomic tasks (tactic + context aware)
        │
        ▼
[Step 4] Map each task → task type + score per-task complexity
        │
        ▼
[Step 5] Score brownfield factors:
        │
        │   Codebase familiarity:         Integration complexity:
        │   High (context loaded) → ×1.0  Standalone module      → ×1.0
        │   Medium (partial)      → ×1.3  Fits existing layer    → ×1.3
        │   Low (cold start)      → ×1.8  Cross-cutting concern  → ×1.7
        │
        │   brownfield_multiplier = codebase_familiarity × integration_complexity
        │
        ▼
[Step 6] Look up cost → apply complexity × brownfield multiplier → sum → confidence band
        │
        ▼
[Step 7] OUTPUT: estimate.md + decomposition.md + assumptions.md + brownfield-context.md
```

**Token cost structure (brownfield):**
```
total_input_tokens  = T_context_total               ← context loading across ALL sessions
                    + task_description_tokens         ← prompts describing each task
                    + iteration_context_tokens        ← follow-up / rework prompts
total_output_tokens = generated_code_tokens
```

Expanded:
$$T_{in} = \underbrace{T_{context\_total}}_{\text{context loading (all sessions)}} + \underbrace{\sum_{j=1}^{m} T_{task\_desc_j}}_{\text{task prompts}} + \underbrace{\sum_{j=1}^{m} T_{iter_j}}_{\text{iteration/follow-up prompts}}$$

Where:
$$T_{context\_total} = \sum_{j=1}^{m} (T_{global} + T_{task\_ctx_j}) \times S_j$$

See Section 6.0 for how to estimate $T_{context\_total}$ from codebase metadata.

**Why track `context_loading_tokens` separately:**
They depend on codebase size and complexity, not task type. Blending them into the library
would inflate task costs and make the library non-portable to greenfield.

**Impact on total cost:** In brownfield projects, context loading tokens typically account
for **50–80% of total input tokens**. Underestimating this component is the most common
source of cost overruns in AI-assisted brownfield development.

**Brownfield-specific risks to flag:**

| Risk | Signal | Mitigation |
|------|--------|------------|
| High regression risk | Touches shared utilities / base classes | Add regression test suite to task list |
| Pattern mismatch | Existing code uses different patterns than AI defaults | Load pattern examples into context |
| Undocumented dependencies | No README or inline docs | Add `documentation` task |
| Legacy code complexity | High cyclomatic complexity | Increase per-task complexity by 1–2 levels |

**Confidence band widening (brownfield):**

| Brownfield Factor | Adjustment |
|---|---|
| Well-documented, clean codebase | No change |
| Average documentation | Widen by ×0.1 each side |
| Legacy / undocumented codebase | Widen by ×0.3 each side |

---

## 7. Cost Formulas

### 7.1 Total AI-Assisted Cost

$$C_{AI} = C_{token} + C_{infra} + (T_{review} + T_{rework} + T_{test} + T_{debug}) \times R_{hourly}$$

Where:
$$C_{token} = \frac{T_{in} \times P_{in} + T_{out} \times P_{out}}{1{,}000{,}000}$$

And $T_{in}$ is composed of:
$$T_{in} = T_{context\_total} + \sum_{j=1}^{m} T_{task\_desc_j} + \sum_{j=1}^{m} T_{iter_j}$$

| Component | Source | Greenfield | Brownfield |
|-----------|--------|------------|------------|
| $T_{context\_total}$ | Section 6.0 (metadata tool or questionnaire) | 0 | Estimated from codebase metadata |
| $\sum T_{task\_desc_j}$ | Task Type Library per-task values | Same | Same (adjusted by brownfield multiplier) |
| $\sum T_{iter_j}$ | Task Type Library iteration estimates | Same | Same (adjusted by brownfield multiplier) |

### 7.2 Human-Only Cost (baseline)

$$C_{Human} = T_{dev} \times R_{hourly}$$

### 7.3 Efficiency Ratio

$$E = \frac{C_{Human}}{C_{AI}}$$

- $E > 1.0$ → AI is cheaper
- $E = 1.0$ → Break even
- $E < 1.0$ → Human is cheaper

### 7.4 AI Productivity Multiplier

$$M = \frac{T_{human\_only}}{T_{review} + T_{rework} + T_{test} + T_{debug}}$$

---

# Part III — Maturity Phases

## 8. Phase 0: Bootstrap (0–9 features)

Used when the historical database has fewer than 10 data points for the relevant task types.

### 8.1 How It Works

1. **AI–Human Solution Dialogue** — AI proposes options, human selects, tactic locked
2. **AI decomposes** — tactic-aware prompt produces atomic task list
3. **Map & score** — each task → task type + per-task complexity score
4. **Lookup** — industry defaults from Section 3.7 (no org data yet)
5. **Calculate** — per task: `library_value × complexity_multiplier`, sum all tasks
6. **Report** — always a range with LOW confidence label

### 8.2 Worked Example

```
Feature: "Add OAuth2 login with Google"

Step 1 — Solution dialogue:
  Human selects: Passport.js (tooling)
  Tactic locked: tooling

Step 2 — Decomposition (tactic-aware):
  Google OAuth callback handler  | auth_flow       | 35% | complexity: 3
  Update user model + migration  | data_model      | 10% | complexity: 2
  Frontend login button + flow   | ui_component    | 20% | complexity: 2
  Unit tests for auth service    | unit_test_suite | 15% | complexity: 2
  Integration tests              | integration_test| 10% | complexity: 3
  Update env config / secrets    | infra_config    | 10% | complexity: 1

Step 3 — Lookup + calculate:
  auth_flow:       (2000+1500) tokens × 1.0 = 3,500 tokens | 1.5 hr × 1.0 = 1.50 hr
  data_model:      (500+400)   tokens × 0.8 =   720 tokens | 0.3 hr × 0.8 = 0.24 hr
  ui_component:    (600+500)   tokens × 0.8 =   880 tokens | 0.4 hr × 0.8 = 0.32 hr
  unit_test_suite: (500+600)   tokens × 0.8 =   880 tokens | 0.3 hr × 0.8 = 0.24 hr
  integration_test:(800+900)   tokens × 1.0 = 1,700 tokens | 0.5 hr × 1.0 = 0.50 hr
  infra_config:    (800+600)   tokens × 0.6 =   840 tokens | 0.6 hr × 0.6 = 0.36 hr
  ─────────────────────────────────────────────────────────────────────────
  TOTAL:                                        8,520 tokens | 3.16 hrs

Step 4 — Apply confidence band (×0.5 – ×2.0, Phase 0):
  Token cost: $0.04 (range: $0.02 – $0.08)     [assuming $2.50/1M in + $10/1M out]
  Human time: 3.2 hrs (range: 1.6 – 6.3 hrs)
  Total cost: $320 (range: $160 – $633)          [assuming $100/hr]
  Confidence: LOW — industry defaults, 0 org data points
```

---

## 9. Phase 1: Calibration (10–29 features)

When 10+ features have actuals collected, two estimation methods become available:

### 9.1 Task Type Library (Improved)

Same as Phase 0, but now the blended formula uses org data:
$$V_{effective} = \frac{n}{n+5} \times V_{org} + \frac{5}{n+5} \times V_{industry}$$

Confidence band narrows to **×0.8 – ×1.3** for task types with 10+ data points.

### 9.2 Analogy Estimation

#### Key insight: similarity is computed on structured attributes, NOT raw text

A new feature arrives as markdown. You cannot compare raw text against historical features.
The solution: **run decomposition first, then query**.

```
Feature F_new (raw markdown)
        │
        ▼
[Run Steps 1–4 of Greenfield/Brownfield Workflow]
  → lock tactic → decompose → map task types → score complexity
        │
        ▼
Structured attributes of F_new:
  task_types[]:   {auth_flow: 35%, data_model: 10%, ui_component: 20%, ...}
  tactic:         tooling
  complexity:     2.6 (weighted avg of per-task scores)
  context_type:   greenfield
  tech_stack:     TypeScript + Express
        │
        ▼  ← only now query historical DB
[Similarity search → top-3 matches → weighted cost]
```

#### Step 1: Build candidate pool

```
Preferred: historical features with same tactic as F_new
Fallback:  all historical features if < 3 same-tactic exist
           (apply cross-tactic penalty: −0.3 to total sim score)
```

#### Step 2: Compute similarity per candidate

$$sim(F_{new}, F_{hist}) = \sum_{i} w_i \times s_i$$

| Attribute | How to compute $s_i$ | Weight $w_i$ | Rationale |
|-----------|---------------------|-------------|-----------|
| Task type overlap | Jaccard: $\frac{\|T_{new} \cap T_{hist}\|}{\|T_{new} \cup T_{hist}\|}$ | 0.35 | Most predictive of cost |
| Complexity match | $1 - \frac{\|c_{new} - c_{hist}\|}{7}$ (range 1–8) | 0.25 | Direct multiplier on cost |
| Tactic match | 1 if same, 0 if different (−0.3 penalty if fallback) | 0.20 | Strong cost driver |
| Context type match | 1 if both greenfield or both brownfield, 0 otherwise | 0.15 | Context loading cost difference |
| Tech stack match | 1.0 same stack, 0.5 same language, 0.0 otherwise | 0.05 | Secondary factor |

**Worked example:**
```
F_new:   task_types={auth_flow, data_model, ui_component, unit_test_suite}
         tactic=tooling, complexity=3, greenfield, TypeScript+Express

F_hist1: task_types={auth_flow, data_model, infra_config, unit_test_suite}
         tactic=tooling, complexity=3, greenfield, TypeScript+Express

  s_task_type = |{auth_flow, data_model, unit_test_suite}|
              / |{auth_flow, data_model, ui_component, infra_config, unit_test_suite}|
              = 3/5 = 0.60
  s_complexity = 1 - |3-3|/7 = 1.0
  s_tactic     = 1.0
  s_context    = 1.0
  s_stack      = 1.0

  sim = 0.35×0.60 + 0.25×1.0 + 0.20×1.0 + 0.15×1.0 + 0.05×1.0
      = 0.21 + 0.25 + 0.20 + 0.15 + 0.05 = 0.86
```

#### Step 3: Top-3 weighted average

$$C_{analogy} = \frac{\sum_{k=1}^{3} sim_k \times C_k^{actual}}{\sum_{k=1}^{3} sim_k}$$

#### Step 4: Blend with library estimate

$$C_{final} = 0.5 \times C_{analogy} + 0.5 \times C_{library}$$

If top-3 all have sim < 0.4 (poor matches), fall back to library estimate only and note
in `assumptions.md`: *"Analogy candidates too dissimilar; library estimate used."*

---

## 10. Phase 2: Parametric Model (30+ features)

Fit a regression model for direct prediction.

### 10.1 Model Form (adapted from COCOMO II)

$$C_{AI} = \alpha \times Size^{\beta} \times \prod_{j=1}^{m} EF_j$$

Where:
- $Size$ = story points or estimated LOC
- $EF_j$ = effort multiplier for factor $j$
- $\alpha, \beta$ = calibrated from org data

### 10.2 Effort Factors

| Factor | Low | Nominal (1.0) | High |
|--------|-----|---------------|------|
| Complexity | Simple patterns (0.8) | Standard logic (1.0) | Novel algorithms (1.3) |
| Spec clarity | Formal, complete (0.8) | Mostly clear (1.0) | Vague, evolving (1.3) |
| Codebase state | Clean, documented (0.8) | Average (1.0) | Legacy, undocumented (1.3) |
| Test coverage | >80% existing (0.8) | 50–80% (1.0) | <50% (1.3) |
| Integration scope | Standalone (0.8) | 2–3 services (1.0) | Distributed system (1.3) |
| AI tool fit | Well-suited (0.8) | Some fit (1.0) | Unproven (1.3) |
| **Implementation tactic** | saas (0.5) | tooling (1.0) | scratch (1.8) |
| **Tech stack AI familiarity** | High — Python, TS (0.8) | Average (1.0) | Low — niche (1.3) |

> **Implementation tactic** has the widest range of any effort factor. A saas tactic can
> cost 3.6× less than scratch for the same task type.

### 10.3 Calibration

```
1. Collect 30+ feature records
2. Log-transform: ln(C_AI) = ln(α) + β·ln(Size) + Σ γj·ln(EFj)
3. Fit α, β, γj using least squares regression
4. Validate using leave-one-out cross-validation (LOOCV)
5. Report MMRE = (1/N) × Σ |actual - predicted| / actual

Target: MMRE < 0.25
Recalibrate trigger: every 20 new features OR when MMRE > 0.30
```

---

# Part IV — Data Collection

## 11. Data Collection Guideline

> This section is the second core deliverable — a step-by-step process for capturing actuals
> so the Task Type Library recalibrates over time.

### 11.1 Overview

```
Feature is DONE (code merged, deployed)
        │
        ▼
[Step 1] Token data — pull from AI tool dashboard           (auto)
        │
        ▼
[Step 2] Code change data — run git script                  (semi-auto)
        │
        ▼
[Step 3] IDE time data — pull from Wakatime                 (semi-auto)
        │
        ▼
[Step 4] Fill end-of-feature form — < 3 minutes             (manual)
        │
        ▼
[Step 5] Attribution — split totals across task types
        │
        ▼
[Step 6] Recalibrate Task Type Library — rolling mean update
        │
        ▼
[Step 7] Validate — check if estimate was within confidence band
```

### 11.2 What to Collect

#### Group A: Auto-collect (zero developer effort)

| Field | Source | Cadence |
|-------|--------|---------|
| `token_input` | OpenAI / Anthropic / Copilot dashboard | Per feature |
| `token_output` | Same | Per feature |
| `token_cost_usd` | Calculated: `(input × P_in) + (output × P_out)` | Per feature |
| `ai_model_version` | API logs | Per feature |
| `test_pass_rate_ci` | CI pipeline output | Per feature |
| `static_analysis_issues` | CI pipeline output | Per feature |

#### Group B: Semi-auto (one-time tool setup)

| Field | Tool | Setup |
|-------|------|-------|
| `time_in_ide_hr` | [Wakatime](https://wakatime.com/) | Install plugin; tag project |
| `lines_generated` | Git script (see 11.3) | Run per PR merge |
| `lines_kept` | Git script | Run per PR merge |
| `rework_rate` | `lines_kept / lines_generated` | Calculated |
| `ai_turns_count` | IDE extension or proxy logger | Per feature |

#### Group C: Manual (end-of-feature form, < 3 min)

| Field | Input Type | Purpose |
|-------|-----------|---------|
| `task_types[]` | Multi-select from taxonomy | Attribution |
| `task_type_pct[]` | % per type (sum to 100%) | Attribution |
| `complexity_score_per_task` | Score per task type | Per-task calibration |
| `implementation_tactic` | Radio: saas / tooling / scratch / adapt | Library lookup key |
| `tactic_detail` | Text — specific solution used | e.g., "Passport.js", "Auth0" |
| `tech_stack` | Text — primary language + runtime | e.g., "TypeScript + Express" |
| `review_time_hr` | Number (1 decimal) | Human effort |
| `rework_time_hr` | Number (1 decimal) | Rework signal |
| `greenfield_brownfield` | Radio | Context type |
| `codebase_familiarity` | Radio: High / Medium / Low | Brownfield only |
| `ai_helpfulness` | 1–5 scale | Quality signal |
| `notes` | Free text, optional | Qualitative |

### 11.3 Tool Setup

#### Wakatime

```
1. Create free account at wakatime.com
2. Install IDE plugin (VS Code / JetBrains / Neovim)
3. Add API key to plugin settings
4. Tag each project by repo name (auto-detected from git)
5. Pull per-project time: wakatime.com/api/v1/users/current/summaries
```

#### Git script — rework rate

```bash
#!/bin/bash
# Usage: ./measure_rework.sh <feature_branch> <base_branch>
# Convention: AI-generated commits prefixed with "[ai]"

FEATURE_BRANCH=$1
BASE_BRANCH=${2:-main}

LINES_GENERATED=$(git log --oneline $BASE_BRANCH..$FEATURE_BRANCH \
  | grep "\[ai\]" \
  | awk '{print $1}' \
  | xargs -I{} git show {} --stat \
  | grep "insertion" \
  | awk '{sum += $4} END {print sum}')

LINES_KEPT=$(git diff $BASE_BRANCH...$FEATURE_BRANCH --stat \
  | tail -1 | awk '{print $4}')

echo "Lines generated by AI: $LINES_GENERATED"
echo "Lines kept in final:   $LINES_KEPT"
echo "Rework rate:           $(echo "scale=2; $LINES_KEPT / $LINES_GENERATED" | bc)"
```

#### AI API token export

| Provider | How |
|----------|-----|
| OpenAI | platform.openai.com → Usage → filter by date → export CSV |
| Anthropic | console.anthropic.com → Usage → filter by date |
| GitHub Copilot | Organization billing dashboard or Copilot API |
| AWS Bedrock | CloudWatch → `InputTokenCount` / `OutputTokenCount` per model |

### 11.4 Collection Triggers

| When | What to Do |
|------|-----------|
| **Feature starts** | Open form draft; pre-fill feature_id, start_date, context type. Begin `[ai]` commit prefix. |
| **During dev** | Use labeled timers: "AI-review" and "AI-rework". Everything else is auto. |
| **PR merged** | Run git script. Pull Wakatime time. Note token dashboard. |
| **End of sprint** | Export AI API tokens → allocate to features by date. Complete forms. Run attribution + recalibration. Check MMRE. |

### 11.5 Attribution — Splitting Totals Across Task Types

```
Example: Feature "OAuth Login"
  Total tokens:       5,200  (from API export)
  Total human time:   4.1 hrs (review + rework from timers)

  Task type split from form:
    auth_flow        35%
    data_model       10%
    ui_component     20%
    unit_test_suite  15%
    integration_test 10%
    infra_config     10%

  Attribution result:
    auth_flow        → 1,820 tokens, 1.44 hrs
    data_model       →   520 tokens, 0.41 hrs
    ui_component     → 1,040 tokens, 0.82 hrs
    unit_test_suite  →   780 tokens, 0.62 hrs
    integration_test →   520 tokens, 0.41 hrs
    infra_config     →   520 tokens, 0.41 hrs
```

Each row becomes one data point in the library under (task_type, tactic).

### 11.6 Recalibrate the Library

```python
def recalibrate(task_type, tactic, new_tokens_in, new_tokens_out, new_human_hr):
    entry = library[(task_type, tactic)]
    n = entry["data_points"]

    entry["org_tokens_input"]  = (entry["org_tokens_input"] * n + new_tokens_in)  / (n + 1)
    entry["org_tokens_output"] = (entry["org_tokens_output"] * n + new_tokens_out) / (n + 1)
    entry["org_human_hr"]      = (entry["org_human_hr"] * n + new_human_hr)        / (n + 1)
    entry["data_points"]       = n + 1
    entry["last_updated"]      = today()
```

### 11.7 Validate — Did the Estimate Hold Up?

After each feature, compare estimate vs actual:

$$MMRE = \frac{1}{N} \sum_{i=1}^{N} \frac{|actual_i - predicted_i|}{actual_i}$$

| MMRE | Status | Action |
|------|--------|--------|
| < 0.15 | Excellent | No action |
| 0.15 – 0.25 | Good | Monitor |
| 0.25 – 0.35 | Degrading | Review last 10 features for systematic bias |
| > 0.35 | Poor | Force recalibration; check taxonomy or model version change |

### 11.8 Data Quality Rules

| Rule | Reason |
|------|--------|
| Tag every record with `implementation_tactic` | Primary lookup key — mismatched records corrupt estimates |
| Tag every record with `tech_stack` | Stack affects human hours; Effort Factor in Phase 2 |
| Tag every record with `ai_model_version` | Capability changes invalidate old data |
| Tag every record with `developer_level` | Proficiency affects human effort |
| Never delete old records — use recency weighting | $w_i = e^{-\lambda \cdot age_i}$ where $\lambda = 0.1$/month |
| Flag outliers (error > 3× median) | Anomalies corrupt the library |
| Backup library snapshot every 10 features | Rollback point |
| Reject records where `task_type_pct[]` ≠ 100% | Attribution math breaks |
| Minimum completeness: Groups A + C required | Group B preferred but not blocking |

### 11.9 Historical Data ROI by Phase

| Phase | Features | Value of Data | Primary Benefit |
|-------|----------|--------------|-----------------|
| Phase 0 | 0–9 | Low | Build habit; detect obvious outliers |
| Phase 1 | 10–29 | Medium | Tactic-specific lookups work; spot org-vs-industry deltas |
| Phase 2 | 30+ | High | Regression calibrated; MMRE < 25%; approach ROI quantified |

**Decision rule:** Start with Group C (manual form only) for the first 10 features. Add
Group B tooling once the team confirms the methodology is worth continuing.

---

# Part V — Operations

## 12. Configuration & File Layout

### 12.1 File Structure

```
.ai/
  task-type-library.json     ← org data + calibrated values (changes over time)
  estimation-config.json     ← static config: hourly rate, model, token pricing
```

Both files are optional. Agent falls back to industry defaults if absent.

### 12.2 `task-type-library.json`

```json
{
  "version": "1.0",
  "last_calibrated": "2026-04-19",
  "entries": [
    {
      "task_type": "auth_flow",
      "tactic": "tooling",
      "industry_tokens_input": 2000,
      "industry_tokens_output": 1500,
      "industry_human_hr": 1.5,
      "org_tokens_input": null,
      "org_tokens_output": null,
      "org_human_hr": null,
      "data_points": 0,
      "last_updated": null
    }
  ]
}
```

### 12.3 `estimation-config.json`

```json
{
  "hourly_rate_usd": 100,
  "ai_model": "claude-sonnet-3.7",
  "token_price": {
    "input_per_1m": 2.50,
    "output_per_1m": 10.00
  },
  "prior_strength_k": 5
}
```

---

## 13. Model Version Handling

AI model version is the **most disruptive source of data drift** in the library.

### 13.1 Sensitivity by Task Group

| Sensitivity | Task Types | Why |
|-------------|-----------|-----|
| **High** | `algorithm`, `bug_fix_complex`, `security_hardening`, `performance_optimization` | Reasoning ability varies significantly |
| **Low** | `crud_endpoint`, `ui_component`, `data_model`, `documentation`, `infra_config` | Formulaic — most models handle equally |
| **Medium** | Everything else | Some variation, absorbed by confidence band |

### 13.2 Same-Tier vs Cross-Tier

```
Same tier (GPT-4o ↔ Claude Sonnet):     variation ±15% → within band, no action
Upgrade (→ o3 / GPT-5):                 human_hr × 0.8 → likely under-estimate
Downgrade (→ mini / Haiku):             human_hr × 1.3 → apply to complex tasks
```

### 13.3 What to Reset on Model Switch

```
Minor version (gpt-4o-2024-05 → gpt-4o-2024-11):
  → No reset. Tag new records. Blended formula handles drift.

Major switch (different model family or tier):
  → High sensitivity types: reset org data_points = 0, revert to defaults
  → Low sensitivity types:  keep org data, widen band by ×0.2
  → Re-collect 5–10 calibration samples on high-sensitivity types
```

### 13.4 Industry Defaults Update Trigger

```
Update when:
  - Switching to a major new model version
  - MMRE > 40% after 10+ features AND org data doesn't explain the bias

Do NOT update on:
  - Token pricing changes → update estimation-config.json only
  - Calendar trigger → no evidence = no update
```

---

## 14. Known Limitations and Risks

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| AI pricing changes frequently | Token cost estimates stale | Tag records with model + price snapshot |
| Attribution by % is approximate | Inaccurate per-task data | Improves with volume |
| Manual time tracking has recall bias | Undercount review/rework | Use timers during work |
| Developer AI proficiency varies | Same task costs differ by person | Tag developer level; stratify |
| AI capabilities improve rapidly | Historical data less predictive | Recency weighting; version-tag |
| Small sample early on | Wide confidence intervals | Communicate uncertainty explicitly |
| Task type misclassification | Wrong entry updated | Periodic audit |

---

## 15. Implementation Roadmap

### Week 1–2: Setup

- [ ] Finalize task type taxonomy
- [ ] Populate `.ai/task-type-library.json` with industry defaults
- [ ] Configure `.ai/estimation-config.json`
- [ ] Set up Wakatime on developer IDEs
- [ ] Set up git script for rework rate
- [ ] Enable AI API usage export
- [ ] Build end-of-feature form
- [ ] Document hourly rate

### Week 3–6: Phase 0 — Bootstrap

- [ ] Run estimation for each new feature before starting
- [ ] Collect actuals for every completed feature
- [ ] Attribute actuals to task types
- [ ] Recalibrate library after each feature
- [ ] Track data_points count

### Week 7–10: Phase 1 — Calibration

- [ ] At 10 features: enable analogy estimation (library + analogy blend)
- [ ] Measure MMRE
- [ ] Identify task types with largest estimation error
- [ ] Adjust complexity multipliers if systematic bias found

### Week 11+: Phase 2 — Parametric

- [ ] At 30 features: run regression calibration
- [ ] Validate with LOOCV
- [ ] If MMRE < 0.25: parametric model becomes primary
- [ ] Set up MMRE monitoring — alert when > 0.30
- [ ] Schedule recalibration every 20 features

### Ongoing

- [ ] Every feature: collect actuals → recalibrate
- [ ] Every 20 features: refit parametric model
- [ ] Every quarter: review taxonomy — add task types based on usage

---

# Appendix

## A. Estimation Agent — Automation Plan

> **Discovery note:** This section captures the vision for automating the estimation workflow
> as a GitHub Copilot agent skill. No implementation started. Documents the approach for
> when moving from discovery to build.

### A.1 Agent Skills

| Skill | Input | Output |
|-------|-------|--------|
| `estimate.greenfield` | Feature/project `.md` file | `estimate.md` + `decomposition.md` + `assumptions.md` |
| `estimate.brownfield` | Feature `.md` + repo context | Same + `brownfield-context.md` |

### A.2 `estimate.greenfield` Flow

```
/estimate.greenfield specs/feature-oauth-login.md
```

1. Read + parse requirement file
2. If project-level: decompose to features first
3. For each feature:
   a. AI-Human Solution Dialogue → lock tactic
   b. Decompose into atomic tasks (tactic-aware)
   c. Map each task → task type
   d. Score per-task complexity (auto-infer; flag for user confirmation)
   e. Lookup cost from library filtered by tactic + fallback
   f. Apply per-task complexity multiplier
   g. Calculate token cost + human time
   h. Apply confidence band
4. Aggregate (if project-level)
5. Write output files

### A.3 `estimate.brownfield` Flow

```
/estimate.brownfield specs/feature-add-payment-webhook.md
```

Same as greenfield, with additions:
1. **Context loading** — read repo README, modules, patterns
2. Solution dialogue **constrained** by detected patterns
3. Flag if tactic conflicts with existing patterns → add `adapt` migration tasks
4. Score brownfield factors → apply multiplier
5. Additional output: `brownfield-context.md`

### A.4 Output: `estimate.md` Structure

```
The estimate:
- Token cost: point estimate + range
- Human time: point estimate + range
- Total USD cost: point estimate + range
- Confidence level and basis (# data points)
- Efficiency ratio E = C_Human / C_AI
- Per-task-type cost breakdown

Model assumption:
- Estimated with: <model from config>
- Same model tier: estimate valid within confidence band
- Upgrade (o3/GPT-5): expect human hours ~20% lower
- Downgrade (mini/Haiku): add ~30% to human hours for complex tasks

Cost-optimal model recommendation:
- Routine tasks (crud_endpoint, ui_component, data_model, documentation):
    → GPT-4o-mini or Claude Haiku adequate. ~60% token savings.
- Complex tasks (algorithm, bug_fix_complex, security_hardening):
    → Claude Sonnet 3.7 or o3 recommended.
    → Mini/Haiku: -60% tokens but +30% human rework → net more expensive
```

### A.5 Shared Behavior

| Behavior | Detail |
|----------|--------|
| Config location | `.ai/task-type-library.json` + `.ai/estimation-config.json` |
| Library source | `.ai/task-type-library.json` if present; else hardcoded defaults |
| Model assumption | From config; default Claude Sonnet 3.7. Always stated in output. |
| Confidence band | Always reported — never a bare point estimate |
| Complexity scoring | Auto-infer per task; flag for user to confirm |
| Ambiguous requirements | List in `assumptions.md`; make reasonable default |
| Output location | `estimates/<feature-slug>/` alongside input file |
| Idempotency | Re-running overwrites previous output |

### A.6 Out of Scope for Agent

- Writing or modifying source code
- Running tests, builds, or terminal commands
- Storing actuals — collection is separate (Section 11)
- Recalibrating the library
- Integrating with Jira, Rally, or external systems
- Gantt charts, sprint plans, resource allocation

### A.7 Open Questions

- [x] Config file location → `.ai/` folder
- [x] Hourly rate input → `.ai/estimation-config.json` + `--hourly-rate` override
- [ ] Brownfield file selection strategy to stay within context limits
- [ ] Agent behavior: ask clarifying questions vs autonomous with assumptions.md
- [ ] Support `--repo-url` for external repos?
- [ ] Handoff to collection template (`/estimate.collect`) after estimation?

---

## B. Worked Example — End to End

### Input

```markdown
# Feature: OAuth2 Login with Google

Allow users to sign in using their Google account.
Affected areas: backend auth service, frontend login page, user DB schema.
Context: Greenfield — new project, TypeScript + Express stack.
```

### Step 1 — Solution Dialogue

```
AI: "Is vendor lock-in acceptable for auth?"
Human: "No, prefer library-based."

AI proposes:
  Option A: Passport.js (tooling) → library, team controls, ~1–2 hr
  Option B: Custom OAuth2 (scratch) → max control, ~4–5 hr

Human selects: Option A
Tactic locked: tooling
```

### Step 2 — Decomposition

| Task | Task Type | Complexity | % Effort |
|------|-----------|:----------:|:--------:|
| Google OAuth callback handler | `auth_flow` | 3 | 35% |
| Update user model + migration | `data_model` | 2 | 10% |
| Frontend login button + flow | `ui_component` | 2 | 20% |
| Unit tests for auth service | `unit_test_suite` | 2 | 15% |
| Integration tests | `integration_test` | 3 | 10% |
| Update env config / secrets | `infra_config` | 1 | 10% |

### Step 3 — Lookup + Calculate

| Task Type | Library (in+out) | × Multiplier | Tokens | Human Hr |
|-----------|:----------------:|:------------:|:------:|:--------:|
| `auth_flow` | 3,500 | ×1.0 | 3,500 | 1.50 |
| `data_model` | 900 | ×0.8 | 720 | 0.24 |
| `ui_component` | 1,100 | ×0.8 | 880 | 0.32 |
| `unit_test_suite` | 1,100 | ×0.8 | 880 | 0.24 |
| `integration_test` | 1,700 | ×1.0 | 1,700 | 0.50 |
| `infra_config` | 1,400 | ×0.6 | 840 | 0.36 |
| **TOTAL** | | | **8,520** | **3.16** |

### Step 4 — Cost + Confidence

```
Token cost: $0.04  (8,520 tokens × blended price)
Human cost: $316   (3.16 hrs × $100/hr)
Total:      $316   (tokens are noise — labor dominates)

Confidence band (Phase 0, ×0.5 – ×2.0):
  Range: $158 – $632
  Human: 1.6 – 6.3 hrs
  Level: LOW — industry defaults, 0 org data points
```

### After Feature is Built — Data Collection

```
Actual tokens:     6,100
Actual human time: 3.8 hrs
MMRE for this feature: |3.16 - 3.8| / 3.8 = 16.8%  ← within band ✓

Attribution → recalibrate library → next estimate is more accurate.
```

---

# Appendix

## A. Questionnaire-Based Context Estimation

Fallback method when the client cannot run the CLI metadata tool. Use during discovery calls
to estimate $T_{context\_total}$ from verbal/written answers.

### Discovery Questions

| # | Question | Purpose |
|---|----------|---------|
| 1 | What is the tech stack? (language, framework, DB) | Complexity profile |
| 2 | How old is the codebase? | Legacy indicator |
| 3 | How many modules or services in total? | Scale indicator |
| 4 | How many modules does this feature touch? | Scope of context loading |
| 5 | What is the documentation quality? (README, API docs, architecture diagrams) | Documentation quality |
| 6 | Monolith or microservices? | Architecture complexity |
| 7 | Does the project have a test suite? Approximate coverage? | Code quality signal |
| 8 | How many developers are actively contributing? | Proxy for codebase size |

### Scoring Matrix — Context Complexity Score (CCS)

| Factor | Low (1) | Medium (2) | High (3) |
|--------|---------|------------|----------|
| Codebase age | < 2 years | 2–5 years | > 5 years |
| Modules touched | 1–3 | 4–8 | 9+ |
| Documentation | Good (README, diagrams, API docs) | Partial | Minimal / none |
| Architecture | Simple monolith or clean microservices | Moderate (few services) | Complex (many services, shared libs) |
| Team size (proxy) | 1–3 devs | 4–10 devs | 10+ devs |

$$CCS = \frac{\sum scores}{5}$$

### CCS → Token Estimate (per session)

| CCS | Profile | $T_{context}$ per session | Typical cost (GPT-4o, $2.50/1M) |
|-----|---------|---------------------------|----------------------------------|
| 1.0–1.4 | Small / clean | 1,000–3,000 | $0.003–$0.008 |
| 1.5–2.0 | Medium | 3,000–10,000 | $0.008–$0.025 |
| 2.1–2.6 | Large / complex | 10,000–30,000 | $0.025–$0.075 |
| 2.7–3.0 | Legacy / monolith | 30,000–60,000 | $0.075–$0.150 |

Multiply by number of sessions (see Section 6.0) and apply the commercial safety buffer
(+50–100% for questionnaire-only estimates) to get $T_{context\_total}$.
