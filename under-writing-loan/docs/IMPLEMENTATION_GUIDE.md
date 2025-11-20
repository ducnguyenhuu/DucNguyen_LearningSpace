# 🛠️ Implementation Guide - Simplified Research Project

**Goal:** Step-by-step guide to build the loan underwriting AI agent system for learning purposes.

---

## Quick Start

```bash
# 1. Install dependencies
pip install openai langchain langchain-openai langgraph fastapi uvicorn streamlit mlflow pdfplumber python-dotenv

# 2. Set up environment
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# 3. Create project structure
mkdir -p data/{applications,policies,test_docs} src/{agents,mcp,rag} ui tests notebooks

# 4. Start building!
```

---

## Phase-by-Phase Implementation

### Phase 1: Test Azure OpenAI (30 mins)

**Test GPT-4:**
```python
from openai import AzureOpenAI
client = AzureOpenAI(api_key="...", azure_endpoint="...")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Phase 2: Document Agent - OCR (2-3 hours)

**Key files to create:**
- `src/models.py` - Pydantic models
- `src/agents/document_agent.py` - OCR extraction logic

**Core functionality:**
1. Read PDF with `pdfplumber`
2. Classify document type with GPT-4
3. Extract structured data with GPT-4
4. Return JSON output

### Phase 3: Risk Agent + MCP (2-3 hours)

**Key files:**
- `src/mcp/server.py` - FastAPI server
- `src/mcp/client.py` - HTTP client
- `src/agents/risk_agent.py` - Risk calculations + AI analysis

**What you'll learn:**
- DTI/LTV/PTI calculations
- Calling external APIs via MCP
- GPT-4 for financial analysis

### Phase 4: RAG System (3-4 hours)

**Key files:**
- `src/rag/indexer.py` - Index policy documents
- `src/rag/retriever.py` - Vector search
- `src/agents/compliance_agent.py` - Policy checking

**Steps:**
1. Create policy documents (5-10 simple text files)
2. Generate embeddings with `text-embedding-ada-002`
3. Store in Azure AI Search
4. Query at runtime
5. Use context with GPT-4

### Phase 5: Decision Agent (2 hours)

**Key files:**
- `src/agents/decision_agent.py`

**Logic:**
1. Aggregate all agent outputs
2. Apply decision rules
3. Use GPT-4 for final reasoning
4. Generate explanation

### Phase 6: LangGraph Orchestration (2-3 hours)

**Key files:**
- `src/orchestrator.py`

**Connect agents:**
```python
from langgraph.graph import StateGraph

workflow = StateGraph(ApplicationState)
workflow.add_node("document_agent", document_agent)
workflow.add_node("risk_agent", risk_agent)
workflow.add_node("compliance_agent", compliance_agent)
workflow.add_node("decision_agent", decision_agent)

workflow.add_edge("document_agent", "risk_agent")
workflow.add_edge("risk_agent", "compliance_agent")
workflow.add_edge("compliance_agent", "decision_agent")

app = workflow.compile()
```

### Phase 7: Streamlit UI (2-3 hours)

**Key files:**
- `ui/streamlit_app.py`

**Simple interface:**
```python
import streamlit as st

st.title("🏦 Loan Application")

# Upload docs
docs = st.file_uploader("Upload Documents", type=['pdf'])

# Input fields
name = st.text_input("Name")
income = st.number_input("Annual Income")
loan_amount = st.number_input("Loan Amount")

# Submit
if st.button("Submit"):
    result = orchestrator.run(...)
    st.success(f"Decision: {result.decision}")
    st.write(f"Rate: {result.rate}%")
    st.markdown(result.explanation)
```

### Phase 8: MLflow Tracking (1-2 hours)

**Track experiments:**
```python
import mlflow

mlflow.start_run()
mlflow.log_param("model", "gpt-4")
mlflow.log_metric("processing_time_ms", 5000)
mlflow.log_metric("risk_score", 42.3)
mlflow.end_run()
```

---

## Sample Policy Documents

Create `data/policies/credit_policy.txt`:

```
CREDIT POLICY

Minimum Credit Score: 640
Acceptable Range: 680-850
Below 680: Requires additional review

Maximum DTI Ratio: 43%
Preferred: Below 36%
Acceptable: 36-43%
Above 43%: Generally declined

Maximum LTV Ratio: 95%
Preferred: Below 80%
Above 80%: Requires PMI (Private Mortgage Insurance)
```

Create `data/policies/income_verification.txt`:

```
INCOME VERIFICATION POLICY

W-2 Employees:
- 2 recent pay stubs required
- W-2 forms for past 2 years

Self-Employed:
- Tax returns for past 2 years required
- Profit/Loss statements
- Bank statements (3 months)
```

---

## Testing Strategy

**Unit tests per agent:**
```python
def test_document_agent():
    agent = DocumentAgent()
    result = agent.run("TEST-001", ["sample.pdf"])
    assert result.completeness_score > 80

def test_risk_agent():
    agent = RiskAgent()
    result = agent.run("TEST-001", ssn="...", income=85000, ...)
    assert 0 <= result.risk_score <= 100

# Similar tests for other agents
```

**Integration test:**
```python
def test_end_to_end():
    result = orchestrator.process_application(
        app_id="TEST-001",
        docs=["paystub.pdf", "bank.pdf"],
        applicant_info={...},
        loan_request={...}
    )
    
    assert result.decision in ["approved", "rejected", "conditional"]
    assert len(result.explanation) > 100
```

---

## Expected Timeline

**Week 1-2: Core Agents**
- Phase 1-3: Document + Risk agents
- Test with mock data

**Week 3-4: RAG + Decision**
- Phase 4-5: Compliance + Decision agents
- Create policy documents

**Week 5-6: Integration**
- Phase 6: LangGraph orchestration
- End-to-end testing

**Week 7-8: UI + Polish**
- Phase 7-8: Streamlit UI + MLflow
- Documentation and demo

---

## Key Learning Moments

1. **OCR Magic:** Watch GPT-4 Vision extract structured data from messy PDFs
2. **RAG Impact:** Compare answers with/without policy context
3. **Agent Coordination:** See LangGraph manage state between agents
4. **AI Reasoning:** Read GPT-4's step-by-step decision explanation
5. **MCP Benefits:** Understand data abstraction value

---

## Troubleshooting

**Issue: Azure OpenAI rate limits**
- Solution: Add retry logic with exponential backoff

**Issue: PDF extraction fails**
- Solution: Use GPT-4 Vision for image-based PDFs

**Issue: RAG returns irrelevant results**
- Solution: Improve chunking, add metadata filtering

**Issue: Agents take too long**
- Solution: Cache results, optimize prompts

---

## Next Steps After Completion

1. **Experiment with prompts** - Try different prompt styles
2. **Add more agents** - Fraud detection, property valuation
3. **Improve RAG** - Better chunking, re-ranking
4. **Add human-in-loop** - Manual review for edge cases
5. **Deploy** - Run on cloud VM
6. **Present findings** - Share learnings

---

**Focus:** Learn by building. Start simple, iterate quickly! 🚀
