# Problem 3: Multi-Agent Expert Debate System

## 1. Problem Statement

Build a **general-purpose multi-agent system** where AI agents act as domain experts, **debating each other** to help humans make better decisions on **any type of problem** — not limited to software development.

### 1.1 Scope: Any Real-World Decision

Examples of problems the system should handle:

| Domain | Example Problem |
|--------|----------------|
| **Personal / Life** | Should I change jobs? Should I relocate to another city? |
| **Business** | Should we enter a new market? Should we acquire this company? |
| **Technology** | Should we migrate to microservices? Which cloud provider? |
| **Finance** | Should I invest in X? How should I allocate budget? |
| **Healthcare** | What treatment approach is best for this patient profile? |
| **Policy** | What are the tradeoffs of this regulation? |
| **Product** | Should we build feature A or feature B first? |
| **Career** | Should I pursue an MBA or stay technical? |

The system is **domain-agnostic**. Expert roles are **configured per problem type**, not hardcoded.

### 1.2 Core Requirements

- **Clarification first**: Before any debate, agents collectively ensure the problem is fully understood
- Each agent has a **configurable role/persona** (e.g., Risk Advisor, Financial Analyst, Psychologist)
- Agents **debate and challenge** each other's positions rather than blindly agreeing
- **Token budget** is configurable per agent and per debate session
- The system produces a **synthesized recommendation** from the debate
- Agent roles, prompts, and configurations are **externalized** (not hard-coded)
- The user can **answer clarifying questions** before debate begins

---

## 2. Discovery Phase

### 2.1 Key Questions to Answer

1. **What debate patterns produce the best decisions?**
   - Round-robin (each agent speaks in turn)?
   - Adversarial (explicit pro/con roles)?
   - Socratic (one agent questions others)?
   - Parliamentary (propose → oppose → rebut → vote)?
   - How many rounds of debate are optimal before diminishing returns?

2. **How should agent roles be defined?**
   - What level of persona detail produces meaningful differentiation?
   - Should roles be static or dynamically assigned based on the problem?
   - How many agents per debate? (too few = groupthink, too many = noise)
   - Should there be a moderator/judge agent?

3. **How to handle token budget constraints?**
   - Fixed budget per agent per round?
   - Pooled budget across all agents?
   - Priority-based allocation (domain expert gets more tokens on relevant topics)?
   - How to prevent one agent from dominating the conversation?

