# DucTesting Loan Constitution

## Core Principles

### I. Code Quality & Maintainability (NON-NEGOTIABLE)
**Clean Code Standards**
- Write self-documenting code with clear, descriptive names for variables, functions, and classes
- Keep functions focused on single responsibilities (SRP)
- Maximum function length: 50 lines; maximum class length: 300 lines
- No magic numbers or hardcoded values - use named constants or configuration
- Code must pass linting (pylint/flake8 for Python, ESLint for JavaScript) with minimum score of 8/10

**Documentation Requirements**
- Every public function/method must have docstrings explaining purpose, parameters, return values, and exceptions
- Complex algorithms require inline comments explaining the "why", not just the "what"
- README files required for each module/package explaining architecture, setup, and usage
- API endpoints must be documented with request/response schemas
- Architecture Decision Records (ADRs) required for significant design choices

**Modularity & Reusability**
- Prefer composition over inheritance
- Create standalone, reusable components/modules with clear interfaces
- Avoid circular dependencies - enforce unidirectional data flow
- External dependencies must be abstracted behind interfaces for testability
- Configuration must be externalized (environment variables, config files)

### II. Testing Standards (NON-NEGOTIABLE)
**Test-First Development**
- Write tests before implementation (TDD methodology)
- Red-Green-Refactor cycle: Test fails → Implement → Test passes → Refactor
- No code merge without corresponding tests

**Test Coverage Requirements**
- Minimum 80% code coverage for all modules
- 100% coverage required for critical business logic (risk assessment, calculations, compliance)
- Unit tests must cover: happy paths, edge cases, error conditions, boundary values
- Integration tests required for: external service interactions, database operations, API contracts

**Test Organization**
- Unit tests: Fast (<100ms each), isolated, no external dependencies
- Integration tests: Test component interactions, may use test databases/mock services
- End-to-end tests: Cover critical user workflows from UI to database
- Test files mirror source structure: `src/module.py` → `tests/test_module.py`

**Test Quality**
- Tests must be deterministic (no flakiness)
- Clear test names following pattern: `test_<method>_<scenario>_<expected_result>`
- Use arrange-act-assert pattern
- Mock external dependencies appropriately
- Tests serve as living documentation

### III. User Experience Consistency
**Design System Adherence**
- Maintain consistent color palette, typography, spacing, and component styles
- Follow accessibility standards (WCAG 2.1 Level AA minimum)
  - All interactive elements keyboard-navigable
  - Proper ARIA labels and roles
  - Color contrast ratio minimum 4.5:1 for text
  - Screen reader compatible

**Responsive Design**
- Mobile-first approach
- Breakpoints: Mobile (<768px), Tablet (768-1024px), Desktop (>1024px)
- Touch targets minimum 44×44px for mobile
- Fluid layouts using relative units (rem, em, %, vw/vh)

**User Feedback**
- Loading states for operations >500ms
- Success/error messages for all user actions
- Form validation with clear error messages
- Confirmation dialogs for destructive actions
- Progressive disclosure for complex workflows

**Usability Standards**
- Maximum 3-click rule for primary actions
- Clear visual hierarchy and information architecture
- Consistent navigation patterns across all pages
- Error messages must be actionable (explain what happened and how to fix)

### IV. Performance Requirements
**Response Time Targets**
- Page load time: <2 seconds on 3G connection
- API response time: <500ms for GET requests, <1s for POST/PUT
- Time to Interactive (TTI): <3 seconds
- First Contentful Paint (FCP): <1.5 seconds

**Resource Optimization**
- Image optimization: WebP format preferred, lazy loading for below-fold images
- Code splitting: Maximum initial bundle size 200KB (gzipped)
- Database queries: Use indexes, avoid N+1 queries, query time <100ms
- Caching: Implement HTTP caching headers, Redis for session/frequently accessed data

**Scalability Targets**
- Support 1000 concurrent users without degradation
- Horizontal scaling capability (stateless services)
- Database connection pooling with configurable limits
- Rate limiting on public APIs (100 requests/minute per user)

**Monitoring Requirements**
- Performance metrics tracked: response times, error rates, throughput
- Alerts for: error rate >1%, response time >2s, CPU >80%, memory >85%
- Application Performance Monitoring (APM) integrated
- Database query performance tracking

### V. Security & Compliance
**Data Protection**
- Encrypt sensitive data at rest (AES-256) and in transit (TLS 1.3)
- PII must be masked in logs and non-production environments
- Password requirements: min 12 chars, complexity rules, bcrypt hashing
- API authentication required: JWT tokens with 15-minute expiry

**Input Validation**
- Validate all user inputs on both client and server
- Sanitize inputs to prevent XSS, SQL injection, command injection
- Implement CSRF protection for state-changing operations
- File upload restrictions: type validation, size limits, virus scanning

**Audit & Logging**
- Log all authentication attempts, authorization failures, data access
- Structured logging with correlation IDs for request tracing
- Log retention: 90 days for application logs, 1 year for audit logs
- Never log passwords, tokens, or credit card numbers

## Development Workflow

**Version Control**
- Feature branch workflow: `feature/<ticket-id>-<description>`
- Commit messages: Follow Conventional Commits (feat:, fix:, docs:, etc.)
- No direct commits to main/production branches
- Squash commits before merging to keep history clean

**Code Review Process**
- All code requires peer review before merge
- Review checklist:
  - Tests pass and coverage maintained
  - Code follows style guide and principles
  - No security vulnerabilities introduced
  - Documentation updated
  - Breaking changes documented
- Maximum 48-hour review turnaround

**Continuous Integration**
- CI pipeline runs on every PR:
  1. Linting checks
  2. Unit tests
  3. Integration tests
  4. Security scanning
  5. Build verification
- All checks must pass (green) before merge allowed

**Deployment Gates**
- Staging deployment required before production
- Smoke tests pass in staging
- Performance tests meet benchmarks
- Security scan passes
- Manual approval for production deployments

## Governance

**Authority & Amendments**
- This constitution supersedes individual team preferences or ad-hoc decisions
- Principle violations require justification and architectural review approval
- Amendments require: written proposal, team consensus, migration plan for existing code
- Constitution review every 6 months

**Enforcement**
- All PRs must verify compliance with these principles
- Automated checks where possible (linting, test coverage, security scans)
- Tech debt from principle violations must be tracked and prioritized
- Zero tolerance for security and testing principle violations

**Exception Process**
- Exceptions require: documented business justification, risk assessment, remediation plan
- Temporary exceptions (<30 days) approved by tech lead
- Permanent exceptions require architecture review board approval
- All exceptions tracked in ADRs

**Living Document**
- Refer to `.specify/memory/constitution.md` as source of truth
- Runtime guidance documents must align with constitution principles
- Team retrospectives include constitution effectiveness review

**Version**: 1.0.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19
