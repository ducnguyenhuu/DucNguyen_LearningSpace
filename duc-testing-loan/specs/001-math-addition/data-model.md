# Data Model: Math Addition Calculator

**Feature**: 001-math-addition  
**Date**: November 19, 2025  
**Purpose**: Define data structures and entities for calculator application

## Overview

This is a client-side only application with no persistent storage. All data exists transiently in memory during user interaction. This document defines the shape of data flowing through the application.

## Core Entities

### 1. NumberInput

Represents a single numeric input from the user.

**Properties**:
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| value | string | - | Raw input value from DOM element |
| parsedValue | number \| null | Must be finite number | Parsed numeric value, null if invalid |
| isValid | boolean | - | Whether input passes validation |
| error | string \| null | - | Error message if validation fails |

**Validation Rules**:
- Required: Input cannot be empty
- Type: Must parse to valid JavaScript number
- Range: Must be within JavaScript safe integer range when integer
- Decimal: Maximum 10 decimal places
- Length: Maximum 15 characters

**Example**:
```javascript
// Valid integer input
{
  value: "42",
  parsedValue: 42,
  isValid: true,
  error: null
}

// Valid decimal input
{
  value: "3.14159",
  parsedValue: 3.14159,
  isValid: true,
  error: null
}

// Invalid input
{
  value: "abc",
  parsedValue: null,
  isValid: false,
  error: "Please enter valid numbers"
}

// Empty input
{
  value: "",
  parsedValue: null,
  isValid: false,
  error: "Please enter both numbers"
}
```

### 2. CalculationRequest

Represents the input data for a calculation operation.

**Properties**:
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| firstNumber | NumberInput | required | First operand |
| secondNumber | NumberInput | required | Second operand |
| operation | string | Must be "add" | Operation type (always addition for this version) |

**Validation Rules**:
- Both inputs must be valid (isValid === true)
- Both parsedValue must not be null
- Operation must be "add"

**Example**:
```javascript
{
  firstNumber: {
    value: "5",
    parsedValue: 5,
    isValid: true,
    error: null
  },
  secondNumber: {
    value: "3",
    parsedValue: 3,
    isValid: true,
    error: null
  },
  operation: "add"
}
```

### 3. CalculationResult

Represents the output of a calculation operation.

**Properties**:
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| value | number | Must be finite | Calculated result |
| displayValue | string | - | Formatted result for display (rounded if needed) |
| precision | number | 0-10 | Number of decimal places in result |
| operands | object | - | Original input values for reference |
| timestamp | number | - | Unix timestamp of calculation |

**Display Rules**:
- Round to maximum 10 decimal places
- Remove trailing zeros after decimal point
- Format large numbers with appropriate precision
- Handle negative results correctly

**Example**:
```javascript
// Integer result
{
  value: 8,
  displayValue: "8",
  precision: 0,
  operands: { first: 5, second: 3 },
  timestamp: 1700409600000
}

// Decimal result
{
  value: 6.2,
  displayValue: "6.2",
  precision: 1,
  operands: { first: 2.5, second: 3.7 },
  timestamp: 1700409600000
}

// Floating-point precision issue handled
{
  value: 0.3,
  displayValue: "0.3",
  precision: 1,
  operands: { first: 0.1, second: 0.2 },
  timestamp: 1700409600000
  // Note: 0.1 + 0.2 = 0.30000000000000004 in JavaScript
  // Rounded to 0.3 for display
}
```

### 4. ValidationError

Represents a validation failure.

**Properties**:
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| type | string | enum: EMPTY, INVALID, TOO_LARGE | Error category |
| message | string | - | User-facing error message |
| field | string | "first" \| "second" \| "both" | Which input(s) caused error |

**Error Types**:
```javascript
const ErrorTypes = {
  EMPTY: 'EMPTY',           // One or both fields empty
  INVALID: 'INVALID',       // Non-numeric input
  TOO_LARGE: 'TOO_LARGE'    // Exceeds safe number limits
};
```

**Example**:
```javascript
// Empty field error
{
  type: "EMPTY",
  message: "Please enter both numbers",
  field: "both"
}

// Invalid input error
{
  type: "INVALID",
  message: "Please enter valid numbers",
  field: "first"
}

// Number too large error
{
  type: "TOO_LARGE",
  message: "Number is too large (max 15 digits)",
  field: "second"
}
```

### 5. UIState

Represents the current state of the user interface.

**Properties**:
| Property | Type | Description |
|----------|------|-------------|
| firstInputValue | string | Current value of first input field |
| secondInputValue | string | Current value of second input field |
| resultDisplay | string | Current result display text |
| errorMessage | string \| null | Current error message (null if no error) |
| isCalculating | boolean | Whether calculation is in progress |
| hasResult | boolean | Whether a result is currently displayed |

