# LigaMX IA Analytics - Development Rules

## 1. Introduction

This document defines development rules, coding standards, workflows, and quality practices for LigaMX IA Analytics. It includes backend and frontend standards, Git workflow, commit conventions, branch strategy, naming conventions, testing strategy, code review, documentation, dependency management, architecture, security, performance, AI coding, Definition of Done, and Definition of Ready.

## 2. Development Principles

- Maintain production-ready code at all times.
- Favor explicit contracts and strong typing.
- Keep domain logic separate from infrastructure.
- Use automated tests to validate behavior.
- Document architecture and decisions.
- Never leave TODOs in production code.

## 3. Git Workflow

### 3.1 Branch Strategy

- `main`: production-ready code.
- `develop`: integration branch for the next release.
- `feature/*`: new features and enhancements.
- `bugfix/*`: production fixes.
- `hotfix/*`: urgent patches to `main`.
- `release/*`: release preparation and final validation.

### 3.2 Pull Request Process

- Create PRs from feature branches into `develop` or `main` as appropriate.
- Include summary, scopes, and testing notes.
- Link to relevant issues.
- Require at least one approving review.

### 3.3 Commit Conventions

Use Conventional Commits:
- `feat(scope): description`
- `fix(scope): description`
- `docs(scope): description`
- `refactor(scope): description`
- `test(scope): description`
- `chore(scope): description`

Examples:
- `feat(prediction): add Poisson score distribution endpoint`
- `fix(portfolio): enforce max risk percentage`
- `docs(api): update predictions schema examples`

## 4. Naming Conventions

### 4.1 Backend

- `snake_case` for variables and functions.
- `PascalCase` for classes and exceptions.
- `snake_case` for module and file names.
- Use domain terminology from `02_DOMAIN_MODEL.md`.

### 4.2 Frontend

- `camelCase` for variables and functions.
- `PascalCase` for components and types.
- Use `kebab-case` for filenames when required by framework conventions.
- Keep component names descriptive and reusable.

### 4.3 API and Database

- Use consistent resource names in plural form, e.g. `/predictions`.
- Use `snake_case` for database columns and JSON keys in the backend code.
- Keep API request/response schema names aligned with domain entities.

## 5. Backend Standards

### 5.1 Language and Framework

- Python 3.13.
- FastAPI for HTTP services.
- SQLAlchemy 2 for ORM.
- Pydantic v2 for schema validation.

### 5.2 Project Layout

- Domain, application, infrastructure, and interfaces are separate.
- Keep API routes lightweight and delegate logic to services.
- Use repository interfaces for persistence.

### 5.3 Dependency Injection

- Use DI frameworks or manual injection for services, repositories, and clients.
- Avoid hardcoded global dependencies.

### 5.4 Validation and Types

- Validate inputs at boundary layers with Pydantic models.
- Use strict types for money, percentages, and enums.
- Avoid `Any` and untyped code.

### 5.5 Error Handling

- Use custom exception types.
- Translate exceptions to HTTP responses in a single layer.
- Log errors with context but not stack traces to clients.

## 6. Frontend Standards

### 6.1 Language and Framework

- TypeScript with `strict` enabled.
- Next.js 15 for application framework.
- TailwindCSS and shadcn/ui for styling.

### 6.2 State Management

- Use Zustand for local and shared state.
- Use TanStack Query for server-side state.

### 6.3 Forms and Validation

- Use React Hook Form and Zod.
- Validate on submit and optionally on blur.
- Provide helpful error messages.

### 6.4 Component Design

- Keep components small and composable.
- Separate presentation and logic.
- Use typed props and avoid `any`.

### 6.5 Accessibility

- Ensure keyboard navigation.
- Use ARIA roles and labels.
- Meet WCAG AA contrast.

## 7. Testing Strategy

### 7.1 Unit Tests

- Cover domain services, business rules, and utility functions.
- Aim for 85% coverage in core domain areas.

### 7.2 Integration Tests

- Validate API routes and database interactions.
- Use test fixtures for realistic scenarios.

### 7.3 End-to-End Tests

- Cover critical user flows: predictions, portfolio management, model promotions, audits.
- Validate UI behavior for loading, success, and error states.

### 7.4 AI Tests

- Test feature transformations for reproducibility.
- Validate model inference outputs against known inputs.
- Use synthetic or snapshot tests for scoring functions.

### 7.5 CI Enforcement

- Run tests on every PR.
- Fail the pipeline on uncovered regressions.
- Use coverage thresholds for key modules.

## 8. Code Review Rules

- Review for architecture compliance and maintainability.
- Ensure changes include tests and documentation updates.
- Check for proper use of domain language.
- Verify no hardcoded secrets or TODOs are introduced.

## 9. Documentation Rules

- Keep `docs/` aligned with implementation.
- Update relevant documents when requirements change.
- Document API changes in `07_API_SPEC.md`.
- Include architecture rationale in `06_ARCHITECTURE.md`.

## 10. Dependency Rules

- Use approved dependencies only.
- Keep dependencies minimal and necessary.
- Review new dependencies for security and license compliance.
- Update dependencies regularly and track changes.

## 11. Architecture Rules

- Keep domain logic isolated from external systems.
- Use repository interfaces for persistence.
- Avoid using framework-specific code in domain entities.
- Apply CQRS for read-heavy analytics where beneficial.

## 12. Security Rules

- Validate all input data.
- Protect endpoints with authentication and authorization.
- Never log sensitive data.
- Protect secrets using environment and vault mechanisms.
- Use HTTPS in production.

## 13. Performance Rules

- Cache read-heavy responses using Redis.
- Optimize database queries with indexes.
- Avoid N+1 queries in persistence layers.
- Use asynchronous tasks for long-running jobs.

## 14. AI Coding Rules

- Separate feature engineering from model training.
- Use explicit random seeds for reproducibility.
- Version dataset snapshots and model artifacts.
- Store explanation metadata for production predictions.
- Keep ML experiments isolated from production inference.

## 15. Definition of Ready

A work item is ready when:
- requirements are clear and documented.
- acceptance criteria are defined.
- dependencies are identified.
- test cases are scoped.
- design or architecture concerns are reviewed.

## 16. Definition of Done

A work item is done when:
- code is implemented and reviewed.
- tests are added and passing.
- documentation is updated.
- linting and formatting pass.
- deployment artifacts are built successfully.
- acceptance criteria are met.

## 17. Release Process

- Use release branches for candidate releases.
- Tag releases with semantic versioning.
- Run full CI suite before merge to `main`.
- Deploy from tagged artifacts.

## 18. References

- `02_DOMAIN_MODEL.md`
- `03_BUSINESS_RULES.md`
- `04_AI_ENGINE.md`
- `05_DATABASE.md`
- `06_ARCHITECTURE.md`
- `07_API_SPEC.md`
- `08_UI_UX.md`
