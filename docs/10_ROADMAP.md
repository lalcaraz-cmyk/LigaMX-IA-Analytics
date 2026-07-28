# LigaMX IA Analytics - Roadmap

## 1. Introduction

This roadmap defines the development plan for LigaMX IA Analytics through Version 1.0. It breaks work into multiple sprints with objectives, deliverables, acceptance criteria, estimated durations, dependencies, and risk mitigation.

## 2. Roadmap Overview

The roadmap is divided into six sprints: Foundation, Prediction Baseline, Portfolio and Risk, Governance and Audit, Production Hardening, and Launch Readiness.

## 3. Sprint 0: Foundation and Discovery

### Objectives
- Establish the architecture, domain model, and database design.
- Configure development environments with Docker Compose.
- Confirm initial product scope and success criteria.

### Deliverables
- `00_PROJECT_CHARTER.md`, `01_MASTER_PRD.md`, `02_DOMAIN_MODEL.md`, `03_BUSINESS_RULES.md`.
- `05_DATABASE.md` with schema design and migration strategy.
- Local Docker Compose environment and baseline repo structure.
- Basic FastAPI backend scaffold and Next.js frontend shell.

### Acceptance Criteria
- Documentation is published and reviewed.
- Local environment boots with backend, frontend, PostgreSQL, and Redis.
- Health endpoint returns 200 from backend.
- Basic repository structure matches `06_ARCHITECTURE.md`.

### Estimated Duration
- 2 weeks

### Dependencies
- Stakeholder alignment on product scope.
- Access to initial Liga MX data samples.
- Infrastructure requirements for local development.

### Risks
- Ambiguous requirements delaying architecture decisions.
- Data mismatches with early schema design.

### Mitigation
- Hold architecture review sessions.
- Use schema iterations with backward-compatible migrations.

## 4. Sprint 1: Prediction and Model Baseline

### Objectives
- Build the core prediction engine.
- Implement baseline statistical and ML models.
- Deliver prediction API and UI components.

### Deliverables
- Prediction domain service.
- Score distribution models using Poisson, bivariate Poisson, and Dixon-Coles.
- `/predictions` endpoint and backend logic.
- Prediction detail page with probability and score charts.
- Backtest pipeline scaffolding.

### Acceptance Criteria
- Backend returns valid predictions for sample matches.
- Predictions include normalized probability vectors and expected goals.
- UI displays prediction details and model outputs.
- Core AI pipeline is versioned and reproducible.

### Estimated Duration
- 4 weeks

### Dependencies
- Historical match data and market odds.
- AI team availability for model development.
- Database schema implementation.

### Risks
- Model calibration issues impacting trust.
- Integration challenges between AI output and API schema.

### Mitigation
- Use baseline analytic models first.
- Validate outputs with domain experts.

## 5. Sprint 2: Portfolio and Risk Management

### Objectives
- Implement portfolio accounting and bet lifecycle.
- Add Kelly stake recommendations and risk controls.
- Build portfolio UI and bet management workflows.

### Deliverables
- Portfolio and Bet entities with validation rules.
- EV and Kelly calculation services.
- Portfolio API endpoints and summary pages.
- Risk limit enforcement and exposure tracking.

### Acceptance Criteria
- Users can create portfolios and place proposed bets.
- The system rejects bets that violate risk rules.
- UI displays portfolio balances, exposure, and active bets.
- Settlement updates portfolio balance and PnL.

### Estimated Duration
- 4 weeks

### Dependencies
- Prediction outputs available for EV calculations.
- Portfolio domain model definition.
- Frontend state management for portfolio workflows.

### Risks
- Risk rules complexity causing false rejections.
- Portfolio balance reconciliation errors.

### Mitigation
- Validate rules with sample cases.
- Add integration tests for portfolio operations.

## 6. Sprint 3: Governance, Audit, and Model Registry

### Objectives
- Enable model version management and governance.
- Implement immutable audit logging.
- Provide governance UI and audit search.

### Deliverables
- Model registry service and endpoints.
- AuditRecord persistence and query API.
- Model promotion workflow.
- Audit and model governance dashboards.

### Acceptance Criteria
- Model versions can be created, promoted, and retired.
- Every prediction and portfolio action creates an audit record.
- Audit search supports filtering by entity type, action, and user.
- Governance UI presents version history and review actions.

### Estimated Duration
- 3 weeks

### Dependencies
- Database schema for model versions and audit records.
- Backend audit service.
- Role-based authorization.

