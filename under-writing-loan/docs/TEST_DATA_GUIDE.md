# Test Data Requirements for Complete Underwriting Workflow

This document explains all the test data needed to run the three underwriting scenarios in `notebooks/07_complete_underwriting_scenarios.ipynb`.

## Quick Start

### Step 1: Generate Paystub PDFs

```bash
python scripts/generate_test_paystubs.py
```

This creates three paystub PDFs in `data/applications/`:
- `paystub_scenario1_approval.pdf` - High income ($180k/year)
- `paystub_scenario2_conditional.pdf` - Moderate income ($95k/year)
- `paystub_scenario3_rejection.pdf` - Low income ($55k/year)

### Step 2: Verify Credit Database

The mock credit database should already contain these profiles (created during setup):

```bash
# Check if profiles exist
sqlite3 data/mock_credit_bureau.db "SELECT ssn, name, credit_score FROM credit_reports;"
```

Expected output:
```
111-11-1111|Test Excellent|780
222-22-2222|Test Good|720
333-33-3333|Test Fair|670
444-44-4444|Test Poor|590
```

If profiles are missing, seed the database:
```bash
python src/mcp/seed_data.py
```

### Step 3: Run Notebook

Open `notebooks/07_complete_underwriting_scenarios.ipynb` and run all cells.

---

## Data Breakdown by Scenario

### Scenario 1: Auto-Approval ✅

**Purpose**: Demonstrate ideal borrower with all criteria strongly met

**Credit Profile** (from `mock_credit_bureau.db`):
- SSN: `111-11-1111`
- Credit Score: **780** (Excellent)
- Payment History: Excellent
- Credit Utilization: 15%
- Derogatory Marks: 0
- Credit Age: 10 years

**Application Data**:
- Annual Income: **$180,000** (high income)
- Monthly Debt: **$3,000** (low for income level)
- Requested Loan: **$300,000**
- Property Value: **$500,000**
- Down Payment: **$200,000** (40%)

**Key Metrics**:
- DTI: ~20% (well below 35% threshold)
- LTV: 60% (well below 75% threshold)
- PTI: ~15% (very manageable)

**Expected Outcome**: ✅ **APPROVED**
- Auto-approve rule triggered (Score >740, DTI <35%, LTV <75%)
- Best interest rate offered
- No conditions or manual review required

**Paystub Document**:
- File: `data/applications/paystub_scenario1_approval.pdf`
- Employee: Alice Excellence
- Gross Biweekly: $6,923.08
- Annual: $180,000 (26 pay periods)

---

### Scenario 2: Conditional Approval ⚠️

**Purpose**: Demonstrate marginal borrower requiring manual review

**Credit Profile** (from `mock_credit_bureau.db`):
- SSN: `222-22-2222`
- Credit Score: **720** (Good, but not excellent)
- Payment History: Good
- Credit Utilization: 28.5%
- Derogatory Marks: 0
- Late Payments (12mo): 1

**Application Data**:
- Annual Income: **$95,000** (moderate income)
- Monthly Debt: **$3,000** (high relative to income)
- Requested Loan: **$340,000**
- Property Value: **$400,000**
- Down Payment: **$60,000** (15%)

**Key Metrics**:
- DTI: ~38% (at warning threshold)
- LTV: 85% (above 80% threshold, requires PMI)
- PTI: ~40% (borderline)

**Expected Outcome**: ⚠️ **CONDITIONAL APPROVAL**
- Does not meet auto-approve criteria
- Does not trigger auto-reject rule
- Falls into "manual review" category
- May require:
  - Additional documentation
  - PMI (Private Mortgage Insurance)
  - Higher interest rate
  - Underwriter approval

**Paystub Document**:
- File: `data/applications/paystub_scenario2_conditional.pdf`
- Employee: Bob Marginal
- Gross Biweekly: $3,653.85
- Annual: $95,000 (26 pay periods)

---

### Scenario 3: Rejection ❌

**Purpose**: Demonstrate high-risk borrower triggering auto-reject

**Credit Profile** (from `mock_credit_bureau.db`):
- SSN: `444-44-4444`
- Credit Score: **590** (Poor)
- Payment History: Poor
- Credit Utilization: 85% (very high)
- Derogatory Marks: 3 (collections/charge-offs)
- Late Payments (12mo): 6
- Hard Inquiries: 8

**Application Data**:
- Annual Income: **$55,000** (low income)
- Monthly Debt: **$2,500** (very high relative to income)
- Requested Loan: **$285,000**
- Property Value: **$300,000**
- Down Payment: **$15,000** (5%)

**Key Metrics**:
- DTI: ~55% (far exceeds 43% limit)
- LTV: 95% (minimal down payment)
- PTI: ~60% (unsustainable)

**Expected Outcome**: ❌ **DENIED**
- Triggers auto-reject rule: **DTI >43% AND Credit Score <640**
- Multiple high-risk flags:
  - Poor payment history
  - High credit utilization
  - Multiple derogatory marks
  - Excessive debt-to-income ratio
- Not eligible for any loan product

**Paystub Document**:
- File: `data/applications/paystub_scenario3_rejection.pdf`
- Employee: Charlie Risky
- Gross Biweekly: $2,115.38
- Annual: $55,000 (26 pay periods)