4. **How to synthesize a final decision from debate?**
   - Voting (each agent votes, majority wins)?
   - Weighted voting (domain expert's vote counts more on relevant topics)?
   - Judge agent synthesizes (separate agent reads debate, decides)?
   - Confidence-weighted consensus?

5. **How to evaluate debate quality?**
   - Did the debate surface risks that a single agent missed?
   - Did the final recommendation change after debate vs initial positions?
   - How often does the debate produce better decisions than a single expert prompt?

6. **How should the clarification phase work?**
   - Who asks the questions — a dedicated Clarifier agent or all agents?
   - How many clarification rounds before forcing debate to start?
   - What happens if user cannot answer a clarifying question?
   - How to detect when the problem is "sufficiently understood" to proceed?
   - Should clarification be synchronous (user responds) or agents infer from context?

7. **What LLM architecture to use?**
   - Same model for all agents (different system prompts)?
   - Different models for different roles (e.g., Claude for analysis, GPT for code)?
   - Local models for cost-sensitive roles?
   - How to manage API calls efficiently?

8. **How to make the system truly domain-agnostic?**
   - How to auto-select relevant expert roles from the problem description?
   - What is the minimal role set that covers most problem types?
   - Should the system suggest roles to the user or pick them automatically?

### 2.2 Discovery Activities

| # | Activity | Purpose | Output |
|---|----------|---------|--------|
| 1 | Survey multi-agent frameworks | Understand existing approaches | Framework comparison matrix |
| 2 | Prototype 3 debate patterns | Test which pattern produces best output | Pattern evaluation report |
| 3 | Prototype clarification phase | Test how agents ask questions | Clarifier design spec |
| 4 | Test on diverse problem domains | Validate domain-agnostic design | Cross-domain role catalog |
| 5 | Run 10 debates on known problems | Measure debate quality vs single-agent | Quality baseline |
| 6 | Test token budget strategies | Find optimal allocation approach | Budget strategy recommendation |
| 7 | Benchmark LLM combinations | Cost vs quality tradeoffs | Model selection matrix |
| 8 | Design configuration schema | Enable role/prompt customization | Config schema spec |
| 9 | Prototype judge/synthesis mechanism | Test decision aggregation methods | Synthesis algorithm |
| 10 | User study: clarification UX | Measure friction of clarification Q&A | UX recommendations |

### 2.3 Problem Taxonomy Discovery

Before building role catalogs, classify problem types to identify the universal dimensions of any decision:

| Dimension | Description | Example Values |
|-----------|-------------|---------------|
| **Reversibility** | Can the decision be undone? | Reversible / Partially / Irreversible |
| **Time horizon** | When do consequences manifest? | Immediate / Months / Years / Decades |
| **Stakeholders** | Who is affected? | Self / Team / Organization / Society |
| **Uncertainty level** | How much is unknown? | Low / Medium / High / Extreme |
| **Value conflicts** | Are there competing values? | None / Tradeoffs / Deep conflicts |
| **Data availability** | Is evidence available? | Rich data / Sparse / None |
| **Expertise required** | What domains must be considered? | Single / Multi-disciplinary / Highly specialized |

This taxonomy drives **which expert roles are relevant** for each problem.

### 2.4 Existing Frameworks to Evaluate

| Framework | Language | Key Feature | Debate Support | Notes |
|-----------|----------|-------------|---------------|-------|
| **AutoGen** (Microsoft) | Python | Multi-agent conversation | Yes, group chat | Most mature, good for debate patterns |
| **CrewAI** | Python | Role-based agents with tasks | Limited | Good role system, less debate-oriented |
| **LangGraph** | Python | Stateful agent graphs | Custom | Flexible but lower-level |
| **Swarm** (OpenAI) | Python | Lightweight agent handoffs | No | Too simple for debate |
| **Custom** | Python | Full control | Full | Most effort but maximum flexibility |

**Recommendation**: Start with **AutoGen** for rapid prototyping, evaluate if custom implementation is needed later.

### 2.5 Expected Discovery Outputs

- **Debate pattern recommendation**: Which pattern works best for decision-making
- **Role catalog**: 6-8 expert roles with system prompts
- **Token budget strategy**: How to allocate tokens across agents and rounds
- **Synthesis algorithm**: How to produce a final recommendation from debate
- **Architecture decision**: Build custom vs use framework
- **Cost projection**: Expected API cost per debate session

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
                    ┌─────────────────────┐
                    │     User Input      │
                    │  (Any Problem /     │
                    │   Decision Needed)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Orchestrator      │
                    │   (Session Mgr)     │
                    └──────────┬──────────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
      ┌────────▼──────┐ ┌─────▼──────┐ ┌──────▼───────┐
      │  Agent Pool   │ │   Token    │ │   Config     │
      │  (Experts)    │ │   Budget   │ │   Store      │
      │               │ │   Manager  │ │  (YAML/JSON) │
      └────────┬──────┘ └─────┬──────┘ └──────────────┘
               │               │
      ┌────────▼───────────────▼────────┐
      │        PHASE 1: CLARIFICATION   │
      │  Clarifier Agent asks questions │
      │  User answers → context built   │
      │  Loop until problem is clear    │
      └────────────────┬────────────────┘
                       │  Problem Brief (finalized)
      ┌────────────────▼────────────────┐
      │        PHASE 2: DEBATE ARENA    │
      │  Round 0: Independent positions │
      │  Round 1..N: Challenge & Refine │
      │  Convergence check each round   │
      └────────────────┬────────────────┘
                       │
              ┌────────▼────────┐
              │  PHASE 3: SYNTH │
              │  Judge Agent    │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Final Report   │
              │ + Recommendation│
              │ + Transcript    │
              └─────────────────┘
```

### 3.2 Core Components

| Component | Responsibility |
|-----------|---------------|
| **Orchestrator** | Manages full session lifecycle: clarification → debate → synthesis |
| **Clarifier Agent** | Asks targeted questions to build a complete problem brief |
| **Role Selector** | Auto-assigns relevant expert roles based on problem type |
| **Agent Pool** | Instantiates agents from role configs, manages personas |
| **Token Budget Manager** | Tracks token usage per agent per phase, enforces limits |
| **Config Store** | Loads role definitions, debate rules, model settings |
| **Debate Arena** | Executes debate rounds, manages conversation history |
| **Judge Agent** | Synthesizes debate into final recommendation |

### 3.3 Full Session Flow

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 0: SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  a. User submits problem statement (free text, any domain)
  b. Orchestrator classifies problem type
  c. Role Selector proposes 3-5 expert roles
  d. User confirms or adjusts roles
  e. Token budgets allocated per phase

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 1: CLARIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Goal: Build a complete, unambiguous Problem Brief
  before any debate begins.

  Step 1 — Each expert agent independently reads the
           problem and submits up to 3 questions it
           needs answered to give useful advice.

  Step 2 — Clarifier Agent deduplicates and prioritizes
           questions. Selects top 5 most critical.

  Step 3 — Questions presented to user. User answers.

  Step 4 — Clarifier Agent evaluates answers:
           IF problem is now clear → generate Problem Brief
           IF still ambiguous → repeat Step 1 (max 3 loops)
           IF user cannot answer → agents note as
             "unknown variable" and proceed with assumptions

  Step 5 — Problem Brief finalized:
           - Restated problem (precise, complete)
           - Key constraints and context
           - Stated assumptions (from unanswered questions)
           - Success criteria (what does a good decision look like?)
           - Explicit out-of-scope boundaries

  User confirms Problem Brief → proceed to Phase 2.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 2: DEBATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Round 0 — Independent Positions
    - Each agent reads Problem Brief only
    - Independently produces: position + top 3 arguments
    - No agent sees others' responses
    - Establishes baseline (did agents start differently?)

  Round 1..N — Structured Debate
    For each round:
      a. Agents receive all positions from previous round
      b. Each agent must:
         - Identify the strongest opposing argument → engage with it
         - Update or defend their position with reasoning
         - Explicitly state if position changed and why
      c. Token budget deducted per response
      d. Convergence check:
         IF ≥80% of agents agree on same recommendation → early stop
      e. Budget check:
         IF tokens exhausted → force final positions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 3: SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - Judge agent receives: Problem Brief + full transcript
  - Produces structured final report (see Section 7.2)
  - Flags any assumptions that significantly affect outcome
  - Provides confidence score and uncertainty range

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - Problem Brief (clarification output)
  - Recommendation with confidence and uncertainty range
  - Key arguments for and against
  - Unresolved risks and dissenting views
  - Assumptions that were made
  - Full debate transcript (audit trail)
  - Token usage summary
```

### 3.4 Clarification Phase — Design Details

#### 3.4.1 Clarifier Agent Behavior

The Clarifier Agent is a **meta-agent** — it does not have a domain opinion. Its only job is to ensure the problem is understood well enough to debate.

**Clarifier system prompt core**:

```
You are a professional facilitator. You do NOT give opinions or
recommendations. Your only role is to ensure a problem is stated
with enough clarity for expert advisors to debate it meaningfully.

For a given problem statement, identify:
1. What key information is MISSING that experts would need?
2. What ASSUMPTIONS are being made implicitly?
3. What CONSTRAINTS or context are unstated?
4. What does SUCCESS look like — what is the decision criteria?
5. What is EXPLICITLY OUT OF SCOPE?

Generate clear, concise questions. Prioritize by impact:
  - High: without this, experts cannot give useful advice
  - Medium: would significantly improve advice quality
  - Low: nice to have

Always output exactly 3-5 HIGH priority questions. No more.
```

#### 3.4.2 Question Categories

| Category | Purpose | Example |
|----------|---------|--------|
| **Context** | Background needed to frame the problem | "What is your current situation / starting point?" |
| **Constraints** | Hard limits experts must respect | "What is your budget / timeline / non-negotiables?" |
| **Success criteria** | What does a good outcome look like? | "How will you know if this decision was right?" |
| **Stakeholders** | Who is affected and whose input matters? | "Who else is impacted by this decision?" |
| **Alternatives** | What options are already on the table? | "What options are you already considering?" |
| **Risk tolerance** | How much downside is acceptable? | "What is the worst outcome you could accept?" |
| **Time horizon** | Short-term vs long-term tradeoffs | "Are you optimizing for 1 year or 5 years?" |

#### 3.4.3 Problem Brief Template

```markdown
## Problem Brief

**Problem Statement** (restated precisely):
[Clear, unambiguous single-paragraph description]

**Key Context**:
- [Context point 1]
- [Context point 2]

**Hard Constraints** (must be respected in any recommendation):
- [Constraint 1]
- [Constraint 2]

**Success Criteria** (what does a good decision look like?):
- [Criterion 1]
- [Criterion 2]

**Options on the Table** (known alternatives):
1. [Option A]
2. [Option B]
3. Open (agents may propose new options)

**Stakeholders Affected**:
- [Stakeholder 1 and their interests]

**Risk Tolerance**:
[Description of acceptable downside]

**Time Horizon**:
[Short / Medium / Long term focus]

**Assumptions** (from unanswered questions):
- [Assumption 1] — flagged as uncertain
- [Assumption 2] — flagged as uncertain

**Out of Scope**:
- [What will NOT be considered]

**Confirmed by user**: [Yes / Pending]
```

#### 3.4.4 Clarification Loop Rules

| Rule | Description |
|------|------------|
| **Max loops** | 3 clarification rounds maximum before forcing debate |
| **Min questions** | Clarifier must ask at least 3 questions in first loop |
| **User skip** | User can skip a question; agents note as assumption |
| **Force proceed** | If user explicitly says "proceed", skip remaining clarification |
| **Brief confirmation** | User must confirm the Problem Brief before debate starts |
| **Brief edits** | User can edit the Problem Brief directly before confirming |

---

## 4. Agent Role Design

### 4.1 Universal Expert Roles (Domain-Agnostic)

These roles can be applied to **any type of problem**, not just software:

| Role | Expertise | Bias | Applicable Domains |
|------|-----------|------|-------------------|
| **Risk Advisor** | Risk identification, probability, mitigation | Risk-averse, sees downside | Any irreversible or high-stakes decision |
| **Financial Analyst** | Cost, ROI, budget, economic tradeoffs | Cost-focused | Business, career, investment, project decisions |
| **Strategist** | Long-term thinking, competitive position, options | Big-picture, may ignore near-term | Business, career, life decisions |
| **Pragmatist** | Execution feasibility, practical constraints | Focuses on what is actually doable | Any decision requiring action plan |
| **Devil's Advocate** | Actively challenges any consensus forming | Contrarian by design | All debates (prevents groupthink) |
| **Ethicist** | Moral implications, stakeholder impact, fairness | Values-focused | Policy, healthcare, AI, org decisions |
| **Data Scientist** | Evidence-based reasoning, stats, research | Demands data before conclusions | Any domain with measurable outcomes |
| **Psychologist** | Human behavior, cognitive biases, motivation | People-focused | Personal, team, product, UX decisions |

### 4.2 Domain-Specific Role Extensions

When the problem is in a specific domain, add domain roles on top of universal ones:

| Domain | Additional Roles |
|--------|----------------|
| **Software** | Software Architect, Security Analyst, QA Engineer, DevOps Engineer, Tech Lead |
| **Business** | Marketing Strategist, Operations Expert, Legal Advisor, HR Consultant |
| **Healthcare** | Medical Expert, Patient Advocate, Regulatory Specialist |
| **Finance/Investment** | Portfolio Manager, Tax Advisor, Market Analyst |
| **Personal/Life** | Life Coach, Career Counselor, Relationship Counselor |
| **Policy/Government** | Economist, Legal Scholar, Sociologist, Public Health Expert |

### 4.3 Recommended Role Sets by Problem Type

| Problem Type | Core Roles (3-5) |
|-------------|------------------|
| Career decision (job change, MBA) | Strategist, Financial Analyst, Pragmatist, Psychologist, Devil's Advocate |
| Business / market entry | Strategist, Financial Analyst, Risk Advisor, Pragmatist, Ethicist |
| Technology choice | Pragmatist, Risk Advisor, Financial Analyst, Data Scientist, Devil's Advocate |
| Investment decision | Financial Analyst, Risk Advisor, Data Scientist, Strategist |
| Life decision (relocate, relationship) | Psychologist, Strategist, Pragmatist, Ethicist, Devil's Advocate |
| AI vs Human (Problem 1) | Pragmatist, Risk Advisor, Financial Analyst, Data Scientist |
| Cost estimation (Problem 2) | Financial Analyst, Data Scientist, Pragmatist, Risk Advisor |
| Policy / regulatory | Ethicist, Data Scientist, Risk Advisor, Strategist, Devil's Advocate |

### 4.4 Role Configuration Schema

```yaml
# agent-config.yaml

# ─────────────────────────────────────────
# CLARIFICATION CONFIG
# ─────────────────────────────────────────
clarification:
  model: "claude-sonnet-4-20250514"
  max_questions_per_round: 5
  max_rounds: 3
  clarifier_max_tokens: 2000
  allow_user_skip: true
  require_brief_confirmation: true

# ─────────────────────────────────────────
# AGENT ROLES
# ─────────────────────────────────────────
agents:
  risk_advisor:
    name: "Risk Advisor"
    model: "claude-sonnet-4-20250514"
    system_prompt: |
      You are a senior risk advisor with expertise across business,
      financial, operational, and strategic risk. You have no domain
      allegiance — you apply rigorous risk thinking to any problem.

      Your core job:
      - Identify the top risks in any proposed course of action
      - Estimate likelihood and severity for each risk (use ranges)
      - Distinguish known risks from unknown unknowns
      - Propose specific mitigations, not vague warnings
      - Acknowledge when a risk is actually acceptable

      When debating:
      - Challenge optimistic positions with concrete failure scenarios
      - Do not block every option — rank risks to help prioritization
      - Quantify risk wherever possible (e.g., "30-50% probability")
    max_tokens_per_round: 1500
    temperature: 0.3
    priority_topics: ["risk", "downside", "failure", "uncertainty"]
    vote_weight: 1.0

  financial_analyst:
    name: "Financial Analyst"
    model: "claude-sonnet-4-20250514"
    system_prompt: |
      You are a financial analyst who thinks in terms of total cost,
      ROI, opportunity cost, and economic tradeoffs. You apply this
      to any domain: business decisions, career choices, project
      planning, personal finance.

      Your core job:
      - Always quantify costs, benefits, and savings in concrete terms
      - Factor in hidden and long-term costs, not just upfront
      - Calculate opportunity cost (what is given up by each choice)
      - Challenge vague claims like "it will pay off" with numbers

      When debating:
      - Require evidence before accepting financial claims
      - Compare alternatives using consistent metrics
      - Be explicit about assumptions in your estimates
    max_tokens_per_round: 1200
    temperature: 0.2
    priority_topics: ["cost", "ROI", "budget", "investment", "savings"]
    vote_weight: 1.0

  devils_advocate:
    name: "Devil's Advocate"
    model: "claude-sonnet-4-20250514"
    system_prompt: |
      You are a professional Devil's Advocate. Your role is NOT to
      have a personal opinion — it is to challenge whatever the
      emerging consensus is. If most agents support Option A,
      you argue for Option B. If agents seem to agree, you find
      the strongest possible counter-argument.

      Your core job:
      - Prevent premature consensus
      - Surface the strongest possible objection to any position
      - Play devil's advocate even if you personally agree with the
        majority — your role demands it
      - Ask "what if we're wrong?" and "what are we not considering?"

      You do NOT have to believe what you argue. You are a
      structured thinking tool to stress-test conclusions.
    max_tokens_per_round: 1000
    temperature: 0.7
    priority_topics: ["counterargument", "assumptions", "overlooked"]
    vote_weight: 0.7  # lower weight in final vote — role is to challenge, not decide

  # ... more agents (pragmatist, strategist, ethicist, psychologist, etc.)

# ─────────────────────────────────────────
# DEBATE CONFIG
# ─────────────────────────────────────────
debate_config:
  max_rounds: 4
  min_rounds: 2
  convergence_threshold: 0.8   # 80% agreement → early stop
  total_token_budget: 50000
  debate_pattern: "parliamentary"  # round-robin | adversarial | parliamentary | socratic
  judge_model: "claude-sonnet-4-20250514"
  judge_max_tokens: 3000

# ─────────────────────────────────────────
# TOKEN BUDGET ALLOCATION
# ─────────────────────────────────────────
token_budget:
  clarification_phase: 0.15   # 15% of total
  initial_positions:   0.15   # 15% of total
  debate_rounds:       0.50   # 50% of total
  synthesis_judge:     0.20   # 20% of total (reserved, never reallocated)

# ─────────────────────────────────────────
# ROLE AUTO-SELECTION
# ─────────────────────────────────────────
role_selection:
  auto_select: true            # let system pick roles from problem description
  min_agents: 3
  max_agents: 5
  always_include: ["devils_advocate"]  # always in every debate
  domain_detection: true       # detect domain and add domain-specific roles
```

---

## 5. Token Budget Management

### 5.1 Budget Allocation Strategy

**Approach: Tiered Budget with Priority Boost**

```
Total Session Budget: B_total (configurable, e.g., 50,000 tokens)

Allocation:
  - Initial positions:  20% of B_total (split equally among agents)
  - Debate rounds:      60% of B_total (split per round, per agent)
  - Synthesis/Judge:    20% of B_total

Per-agent per-round budget:
  B_agent_round = (0.6 × B_total) / (N_agents × N_rounds)

Priority boost:
  If agent's priority_topics match the current problem:
    B_agent_round *= 1.3 (30% boost)
    Deducted from other agents proportionally
```

### 5.2 Budget Enforcement Rules

| Rule | Description |
|------|-------------|
| **Hard cap** | Agent cannot exceed max_tokens_per_round (response truncated) |
| **Soft cap** | Warning at 80% of round budget; agent must conclude |
| **Rollover** | Unused tokens from early rounds roll over to later rounds |
| **Minimum** | Every agent gets at least 500 tokens per round (prevents silencing) |
| **Judge reserve** | 20% of total budget is reserved for synthesis (never reallocated) |

### 5.3 Cost Estimation Per Session

| Model | Input $/1M tokens | Output $/1M tokens | 50K session cost |
|-------|-------------------|--------------------|-----------------:|
| GPT-4o | $2.50 | $10.00 | ~$0.30 |
| Claude Sonnet | $3.00 | $15.00 | ~$0.45 |
| Claude Opus | $15.00 | $75.00 | ~$2.25 |
| GPT-4o mini | $0.15 | $0.60 | ~$0.02 |

**Strategy**: Use cheaper models for initial positions, premium models for judge synthesis.

---

## 6. Debate Patterns (Detailed)

### 6.1 Parliamentary Pattern (Recommended for Decisions)

Adapted from parliamentary debate, best for binary/ternary decisions (AI vs Human vs Hybrid).

```
Round 1: Opening Statements
  - Each agent states initial position with reasoning
  - No references to other agents (independent analysis)

Round 2: Cross-examination
  - Each agent reads all Round 1 positions
  - Must identify the WEAKEST argument from another agent and challenge it
  - Must identify the STRONGEST argument from another agent and acknowledge it

Round 3: Rebuttal
  - Each agent responds to challenges directed at them
  - May update their position based on new information
  - Must explicitly state: "I maintain" or "I revise my position"

Round 4: Closing Statements
  - Final position with confidence level (0-100%)
  - Top 3 factors driving the decision
  - Remaining concerns / risks
```

### 6.2 Adversarial Pattern (Best for Risk Analysis)

Explicitly assigns pro/con roles.

```
Setup:
  - Half the agents argue FOR the proposal (e.g., "use AI")
  - Half argue AGAINST
  - Roles may not match their natural bias (forces deeper thinking)

Round 1: Pro case → Con case
Round 2: Pro rebuts Con → Con rebuts Pro
Round 3: Both sides present revised positions
Judge: Evaluates both sides
```

### 6.3 Socratic Pattern (Best for Requirements Clarification)

One agent asks questions, others answer.

```
Setup:
  - Socratic Questioner (asks probing questions)
  - Expert Panel (answers from their domain)

Round 1: Questioner asks 3-5 targeted questions about the feature
Round 2: Each expert answers from their perspective
Round 3: Questioner identifies contradictions and asks follow-ups
Round 4: Experts reconcile contradictions
```

---

## 7. Synthesis & Decision Aggregation

### 7.1 Judge Agent

A separate agent that does NOT participate in the debate. It reads the full transcript and produces the final output.

**Judge system prompt core**:

```
You are an impartial judge synthesizing a multi-expert debate.
Your job is NOT to add your own opinion but to:
1. Identify the strongest arguments from each side
2. Determine where genuine consensus exists vs performative agreement
3. Flag unresolved risks that no agent adequately addressed
4. Produce a clear recommendation with confidence level
5. Document dissenting views that the team should consider
```

### 7.2 Output Format

```markdown
## Debate Summary

**Problem**: [Feature description]
**Agents**: [List of participating agents]
**Pattern**: Parliamentary | Rounds: 4
**Token Usage**: 42,300 / 50,000

## Recommendation

**Decision**: [AI-first | Hybrid | Human-first]
**Confidence**: 78%

## Key Arguments

### For AI-first (supported by: Cost Analyst, AI Specialist)
1. [Argument 1 with evidence]
2. [Argument 2 with evidence]

### For Human-first (supported by: Security Analyst)
1. [Argument 1 with evidence]

### Consensus Points
- All agents agreed that [X]
- All agents agreed that [Y]

### Unresolved Disagreements
- Security Analyst raised [concern] which was not fully addressed
- Cost Analyst's estimate of [X hours] was disputed by Tech Lead

## Risk Register
| Risk | Raised By | Severity | Mitigated? |
|------|-----------|----------|-----------|
| ... | ... | ... | ... |

## Agent Position Summary
| Agent | Initial Position | Final Position | Changed? | Confidence |
|-------|-----------------|----------------|----------|-----------|
| ... | ... | ... | ... | ... |

## Full Transcript
[Collapsible section with complete debate log]
```

---

## 8. Integration with Problems 1 & 2

### 8.1 Multi-Agent as Decision Engine for Problem 1

Instead of a static scoring model, the multi-agent debate **replaces or augments** the weighted scoring:

```
Feature Spec → Clarification Phase → Agent Debate → AI/Hybrid/Human Recommendation
                       ↓                    ↓
              Makes ambiguous specs    Surfaces risks a scoring
              concrete before debate   model would miss
```

**When to use debate vs scoring model**:
- **Scoring model**: Quick triage, low-stakes features, batch evaluation
- **Agent debate**: High-stakes features, ambiguous cases, when scoring confidence is low

### 8.2 Multi-Agent for Cost Estimation (Problem 2)

Agents can debate cost estimates:
- Financial Analyst provides base estimate
- Pragmatist challenges with execution complexity
- Risk Advisor adds contingency factors
- Data Scientist validates with historical analogy data
- Debate produces a **range** (optimistic / likely / pessimistic) instead of a point estimate

### 8.3 General Decision Questions (Beyond Software)

Examples of the system being used for non-software decisions:

```
User: "Should I leave my current job to join an early-stage startup?"

Clarifier asks:
  1. What is your current financial situation (savings runway)?
  2. What stage is the startup (pre-seed / seed / Series A)?
  3. What is your equity offer and vesting schedule?
  4. What is your risk tolerance — how would you handle 0 income for 6 months?
  5. What does success look like for you in 3 years?

Agents assigned: Strategist, Financial Analyst, Risk Advisor, Psychologist, Devil's Advocate

Debate outcome: Structured recommendation with confidence score,
                key risks, and conditions under which each option wins.
```

---

## 9. Implementation Roadmap

### Phase 1: Clarification Prototype (Week 1-2)
- [ ] Choose framework (AutoGen vs custom)
- [ ] Build Clarifier Agent with structured question generation
- [ ] Implement Problem Brief template and confirmation loop
- [ ] Test clarification on 5 diverse problem types (career, business, tech, life, policy)
- [ ] Evaluate: does clarification improve debate quality?

### Phase 2: Core Debate Engine (Week 3-4)
- [ ] Define 5 universal roles: Risk Advisor, Financial Analyst, Strategist, Devil's Advocate, Pragmatist
- [ ] Implement basic round-robin debate (2 rounds)
- [ ] Implement token budget manager
- [ ] Test end-to-end (clarification → debate) on 5 known problems
- [ ] Evaluate: does the full flow produce better output than a single agent?

### Phase 3: Debate Patterns (Week 5-6)
- [ ] Implement parliamentary pattern
- [ ] Implement adversarial pattern
- [ ] Implement socratic pattern
- [ ] Compare pattern quality on 5 diverse problems
- [ ] Select default pattern per problem type

### Phase 4: Configuration & Role Catalog (Week 7-8)
- [ ] Design and implement YAML configuration schema
- [ ] Define all 8 universal + domain-specific roles with detailed prompts
- [ ] Implement auto role selection from problem description
- [ ] Build judge/synthesis agent
- [ ] Test domain-agnostic role assignment across 5 domains

### Phase 5: Evaluation & Tuning (Week 9-10)
- [ ] Run 20 debates across diverse problem domains
- [ ] Measure: debate quality, token efficiency, recommendation accuracy
- [ ] Tune system prompts based on failure modes
- [ ] Tune token budgets and convergence thresholds
- [ ] Document best practices per role

### Phase 6: Integration (Week 11-12)
- [ ] Connect to Problem 1 (AI vs Human decision framework)
- [ ] Connect to Problem 2 (cost estimation)
- [ ] Build CLI interface for running sessions
- [ ] Add session transcript logging and export
- [ ] Implement token usage reporting

### Phase 7: Web UI (Optional)
- [ ] Session input form (any problem, free text)
- [ ] Live clarification Q&A interface
- [ ] Live debate progress viewer
- [ ] Configuration editor for agent roles
- [ ] Historical session browser and analytics

---

## 10. Evaluation Criteria

### 10.1 Debate Quality Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Diversity of arguments** | Number of unique arguments across agents | ≥ 3 distinct arguments per side |
| **Challenge rate** | % of positions that were challenged by another agent | ≥ 60% |
| **Position change rate** | % of agents that revised their position during debate | 20-50% (too low = no real debate; too high = instability) |
| **Risk surface rate** | Number of risks identified that wouldn't appear in single-agent | ≥ 2 per debate |
| **Decision accuracy** | Does the recommendation match the actual best approach (measured retroactively) | ≥ 75% |

### 10.2 Efficiency Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Token efficiency** | Useful insights per 1000 tokens | Subjective; track over time |
| **Rounds to convergence** | Average rounds before early stop | 2-3 rounds |
| **Cost per debate** | USD per debate session | < $1.00 for standard decisions |
| **Latency** | Wall-clock time per debate | < 3 minutes (parallel agent calls) |

---

## 11. Technical Considerations

### 11.1 Parallelization

Within each round, agent responses are **independent** (they all respond to the same input). Call all agents in parallel to reduce latency:

```
Round N:
  Input = debate history from Round N-1
  [Agent1(input)] ──┐
  [Agent2(input)] ──┤── All called in parallel
  [Agent3(input)] ──┤
  [Agent4(input)] ──┘
  Collect all responses → build Round N history
```

### 11.2 Context Window Management

Each round, agents receive the full debate history. This grows linearly:

```
Round 1: ~500 tokens context (problem only)
Round 2: ~3,000 tokens (problem + 4 agent responses)
Round 3: ~6,000 tokens (problem + 8 agent responses)
Round 4: ~10,000 tokens (problem + 12 agent responses)
Judge:   ~12,000 tokens (full transcript)
```

**Mitigation for long debates**:
- Summarize previous rounds instead of passing full transcript
- Use a "memory" agent that compresses history between rounds
- Limit to 4 rounds maximum

### 11.3 Preventing Degenerate Debates

| Problem | Symptom | Solution |
|---------|---------|----------|
| **Groupthink** | All agents agree immediately | Assign adversarial roles; require at least one dissent |
| **Echo chamber** | Agents repeat each other's points | Score for novelty; penalize repetition in prompts |
| **Token waste** | Agents give long preambles, repeat the question | Enforce structured response format |
| **Deadlock** | Agents never converge | Force final vote after max rounds; judge breaks ties |
| **Hallucination amplification** | One agent's hallucination is accepted by others | Require evidence/citations; judge flags unsupported claims |

---

## 12. Open Questions

- [ ] Should agents have "memory" across debates (learn from past decisions)?
- [ ] How to handle domain-specific knowledge (e.g., inject codebase context)?
- [ ] Should users be able to intervene mid-debate (provide clarification)?
- [ ] How to version-control agent prompts and track prompt evolution?
- [ ] What is the minimum viable set of agents for useful debate? (3? 4?)
- [ ] How to handle conflicting model outputs (e.g., Claude vs GPT disagree on approach)?
- [ ] Should the system support async debates (agents respond over hours, not minutes)?

---

## 13. Notes

-
