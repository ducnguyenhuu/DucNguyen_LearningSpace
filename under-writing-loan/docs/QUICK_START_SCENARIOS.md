# Complete Underwriting Workflow - Quick Start Guide

## 🎯 Overview

This notebook demonstrates the **complete multi-agent loan underwriting system** with three realistic scenarios showing different outcomes: approval, conditional approval, and rejection.

## 📋 Prerequisites Checklist

### ✅ All Prerequisites Ready!

1. **Credit Profiles** - ✅ Database seeded with 4 test profiles
2. **Paystub PDFs** - ✅ Generated 3 scenario-specific paystubs
3. **Orchestrator** - ✅ LangGraph workflow implemented
4. **All Agents** - ✅ Document, Risk, Compliance, Decision agents ready

## 🚀 How to Run

### Step 1: Open the Notebook
```bash
# From VS Code or Jupyter
notebooks/07_complete_underwriting_scenarios.ipynb
```

### Step 2: Execute All Cells
Run cells in order from top to bottom. Each scenario takes ~10-15 seconds to complete.

### Step 3: Review Results
Compare the three outcomes in the final comparison chart and table.

---

## 📊 Three Test Scenarios

### Scenario 1: Auto-Approval ✅

**Profile**: Alice Excellence
- **Credit Score**: 780 (Excellent)
- **Income**: $180,000/year
- **DTI**: 20% (Low debt)
- **LTV**: 60% (Strong down payment)

**Expected Result**: ✅ **APPROVED**
- Best interest rate (~6.25%)
- No conditions
- Instant approval

**Why Approved**: 
- Credit score >740 ✓
- DTI <35% ✓  
- LTV <75% ✓

---

### Scenario 2: Conditional Approval ⚠️

**Profile**: Bob Marginal
- **Credit Score**: 720 (Good)
- **Income**: $95,000/year
- **DTI**: 38% (At threshold)
- **LTV**: 85% (High)

**Expected Result**: ⚠️ **CONDITIONAL APPROVAL**
- Moderate interest rate (~7.12%)
- Requires manual review
- May need PMI

**Why Conditional**:
- DTI at warning level (38% near 43% limit)
- LTV >80% (requires PMI)
- One late payment in history
- Does NOT trigger auto-reject

---

### Scenario 3: Rejection ❌

**Profile**: Charlie Risky
- **Credit Score**: 590 (Poor)
- **Income**: $55,000/year
- **DTI**: 55% (Very high)
- **LTV**: 95% (Minimal down)

**Expected Result**: ❌ **DENIED**
- No rate offered
- Cannot be approved
- Multiple risk factors

**Why Denied**:
- **Auto-reject rule triggered**: DTI >43% AND Credit <640
- Multiple derogatory marks
- Poor payment history
- High credit utilization (85%)

---

## 🔑 Decision Rules Summary

### Auto-Reject (Immediate Denial)
```
IF DTI > 43% AND Credit Score < 640
THEN deny = TRUE
```

### Auto-Approve (Instant Approval)
```
IF Credit Score > 740 
   AND DTI < 35% 
   AND LTV < 75%
THEN approve = TRUE
```

### Conditional (Manual Review)
```
ELSE (everything in between)
THEN conditional = TRUE
```

---

## 📁 Test Data Mapping

| Scenario | SSN | Credit Score | Paystub File |
|----------|-----|--------------|--------------|
| 1. Auto-Approval | 111-11-1111 | 780 | `paystub_scenario1_approval.pdf` |
| 2. Conditional | 222-22-2222 | 720 | `paystub_scenario2_conditional.pdf` |
| 3. Rejection | 444-44-4444 | 590 | `paystub_scenario3_rejection.pdf` |

All files are in:
- Credit data: `data/mock_credit_bureau.db`
- Paystubs: `data/applications/`

---

## 🎓 Learning Points

### What You'll Learn:

1. **How DTI impacts decisions** - Compare 20% vs 38% vs 55%
2. **Credit score thresholds** - See how 780 vs 720 vs 590 affects outcomes
3. **LTV requirements** - Understand why 60% approves but 95% denies
4. **Multi-agent coordination** - See how 4 agents work together
5. **Risk assessment** - GPT-4o analyzes each profile differently
6. **Compliance checking** - RAG system retrieves relevant policies
7. **Rate calculation** - Higher risk = higher interest rate

