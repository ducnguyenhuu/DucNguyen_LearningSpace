# Rule-Based Validation System

## Overview

Instead of hardcoding validation rules in Python, the system now uses **configurable YAML files** where business rules can be easily added, modified, or disabled without touching code.

## Architecture

```
src/
├── validation_rules.yaml           # ← Edit this to add/modify rules
├── agents/
│   ├── validation_engine.py       # Rule engine (no need to modify)
│   └── document_agent.py          # Can use either DataValidator or ValidationRuleEngine
```

## Quick Start

### 1. Use the Rule-Based Validator

```python
from src.agents.validation_engine import ValidationRuleEngine
from src.models import DocumentType

# Initialize engine (loads rules from YAML)
engine = ValidationRuleEngine("src/validation_rules.yaml")

# Validate data
data = {
    "gross_monthly_income": 5000.00,
    "net_monthly_income": 3800.00,
    # ... other fields
}

is_valid, errors = engine.validate(data, DocumentType.PAY_STUB)

if not is_valid:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")
```

### 2. Add a New Rule (No Code Changes!)

Edit `src/validation_rules.yaml`:

```yaml
pay_stub:
  rules:
    # ... existing rules ...
    
    - rule_id: PAY_006
      name: "Maximum income check"
      type: range
      fields:
        - gross_monthly_income
      min_value: 0
      max_value: 50000  # $50k/month cap
      error_message: "Gross income ({value}) exceeds maximum ($50,000)"
      severity: warning
      optional: false
```

That's it! No Python changes needed. ✨

## Rule Types

### 1. Comparison Rules
Compare two fields (e.g., net ≤ gross)

```yaml
- rule_id: PAY_001
  type: comparison
  field1: net_monthly_income
  operator: "<="
  field2: gross_monthly_income
  error_message: "Net ({field1}) exceeds gross ({field2})"
  severity: critical
```

**Operators**: `<=`, `<`, `>=`, `>`, `==`, `!=`

### 2. Range Rules
Check value is within bounds

```yaml
- rule_id: PAY_003
  type: range
  fields:
    - gross_monthly_income
    - net_monthly_income
  min_value: 0
  max_value: 1000000  # Or null for no limit
  error_message: "{field} outside valid range: {value}"
  severity: critical
```

### 3. Date Order Rules
Verify chronological dates

```yaml
- rule_id: PAY_002
  type: date_order
  start_field: pay_period_start
  end_field: pay_period_end
  error_message: "Start ({start_field}) must be before end ({end_field})"
  severity: critical
```

**Special date keywords**: `TODAY`, `ONE_YEAR_AGO`, `ONE_YEAR_FROM_NOW`

### 4. Format Rules
Validate using regex patterns

```yaml
- rule_id: PAY_005
  type: format
  field: employee_ssn
  patterns:
    - '^\d{3}-\d{2}-\d{4}$'  # Full SSN
    - '^\d{4}$'               # Last 4 only
  error_message: "Invalid SSN format: {value}"
  severity: warning
  optional: true
```

**Options**:
- `negate: true` - Pattern should NOT match (useful for detecting placeholders)
- `case_insensitive: true` - Ignore case

### 5. Calculation Rules
Verify mathematical calculations

```yaml
- rule_id: BANK_002
  type: calculation
  formula: "ending_balance = beginning_balance + total_deposits - total_withdrawals"
  tolerance: 1.00  # $1 tolerance for rounding
  fields:
    beginning_balance: required
    total_deposits: required
    total_withdrawals: required
    ending_balance: required
  error_message: "Balance equation doesn't match"
  severity: critical
```

**Supported formulas**:
- Balance equation: `ending = beginning + deposits - withdrawals`
- Monthly calculation: `monthly = annual / 12`
- YTD consistency: `ytd ~= monthly * months_worked`

## Rule Properties

| Property | Required | Description |
|----------|----------|-------------|
| `rule_id` | Yes | Unique identifier (e.g., PAY_001) |
| `name` | Yes | Human-readable description |
| `type` | Yes | Rule type (comparison, range, etc.) |
| `error_message` | Yes | Message shown when rule fails (supports {placeholders}) |
| `severity` | Yes | `critical`, `warning`, or `info` |
| `optional` | No | If `true`, rule only runs when fields exist |

## Severity Levels

- **critical**: Must pass for document to be valid (blocks processing)
- **warning**: Should pass but doesn't block (flagged for review)
- **info**: Informational only (logged but not reported)

## Execution Configuration

```yaml
execution:
  stop_on_first_critical: false  # Continue checking all rules
  max_errors_per_document: 20    # Prevent overwhelming output
  skip_warnings_if_critical: false  # Show warnings even when critical errors exist
```

## Common Patterns

### Pattern 1: Optional Field Validation
Only validate if field exists:

```yaml
- rule_id: PAY_005
  type: format
  field: employee_ssn
  patterns: ['^\d{3}-\d{2}-\d{4}$']
  error_message: "Invalid SSN: {value}"
  severity: warning
  optional: true  # ← Only check if SSN is provided
```

### Pattern 2: Placeholder Detection
Catch placeholder values:

