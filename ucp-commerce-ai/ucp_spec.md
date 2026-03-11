# UCP Multi-Agent Shopping Platform — Feature Specification

## 1. Overview

### 1.1 Project Name
**Bazaar** — A Multi-Agent Agentic Commerce Platform built on UCP (Universal Commerce Protocol)

### 1.2 Elevator Pitch
Bazaar is a multi-agent system where specialized AI agents collaborate to fulfill a user's shopping intent — from understanding what they want, discovering merchants, comparing prices, negotiating fulfillment options, to completing checkout — all orchestrated through UCP as the standard commerce protocol.

### 1.3 Problem Statement
Current e-commerce experiences require users to manually:
- Search across multiple merchant websites
- Compare prices, shipping options, and discounts
- Manage different checkout flows per merchant
- Track orders across fragmented systems

AI agents can automate this, but **without a standard protocol**, each agent-merchant integration is a custom build. UCP solves the protocol problem. This project solves the **multi-agent orchestration** problem on top of UCP.

### 1.4 Goals
| Goal | Description |
|------|-------------|
| **G1** | Build a working multi-agent system that demonstrates UCP's full checkout lifecycle |
| **G2** | Implement agent-to-agent communication using A2A protocol for inter-agent coordination |
| **G3** | Support 3-5 mock merchants with different capability profiles (varying extensions) |
| **G4** | Demonstrate UCP discovery, negotiation, checkout, fulfillment, discount, and order capabilities |
| **G5** | Create a chat-based UI where users interact naturally and agents work collaboratively behind the scenes |
| **G6** | Serve as a portfolio project demonstrating deep UCP + multi-agent expertise |

### 1.5 Non-Goals
- Production payment processing (all payments are mocked/simulated)
- Real merchant integrations (all merchants are mock UCP servers)
- Mobile app (web-only for MVP)
- User authentication against real OAuth providers (simulated identity linking)
- Production-grade security (no real PCI-DSS compliance needed)

---

## 2. Architecture

### 2.1 High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│               (Chat UI — React + Vite + Tailwind)                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ WebSocket / SSE
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PYTHON BACKEND (FastAPI + MS Agent Framework)           │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │            ORCHESTRATOR AGENT (Workflow Graph)                │   │
│  │    MS Agent Framework graph-based workflow orchestration      │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Intent   │  │ Discovery│  │ Comparison│  │ Checkout         │   │
│  │ Agent    │  │ Agent    │  │ Agent     │  │ Agent            │   │
│  └────┬─────┘  └────┬─────┘  └─────┬────┘  └───────┬──────────┘   │
│       │              │              │               │              │
│  ┌────┴─────┐  ┌─────┴────┐  ┌─────┴────┐  ┌───────┴──────────┐   │
│  │ Budget   │  │ Review   │  │ Order    │  │ Notification     │   │
│  │ Agent    │  │ Agent    │  │ Tracker  │  │ Agent            │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              LLM PROVIDER INTERFACE                           │   │
│  │   ┌──────────┐  ┌──────────────┐  ┌───────────────────┐      │   │
│  │   │ Distilled│  │ OpenAI API   │  │ Anthropic API     │      │   │
│  │   │ (Ollama) │  │ (GPT-4o-mini)│  │ (Claude Haiku)    │      │   │
│  │   └──────────┘  └──────────────┘  └───────────────────┘      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ UCP REST / A2A / MCP
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  MERCHANT LAYER (FastAPI servers)                    │
│                                                                     │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐          │
│  │ TechStore │ │ FashionHQ │ │ BookWorld │ │ HomeGoods │          │
│  │ (Full)    │ │ (+ Disc.) │ │ (Basic)   │ │ (+ Fulfil)│          │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘          │
│                                                                     │
│  Each merchant: UCP profile at /.well-known/ucp                    │
│  Different capability sets — simulates real-world variance          │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Communication Patterns

```
User ──► Orchestrator ──► Intent Agent        (understand request)
                     ──► Discovery Agent      (find merchants via UCP)
                     ──► Comparison Agent     (compare offers)
                     ──► Budget Agent         (validate budget constraints)
                     ──► Checkout Agent       (execute purchase via UCP)
                     ──► Review Agent         (product reviews/ratings)
                     ──► Order Tracker Agent  (post-purchase tracking)
                     ──► Notification Agent   (status updates to user)
```

**Inter-agent protocol**: Agents communicate via MS Agent Framework's graph-based workflow engine with typed edges and executors. Each agent is an `Agent` node in the workflow graph, orchestrated by handoff, sequential, or concurrent patterns.

---

## 3. Agent Specifications

### 3.1 Orchestrator Agent

**Role**: Central coordinator. Receives user messages, decomposes into tasks, delegates to specialist agents, aggregates results, and responds to user.

**Capabilities**:
- Parse user intent and create execution plan
- Route tasks to appropriate specialist agents
- Manage conversation state and context
- Handle agent failures with fallback strategies
- Maintain shopping session state (cart, preferences, budget)

**Internal State**:
```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class OrchestratorState(BaseModel):
    session_id: str
    conversation_history: list[Message]
    active_agents: dict[AgentId, AgentStatus]
    shopping_context: ShoppingContext
    execution_plan: list[Task]

class ShoppingContext(BaseModel):
    user_preferences: UserPreferences
    budget: BudgetConstraints
    cart: list[CartItem]
    discovered_merchants: list[MerchantProfile]
    checkout_sessions: dict[str, CheckoutSession]
```

**Decision Logic**:
```
IF user says "find me X under $Y"
  → spawn IntentAgent → DiscoveryAgent → ComparisonAgent → present to user

IF user says "buy it" or confirms selection
  → spawn BudgetAgent (validate) → CheckoutAgent (execute UCP checkout)

IF user says "track my order"
  → spawn OrderTrackerAgent

IF user says "compare these two"
  → spawn ComparisonAgent with specific items
```

---

### 3.2 Intent Agent

**Role**: Understand user's natural language shopping intent and extract structured parameters.

**Input**: Raw user message (natural language)
**Output**: Structured shopping intent