### Risks
- Audit performance degradation with large volumes.
- Governance workflow ambiguity.

### Mitigation
- Use partitioning and indexing for audit tables.
- Document approval flows clearly.

## 7. Sprint 4: Production Hardening and Observability

### Objectives
- Harden security, observability, and deployment.
- Ensure API and UI meet production reliability standards.

### Deliverables
- TLS, authentication, and authorization hardening.
- Structured logging, monitoring dashboards, and alerts.
- CI/CD pipeline for tests, builds, and deployments.
- Performance tuning and load validation.

### Acceptance Criteria
- Production-like deployment passes health checks.
- Monitoring captures API, Celery, Redis, and database metrics.
- Alerts trigger on defined failure conditions.
- CI pipeline runs linting, tests, and image builds automatically.

### Estimated Duration
- 4 weeks

### Dependencies
- Infrastructure for monitoring and logging.
- CI/CD platform access.

### Risks
- Infrastructure configuration mismatches.
- Hidden performance bottlenecks.

### Mitigation
- Use staging environment for validation.
- Monitor early and iterate quickly.

## 8. Sprint 5: Launch Readiness and Version 1.0

### Objectives
- Complete end-to-end validation for Version 1.0.
- Finalize documentation and operational readiness.

### Deliverables
- Full end-to-end tests for predictions, portfolios, and audits.
- User acceptance testing and feedback incorporation.
- Release notes and runbooks.
- Version 1.0 production deployment.

### Acceptance Criteria
- All core flows validated by stakeholders.
- Release candidate passes performance and security checks.
- Documentation is complete and aligned.
- Production rollout plan is ready.

### Estimated Duration
- 3 weeks

### Dependencies
- Completion of earlier sprints.
- Stakeholder availability for validation.

### Risks
- Last-minute defect discovery.
- Deployment regression.

### Mitigation
- Allocate buffer for stabilization.
- Use feature toggles and rollback plans.

## 9. Sprint 6: Post-Launch Stabilization
This roadmap covers Version 1.0 delivery and immediate post-launch stabilization.

### Objectives
- Monitor production performance.
- Fix critical bugs and refine operational workflows.
- Prepare the first incremental release.

### Deliverables
- Production incident response readiness.
- Minor improvements to dashboard UX and model observability.
- Backlog for Version 1.1 prioritization.

### Acceptance Criteria
- No critical production incidents remain open.
- Monitoring validates stable performance.
- Team has identified enhancements for next release.

### Estimated Duration
- 2 weeks

### Dependencies
- Production deployment of Version 1.0.
- Operational monitoring.

### Risks
- Post-launch issues requiring urgent fixes.
- Prioritization drift.

### Mitigation
- Maintain a dedicated stabilization team.
- Use clear severity triage.

## 10. Roadmap Milestones

| Milestone | Sprint | Outcome |
|---|---|---|
| Foundation complete | Sprint 0 | Architecture and environment established |
| Prediction MVP | Sprint 1 | Predictions and score distributions live |
| Portfolio MVP | Sprint 2 | Bets and risk controls live |
| Governance MVP | Sprint 3 | Model registry and audit live |
| Production hardened | Sprint 4 | Secure deployable platform |
| Version 1.0 launch | Sprint 5 | Release candidate deployed |
| Stabilization | Sprint 6 | Post-launch improvements |

## 11. Dependencies

- Trusted Liga MX match and odds data.
- PostgreSQL and Redis infrastructure.
- CI/CD and monitoring environments.
- AI team capacity for model development.
- UX team support for frontend workflows.

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Data quality issues | High | Validate ingest and build data checks |
| Model drift | Medium | Monitor calibration and retain rollback options |
| Infrastructure failures | High | Use staging and automated recovery |
| Scope creep | Medium | Enforce sprint goals and acceptance criteria |

## 13. Governance

- Review roadmap every sprint.
- Adjust based on stakeholder feedback.
- Maintain alignment with product goals in `01_MASTER_PRD.md`.

## 14. References

- `00_PROJECT_CHARTER.md`
- `01_MASTER_PRD.md`
- `02_DOMAIN_MODEL.md`
- `03_BUSINESS_RULES.md`
- `04_AI_ENGINE.md`
- `05_DATABASE.md`
- `06_ARCHITECTURE.md`
- `07_API_SPEC.md`
- `08_UI_UX.md`
- `09_DEVELOPMENT_RULES.md`