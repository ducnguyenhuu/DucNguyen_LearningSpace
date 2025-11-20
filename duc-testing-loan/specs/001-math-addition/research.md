# Research: Math Addition Calculator

**Feature**: 001-math-addition  
**Date**: November 19, 2025  
**Purpose**: Research and document technical decisions for vanilla JS calculator with Vite

## Research Tasks

### 1. Vite Configuration for Vanilla JavaScript

**Decision**: Use Vite 5.x with minimal configuration, vanilla JavaScript template

**Rationale**:
- Vite provides fast dev server with Hot Module Replacement (HMR)
- Zero-config setup for vanilla JS projects
- Built-in optimization (minification, tree-shaking, code splitting)
- Native ES modules support in development
- Production build with Rollup for optimal bundling
- Significantly faster than Webpack for simple projects
- No framework overhead matches requirement for minimal dependencies

**Configuration**:
```javascript
// vite.config.js
export default {
  root: 'math-calculator',
  build: {
    outDir: 'dist',
    target: 'es2015', // Support last 2 versions of modern browsers
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: undefined // Single bundle for this small app
      }
    }
  }
}
```

**Alternatives Considered**:
- Parcel: Good zero-config option but Vite has faster HMR
- Plain HTML/no bundler: Works but loses optimization, dev server benefits
- Webpack: Too complex for simple vanilla JS app

### 2. Testing Strategy with Vitest and Playwright

**Decision**: Vitest for unit tests, Playwright for E2E tests

**Rationale - Vitest**:
- Native Vite integration, same config
- Jest-compatible API (familiar to most developers)
- Fast execution with smart watch mode
- Built-in code coverage with c8
- ES modules support out of the box
- TypeScript support for future needs

**Rationale - Playwright**:
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Mobile viewport emulation for responsive testing
- Reliable auto-wait mechanism (no flaky tests)
- Built-in test runner and reporters
- Screenshot/video capture for debugging
- Keyboard navigation testing for accessibility

**Test Organization**:
```text
tests/
├── unit/
│   ├── calculator.test.js    # Pure calculation logic
│   ├── validator.test.js     # Input validation rules
│   └── ui.test.js            # DOM manipulation (with JSDOM)
└── e2e/
    └── calculator.spec.js    # Full user scenarios from spec
```

**Alternatives Considered**:
- Jest: Industry standard but requires more configuration with ES modules
- Cypress: Popular E2E tool but Playwright has better cross-browser support
- Testing Library: Considered but JSDOM sufficient for simple DOM tests

### 3. Input Validation Pattern

**Decision**: Client-side validation with HTML5 input attributes + JavaScript validation layer

**Rationale**:
- HTML5 `type="number"` provides basic browser validation
- Additional JavaScript validation for edge cases (empty, non-numeric, large numbers)
- Validate on both input change and form submit
- Clear error messages follow constitution requirement
- No server-side validation needed (no backend)

**Validation Rules**:
```javascript
// validator.js patterns
const VALIDATION_RULES = {
  required: true,
  type: 'number',
  maxLength: 15, // Prevent JS MAX_SAFE_INTEGER issues
  allowNegative: true,
  allowDecimal: true,
  maxDecimalPlaces: 10
};
```

**Error Message Strategy**:
```javascript
// constants/config.js
const ERROR_MESSAGES = {
  EMPTY_FIELDS: 'Please enter both numbers',
  INVALID_NUMBER: 'Please enter valid numbers',
  NUMBER_TOO_LARGE: 'Number is too large (max 15 digits)',
  CALCULATION_ERROR: 'Unable to calculate result'
};
```

**Alternatives Considered**:
- Schema validation library (Yup, Zod): Overkill for simple number validation
- Regex-only validation: Less user-friendly, doesn't handle edge cases well
- No validation: Violates spec requirements and constitution principles

### 4. Accessibility Implementation

**Decision**: Full WCAG 2.1 Level AA compliance with semantic HTML and ARIA

**Rationale**:
- Constitution requires WCAG 2.1 Level AA compliance
- Keyboard navigation is critical for calculator
- Screen reader support ensures inclusive design
- Color contrast 4.5:1 minimum for text

**Implementation Approach**:
```html
<!-- Semantic HTML -->
<form role="form" aria-label="Addition Calculator">
  <label for="number1">First Number</label>
  <input 
    type="number" 
    id="number1" 
    aria-required="true"
    aria-describedby="number1-error"
  />
  
  <button type="submit" aria-label="Calculate sum">
    Calculate
  </button>
  
  <output id="result" aria-live="polite" role="status">
    <!-- Result displayed here -->
  </output>
  
  <div id="error" role="alert" aria-live="assertive">
    <!-- Error messages -->
  </div>
</form>
```

**Keyboard Support**:
- Tab navigation between inputs and button
- Enter key submits calculation
- Escape key clears form (optional enhancement)
- Focus visible styles for keyboard users

**Screen Reader Support**:
- ARIA labels on all interactive elements
- `aria-live="polite"` for result updates
- `aria-live="assertive"` for error messages
- Proper heading hierarchy

**Color Contrast**:
- Text on background: 7:1 (exceeds 4.5:1 requirement)
- Error messages: red with 5:1 contrast
- Focus indicators: 3:1 contrast minimum

**Alternatives Considered**:
- Basic HTML only: Doesn't meet WCAG AA requirements
- Third-party a11y library: Not needed for simple form

### 5. Responsive Design Strategy

**Decision**: Mobile-first CSS with CSS Grid for layout, CSS custom properties for theming