```yaml
- rule_id: COMMON_002
  type: format
  pattern: "^(null|none|n/a)$"
  negate: true  # ← Should NOT match these values
  error_message: "Field '{field}' contains placeholder: {value}"
  severity: warning
  case_insensitive: true
```

### Pattern 3: Cross-Document Rules
Validate consistency across related documents:

```yaml
- rule_id: CROSS_001
  type: comparison
  field1: pay_stub.employer_name
  operator: "=="
  field2: employment_letter.employer_name
  error_message: "Employer name mismatch between documents"
  severity: warning
```

## Hot-Reloading in Production

```python
# Load initial rules
engine = ValidationRuleEngine("src/validation_rules.yaml")

# ... later, after YAML file is updated ...

# Reload without restarting application
engine.reload_rules()

print("Rules updated!")
```

## Migration from Hardcoded Validation

### Old Way (Hardcoded)
```python
class DataValidator:
    def _validate_pay_stub(self, data):
        errors = []
        if data["net"] > data["gross"]:
            errors.append("Net exceeds gross")
        return errors
```

**Problems**:
- ❌ Need to modify Python code for new rules
- ❌ Requires deployment to change rules
- ❌ Business users can't configure
- ❌ Hard to audit rule changes

### New Way (Configurable)
```yaml
pay_stub:
  rules:
    - rule_id: PAY_001
      type: comparison
      field1: net_monthly_income
      operator: "<="
      field2: gross_monthly_income
      error_message: "Net exceeds gross"
      severity: critical
```

**Benefits**:
- ✅ Edit YAML file to add rules
- ✅ No deployment needed (hot-reload)
- ✅ Business users can configure
- ✅ Git tracks all rule changes

## Testing Rules

```bash
# Test the rule engine
python3 scripts/test_validation_engine.py

# Test specific document type
python3 -c "
from src.agents.validation_engine import ValidationRuleEngine
from src.models import DocumentType

engine = ValidationRuleEngine()
data = {'gross_monthly_income': 5000, 'net_monthly_income': 3800}
is_valid, errors = engine.validate(data, DocumentType.PAY_STUB)
print(f'Valid: {is_valid}, Errors: {errors}')
"
```

## Rule Development Workflow

1. **Identify Business Rule**: "Net income should never exceed gross income"

2. **Add to YAML**:
   ```yaml
   - rule_id: PAY_XXX
     type: comparison
     field1: net_monthly_income
     operator: "<="
     field2: gross_monthly_income
     error_message: "Net ({field1}) exceeds gross ({field2})"
     severity: critical
   ```

3. **Test**:
   ```bash
   python3 scripts/test_validation_engine.py
   ```

4. **Deploy**: Just commit the YAML file!

5. **Monitor**: Check logs for rule violations

## Best Practices

### 1. Use Descriptive Rule IDs
- ✅ `PAY_001`, `BANK_002` (clear prefix)
- ❌ `RULE_1`, `CHECK_A` (unclear)

### 2. Write Clear Error Messages
- ✅ `"Net income ($6000) exceeds gross income ($5000)"`
- ❌ `"Validation failed"`

### 3. Set Appropriate Severity
- **critical**: Fraud indicators, impossible values
- **warning**: Unusual but possible scenarios
- **info**: Informational only

### 4. Use Tolerance for Financial Calculations
```yaml
tolerance: 1.00  # $1 tolerance for rounding errors
```

### 5. Make Optional Rules Optional
```yaml
optional: true  # Only validate if field exists
```

## Comparison: Old vs New

| Feature | Hardcoded (DataValidator) | Rule-Based (ValidationRuleEngine) |
|---------|---------------------------|-----------------------------------|
| Add new rule | Modify Python code | Edit YAML file |
| Deployment | Code deployment required | Config file update only |
| Hot-reload | Restart application | `reload_rules()` |
| Business user friendly | No (requires coding) | Yes (edit YAML) |
| Version control | Code diffs | YAML diffs (clearer) |
| Audit trail | Code commits | Config commits |
| Testing | Unit tests | YAML + unit tests |
| Rule reuse | Duplicate code | Reusable rule types |

## When to Use Which?

### Use Rule-Based Engine When:
- ✅ Rules change frequently
- ✅ Business users need to configure
- ✅ Need audit trail of rule changes
- ✅ Want hot-reload capability
- ✅ Rules are data-driven (thresholds, limits)

### Use Hardcoded Validator When:
- ✅ Complex validation logic (custom algorithms)
- ✅ Performance is critical (no YAML parsing)
- ✅ Rules are stable and rarely change
- ✅ Need tight integration with code

## Migration Strategy

**Option 1: Hybrid Approach** (Recommended)
```python
# Use both validators
engine = ValidationRuleEngine()
validator = DataValidator()

# Try rule-based first
is_valid, errors = engine.validate(data, doc_type)

# Fall back to hardcoded for complex rules
if is_valid:
    is_valid2, errors2 = validator.validate(data, doc_type)
```

**Option 2: Full Migration**
Replace `DataValidator` with `ValidationRuleEngine` everywhere.

**Option 3: Keep Both**
Use for different purposes (rule-based for business rules, hardcoded for technical validation).

---

**Summary**: The rule-based validation system makes it **easy to add, modify, and audit business rules without coding**, perfect for evolving loan underwriting requirements! 🎯