### Key Insights:

- **One risk factor** (e.g., high LTV) → Conditional approval
- **Two risk factors** (e.g., high DTI + high LTV) → Manual review required
- **Three+ risk factors** → Likely denial
- **Auto-reject rule** is binary: DTI >43% AND Score <640 = immediate denial

---

## 💡 Customization Ideas

### Create Your Own Scenarios:

1. **Test edge cases**:
   - DTI exactly at 43%
   - Credit score exactly at 640
   - LTV exactly at 80%

2. **Test borderline cases**:
   - Credit 700, DTI 36%, LTV 78% (which way will it go?)

3. **Test extreme cases**:
   - Perfect credit (800+), but high DTI (40%)
   - Poor credit (600), but low DTI (25%)

### How to Add Custom Scenarios:

See `docs/TEST_DATA_GUIDE.md` for detailed instructions on:
- Adding credit profiles to database
- Generating custom paystubs
- Creating application dictionaries

---

## 📈 Expected Output

### Console Output Per Scenario:
```
🚀 Starting multi-agent workflow...

📄 Document Agent: Extracting data from paystubs...
   ✓ Extracted 1 document (2.5s)

📊 Risk Agent: Calculating financial metrics...
   ✓ DTI: 20.00%, LTV: 60.00%, Risk: low (3.2s)

✅ Compliance Agent: Checking policy compliance...
   ✓ Retrieved 7 policy chunks (4.8s)

⚖️ Decision Agent: Making final decision...
   ✓ Decision: APPROVED, Rate: 6.250% (2.9s)

📊 WORKFLOW EXECUTION COMPLETE
```

### Final Comparison Chart:
Interactive Plotly visualization showing:
- Credit scores across scenarios
- Risk ratios (DTI, LTV, PTI)
- Risk scores
- Final decisions (color-coded)

---

## ⚠️ Troubleshooting

### Issue: "Credit profile not found"
**Solution**: Run `python3 src/mcp/seed_data.py`

### Issue: "Paystub file not found"
**Solution**: Run `python3 scripts/generate_test_paystubs.py`

### Issue: "MCP server connection refused"
**Note**: This is normal and expected. System uses direct SQLite queries as fallback.

### Issue: Unexpected decision outcome
**Check**:
1. DTI calculation: `(monthly_debt * 12 / annual_income) * 100`
2. LTV calculation: `(loan_amount / property_value) * 100`
3. Credit score matches database: `SELECT * FROM credit_reports WHERE ssn='XXX-XX-XXXX'`

---

## 📊 Performance Metrics

Expected execution time per application:
- **Document Agent**: 2-3 seconds
- **Risk Agent**: 3-4 seconds  
- **Compliance Agent**: 5-6 seconds
- **Decision Agent**: 3-4 seconds
- **Total**: ~13-17 seconds per application

Expected costs per application:
- **Document Intelligence**: $0.001 per page
- **Azure OpenAI (GPT-4o-mini)**: ~$0.002-0.005 per application
- **Embeddings**: ~$0.0001 per application
- **Total**: ~$0.003-0.006 per application

---

## 🎯 Success Criteria

After running the notebook, you should see:

✅ **Scenario 1**: APPROVED with low rate (6-6.5%)  
✅ **Scenario 2**: CONDITIONAL with moderate rate (7-7.5%)  
✅ **Scenario 3**: DENIED with no rate offered  

All three scenarios should complete without errors and show different decision outcomes based on their risk profiles.

---

## 📚 Additional Resources

- **Full Data Guide**: `docs/TEST_DATA_GUIDE.md`
- **Decision Logic**: `src/agents/decision_agent.py`
- **Orchestrator**: `src/orchestrator.py`
- **All Agent Notebooks**: `notebooks/01-06_*.ipynb`

---

## 🎓 Next Steps

1. ✅ Run all three scenarios
2. 🔍 Analyze comparative results
3. 🛠️ Create custom test cases
4. 🎨 Experiment with prompt variations
5. 📊 Add MLflow tracking (Phase 8)
6. 🚀 Deploy to production

Happy underwriting! 🏦
