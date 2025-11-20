# Quickstart Guide: Math Addition Calculator

**Feature**: 001-math-addition  
**Date**: November 19, 2025  
**Purpose**: Setup and run instructions for development and testing

## Prerequisites

- **Node.js**: Version 18.x or higher
- **npm**: Version 9.x or higher (comes with Node.js)
- **Git**: For version control
- **Modern Browser**: Chrome, Firefox, Safari, or Edge (last 2 versions)

**Verify Prerequisites**:
```bash
node --version    # Should be v18.x or higher
npm --version     # Should be 9.x or higher
git --version     # Any recent version
```

## Initial Setup

### 1. Navigate to Feature Directory

```bash
cd /Users/ducnguyenhuu/Documents/GitHub/DucNguyen_LearningSpace/duc-testing-loan
mkdir -p math-calculator
cd math-calculator
```

### 2. Initialize Project

```bash
# Initialize npm project
npm init -y

# Install Vite (build tool)
npm install --save-dev vite@^5.0.0

# Install testing dependencies
npm install --save-dev vitest@^1.0.0
npm install --save-dev @vitest/ui@^1.0.0
npm install --save-dev @playwright/test@^1.40.0
npm install --save-dev jsdom@^23.0.0

# Install linting dependencies
npm install --save-dev eslint@^8.0.0
npm install --save-dev eslint-config-standard@^17.0.0
npm install --save-dev eslint-plugin-import@^2.29.0
npm install --save-dev eslint-plugin-node@^11.1.0
npm install --save-dev eslint-plugin-promise@^6.1.0
```

### 3. Configure package.json Scripts

Add these scripts to `package.json`:

```json
{
  "name": "math-calculator",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix"
  }
}
```

## Project Structure

Create the following directory structure:

```bash
mkdir -p src/modules
mkdir -p src/constants
mkdir -p src/styles
mkdir -p tests/unit
mkdir -p tests/e2e
```

Your structure should look like:

```text
math-calculator/
├── index.html
├── package.json
├── vite.config.js
├── vitest.config.js
├── playwright.config.js
├── .eslintrc.json
├── src/
│   ├── main.js
│   ├── modules/
│   │   ├── calculator.js
│   │   ├── validator.js
│   │   └── ui.js
│   ├── constants/
│   │   └── config.js
│   └── styles/
│       ├── main.css
│       ├── calculator.css
│       └── responsive.css
├── tests/
│   ├── unit/
│   │   ├── calculator.test.js
│   │   ├── validator.test.js
│   │   └── ui.test.js
│   └── e2e/
│       └── calculator.spec.js
└── README.md
```

## Configuration Files

### vite.config.js

```javascript
import { defineConfig } from 'vite';

export default defineConfig({
  root: './',
  build: {
    outDir: 'dist',
    target: 'es2015',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        dead_code: true
      }
    },
    cssMinify: true,
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
  server: {
    port: 3000,
    open: true
  }
});
```

### vitest.config.js

```javascript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'tests/',
        '*.config.js'
      ],
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
});
```

### playwright.config.js

```javascript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### .eslintrc.json

```json
{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "extends": [
    "standard"
  ],
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "semi": ["error", "always"],
    "quotes": ["error", "single"],
    "max-len": ["warn", { "code": 100 }],
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
  }
}
```

## Development Workflow

### Start Development Server

```bash
npm run dev
```

This will:
- Start Vite dev server on http://localhost:3000
- Open browser automatically
- Enable hot module replacement (HMR)
- Watch for file changes

### Run Tests

**Unit Tests** (TDD - run continuously while developing):
```bash
npm run test        # Run tests in watch mode
npm run test:ui     # Run with visual UI
```

**Unit Tests with Coverage**:
```bash
npm run test:coverage
```

Coverage report will be generated in `coverage/` directory.

**E2E Tests**:
```bash
npm run test:e2e       # Run all E2E tests
npm run test:e2e:ui    # Run with Playwright UI
```

### Linting

```bash
npm run lint          # Check for linting errors
npm run lint:fix      # Auto-fix linting errors
```

### Build for Production

```bash
npm run build
```

Build artifacts will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

This serves the production build locally for testing.

## Development Guidelines

### Test-Driven Development (TDD)

**Constitution Requirement**: Write tests before implementation.

**Workflow**:
1. Write failing test
2. Run test (should fail - RED)
3. Implement minimal code to pass
4. Run test (should pass - GREEN)
5. Refactor code
6. Run test (should still pass)
7. Repeat

**Example**:
```bash
# Terminal 1: Keep tests running
npm run test