```python
class ActionType(str, Enum):
    SEARCH = "search"
    COMPARE = "compare"
    BUY = "buy"
    TRACK = "track"
    CANCEL = "cancel"
    REVIEW = "review"

class FulfillmentType(str, Enum):
    SHIPPING = "shipping"
    PICKUP = "pickup"
    DIGITAL = "digital"

class DeliverySpeed(str, Enum):
    EXPRESS = "express"
    STANDARD = "standard"
    ECONOMY = "economy"

class ProductQuery(BaseModel):
    category: str | None = None        # "electronics", "books", "clothing"
    keywords: list[str]                # ["wireless", "headphones", "noise-cancelling"]
    attributes: dict[str, str] = {}    # {"color": "black", "brand": "Sony"}

class SearchConstraints(BaseModel):
    max_price: int | None = None       # in cents (UCP standard)
    min_rating: float | None = None    # 1-5
    fulfillment: FulfillmentType | None = None
    delivery_speed: DeliverySpeed | None = None

class ShoppingIntent(BaseModel):
    action: ActionType
    product: ProductQuery
    constraints: SearchConstraints = SearchConstraints()
    quantity: int | None = None
    merchant_preference: str | None = None
```

**LLM Integration**: Uses the configured LLM provider (distilled model for cost efficiency or OpenAI/Anthropic for complex queries) with structured output (JSON mode) to extract intent. Falls back to clarification questions if ambiguous.

**Example Flows**:
```
User: "I need noise-cancelling headphones under $200, preferably Sony"
→ Intent: {
    action: "search",
    product: { category: "electronics", keywords: ["noise-cancelling", "headphones"], attributes: { brand: "Sony" } },
    constraints: { maxPrice: 20000 }
  }

User: "Compare the top 3 options"
→ Intent: { action: "compare" } // uses context from previous search

User: "Buy the second one with express shipping"
→ Intent: { action: "buy", quantity: 1, constraints: { deliverySpeed: "express" } }
```

---

### 3.3 Discovery Agent

**Role**: Discover UCP-compliant merchants and their capabilities.

**Capabilities**:
- Fetch and cache merchant profiles from `/.well-known/ucp`
- Parse capability declarations (checkout, fulfillment, discounts, etc.)
- Run capability intersection algorithm
- Rank merchants by capability match for the shopping intent
- Resolve and compose schemas for negotiated capabilities

**UCP Integration Points**:
```python
class MerchantCapabilities(BaseModel):
    checkout: bool = False
    fulfillment: bool = False          # dev.ucp.shopping.fulfillment
    discounts: bool = False            # dev.ucp.shopping.discount
    identity_linking: bool = False     # dev.ucp.common.identity_linking
    order: bool = False                # dev.ucp.shopping.order
    buyer_consent: bool = False        # dev.ucp.shopping.buyer_consent

class TransportType(str, Enum):
    REST = "rest"
    MCP = "mcp"
    A2A = "a2a"
    EMBEDDED = "embedded"

class DiscoveryResult(BaseModel):
    merchant: MerchantInfo
    capabilities: MerchantCapabilities
    transports: list[TransportType]
    payment_handlers: list[PaymentHandler]
    match_score: float                  # 0-100 relevance to intent

class MerchantInfo(BaseModel):
    id: str
    name: str
    base_url: str
    profile: dict  # raw /.well-known/ucp
```

**Merchant Registry**: Maintains a local registry of known merchants (simulating a search index). In production, this could be a crawled index or a directory service.

```python
# Merchant registry (simulated — in production this would be a search engine)
MERCHANT_REGISTRY = [
    {"name": "TechStore",  "url": "http://localhost:3001"},
    {"name": "FashionHQ", "url": "http://localhost:3002"},
    {"name": "BookWorld", "url": "http://localhost:3003"},
    {"name": "HomeGoods", "url": "http://localhost:3004"},
]
```

---

### 3.4 Comparison Agent

**Role**: Compare products across multiple merchants on price, capabilities, fulfillment, and total cost.

**Capabilities**:
- Create checkout sessions on multiple merchants simultaneously
- Extract and normalize pricing (handle different currencies, minor units)
- Compare fulfillment options (if merchant supports fulfillment extension)
- Compare discount availability (if merchant supports discount extension)
- Calculate total cost of ownership (price + shipping + tax)
- Generate ranked comparison with explanation

**Comparison Matrix**:
```python
class TotalCost(BaseModel):
    subtotal: int
    shipping: int
    tax: int
    discount: int
    total: int

class FulfillmentOption(BaseModel):
    method: str
    cost: int
    estimated_days: int

class ComparisonItem(BaseModel):
    merchant: str
    product: Product
    fulfillment: list[FulfillmentOption] | None = None
    cheapest_shipping: int | None = None
    fastest_delivery: str | None = None
    discounts: list[Discount] | None = None
    best_discount: int | None = None
    total_cost: TotalCost
    checkout_session_id: str | None = None   # UCP session ID if created
    score: float                              # 0-100 composite score

class Recommendation(BaseModel):
    best_overall: ComparisonItem
    best_price: ComparisonItem
    best_delivery: ComparisonItem
    best_value: ComparisonItem    # price + quality + delivery combined

class ComparisonResult(BaseModel):
    items: list[ComparisonItem]
    recommendation: Recommendation
    reasoning: str                # LLM-generated explanation
```

**Scoring Algorithm**:
```
score = (priceScore * 0.35) + (deliveryScore * 0.25) +
        (capabilityScore * 0.20) + (discountScore * 0.20)

where:
  priceScore     = 100 * (1 - (price - minPrice) / (maxPrice - minPrice))
  deliveryScore  = based on fastest/cheapest shipping option
  capabilityScore = bonus for fulfillment tracking, buyer consent, etc.
  discountScore  = value of best available discount relative to price
```

---

### 3.5 Budget Agent

**Role**: Enforce user's budget constraints and financial preferences.

**Capabilities**:
- Validate purchases against stated budget
- Track cumulative spending in session
- Warn about price changes between comparison and checkout
- Suggest alternatives if over budget
- Calculate value-for-money metrics

**State**:
```python
class PendingPurchase(BaseModel):
    merchant: str
    product_id: str
    amount: int
    checkout_session_id: str

class PriceAlert(BaseModel):
    product_id: str
    previous_price: int
    current_price: int
    change_percent: float

class BudgetState(BaseModel):
    session_budget: int | None = None      # user-stated max budget
    spent: int = 0                          # cumulative in session
    pending_purchases: list[PendingPurchase] = []
    price_alerts: list[PriceAlert] = []     # if price changed since comparison
```

**Rules Engine**:
```
RULE: If totalCost > sessionBudget → BLOCK and notify user with alternatives
RULE: If price changed > 5% since comparison → WARN user before proceeding
RULE: If cumulative spending > 80% of budget → INFO user about remaining budget
RULE: If no budget set and totalCost > $500 → ASK user to confirm
```

