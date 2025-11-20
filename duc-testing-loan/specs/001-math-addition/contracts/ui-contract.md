# UI Component Contracts

**Feature**: 001-math-addition  
**Date**: November 19, 2025  
**Purpose**: Define interfaces between UI components and business logic modules

## Module Interfaces

### 1. Calculator Module

**File**: `src/modules/calculator.js`

**Purpose**: Pure calculation logic with no UI dependencies

#### Function: `add(num1, num2)`

Calculates the sum of two numbers.

**Parameters**:
- `num1` (number): First operand, must be a finite number
- `num2` (number): Second operand, must be a finite number

**Returns**:
- `number`: The sum of num1 and num2, rounded to 10 decimal places

**Throws**:
- `TypeError`: If either parameter is not a number
- `RangeError`: If either parameter is not finite (Infinity, -Infinity, NaN)

**Examples**:
```javascript
add(5, 3)          // Returns: 8
add(2.5, 3.7)      // Returns: 6.2
add(-10, 5)        // Returns: -5
add(0.1, 0.2)      // Returns: 0.3 (handles floating-point precision)
add("5", 3)        // Throws: TypeError
add(Infinity, 5)   // Throws: RangeError
```

**Test Requirements**:
- 100% code coverage (critical business logic per constitution)
- Test all numeric types: integers, decimals, negatives, zero
- Test edge cases: large numbers, floating-point precision
- Test error cases: invalid types, infinite values

---

### 2. Validator Module

**File**: `src/modules/validator.js`

**Purpose**: Input validation logic independent of DOM

#### Function: `validateNumberInput(value)`

Validates a single number input.

**Parameters**:
- `value` (string): Raw input value from user

**Returns**:
- `Object`: NumberInput object with validation results
  ```javascript
  {
    value: string,
    parsedValue: number | null,
    isValid: boolean,
    error: string | null
  }
  ```

**Validation Rules**:
1. Empty string → `{ isValid: false, error: ERROR_MESSAGES.EMPTY_FIELDS }`
2. Non-numeric → `{ isValid: false, error: ERROR_MESSAGES.INVALID_NUMBER }`
3. Length > 15 → `{ isValid: false, error: ERROR_MESSAGES.NUMBER_TOO_LARGE }`
4. Valid number → `{ isValid: true, parsedValue: <number>, error: null }`

**Examples**:
```javascript
validateNumberInput("42")
// Returns: { value: "42", parsedValue: 42, isValid: true, error: null }

validateNumberInput("")
// Returns: { value: "", parsedValue: null, isValid: false, error: "Please enter both numbers" }

validateNumberInput("abc")
// Returns: { value: "abc", parsedValue: null, isValid: false, error: "Please enter valid numbers" }

validateNumberInput("12345678901234567")
// Returns: { value: "...", parsedValue: null, isValid: false, error: "Number is too large (max 15 digits)" }
```

#### Function: `validateCalculationRequest(input1, input2)`

Validates both inputs for a calculation.

**Parameters**:
- `input1` (NumberInput): First validated input
- `input2` (NumberInput): Second validated input

**Returns**:
- `Object`: Validation result
  ```javascript
  {
    isValid: boolean,
    error: ValidationError | null,
    canCalculate: boolean
  }
  ```

**Examples**:
```javascript
const num1 = validateNumberInput("5");
const num2 = validateNumberInput("3");
validateCalculationRequest(num1, num2)
// Returns: { isValid: true, error: null, canCalculate: true }

const num1 = validateNumberInput("abc");
const num2 = validateNumberInput("3");
validateCalculationRequest(num1, num2)
// Returns: { isValid: false, error: {...}, canCalculate: false }
```

---

### 3. UI Module

**File**: `src/modules/ui.js`

**Purpose**: DOM manipulation and event handling

#### Function: `initializeUI()`

Sets up event listeners and initial UI state.

**Parameters**: None

**Returns**: `void`

**Side Effects**:
- Attaches event listeners to form elements
- Sets up keyboard shortcuts
- Initializes ARIA live regions
- Sets focus to first input field

**Example**:
```javascript
// Called once on page load
initializeUI();
```

#### Function: `handleCalculateClick()`

Handles calculate button click event.

**Parameters**: None

**Returns**: `void`

**Process**:
1. Get input values from DOM
2. Validate inputs using validator module
3. If valid: Calculate using calculator module
4. Update UI with result or error
5. Update ARIA live regions for screen readers

**Example**:
```javascript
// Attached to button click event
calculateButton.addEventListener('click', handleCalculateClick);
```

#### Function: `handleClearClick()`

Handles clear button click event.

**Parameters**: None

**Returns**: `void`

**Side Effects**:
- Clears all input fields
- Clears result display
- Clears error messages
- Resets UI state
- Sets focus to first input

**Example**:
```javascript
// Attached to clear button click event
clearButton.addEventListener('click', handleClearClick);
```

#### Function: `displayResult(result)`

Displays calculation result to user.

**Parameters**:
- `result` (CalculationResult): Result object from calculator module

**Returns**: `void`

**Side Effects**:
- Updates result element textContent
- Updates ARIA live region
- Clears any existing error messages
- Updates UI state

**Example**:
```javascript
const result = { value: 8, displayValue: "8", ... };
displayResult(result);
// DOM: <output id="result">8</output>
```

#### Function: `displayError(error)`

Displays validation or calculation error.