# Terminal 2: Write code
# 1. Write test in tests/unit/calculator.test.js
# 2. See it fail (RED)
# 3. Implement in src/modules/calculator.js
# 4. See it pass (GREEN)
# 5. Refactor if needed
```

### Code Quality Checklist

Before committing code, ensure:

- [ ] All tests pass (`npm run test`)
- [ ] 80%+ test coverage (`npm run test:coverage`)
- [ ] No linting errors (`npm run lint`)
- [ ] All functions have JSDoc comments
- [ ] No functions exceed 50 lines
- [ ] E2E tests pass for affected scenarios

### Git Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit with conventional commit message
git commit -m "feat: add calculator module with tests"

# Push to feature branch (if using branches)
git push origin 001-math-addition
```

**Conventional Commit Types**:
- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Adding or updating tests
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, no logic change)
- `refactor:` - Code refactoring

## Testing Guide

### Running Specific Tests

```bash
# Run specific test file
npm run test calculator.test.js

# Run tests matching pattern
npm run test --grep "addition"

# Run E2E tests for specific browser
npm run test:e2e --project=chromium
```

### Debugging Tests

**Unit Tests**:
```bash
# Run with debugger
npm run test -- --inspect-brk

# Then open chrome://inspect in Chrome
```

**E2E Tests**:
```bash
# Run in headed mode (see browser)
npm run test:e2e -- --headed

# Run in debug mode
npm run test:e2e -- --debug
```

### Coverage Thresholds

Constitution requires:
- Minimum 80% coverage overall
- 100% coverage for calculator module (critical business logic)

View coverage:
```bash
npm run test:coverage
open coverage/index.html  # View detailed report
```

## Accessibility Testing

### Manual Testing Checklist

- [ ] Tab through all interactive elements
- [ ] Verify focus visible styles
- [ ] Test with keyboard only (no mouse)
- [ ] Test with screen reader (VoiceOver on Mac, NVDA on Windows)
- [ ] Verify color contrast (use browser DevTools)
- [ ] Test on mobile device (real device or emulator)

### Screen Reader Testing

**Mac (VoiceOver)**:
```bash
# Enable VoiceOver
Cmd + F5

# Navigate: Control + Option + Arrow keys
```

**Windows (NVDA)**:
Download from: https://www.nvaccess.org/

### Automated Accessibility Testing

Add axe-core for automated a11y testing:

```bash
npm install --save-dev @axe-core/playwright
```

Include in E2E tests to catch accessibility issues automatically.

## Performance Testing

### Lighthouse

```bash
# Build production version
npm run build
npm run preview

# Run Lighthouse (in Chrome DevTools)
# Or use CLI:
npm install -g lighthouse
lighthouse http://localhost:4173 --view
```

**Performance Targets** (from constitution):
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Performance score: >90
- Accessibility score: 100
- Best Practices score: >90

### Bundle Size Analysis

Check bundle size:
```bash
npm run build

# Check gzipped size
du -sh dist/*.js
```

Should be <50KB gzipped.

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill
```

### Tests Failing

1. Ensure all dependencies installed: `npm install`
2. Clear cache: `rm -rf node_modules/.vite`
3. Restart dev server: `npm run dev`
4. Check browser console for errors

### Linting Errors

```bash
# Auto-fix most issues
npm run lint:fix

# If errors persist, check .eslintrc.json configuration
```

## Next Steps

After setup is complete:

1. **Read the contracts**: Review `contracts/ui-contract.md`
2. **Understand data model**: Review `data-model.md`
3. **Start with tests**: Write first test in `tests/unit/calculator.test.js`
4. **Follow TDD**: Red → Green → Refactor
5. **Run `/speckit.tasks`**: Generate implementation task list

## Additional Resources

- [Vite Documentation](https://vitejs.dev/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [ESLint Rules](https://eslint.org/docs/rules/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## Support

For questions or issues:
1. Check this quickstart guide
2. Review technical plan: `plan.md`
3. Review specification: `spec.md`
4. Check constitution: `.specify/memory/constitution.md`