---

### 3.6 Checkout Agent

**Role**: Execute the UCP checkout lifecycle on the selected merchant.

**UCP Operations** (maps 1:1 to UCP Checkout REST Binding):

| Step | UCP Operation | HTTP Method | Endpoint |
|------|--------------|-------------|----------|
| 1. Create session | Create Checkout | `POST` | `/checkout-sessions` |
| 2. Set buyer info | Update Checkout | `PUT` | `/checkout-sessions/{id}` |
| 3. Set fulfillment | Update Checkout | `PUT` | `/checkout-sessions/{id}` |
| 4. Review & confirm | Get Checkout | `GET` | `/checkout-sessions/{id}` |
| 5. Complete purchase | Complete Checkout | `POST` | `/checkout-sessions/{id}/complete` |
| 6. Cancel (if needed) | Cancel Checkout | `POST` | `/checkout-sessions/{id}/cancel` |

**Checkout Flow State Machine**:
```
                    ┌─────────┐
                    │  IDLE   │
                    └────┬────┘
                         │ createCheckout()
                         ▼
                  ┌──────────────┐
                  │  INCOMPLETE  │◄──────────────┐
                  └──────┬───────┘               │
                         │ updateBuyer()          │ updateFulfillment()
                         │ updateFulfillment()    │
                         ▼                        │
              ┌─────────────────────┐             │
              │ READY_FOR_COMPLETE  │─────────────┘
              └──────────┬──────────┘   (if changes needed)
                         │ completeCheckout()
                         ▼
              ┌─────────────────────┐
              │     COMPLETED       │
              └─────────────────────┘

  At any point:  ──► CANCELLED (via cancelCheckout())
  On error:      ──► REQUIRES_ESCALATION (3DS challenge, buyer input needed)
```

**UCP Header Requirements**:
```python
import uuid

def ucp_headers() -> dict[str, str]:
    """Every request must include platform profile."""
    return {
        "Content-Type": "application/json",
        "UCP-Agent": f'profile="{PLATFORM_PROFILE_URL}"',
        "Idempotency-Key": str(uuid.uuid4()),
        "Request-Id": str(uuid.uuid4()),
    }
```

**Error Handling**:
```python
class MessageSeverity(str, Enum):
    REQUIRES_BUYER_INPUT = "requires_buyer_input"
    INFORMATIONAL = "informational"

class CheckoutMessage(BaseModel):
    type: str = "error"
    code: str            # 'invalid_cart_items', 'requires_3ds', 'version_unsupported'
    content: str
    severity: MessageSeverity

class CheckoutError(BaseModel):
    status: str = "requires_escalation"
    messages: list[CheckoutMessage]
    continue_url: str | None = None    # for 3DS or external challenges
```

**A2A Alternative Path**: For merchants that expose A2A transport, the Checkout Agent can use structured A2A messages instead of REST:
```
DataPart: a2a.ucp.checkout → checkout object
DataPart: a2a.ucp.checkout.payment → payment instruments
DataPart: a2a.ucp.checkout.risk_signals → risk data
```

---

### 3.7 Review Agent

**Role**: Provide product information, reviews, and ratings to aid decision-making.

**Capabilities**:
- Aggregate simulated product reviews
- Generate pros/cons summaries via LLM
- Answer user questions about specific products
- Compare products qualitatively (not just price)

**Data Model**:
```python
class ProductReview(BaseModel):
    merchant_id: str
    product_id: str
    rating: float           # 1-5
    review_count: int
    summary: str            # LLM-generated
    pros: list[str]
    cons: list[str]
    quality_score: float    # 0-100 derived from reviews
```

---

### 3.8 Order Tracker Agent

**Role**: Track post-purchase order status via UCP Order capability.

**UCP Integration**: Listens for Order webhooks from merchants:
```python
from typing import Literal

class OrderConfirmed(BaseModel):
    type: Literal["order_confirmed"] = "order_confirmed"
    order_id: str
    estimated_delivery: str

class OrderShipped(BaseModel):
    type: Literal["order_shipped"] = "order_shipped"
    order_id: str
    tracking_number: str
    carrier: str

class OrderDelivered(BaseModel):
    type: Literal["order_delivered"] = "order_delivered"
    order_id: str
    delivered_at: str

class OrderReturned(BaseModel):
    type: Literal["order_returned"] = "order_returned"
    order_id: str
    return_id: str
    status: str

OrderEvent = OrderConfirmed | OrderShipped | OrderDelivered | OrderReturned
```

**Capabilities**:
- Register webhook URLs with merchants (via UCP Order capability config)
- Process incoming order status webhooks
- Maintain order history per session
- Answer "where's my order?" queries
- Alert user on delivery or issues

---

### 3.9 Notification Agent

**Role**: Manage user-facing notifications and status updates.

**Capabilities**:
- Real-time status updates during agent operations (via WebSocket)
- Progress indicators ("Searching 4 merchants...", "Comparing prices...")
- Alerts (price changes, order updates, agent errors)
- Summary generation after complex operations

**Message Types**:
```python
class ProgressNotification(BaseModel):
    type: Literal["progress"] = "progress"
    agent: str
    message: str
    percent: int | None = None

class ResultNotification(BaseModel):
    type: Literal["result"] = "result"
    agent: str
    data: dict

class AlertNotification(BaseModel):
    type: Literal["alert"] = "alert"
    severity: Literal["info", "warning", "error"]
    message: str

class ConfirmationNotification(BaseModel):
    type: Literal["confirmation"] = "confirmation"
    question: str
    options: list[str]

class SummaryNotification(BaseModel):
    type: Literal["summary"] = "summary"
    content: str

Notification = (
    ProgressNotification | ResultNotification | AlertNotification
    | ConfirmationNotification | SummaryNotification
)
```

---

## 4. Mock Merchant Specifications

### 4.1 Merchant Profiles

Each merchant is a standalone Python FastAPI server implementing UCP spec.

| Merchant | Port | Category | Capabilities | Extensions | Transport |
|----------|------|----------|-------------|------------|-----------|
| **TechStore** | 3001 | Electronics | Checkout, Identity, Order | Fulfillment, Discount, Buyer Consent | REST, MCP |
| **FashionHQ** | 3002 | Clothing | Checkout, Order | Discount | REST |
| **BookWorld** | 3003 | Books | Checkout | _(none)_ | REST |
| **HomeGoods** | 3004 | Home & Garden | Checkout, Identity, Order | Fulfillment | REST, A2A |