**Rationale**:
- Constitution requires mobile-first approach
- CSS Grid provides clean, modern layout without framework
- Custom properties (CSS variables) enable consistent theming
- Media queries at defined breakpoints (768px, 1024px)
- Fluid typography with clamp()

**Layout Approach**:
```css
/* Mobile-first base styles */
.calculator {
  display: grid;
  gap: 1rem;
  padding: 1rem;
  max-width: 100%;
}

/* Tablet (768px+) */
@media (min-width: 768px) {
  .calculator {
    max-width: 400px;
    margin: 0 auto;
  }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .calculator {
    max-width: 500px;
  }
}
```

**Typography**:
```css
:root {
  --font-size-base: clamp(1rem, 2vw, 1.125rem);
  --font-size-large: clamp(1.5rem, 3vw, 2rem);
}
```

**Touch Targets**:
- All buttons minimum 44×44px (constitution requirement)
- Input fields minimum 44px height on mobile
- Adequate spacing between interactive elements (8px minimum)

**Alternatives Considered**:
- CSS framework (Bootstrap, Tailwind): Violates minimal dependencies requirement
- Flexbox only: Grid is cleaner for 2D layouts
- Fixed pixel sizing: Not responsive, fails mobile-first requirement

### 6. Performance Optimization

**Decision**: Inline critical CSS, code splitting not needed, tree-shaking enabled

**Rationale**:
- Small app (<50KB) doesn't need aggressive code splitting
- Inline critical CSS in `<head>` for FCP <1.5s
- Vite automatically tree-shakes unused code
- Minification with Terser for production
- No external dependencies in runtime bundle

**Build Optimization**:
```javascript
// vite.config.js
build: {
  target: 'es2015',
  minify: 'terser',
  terserOptions: {
    compress: {
      drop_console: true, // Remove console.logs in production
      dead_code: true
    }
  },
  cssMinify: true
}
```

**Loading Strategy**:
- No lazy loading needed (single page, small bundle)
- Defer non-critical JavaScript
- Inline critical CSS (~2-3KB)
- Separate CSS file for non-critical styles

**Alternatives Considered**:
- Dynamic imports: Not needed for this small app
- Service worker caching: Overkill for single-page calculator
- CDN for dependencies: No runtime dependencies to serve

### 7. Error Handling Strategy

**Decision**: Graceful error handling with user-friendly messages, no crashes

**Rationale**:
- Constitution requires actionable error messages
- Try-catch blocks around calculation and DOM operations
- Clear error states with ARIA live regions
- Log errors to console for debugging (development only)

**Error Categories**:
```javascript
// Error handling patterns
try {
  const result = calculate(num1, num2);
  displayResult(result);
} catch (error) {
  if (error instanceof ValidationError) {
    showError(ERROR_MESSAGES.INVALID_NUMBER);
  } else if (error instanceof CalculationError) {
    showError(ERROR_MESSAGES.CALCULATION_ERROR);
  } else {
    console.error('Unexpected error:', error);
    showError('An unexpected error occurred');
  }
}
```

**Edge Cases Handled**:
- Empty inputs
- Non-numeric inputs
- Numbers exceeding MAX_SAFE_INTEGER (9007199254740991)
- Floating-point precision issues (round to 10 decimals)
- Rapid button clicks (debounce not needed, calculations are instant)

**Alternatives Considered**:
- Generic error messages: Violates constitution (errors must be actionable)
- No error handling: Unacceptable, would cause crashes
- Error boundary pattern: Not applicable to vanilla JS

## Technology Stack Summary

| Component | Choice | Version | Justification |
|-----------|--------|---------|---------------|
| Build Tool | Vite | 5.x | Fast, minimal config, optimized bundling |
| Testing (Unit) | Vitest | 1.x | Native Vite integration, Jest-compatible |
| Testing (E2E) | Playwright | 1.x | Cross-browser, reliable, mobile testing |
| Linting | ESLint | 8.x | Constitution requirement, configurable |
| Language | JavaScript ES6+ | ES2015+ | Modern syntax, broad browser support |
| CSS | Vanilla CSS3 | - | Grid, custom properties, no framework needed |

## Best Practices Applied

1. **Modular Code Organization**
   - Separate modules for concerns: calculation, validation, UI
   - Pure functions for calculation logic (testable, no side effects)
   - Clear interfaces between modules

2. **Test-Driven Development**
   - Write tests before implementation (constitution requirement)
   - 100% coverage for calculation logic (critical business logic)
   - 80%+ overall coverage (constitution requirement)

3. **Semantic HTML**
   - Use proper form elements (`<form>`, `<label>`, `<input>`)
   - `<output>` element for calculation result
   - Proper heading hierarchy

4. **Progressive Enhancement**
   - HTML5 validation as first layer
   - JavaScript validation as second layer
   - Graceful degradation if JavaScript fails

5. **Code Quality**
   - ESLint with strict rules (score 8/10 minimum)
   - JSDoc comments on all public functions
   - Named constants instead of magic values
   - Functions under 50 lines (constitution limit)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Floating-point precision errors | Medium | Round results to 10 decimals, document limitation |
| Large number overflow | Low | Validate input length (15 digits max), show error |
| Browser compatibility issues | Low | Target ES2015, test on last 2 browser versions |
| Accessibility gaps | Medium | Use automated testing (axe-core), manual keyboard testing |
| Slow page load on mobile | Low | Small bundle (<50KB), inline critical CSS |

## Open Questions

None - all technical decisions resolved. Ready to proceed to Phase 1 (Design & Contracts).