**State Transitions**:
```javascript
// Initial state
{
  firstInputValue: "",
  secondInputValue: "",
  resultDisplay: "",
  errorMessage: null,
  isCalculating: false,
  hasResult: false
}

// After successful calculation
{
  firstInputValue: "5",
  secondInputValue: "3",
  resultDisplay: "8",
  errorMessage: null,
  isCalculating: false,
  hasResult: true
}

// After validation error
{
  firstInputValue: "abc",
  secondInputValue: "3",
  resultDisplay: "",
  errorMessage: "Please enter valid numbers",
  isCalculating: false,
  hasResult: false
}

// After clear
{
  firstInputValue: "",
  secondInputValue: "",
  resultDisplay: "",
  errorMessage: null,
  isCalculating: false,
  hasResult: false
}
```

## Data Flow

```text
User Input (DOM Events)
    ↓
NumberInput (Raw Value)
    ↓
Validator Module → ValidationError (if invalid)
    ↓
CalculationRequest (Valid Inputs)
    ↓
Calculator Module
    ↓
CalculationResult
    ↓
UI Module → DOM Update
    ↓
Display to User
```

## Constants and Configuration

### Validation Constants

```javascript
const VALIDATION_CONFIG = {
  MAX_INPUT_LENGTH: 15,
  MAX_DECIMAL_PLACES: 10,
  MAX_SAFE_INTEGER: Number.MAX_SAFE_INTEGER,  // 9007199254740991
  MIN_SAFE_INTEGER: Number.MIN_SAFE_INTEGER   // -9007199254740991
};
```

### Error Messages

```javascript
const ERROR_MESSAGES = {
  EMPTY_FIELDS: 'Please enter both numbers',
  INVALID_NUMBER: 'Please enter valid numbers',
  NUMBER_TOO_LARGE: 'Number is too large (max 15 digits)',
  CALCULATION_ERROR: 'Unable to calculate result'
};
```

### Display Constants

```javascript
const DISPLAY_CONFIG = {
  MAX_DECIMAL_PLACES: 10,
  MIN_SIGNIFICANT_DIGITS: 1,
  RESULT_PREFIX: 'Result: ',
  EMPTY_RESULT_TEXT: ''
};
```

## Type Definitions (JSDoc)

```javascript
/**
 * @typedef {Object} NumberInput
 * @property {string} value - Raw input value
 * @property {number|null} parsedValue - Parsed numeric value
 * @property {boolean} isValid - Validation status
 * @property {string|null} error - Error message if invalid
 */

/**
 * @typedef {Object} CalculationRequest
 * @property {NumberInput} firstNumber - First operand
 * @property {NumberInput} secondNumber - Second operand
 * @property {string} operation - Operation type
 */

/**
 * @typedef {Object} CalculationResult
 * @property {number} value - Calculated result
 * @property {string} displayValue - Formatted display value
 * @property {number} precision - Decimal places
 * @property {Object} operands - Original input values
 * @property {number} timestamp - Calculation timestamp
 */

/**
 * @typedef {Object} ValidationError
 * @property {string} type - Error category
 * @property {string} message - User-facing message
 * @property {string} field - Affected input field
 */

/**
 * @typedef {Object} UIState
 * @property {string} firstInputValue - First input value
 * @property {string} secondInputValue - Second input value
 * @property {string} resultDisplay - Result display text
 * @property {string|null} errorMessage - Current error message
 * @property {boolean} isCalculating - Calculation in progress
 * @property {boolean} hasResult - Result displayed
 */
```

## Relationships

```text
CalculationRequest
    ├── contains → NumberInput (firstNumber)
    ├── contains → NumberInput (secondNumber)
    └── produces → CalculationResult | ValidationError

NumberInput
    └── validates to → ValidationError (if invalid)

CalculationResult
    └── updates → UIState (resultDisplay)

ValidationError
    └── updates → UIState (errorMessage)

UIState
    └── renders → DOM
```

## Data Validation Summary

| Entity | Validation Point | Rules Applied |
|--------|-----------------|---------------|
| NumberInput | On input change | Required, type, length, range |
| NumberInput | On form submit | All validation rules |
| CalculationRequest | Before calculation | Both inputs valid |
| CalculationResult | After calculation | Finite number, precision limits |

## Edge Cases Handled

1. **Floating-Point Precision**
   - Input: 0.1 + 0.2
   - Expected: 0.30000000000000004
   - Display: "0.3" (rounded to 10 decimals, trailing zeros removed)

2. **Large Numbers**
   - Input: 999999999999999 (15 digits)
   - Validated: Within safe integer range
   - Calculated: Exact result
   - Input: 9999999999999999 (16 digits)
   - Validated: Rejected (too large)

3. **Negative Numbers**
   - Input: -10 + 5
   - Result: -5
   - Display: "-5"

4. **Zero Values**
   - Input: 0 + 0
   - Result: 0
   - Display: "0"

5. **Mixed Integer and Decimal**
   - Input: 5 + 3.7
   - Result: 8.7
   - Display: "8.7"

## Future Extensibility

While this version only supports addition, the data model is designed for extensibility:

- `operation` field in CalculationRequest can support other operations
- Calculator module can be extended with additional operation methods
- Validation rules can be operation-specific
- UI can be enhanced to select operation type

**Note**: Do not implement extensibility now. This is design-time consideration only.