### 4.2 Capability Variance Rationale

This variance is **intentional** to demonstrate real-world scenarios:

- **TechStore** (full capabilities): Tests the happy path with all features
- **FashionHQ** (discounts only): Tests discount extension without fulfillment tracking
- **BookWorld** (bare minimum): Tests graceful degradation when merchant is basic
- **HomeGoods** (A2A transport): Tests agent-to-agent commerce + fulfillment

### 4.3 Product Catalogs

Each merchant has 10-15 products. Products overlap across merchants to enable comparison:

```python
# Example: Noise-cancelling headphones available at TechStore and HomeGoods
# Different prices, different capabilities
tech_store_product = {
    "id": "tech_nc_headphones_001",
    "title": "Sony WH-1000XM6 Wireless Headphones",
    "price": 29999,  # $299.99
    "category": "electronics",
}

home_goods_product = {
    "id": "hg_nc_headphones_001",
    "title": "Sony WH-1000XM6 Noise Cancelling",
    "price": 27999,  # $279.99 — cheaper but different fulfillment
    "category": "electronics",
}
```

### 4.4 UCP Profile Example (TechStore)

```json
{
  "ucp": {
    "version": "2026-01-23",
    "services": {
      "dev.ucp.shopping": [
        {
          "version": "2026-01-23",
          "spec": "https://ucp.dev/specification/overview",
          "transport": "rest",
          "endpoint": "http://localhost:3001/api/ucp",
          "schema": "https://ucp.dev/2026-01-23/services/shopping/openapi.json"
        },
        {
          "version": "2026-01-23",
          "spec": "https://ucp.dev/specification/overview",
          "transport": "mcp",
          "endpoint": "http://localhost:3001/mcp",
          "schema": "https://ucp.dev/2026-01-23/services/shopping/mcp.openrpc.json"
        }
      ]
    },
    "capabilities": {
      "dev.ucp.shopping.checkout": [
        {
          "version": "2026-01-23",
          "spec": "https://ucp.dev/specification/checkout",
          "schema": "https://ucp.dev/2026-01-23/schemas/shopping/checkout.json"
        }
      ],
      "dev.ucp.shopping.fulfillment": [
        {
          "version": "2026-01-23",
          "spec": "https://ucp.dev/specification/fulfillment",
          "schema": "https://ucp.dev/2026-01-23/schemas/shopping/fulfillment.json",
          "extends": "dev.ucp.shopping.checkout"
        }
      ],
      "dev.ucp.shopping.discount": [
        {
          "version": "2026-01-23",
          "spec": "https://ucp.dev/specification/discount",
          "schema": "https://ucp.dev/2026-01-23/schemas/shopping/discount.json",
          "extends": "dev.ucp.shopping.checkout"
        }
      ],
      "dev.ucp.shopping.buyer_consent": [
        {
          "version": "2026-01-23",
          "spec": "https://ucp.dev/specification/buyer-consent",
          "schema": "https://ucp.dev/2026-01-23/schemas/shopping/buyer_consent.json",
          "extends": "dev.ucp.shopping.checkout"
        }
      ]
    },
    "payment_handlers": {
      "com.mock.processor_tokenizer": [
        {
          "id": "mock_processor",
          "version": "2026-01-23",
          "spec": "http://localhost:3001/specs/mock-payment",
          "schema": "http://localhost:3001/specs/mock-payment.json",
          "config": {
            "type": "CARD",
            "tokenization_specification": {
              "type": "PUSH",
              "parameters": {
                "token_retrieval_url": "http://localhost:3001/api/tokens"
              }
            }
          }
        }
      ]
    }
  },
  "signing_keys": [
    {
      "kid": "techstore_2026",
      "kty": "EC",
      "crv": "P-256",
      "x": "...",
      "y": "...",
      "use": "sig",
      "alg": "ES256"
    }
  ]
}
```

---

## 5. Inter-Agent Communication

### 5.1 MS Agent Framework Workflow Graph

Agents are orchestrated using Microsoft Agent Framework's graph-based workflow engine. Each agent is an executor node, connected by typed edges with conditional routing.

```python
from agent_framework import Workflow, Edge
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

# Example: Define the shopping workflow graph
workflow = Workflow(name="bazaar-shopping")

# Agents as workflow nodes
intent_agent = create_intent_agent(llm_client)
discovery_agent = create_discovery_agent(llm_client)
comparison_agent = create_comparison_agent(llm_client)
budget_agent = create_budget_agent(llm_client)
checkout_agent = create_checkout_agent(llm_client)

# Sequential edges for search flow
workflow.add_edge(Edge(source="intent", target="discovery"))
workflow.add_edge(Edge(source="discovery", target="comparison"))

# Conditional edge for checkout flow
workflow.add_edge(Edge(
    source="comparison",
    target="budget",
    condition=lambda output: output.action == ActionType.BUY,
))
workflow.add_edge(Edge(
    source="budget",
    target="checkout",
    condition=lambda output: output.approved,
))
```

### 5.2 Agent Definition Pattern

Each agent is built using MS Agent Framework's `as_agent()` pattern with tools (Python functions exposed to the LLM):

```python
from agent_framework import Agent, ai_function
from bazaar.llm import get_llm_client

class DiscoveryAgent:
    """Discovers UCP-compliant merchants and their capabilities."""

    @ai_function(description="Fetch UCP profile from a merchant")
    async def fetch_merchant_profile(self, merchant_url: str) -> dict:
        """Fetches /.well-known/ucp from merchant and parses capabilities."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{merchant_url}/.well-known/ucp")
            return resp.json()

    @ai_function(description="Compute capability intersection between platform and merchant")
    async def negotiate_capabilities(
        self, platform_caps: list[str], merchant_caps: list[str]
    ) -> list[str]:
        """Returns the intersection of platform and merchant capabilities."""
        return list(set(platform_caps) & set(merchant_caps))

    @ai_function(description="Search and rank merchants for a shopping intent")
    async def discover_merchants(self, intent: dict) -> list[dict]:
        """Discovers, fetches profiles, and ranks merchants by match score."""
        results = []
        for merchant in MERCHANT_REGISTRY:
            profile = await self.fetch_merchant_profile(merchant["url"])
            score = self._compute_match_score(profile, intent)
            results.append({"merchant": merchant, "profile": profile, "score": score})
        return sorted(results, key=lambda x: x["score"], reverse=True)

# Create an agent from the tool class
def create_discovery_agent(llm_client) -> Agent:
    tools = DiscoveryAgent()
    return llm_client.as_agent(
        name="DiscoveryAgent",
        instructions="You discover UCP-compliant merchants. Fetch their profiles, "
                     "analyze capabilities, and rank them by relevance to the user's intent.",
        tools=[tools.fetch_merchant_profile, tools.negotiate_capabilities, tools.discover_merchants],
    )
```