**Parameters**:
- `error` (ValidationError): Error object from validator

**Returns**: `void`

**Side Effects**:
- Updates error element textContent
- Updates ARIA live region (assertive)
- Clears result display
- Adds error styling classes
- Announces error to screen readers

**Example**:
```javascript
const error = { type: "INVALID", message: "Please enter valid numbers", field: "first" };
displayError(error);
// DOM: <div id="error" role="alert">Please enter valid numbers</div>
```

#### Function: `clearUI()`

Resets all UI elements to initial state.

**Parameters**: None

**Returns**: `void`

**Side Effects**:
- Clears input values
- Clears result display
- Clears error messages
- Removes error styling
- Resets focus

---

## Event Flow Diagrams

### Calculate Flow

```text
User clicks "Calculate"
    ↓
handleCalculateClick()
    ↓
Get input values from DOM
    ↓
validateNumberInput(value1) → NumberInput
validateNumberInput(value2) → NumberInput
    ↓
validateCalculationRequest(input1, input2)
    ↓
    ├── Invalid → displayError(error)
    │                    ↓
    │              Update DOM with error message
    │
    └── Valid → add(num1, num2) → CalculationResult
                     ↓
                displayResult(result)
                     ↓
                Update DOM with result
```

### Clear Flow

```text
User clicks "Clear"
    ↓
handleClearClick()
    ↓
clearUI()
    ↓
Reset all DOM elements
    ↓
Set focus to first input
```

### Keyboard Flow

```text
User presses Enter in input field
    ↓
Trigger form submit event
    ↓
Prevent default form submission
    ↓
Call handleCalculateClick()
    ↓
(same as calculate flow)
```

## DOM Element Contracts

### Required HTML Elements

```html
<!-- Form container -->
<form id="calculator-form" role="form" aria-label="Addition Calculator">
  
  <!-- First input -->
  <label for="first-number">First Number</label>
  <input 
    type="number" 
    id="first-number" 
    name="firstNumber"
    aria-required="true"
    aria-describedby="error-message"
  />
  
  <!-- Second input -->
  <label for="second-number">Second Number</label>
  <input 
    type="number" 
    id="second-number" 
    name="secondNumber"
    aria-required="true"
    aria-describedby="error-message"
  />
  
  <!-- Calculate button -->
  <button 
    type="submit" 
    id="calculate-btn"
    aria-label="Calculate sum"
  >
    Calculate
  </button>
  
  <!-- Clear button -->
  <button 
    type="button" 
    id="clear-btn"
    aria-label="Clear all fields"
  >
    Clear
  </button>
  
  <!-- Result display -->
  <output 
    id="result" 
    for="first-number second-number"
    aria-live="polite" 
    role="status"
  ></output>
  
  <!-- Error message -->
  <div 
    id="error-message" 
    role="alert" 
    aria-live="assertive"
    class="error-message hidden"
  ></div>
  
</form>
```

### CSS Class Contracts

**Required Classes**:
- `.error-message`: Styles for error message container
- `.hidden`: Utility class to hide elements (display: none)
- `.error`: Applied to inputs with validation errors
- `.has-result`: Applied to result element when displaying result

**Focus Styles**:
- All interactive elements must have visible focus indicators
- Minimum 3:1 contrast ratio for focus outlines

## Module Dependencies

```text
main.js
    ├── imports → ui.js
    ├── imports → calculator.js
    ├── imports → validator.js
    └── imports → config.js

ui.js
    ├── imports → calculator.js
    ├── imports → validator.js
    └── imports → config.js

calculator.js
    └── imports → config.js

validator.js
    └── imports → config.js

config.js
    └── (no dependencies)
```

## Error Handling Contract

All modules must handle errors consistently:

1. **Calculator Module**:
   - Throw typed errors (TypeError, RangeError)
   - Never return invalid results
   - Log errors to console (development only)

2. **Validator Module**:
   - Return structured error objects
   - Never throw exceptions
   - Always include error message

3. **UI Module**:
   - Catch all errors from calculator/validator
   - Display user-friendly messages
   - Log detailed errors to console
   - Never crash or show technical details to user

## Testing Contracts

### Unit Test Requirements

Each module must have unit tests covering:

**Calculator Module**:
- All numeric types (integer, decimal, negative, zero)
- Edge cases (large numbers, floating-point precision)
- Error cases (invalid types, infinite values)
- 100% code coverage required

**Validator Module**:
- All validation rules
- All error message types
- Boundary conditions (empty, max length, special characters)
- 80%+ code coverage required

**UI Module**:
- Event handlers (click, submit, keyboard)
- DOM updates (result, error, clear)
- ARIA live region updates
- 80%+ code coverage required

### E2E Test Requirements

Must cover all acceptance scenarios from spec:
- 7 scenarios across 3 user stories
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Mobile viewport testing
- Keyboard navigation testing
- Screen reader compatibility testing

## Performance Contracts

All functions must meet constitution requirements:

- `add()`: Execute in <1ms
- `validateNumberInput()`: Execute in <1ms
- `handleCalculateClick()`: Complete in <100ms (includes DOM updates)
- `displayResult()`: Complete in <50ms
- `displayError()`: Complete in <50ms

## Accessibility Contracts

All UI functions must:

- Update ARIA live regions appropriately
- Maintain keyboard focus management
- Provide clear screen reader announcements
- Support keyboard navigation
- Meet WCAG 2.1 Level AA standards