---

## Decision Rules Reference

From `src/agents/decision_agent.py::DecisionRules`:

### Auto-Reject Rule
```python
if dti_ratio > 43 and credit_score < 640:
    return 'denied'
```

### Auto-Approve Criteria (ALL must be true)
```python
if credit_score > 740 and dti_ratio < 35 and ltv_ratio < 75:
    return 'approved'
```

### High-Risk Flags
- DTI > 38%
- LTV > 80%
- Credit Score < 680
- Derogatory marks > 0
- Late payments in last 12 months

### Risk Levels
- **Low Risk**: Credit >740, DTI <28%, LTV <60%
- **Medium Risk**: Credit 680-740, DTI 28-38%, LTV 60-80%
- **High Risk**: Credit <680, DTI >38%, LTV >80%

---

## Adding Custom Test Cases

### To create a new scenario:

1. **Add credit profile to database**:
```python
import sqlite3
conn = sqlite3.connect('data/mock_credit_bureau.db')
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO credit_reports (
        ssn, name, credit_score, credit_utilization,
        accounts_open, derogatory_marks, credit_age_months,
        payment_history, late_payments_12mo, hard_inquiries_12mo,
        bureau_source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    '555-55-5555',  # Your custom SSN
    'Test Custom',
    700,  # Your credit score
    30.0,  # Utilization %
    10,  # Accounts
    0,  # Derogatory marks
    96,  # Credit age (months)
    'good',
    2,  # Late payments
    3,  # Hard inquiries
    'mock_credit_bureau'
))

conn.commit()
conn.close()
```

2. **Generate matching paystub**:
```python
# Add to scripts/generate_test_paystubs.py
create_paystub(
    output_path=output_dir / "paystub_custom.pdf",
    employee_name="Your Name",
    employee_id="EMP-XXXXX",
    company_name="Your Company",
    company_address="123 Your St, City, ST 12345",
    gross_biweekly=3846.15,  # $100k/year ÷ 26
    regular_hours=80.0,
    overtime_hours=0.0
)
```

3. **Create application dict in notebook**:
```python
custom_application = {
    "application_id": "APP-2025-XXX",
    "ssn": "555-55-5555",  # Match DB
    "annual_income": 100000,
    "monthly_debt_payments": 2000,
    "requested_amount": 250000,
    "property_value": 350000,
    # ... other fields
}
```

---

## Troubleshooting

### "SSN not found in credit database"
- Run `python src/mcp/seed_data.py` to create test profiles
- Or add custom profile via SQL (see above)

### "Document not found"
- Run `python scripts/generate_test_paystubs.py` to create PDFs
- Or use existing `paystub_sample.pdf` for all scenarios

### "MCP server connection refused"
- This is normal - system uses mock data when MCP server unavailable
- Credit data is queried directly from SQLite database

### Unexpected decision outcomes
- Check DTI calculation: `(monthly_debt * 12 / annual_income) * 100`
- Check LTV calculation: `(loan_amount / property_value) * 100`
- Verify credit score matches expected profile in database
- Review decision rules in `src/agents/decision_agent.py`

---

## File Locations Summary

```
data/
├── mock_credit_bureau.db          # Credit profiles (4 test SSNs)
└── applications/
    ├── paystub_scenario1_approval.pdf      # $180k/year
    ├── paystub_scenario2_conditional.pdf   # $95k/year
    └── paystub_scenario3_rejection.pdf     # $55k/year

notebooks/
└── 07_complete_underwriting_scenarios.ipynb  # Main demo notebook

scripts/
└── generate_test_paystubs.py      # Creates paystub PDFs

src/
├── mcp/seed_data.py              # Seeds credit database
└── agents/decision_agent.py      # Decision rules logic
```

---

## Expected Execution Output

When running the notebook, you should see:

**Scenario 1 (Auto-Approval)**:
```
✅ FINAL DECISION: APPROVED
   Confidence: 95%
   Approved Amount: $300,000
   Interest Rate: 6.250%
   Monthly Payment: $1,847.15
```

**Scenario 2 (Conditional)**:
```
⚠️ FINAL DECISION: CONDITIONAL APPROVAL
   Confidence: 70%
   Approved Amount: $340,000
   Interest Rate: 7.125%
   Conditions:
      1. Provide additional income verification
      2. PMI required (LTV > 80%)
      3. Manual underwriter review required
```

**Scenario 3 (Rejection)**:
```
❌ FINAL DECISION: DENIED
   Confidence: 90%
   Reasons:
      1. DTI ratio 55% exceeds maximum 43%
      2. Credit score 590 below minimum 640
      3. Multiple derogatory marks on credit report
```

---

## Next Steps

After running all three scenarios:

1. **Analyze comparative results** - See how different risk factors impact decisions
2. **Experiment with edge cases** - Test DTI exactly at 43%, credit at 640, etc.
3. **Modify prompts** - Try different risk analysis or decision prompts
4. **Add more scenarios** - Create custom test cases for specific learning goals
5. **Review compliance** - Examine how RAG retrieval grounds compliance decisions
6. **Cost analysis** - Track Azure OpenAI token usage across scenarios

Happy underwriting! 🏦