### 5.3 Orchestration Patterns Used

MS Agent Framework provides multiple orchestration patterns. Bazaar uses:

| Pattern | Use Case | MS Agent Framework Feature |
|---------|----------|---------------------------|
| **Sequential** | Intent → Discovery → Comparison | `workflow.add_edge()` linear chain |
| **Handoff** | Orchestrator delegates to specialist | Handoff orchestration with tool-approval |
| **Concurrent (Fan-out)** | Query all 4 merchants simultaneously | `fan_out_fan_in_edges` parallelism |
| **Conditional** | Buy flow vs. search flow | `Edge(condition=...)` conditional routing |
| **Human-in-the-Loop** | Budget confirmation, checkout approval | `ctx.request_info()` pattern |
| **Workflow-as-Agent** | Nest sub-workflows as agents | `workflow.as_agent()` composition |

### 5.4 LLM Provider Interface

A key design feature is the configurable LLM provider abstraction, supporting cost-effective distilled models as default and premium API providers when needed:

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from enum import Enum

class LLMProvider(str, Enum):
    OLLAMA = "ollama"           # Local distilled models (cost-effective)
    OPENAI = "openai"           # OpenAI API (GPT-4o-mini, GPT-4o)
    ANTHROPIC = "anthropic"     # Anthropic API (Claude Haiku, Sonnet)
    AZURE_OPENAI = "azure"      # Azure OpenAI (enterprise)

class LLMConfig(BaseModel):
    provider: LLMProvider = LLMProvider.OLLAMA
    model: str = "llama3.2:3b"  # Default: small distilled model
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.1
    max_tokens: int = 4096

    class Config:
        env_prefix = "BAZAAR_LLM_"

class LLMProviderFactory:
    """Creates MS Agent Framework compatible LLM clients from config."""

    @staticmethod
    def create(config: LLMConfig):
        match config.provider:
            case LLMProvider.OLLAMA:
                from agent_framework_ollama import OllamaChatCompletionClient
                return OllamaChatCompletionClient(
                    model=config.model,
                    base_url=config.base_url or "http://localhost:11434",
                )
            case LLMProvider.OPENAI:
                from agent_framework_openai import OpenAIChatCompletionClient
                return OpenAIChatCompletionClient(
                    model=config.model or "gpt-4o-mini",
                    api_key=config.api_key,
                )
            case LLMProvider.ANTHROPIC:
                from agent_framework_anthropic import AnthropicChatCompletionClient
                return AnthropicChatCompletionClient(
                    model=config.model or "claude-3-haiku-20240307",
                    api_key=config.api_key,
                )
            case LLMProvider.AZURE_OPENAI:
                from agent_framework.azure import AzureOpenAIResponsesClient
                from azure.identity import DefaultAzureCredential
                return AzureOpenAIResponsesClient(
                    endpoint=config.base_url,
                    deployment_name=config.model,
                    credential=DefaultAzureCredential(),
                )

# Usage: configure via environment or config file
# BAZAAR_LLM_PROVIDER=ollama          → Free, local, fast
# BAZAAR_LLM_PROVIDER=openai          → Better quality, pay-per-use
# BAZAAR_LLM_PROVIDER=anthropic       → Alternative premium option
```

**Cost Strategy**:
| Task | Recommended Provider | Rationale |
|------|---------------------|-----------|
| Intent extraction | Distilled (Ollama) | Simple JSON extraction, fast |
| Comparison summaries | Distilled (Ollama) | Template-based, low complexity |
| Complex reasoning | OpenAI / Anthropic | Multi-step planning, nuanced |
| Review generation | Distilled (Ollama) | Summarization, cost-effective |
| Checkout decisions | OpenAI / Anthropic | Safety-critical, needs accuracy |

### 5.5 Example: Full Shopping Flow

```
1. User: "Find me wireless headphones under $300 with fast shipping"

2. Orchestrator Workflow → Intent Agent (Executor node):
   Input: {"text": "Find me wireless..."}

3. Intent Agent → Workflow State:
   Output: {"action": "search", "product": {...}, "constraints": {...}}

4. Workflow edge → Discovery Agent (Executor node):
   Input: {"intent": shopping_intent}

5. Discovery Agent (concurrent fan-out):
   - Fetches /.well-known/ucp from TechStore, FashionHQ, BookWorld, HomeGoods
   - Returns: [TechStore (score: 95), HomeGoods (score: 80)]
   - BookWorld excluded (no electronics), FashionHQ excluded (no electronics)

6. Workflow edge → Comparison Agent (Executor node):
   Input: {"merchants": [TechStore, HomeGoods], "intent": {...}}

7. Comparison Agent (concurrent fan-out):
   - POST /checkout-sessions on TechStore (creates session, gets price + fulfillment)
   - POST /checkout-sessions on HomeGoods (creates session, gets price + fulfillment)
   - Compares: TechStore $299.99 + free 5-day shipping vs HomeGoods $279.99 + $9.99 express
   - Calculates total cost, scores, recommendation

8. Workflow → Notification Agent (via event):
   Displays comparison table with recommendation to user via WebSocket

9. User: "Buy the cheaper one with standard shipping"

10. Workflow conditional edge → Budget Agent:
    Input: {"amount": 28998, "budget": 30000}

11. Budget Agent → Workflow State:
    Output: {"approved": True, "remaining": 1002}

12. Workflow edge → Checkout Agent:
    Input: {"merchant_url": "http://localhost:3004", "session_id": "chk_hg_123", "fulfillment_option": "standard"}

13. Checkout Agent:
    - PUT /checkout-sessions/{id} (buyer info + fulfillment selection)
    - GET /checkout-sessions/{id} (verify ready_for_complete)
    - POST /checkout-sessions/{id}/complete (with mock payment instrument)

14. Workflow → Order Tracker Agent:
    Event: {"order_id": "ord_456", "merchant_url": "..."}

