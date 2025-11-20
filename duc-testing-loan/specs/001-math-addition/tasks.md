# Tasks: Math Addition Calculator

**Input**: Design documents from `/specs/001-math-addition/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-contract.md

**Tests**: Test tasks are included as this project follows TDD methodology (constitution requirement).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure with math-calculator/ as feature directory:
- Source: `math-calculator/src/`
- Tests: `math-calculator/tests/`
- Config: `math-calculator/*.config.js`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create math-calculator directory structure (src/, src/modules/, src/constants/, src/styles/, tests/unit/, tests/e2e/)
- [ ] T002 Initialize npm project in math-calculator/ with package.json
- [ ] T003 [P] Install Vite 5.x, Vitest, and development dependencies per quickstart.md
- [ ] T004 [P] Install Playwright and E2E testing dependencies
- [ ] T005 [P] Install ESLint and linting dependencies
- [ ] T006 Create vite.config.js with build optimization settings
- [ ] T007 Create vitest.config.js with coverage thresholds (80% overall, 100% for calculator)
- [ ] T008 Create playwright.config.js with cross-browser and mobile device configurations
- [ ] T009 Create .eslintrc.json with constitution-compliant rules (score 8/10 minimum)
- [ ] T010 Create math-calculator/README.md with project overview and development instructions
- [ ] T011 Create .gitignore for node_modules/, dist/, coverage/

**Checkpoint**: Project structure ready, all tools configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T012 Create math-calculator/index.html with semantic HTML structure and accessibility attributes per contracts
- [ ] T013 Create src/constants/config.js with ERROR_MESSAGES, VALIDATION_CONFIG, and DISPLAY_CONFIG constants
- [ ] T014 [P] Create src/styles/main.css with CSS reset, CSS custom properties (variables), and base typography
- [ ] T015 [P] Create src/styles/calculator.css with calculator component styles and focus indicators
- [ ] T016 [P] Create src/styles/responsive.css with mobile-first media queries (768px, 1024px breakpoints)
- [ ] T017 Create src/main.js as application entry point with module imports and initialization

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Two-Number Addition (Priority: P1) 🎯 MVP

**Goal**: Users can enter two numbers and see their sum displayed immediately

**Independent Test**: Enter "5" and "3", click Calculate, verify "8" displays. This is the core calculator functionality.

### Tests for User Story 1 (Write FIRST, ensure they FAIL)

> **TDD REQUIREMENT**: Write these tests FIRST, ensure they FAIL before implementation

- [ ] T018 [P] [US1] Create tests/unit/calculator.test.js with test suite structure and imports
- [ ] T019 [US1] Write test: add(5, 3) should return 8 in tests/unit/calculator.test.js
- [ ] T020 [US1] Write test: add(0, 0) should return 0 in tests/unit/calculator.test.js
- [ ] T021 [US1] Write test: add(-10, 5) should return -5 in tests/unit/calculator.test.js
- [ ] T022 [US1] Write test: add(2.5, 3.7) should return 6.2 in tests/unit/calculator.test.js
- [ ] T023 [US1] Write test: add(0.1, 0.2) should return 0.3 (floating-point precision) in tests/unit/calculator.test.js
- [ ] T024 [US1] Write test: add with large numbers within safe integer range in tests/unit/calculator.test.js
- [ ] T025 [US1] Write test: add should throw TypeError for non-number inputs in tests/unit/calculator.test.js
- [ ] T026 [US1] Write test: add should throw RangeError for Infinity/-Infinity/NaN in tests/unit/calculator.test.js
- [ ] T027 [US1] Run tests and verify they FAIL (no implementation yet) with npm run test

### Implementation for User Story 1

- [ ] T028 [US1] Implement add(num1, num2) function in src/modules/calculator.js with type checking
- [ ] T029 [US1] Add floating-point precision handling (round to 10 decimals) in src/modules/calculator.js
- [ ] T030 [US1] Add error handling for invalid inputs (TypeError, RangeError) in src/modules/calculator.js
- [ ] T031 [US1] Add JSDoc comments to calculator module functions per constitution requirements
- [ ] T032 [US1] Run tests and verify they PASS with npm run test
- [ ] T033 [US1] Verify 100% code coverage for calculator.js with npm run test:coverage (constitution requirement)
- [ ] T034 [P] [US1] Create tests/unit/ui.test.js for UI module with JSDOM setup
- [ ] T035 [US1] Write test: displayResult should update DOM with calculation result in tests/unit/ui.test.js
- [ ] T036 [US1] Write test: displayResult should update ARIA live region in tests/unit/ui.test.js
- [ ] T037 [US1] Create src/modules/ui.js with initializeUI() function
- [ ] T038 [US1] Implement displayResult(result) function in src/modules/ui.js with DOM updates
- [ ] T039 [US1] Implement handleCalculateClick() event handler in src/modules/ui.js
- [ ] T040 [US1] Add keyboard support (Enter key triggers calculation) in src/modules/ui.js
- [ ] T041 [US1] Add ARIA live region updates for screen readers in src/modules/ui.js
- [ ] T042 [US1] Add JSDoc comments to UI module functions per constitution requirements
- [ ] T043 [US1] Run UI tests and verify they PASS with npm run test
- [ ] T044 [US1] Create tests/e2e/calculator.spec.js with Playwright test setup
- [ ] T045 [US1] Write E2E test: User enters 5 and 3, clicks Calculate, sees 8 in tests/e2e/calculator.spec.js
- [ ] T046 [US1] Write E2E test: User enters 0 and 0, clicks Calculate, sees 0 in tests/e2e/calculator.spec.js
- [ ] T047 [US1] Write E2E test: User enters -10 and 5, clicks Calculate, sees -5 in tests/e2e/calculator.spec.js
- [ ] T048 [US1] Write E2E test: User enters 2.5 and 3.7, clicks Calculate, sees 6.2 in tests/e2e/calculator.spec.js
- [ ] T049 [US1] Run E2E tests in Chrome, Firefox, Safari with npm run test:e2e
- [ ] T050 [US1] Update src/main.js to initialize calculator UI on page load

**Checkpoint**: At this point, User Story 1 (basic addition) should be fully functional and testable independently. This is the MVP!

---

## Phase 4: User Story 2 - Input Validation and Error Handling (Priority: P2)

**Goal**: Users receive clear, actionable error messages for invalid inputs

**Independent Test**: Enter "abc" in first field, click Calculate, verify error message "Please enter valid numbers" displays

### Tests for User Story 2 (Write FIRST, ensure they FAIL)

> **TDD REQUIREMENT**: Write these tests FIRST, ensure they FAIL before implementation

- [ ] T051 [P] [US2] Create tests/unit/validator.test.js with test suite structure
- [ ] T052 [US2] Write test: validateNumberInput("42") should return valid NumberInput in tests/unit/validator.test.js
- [ ] T053 [US2] Write test: validateNumberInput("") should return error "Please enter both numbers" in tests/unit/validator.test.js
- [ ] T054 [US2] Write test: validateNumberInput("abc") should return error "Please enter valid numbers" in tests/unit/validator.test.js
- [ ] T055 [US2] Write test: validateNumberInput with 16+ digit number should return "Number is too large" in tests/unit/validator.test.js
- [ ] T056 [US2] Write test: validateNumberInput("-5.5") should return valid negative decimal in tests/unit/validator.test.js
- [ ] T057 [US2] Write test: validateCalculationRequest with two valid inputs should return canCalculate: true in tests/unit/validator.test.js
- [ ] T058 [US2] Write test: validateCalculationRequest with invalid input should return canCalculate: false in tests/unit/validator.test.js
- [ ] T059 [US2] Run validator tests and verify they FAIL with npm run test

### Implementation for User Story 2

- [ ] T060 [US2] Create src/modules/validator.js with validateNumberInput(value) function
- [ ] T061 [US2] Implement empty field validation in validator.js
- [ ] T062 [US2] Implement non-numeric input validation using parseFloat and isNaN in validator.js
- [ ] T063 [US2] Implement length validation (max 15 characters) in validator.js
- [ ] T064 [US2] Implement validateCalculationRequest(input1, input2) function in validator.js
- [ ] T065 [US2] Add JSDoc comments with @typedef for NumberInput and ValidationError types in validator.js
- [ ] T066 [US2] Run validator tests and verify they PASS with npm run test
- [ ] T067 [US2] Write UI test: displayError should show error message in DOM in tests/unit/ui.test.js
- [ ] T068 [US2] Write UI test: displayError should update ARIA live region (assertive) in tests/unit/ui.test.js
- [ ] T069 [US2] Write UI test: displayError should clear result display in tests/unit/ui.test.js
- [ ] T070 [US2] Implement displayError(error) function in src/modules/ui.js
- [ ] T071 [US2] Update handleCalculateClick() to validate inputs before calculation in src/modules/ui.js
- [ ] T072 [US2] Add error styling classes (.error, .error-message) to show/hide errors in src/modules/ui.js
- [ ] T073 [US2] Run UI tests with validation and verify they PASS with npm run test
- [ ] T074 [US2] Write E2E test: Empty fields show "Please enter both numbers" in tests/e2e/calculator.spec.js
- [ ] T075 [US2] Write E2E test: "abc" in first field shows "Please enter valid numbers" in tests/e2e/calculator.spec.js
- [ ] T076 [US2] Write E2E test: One empty field shows "Please enter both numbers" in tests/e2e/calculator.spec.js
- [ ] T077 [US2] Run E2E validation tests across browsers with npm run test:e2e
- [ ] T078 [US2] Verify overall test coverage remains above 80% with npm run test:coverage

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Calculator handles errors gracefully.

---

## Phase 5: User Story 3 - Clear and Reset Functionality (Priority: P3)

**Goal**: Users can quickly clear all inputs and results to start fresh

**Independent Test**: Enter numbers, calculate result, click Clear, verify all fields are empty

### Tests for User Story 3 (Write FIRST, ensure they FAIL)

> **TDD REQUIREMENT**: Write these tests FIRST, ensure they FAIL before implementation

- [ ] T079 [US3] Write UI test: clearUI() should clear input values in tests/unit/ui.test.js
- [ ] T080 [US3] Write UI test: clearUI() should clear result display in tests/unit/ui.test.js
- [ ] T081 [US3] Write UI test: clearUI() should clear error messages in tests/unit/ui.test.js
- [ ] T082 [US3] Write UI test: clearUI() should reset focus to first input in tests/unit/ui.test.js
- [ ] T083 [US3] Run UI tests and verify clear tests FAIL with npm run test

### Implementation for User Story 3

- [ ] T084 [US3] Implement clearUI() function in src/modules/ui.js
- [ ] T085 [US3] Implement handleClearClick() event handler in src/modules/ui.js
- [ ] T086 [US3] Add Clear button event listener in initializeUI() in src/modules/ui.js
- [ ] T087 [US3] Add focus management to return to first input after clear in src/modules/ui.js
- [ ] T088 [US3] Add JSDoc comments for new clear functions in src/modules/ui.js
- [ ] T089 [US3] Run UI tests and verify clear tests PASS with npm run test
- [ ] T090 [US3] Write E2E test: Clear button clears inputs and results in tests/e2e/calculator.spec.js
- [ ] T091 [US3] Write E2E test: Clear button clears error messages in tests/e2e/calculator.spec.js
- [ ] T092 [US3] Run E2E clear tests across browsers with npm run test:e2e

**Checkpoint**: All user stories should now be independently functional. Calculator is feature-complete!

---

## Phase 6: Accessibility & Cross-Browser Testing

**Purpose**: Ensure WCAG 2.1 Level AA compliance and cross-browser compatibility

- [ ] T093 [P] Test keyboard navigation (Tab, Enter) across all interactive elements
- [ ] T094 [P] Test with screen reader (VoiceOver on Mac, NVDA on Windows) and verify announcements
- [ ] T095 [P] Verify color contrast ratios meet 4.5:1 minimum using browser DevTools
- [ ] T096 [P] Test focus visible indicators meet 3:1 contrast on all browsers
- [ ] T097 [P] Run E2E tests on mobile viewports (Pixel 5, iPhone 12) with npm run test:e2e
- [ ] T098 Verify all ARIA attributes are correctly implemented per contracts/ui-contract.md
- [ ] T099 Test rapid button clicks and verify no double calculations occur
- [ ] T100 Test keyboard shortcut (Escape to clear) if implemented
- [ ] T101 Verify touch targets are minimum 44×44px on mobile viewports
- [ ] T102 Test with browser zoom at 200% and verify layout remains usable

**Checkpoint**: Accessibility requirements met, all browsers/devices tested

---

## Phase 7: Performance Optimization & Polish

**Purpose**: Meet performance targets and finalize production build

- [ ] T103 Run production build with npm run build
- [ ] T104 Verify bundle size is <50KB gzipped using du -sh dist/*.js
- [ ] T105 Run Lighthouse audit and verify scores: Performance >90, Accessibility 100, Best Practices >90
- [ ] T106 Verify First Contentful Paint <1.5s and Time to Interactive <3s in Lighthouse
- [ ] T107 [P] Optimize CSS: Remove unused styles, inline critical CSS in <head>
- [ ] T108 [P] Add HTML meta tags for viewport, description, and mobile optimization
- [ ] T109 Test calculation performance with edge cases (very large numbers, many decimals)
- [ ] T110 Verify error handling for edge cases: copy-paste numbers, thousands separators
- [ ] T111 Run linting and verify score 8/10+ with npm run lint
- [ ] T112 Fix any remaining linting errors or warnings
- [ ] T113 Run full test suite and verify 100% pass rate with npm test
- [ ] T114 Verify final coverage: 80%+ overall, 100% for calculator.js with npm run test:coverage
- [ ] T115 Update README.md with usage instructions, features, and screenshots
- [ ] T116 Add JSDoc documentation for all public functions (verify constitution compliance)
- [ ] T117 Test production preview with npm run preview
- [ ] T118 Perform final cross-browser smoke test on production build

**Checkpoint**: Production-ready build, all quality gates passed

---

## Phase 8: Documentation & Deployment Prep

**Purpose**: Final documentation and deployment readiness

- [ ] T119 [P] Create or update math-calculator/README.md with complete feature documentation
- [ ] T120 [P] Document all environment variables and configuration in README.md
- [ ] T121 [P] Create deployment guide with build and hosting instructions
- [ ] T122 Verify quickstart.md instructions are accurate by following them from scratch
- [ ] T123 Add troubleshooting section to README.md for common issues
- [ ] T124 Create CHANGELOG.md documenting this feature release
- [ ] T125 Verify all acceptance scenarios from spec.md are passing
- [ ] T126 Create demo video or screenshots for documentation
- [ ] T127 Final constitution compliance check against all principles
- [ ] T128 Tag release version in git (e.g., v1.0.0-math-calculator)

**Checkpoint**: Documentation complete, ready for deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Integrates with US1 but independently testable
  - User Story 3 (P3): Can start after Foundational - Uses US1 & US2 components but independently testable
- **Accessibility (Phase 6)**: Depends on all user stories being complete
- **Performance (Phase 7)**: Depends on Phase 6 completion
- **Documentation (Phase 8)**: Depends on Phase 7 completion

### User Story Dependencies

- **User Story 1 (P1)**: ✅ Independent - Core calculator functionality, no dependencies
- **User Story 2 (P2)**: 🔗 Integrates with US1 - Adds validation to US1's calculation flow
- **User Story 3 (P3)**: 🔗 Integrates with US1 & US2 - Clears state from both previous stories

**Note**: While US2 and US3 integrate with US1, each should still be independently testable. US2 validates inputs before calculation. US3 resets state after calculation/validation.

### Within Each User Story (TDD Workflow)

1. **Tests FIRST** (marked with "Write FIRST, ensure they FAIL")
   - Write all test cases for the story
   - Run tests and verify they FAIL (no implementation yet)
   
2. **Implementation** (after tests fail)
   - Implement just enough code to pass tests
   - Run tests frequently during implementation
   - Refactor when tests pass
   
3. **Integration** (after tests pass)
   - Connect components within the story
   - Run E2E tests for the story
   - Verify story is independently functional

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T003, T004, T005 can run in parallel (different dependency installs)

**Phase 2 (Foundational)**: Tasks T014, T015, T016 can run in parallel (different CSS files)

**User Story 1 Tests**: Tasks T018-T026 can run in parallel (writing different test cases in same file)

**User Story 1 UI**: Task T034 can run in parallel with calculator implementation (different files)

**User Story 2 Tests**: Tasks T051-T058 can run in parallel (writing different validator tests)

**Phase 6 (Accessibility)**: Tasks T093-T097, T100-T102 can run in parallel (independent testing activities)

**Phase 7 (Performance)**: Tasks T107, T108 can run in parallel (different optimizations)

**Phase 8 (Documentation)**: Tasks T119, T120, T121 can run in parallel (different documentation files)

---

## Parallel Example: User Story 1 Implementation

```bash
# After tests are written and failing, launch implementation tasks together:

# Parallel Group 1: Core logic implementation
Task T028: "Implement add() function in src/modules/calculator.js"
Task T034: "Create UI test file tests/unit/ui.test.js" (different file)

# Sequential: Complete calculator.js (T028-T033), then move to UI

# Parallel Group 2: E2E tests (after implementation)
Task T045: "E2E test: 5+3=8"
Task T046: "E2E test: 0+0=0"  
Task T047: "E2E test: -10+5=-5"
Task T048: "E2E test: 2.5+3.7=6.2"
# All in same file but can be written simultaneously
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - RECOMMENDED

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T017) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T018-T050)
4. **STOP and VALIDATE**: 
   - Run all tests: `npm test`
   - Run E2E tests: `npm run test:e2e`
   - Verify 100% calculator coverage
   - Manual test in browser
5. **MVP READY**: You now have a working calculator!
6. Decide if you want to add US2 (validation) and US3 (clear)

### Incremental Delivery (Recommended for Learning)

1. Complete Setup + Foundational (T001-T017) → Foundation ready ✅
2. Add User Story 1 (T018-T050) → Test independently → **MVP DEPLOYED** 🎯
3. Add User Story 2 (T051-T078) → Test independently → Better UX with validation 🎯
4. Add User Story 3 (T079-T092) → Test independently → Complete feature set 🎯
5. Polish (T093-T128) → Production ready 🚀

Each increment adds value without breaking previous functionality!

### Parallel Team Strategy

With 2-3 developers:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2)
2. **Once Foundational done**:
   - Developer A: User Story 1 (T018-T050)
   - Developer B: User Story 2 (T051-T078) - Can start after US1 tests defined
   - Developer C: User Story 3 (T079-T092) - Can start after US1 & US2 tests defined
3. **Integration**: Quick integration testing since stories designed to be independent
4. **Together**: Accessibility, Performance, Documentation (T093-T128)

---

## Notes

- **TDD Workflow**: All test tasks MUST be completed and verified to FAIL before implementation tasks
- **Constitution Compliance**: 
  - 100% coverage required for calculator.js (critical business logic)
  - 80%+ coverage required overall
  - All functions must have JSDoc comments
  - ESLint score minimum 8/10
  - Functions maximum 50 lines
- **[P] tasks**: Different files, no dependencies, can run in parallel
- **[Story] labels**: Map tasks to user stories for independent delivery
- **File paths**: All paths are absolute from repository root
- **Checkpoints**: Stop and validate after each user story phase
- **Coverage gates**: Run `npm run test:coverage` after each story to verify thresholds
- **Commit strategy**: Commit after each phase or logical group of tasks
- **Test-first**: Never implement before tests are written and failing
- **Independent stories**: Each story should be deployable without the others (MVP = US1 only)

---

## Total Task Count: 128 tasks

**Breakdown by Phase**:
- Phase 1 (Setup): 11 tasks
- Phase 2 (Foundational): 6 tasks (BLOCKS all stories)
- Phase 3 (User Story 1 - P1): 33 tasks ← **MVP SCOPE**
- Phase 4 (User Story 2 - P2): 28 tasks
- Phase 5 (User Story 3 - P3): 14 tasks
- Phase 6 (Accessibility): 10 tasks
- Phase 7 (Performance): 16 tasks
- Phase 8 (Documentation): 10 tasks

**Parallel Opportunities**: 24+ tasks can run in parallel (marked with [P])

**Independent Test Criteria**:
- **US1**: Enter two numbers, click Calculate, see result
- **US2**: Enter invalid input, see error message
- **US3**: Click Clear, all fields reset

**Suggested MVP**: Complete through Phase 3 (T001-T050) for working calculator = 50 tasks