15. Workflow → Notification Agent → User:
    "✅ Order placed! Sony WH-1000XM6 from HomeGoods for $289.98.
     Estimated delivery: March 16. I'll track it for you."
```

---

## 6. Technology Stack

### 6.1 Core Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend Language** | Python 3.12+ | Rich AI/ML ecosystem, MS Agent Framework native support |
| **Frontend Language** | TypeScript | Type safety for React components |
| **Package Manager** | uv (Python) / pnpm (JS) | Fast, modern dependency management |
| **Monorepo** | uv workspaces + pnpm workspace | Unified Python backend + React frontend |

### 6.2 Frontend

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Framework** | React 19 + Vite | Lightweight SPA, fast HMR, no SSR overhead |
| **UI Library** | shadcn/ui + Tailwind CSS | Rapid prototyping, clean design |
| **Real-time** | WebSocket (native) | Live agent status updates from FastAPI |
| **State** | Zustand | Lightweight, good for chat-like apps |
| **HTTP Client** | TanStack Query + fetch | Caching, auto-retry for API calls |

### 6.3 Backend / Agents

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Web Framework** | FastAPI | Async, WebSocket support, auto-docs, Pydantic native |
| **Agent Framework** | Microsoft Agent Framework (`agent-framework`) | Graph-based workflows, multi-agent orchestration, built-in providers |
| **LLM Providers** | MS Agent Framework providers | Ollama (distilled), OpenAI, Anthropic, Azure via provider packages |
| **HTTP Client** | httpx | Async HTTP for UCP REST calls |
| **Validation** | Pydantic v2 | Runtime validation of UCP JSON schemas |
| **Task Queue** | asyncio | Async inter-agent coordination via workflow graph |
| **Config** | pydantic-settings | Type-safe env config for LLM providers |

### 6.4 LLM Provider Matrix

| Provider | Package | Models | Cost | Use Case |
|----------|---------|--------|------|----------|
| **Ollama** | `agent-framework-ollama` | Llama 3.2 3B, Phi-3, Qwen 2.5 | Free (local) | Default for development & most tasks |
| **OpenAI** | `agent-framework-openai` | GPT-4o-mini, GPT-4o | Pay-per-use | Complex reasoning, fallback |
| **Anthropic** | `agent-framework-anthropic` | Claude Haiku, Sonnet | Pay-per-use | Alternative premium provider |
| **Azure OpenAI** | `agent-framework[azure]` | GPT-4o-mini (hosted) | Enterprise | Production deployment option |

### 6.5 Mock Merchants

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Framework** | FastAPI | Same stack as backend, consistent patterns |
| **Data** | In-memory (dict/JSON) | No database needed for mock data |
| **Validation** | Pydantic v2 | Validate UCP request/response payloads |

### 6.6 Testing

| Type | Tool | Target |
|------|------|--------|
| **Unit** | pytest + pytest-asyncio | Agent logic, UCP schema validation |
| **Integration** | pytest + httpx | Agent ↔ Merchant UCP flows |
| **E2E** | Playwright | Full user flow through UI |
| **Coverage** | pytest-cov | Ensure >80% coverage on agent logic |

---

## 7. Project Structure

```
bazaar/
├── frontend/                             # React SPA (Vite + TypeScript)
│   ├── src/
│   │   ├── App.tsx                       # Main app with routing
│   │   ├── main.tsx                      # Vite entry point
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── ComparisonTable.tsx
│   │   │   ├── CheckoutProgress.tsx
│   │   │   ├── AgentStatusPanel.tsx
│   │   │   └── OrderTracker.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts           # WebSocket connection to FastAPI
│   │   │   └── useAgents.ts              # Agent status polling
│   │   ├── stores/
│   │   │   └── chatStore.ts              # Zustand store
│   │   └── lib/
│   │       └── api.ts                    # TanStack Query + fetch client
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                              # Python FastAPI backend
│   ├── pyproject.toml                    # uv project config
│   ├── bazaar/
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app entry point
│   │   ├── config.py                     # LLM & app configuration (pydantic-settings)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py                   # WebSocket endpoint for chat
│   │   │   ├── agents.py                 # Agent status REST endpoints
│   │   │   └── webhooks.py               # Order webhook receiver
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── provider.py               # LLMProviderFactory (Ollama/OpenAI/Anthropic)
│   │   │   └── models.py                 # LLMConfig, LLMProvider enum
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py           # Workflow graph definition + routing
│   │   │   ├── intent.py                 # Intent extraction agent
│   │   │   ├── discovery.py              # UCP merchant discovery agent
│   │   │   ├── comparison.py             # Multi-merchant comparison agent
│   │   │   ├── budget.py                 # Budget validation agent
│   │   │   ├── checkout.py               # UCP checkout lifecycle agent
│   │   │   ├── review.py                 # Product review agent
│   │   │   ├── order_tracker.py          # Post-purchase tracking agent
│   │   │   └── notification.py           # User notification agent
│   │   ├── ucp/
│   │   │   ├── __init__.py
│   │   │   ├── client.py                 # UCP REST client (httpx-based)
│   │   │   ├── discovery.py              # Profile fetch + parse
│   │   │   ├── negotiation.py            # Capability intersection algorithm
│   │   │   ├── checkout.py               # Checkout operations
│   │   │   ├── schemas.py                # Pydantic models for UCP payloads
│   │   │   └── a2a_client.py             # UCP A2A transport client
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── agents.py                 # Agent state models
│   │       ├── commerce.py               # Product, Cart, Order models
│   │       └── ucp.py                    # UCP-specific types
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                   # pytest fixtures (mock merchants, LLM)
│       ├── test_agents/
│       │   ├── test_intent.py
│       │   ├── test_discovery.py
│       │   ├── test_comparison.py
│       │   ├── test_checkout.py
│       │   └── test_budget.py
│       ├── test_ucp/
│       │   ├── test_client.py
│       │   ├── test_negotiation.py
│       │   └── test_schemas.py
│       └── test_integration/
│           └── test_shopping_flow.py     # End-to-end agent flow tests
│
├── merchants/                            # Mock UCP merchant servers (FastAPI)
│   ├── pyproject.toml
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── ucp_middleware.py             # UCP header validation, profile serving
│   │   ├── checkout_handler.py           # Base checkout session logic
│   │   └── models.py                     # Shared UCP Pydantic types
│   ├── techstore/                        # Port 3001 — full capabilities
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── catalog.py
│   │   ├── profile.json                  # /.well-known/ucp
│   │   └── routes/
│   ├── fashionhq/                        # Port 3002 — with discounts
│   │   └── ...
│   ├── bookworld/                        # Port 3003 — basic
│   │   └── ...
│   └── homegoods/                        # Port 3004 — A2A + fulfillment
│       └── ...
│
├── e2e/                                  # Playwright E2E tests
│   ├── tests/
│   └── playwright.config.ts
│
├── docker-compose.yml                    # Run all services locally
├── Makefile                              # Common commands (dev, test, lint)
├── pyproject.toml                        # Root workspace config
├── .env.example                          # LLM provider config template
└── README.md
```

---

## 8. User Interface

### 8.1 Chat Interface

Primary interaction model is a chat window with rich embedded components.

**Chat Message Types**:
- **Text**: Regular conversation with the orchestrator
- **Comparison Card**: Side-by-side product comparison with action buttons
- **Checkout Progress**: Step-by-step checkout status indicator
- **Order Card**: Order confirmation with tracking link
- **Agent Status**: Collapsible panel showing which agents are active

### 8.2 Wireframes (ASCII)

```
┌─────────────────────────────────────────────────────┐
│  🛒 Bazaar — Multi-Agent Shopping Assistant          │
│  ─────────────────────────────────────────────────── │
│                                                       │
│  You: Find me noise-cancelling headphones under $300  │
│                                                       │
│  ┌─ 🤖 Bazaar ──────────────────────────────────┐   │
│  │ Searching 4 merchants for headphones...        │   │
│  │ ████████████░░░░░░░ 60%                        │   │
│  │ ✅ TechStore — 3 matches found                 │   │
│  │ ✅ HomeGoods — 2 matches found                 │   │
│  │ ⏳ FashionHQ — searching...                    │   │
│  │ ❌ BookWorld — no electronics                  │   │
│  └───────────────────────────────────────────────┘   │
│                                                       │
│  ┌─ 🤖 Bazaar ──────────────────────────────────┐   │
│  │ Found 5 options across 2 merchants. Here's     │   │
│  │ my comparison:                                  │   │
│  │                                                 │   │
│  │ ┌──────────────┬──────────────┬────────────┐   │   │
│  │ │              │  TechStore   │  HomeGoods  │   │   │
│  │ ├──────────────┼──────────────┼────────────┤   │   │
│  │ │ Product      │ Sony XM6     │ Sony XM6   │   │   │
│  │ │ Price        │ $299.99      │ $279.99 ⭐ │   │   │
│  │ │ Shipping     │ Free (5 day) │ $9.99 (2d) │   │   │
│  │ │ Total        │ $299.99      │ $289.98    │   │   │
│  │ │ Discount     │ 10% off! 🏷  │ None       │   │   │
│  │ │ After disc.  │ $269.99 ⭐   │ $289.98    │   │   │
│  │ │ Fulfillment  │ ✅ Tracking  │ ✅ Tracking│   │   │
│  │ │ Score        │ ⭐ 92/100    │ 78/100     │   │   │
│  │ └──────────────┴──────────────┴────────────┘   │   │
│  │                                                 │   │
│  │ 💡 Recommendation: TechStore has a 10%          │   │
│  │ discount making it cheaper after discount       │   │
│  │ ($269.99 vs $289.98), plus free shipping.       │   │
│  │                                                 │   │
│  │ [Buy from TechStore] [Buy from HomeGoods]       │   │
│  │ [Compare more]       [Change search]            │   │
│  └───────────────────────────────────────────────┘   │
│                                                       │
│  You: Buy from TechStore with the discount            │
│                                                       │
│  ┌─ 🤖 Bazaar ──────────────────────────────────┐   │
│  │ Processing checkout with TechStore...          │   │
│  │                                                 │   │
│  │ Step 1: Create session     ✅                  │   │
│  │ Step 2: Apply discount     ✅ (-$30.00)        │   │
│  │ Step 3: Set shipping       ✅ Free Standard    │   │
│  │ Step 4: Payment            ✅ Mock Visa ****42 │   │
│  │ Step 5: Complete order     ✅                  │   │
│  │                                                 │   │
│  │ 🎉 Order confirmed! #ORD-TS-789               │   │
│  │ Sony WH-1000XM6 — $269.99                     │   │
│  │ Est. delivery: March 14, 2026                  │   │
│  │ I'll track this for you automatically.         │   │
│  └───────────────────────────────────────────────┘   │
│                                                       │
│  ┌─────────────────────────────────────────────┐     │
│  │ Type a message...                     [Send] │     │
│  └─────────────────────────────────────────────┘     │
│                                                       │
│  ┌─ Active Agents ──────────────────────────────┐   │
│  │ 🟢 Orchestrator  🟢 Order Tracker            │   │
│  │ 🔴 Discovery     🔴 Comparison               │   │
│  └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 9. Implementation Phases

### Phase 1: Foundation (Week 1-2)
| Task | Description | Deliverable |
|------|-------------|-------------|
| P1.1 | Set up monorepo (Python uv + React Vite) | Working project scaffold with `docker-compose.yml` |
| P1.2 | Build `bazaar.ucp` client package (httpx + Pydantic) | Discovery, negotiation, checkout REST client |
| P1.3 | Set up MS Agent Framework + LLM provider interface | `LLMProviderFactory` supporting Ollama/OpenAI/Anthropic |
| P1.4 | Create first mock merchant (BookWorld — basic FastAPI) | Working UCP server with checkout |
| P1.5 | Write UCP conformance tests (pytest) | Validate merchant responses against spec |

### Phase 2: Core Agents (Week 3-4)
| Task | Description | Deliverable |
|------|-------------|-------------|
| P2.1 | Implement Intent Agent with LLM integration | Structured intent extraction via `@ai_function` |
| P2.2 | Implement Discovery Agent | Profile fetch, capability parsing |
| P2.3 | Implement Checkout Agent (REST path) | Full checkout lifecycle |
| P2.4 | Build Orchestrator workflow graph (MS Agent Framework) | Intent → Discovery → Checkout flow via workflow edges |
| P2.5 | Build remaining merchants (TechStore, FashionHQ, HomeGoods) | 4 FastAPI merchants with varying capabilities |

### Phase 3: Advanced Agents (Week 5-6)
| Task | Description | Deliverable |
|------|-------------|-------------|
| P3.1 | Implement Comparison Agent with fan-out | Multi-merchant comparison with scoring |
| P3.2 | Implement Budget Agent | Budget validation + rules engine |
| P3.3 | Implement Review Agent | Product review aggregation |
| P3.4 | Implement Order Tracker Agent | Webhook listener + status tracking |
| P3.5 | Implement Notification Agent | Real-time WebSocket status updates |

### Phase 4: Frontend + Integration (Week 7-8)
| Task | Description | Deliverable |
|------|-------------|-------------|
| P4.1 | Build chat UI (React + Vite + shadcn/ui) | Working chat interface |
| P4.2 | Build comparison table component | Rich embedded comparison cards |
| P4.3 | Build checkout progress component | Step-by-step checkout visualization |
| P4.4 | WebSocket integration (FastAPI ↔ React) | Real-time agent status updates |
| P4.5 | End-to-end flow testing (pytest + Playwright) | Complete user journey works |

### Phase 5: Polish + Advanced Features (Week 9-10)
| Task | Description | Deliverable |
|------|-------------|-------------|
| P5.1 | A2A transport support (HomeGoods) | Agent-to-agent UCP commerce |
| P5.2 | Fulfillment + Discount extension handling | Extension negotiation in action |
| P5.3 | Agent status dashboard + MS Agent Framework DevUI | Visualize agent activity in real-time |
| P5.4 | Error handling & edge cases | 3DS challenges, timeouts, merchant failures |
| P5.5 | Documentation + README + demo recording | Portfolio-ready project |

---

## 10. Key UCP Concepts Demonstrated

This project covers the following UCP specification areas:

| UCP Concept | Where Demonstrated |
|---|---|
| **Discovery** (`/.well-known/ucp`) | Discovery Agent fetching merchant profiles |
| **Capability Negotiation** | Discovery Agent computing capability intersection |
| **Schema Composition** | UCP Client resolving base + extension schemas |
| **Checkout Lifecycle** | Checkout Agent (create → update → complete) |
| **Fulfillment Extension** | Comparison Agent comparing shipping options |
| **Discount Extension** | Comparison Agent applying discount codes |
| **Buyer Consent Extension** | Checkout Agent handling consent requirements |
| **Order Capability** | Order Tracker Agent receiving webhooks |
| **Identity Linking** | OAuth simulation for returning customers |
| **Payment Handlers** | Mock tokenizer for payment processing |
| **REST Transport** | Primary transport for all merchants |
| **MCP Transport** | TechStore alternative transport path |
| **A2A Transport** | HomeGoods agent-to-agent commerce |
| **Version Negotiation** | Platform ↔ Business version compatibility |
| **Error Handling** | `requires_escalation` with `continue_url` for 3DS |
| **Idempotency** | Idempotency-Key headers on state-changing operations |

---

## 11. Success Criteria

### 11.1 Functional Requirements
- [ ] User can search for products across multiple merchants via natural language
- [ ] System discovers merchant capabilities via UCP profiles automatically
- [ ] Comparison table shows normalized prices, shipping, and discounts
- [ ] Checkout completes successfully via UCP REST and A2A transports
- [ ] Budget constraints are enforced before checkout
- [ ] Order tracking works via webhook simulation
- [ ] Graceful degradation when merchants lack extensions (BookWorld scenario)
- [ ] User receives real-time status updates during agent operations

### 11.2 Non-Functional Requirements
- [ ] Agent response time < 3s for simple queries (excluding LLM latency)
- [ ] Parallel merchant discovery (all 4 merchants queried simultaneously via fan-out)
- [ ] Typed inter-agent messages (Pydantic models, no `dict[str, Any]` in message bus)
- [ ] All UCP payloads validated with Pydantic schemas
- [ ] Unit test coverage > 80% for agent logic and UCP client (pytest-cov)
- [ ] Clear separation between UCP protocol logic and agent orchestration
- [ ] LLM provider switchable via environment config without code changes

### 11.3 Portfolio / Learning Goals
- [ ] Deep understanding of UCP discovery, negotiation, and checkout
- [ ] Working knowledge of multi-agent architecture patterns (MS Agent Framework)
- [ ] Experience with A2A protocol for agent-to-agent communication
- [ ] Hands-on with LLM provider abstraction (distilled models vs. API providers)
- [ ] Published to GitHub with clear README and demo video/GIF
- [ ] Blog post or documentation explaining architectural decisions

---

## 12. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| UCP spec changes (still evolving) | Schema/API breaking changes | Pin to version `2026-01-23`, abstract UCP interactions behind client library |
| LLM costs during development | Budget overrun | Use Ollama distilled models by default (free), switch to API only for complex tasks |
| MS Agent Framework still RC | Breaking changes before v1.0 | Pin to `1.0.0rc3`, monitor release notes, keep agent logic decoupled from framework |
| Scope creep (too many agents) | Never finishing | Start with 4 core agents (Intent, Discovery, Comparison, Checkout), add others incrementally |
| A2A protocol complexity | Delays Phase 5 | A2A is stretch goal; REST path works for 3/4 merchants without it |
| Mock merchants diverge from real UCP | False confidence | Use official UCP samples as reference, run conformance tests |
| Distilled model quality | Poor intent extraction | Fallback to OpenAI/Anthropic for complex queries, per-agent provider config |

---

## 13. References

- [UCP Specification](https://ucp.dev/latest/specification/overview/)
- [UCP Core Concepts](https://ucp.dev/documentation/core-concepts/)
- [UCP Checkout REST Binding](https://ucp.dev/latest/specification/checkout-rest/)
- [UCP Checkout A2A Binding](https://ucp.dev/latest/specification/checkout-a2a/)
- [UCP Official Samples](https://github.com/Universal-Commerce-Protocol/samples)
- [UCP GitHub Repository](https://github.com/Universal-Commerce-Protocol/ucp)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) — Multi-agent orchestration framework
- [MS Agent Framework Python Docs](https://learn.microsoft.com/en-us/agent-framework/)
- [MS Agent Framework Workflows](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows)
- [MS Agent Framework Providers](https://github.com/microsoft/agent-framework/tree/main/python/packages) — Ollama, Anthropic, OpenAI
- [A2A Protocol](https://a2a-protocol.org/latest/)
- [Agent Payments Protocol (AP2)](https://ap2-protocol.org/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [UCP Roadmap](https://ucp.dev/documentation/roadmap/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Ollama](https://ollama.com/) — Local LLM runtime for distilled models
