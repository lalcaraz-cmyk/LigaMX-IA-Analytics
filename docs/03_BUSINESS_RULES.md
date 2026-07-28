# LigaMX IA Analytics - Business Rules

## 1. Introduction

This document defines every business rule governing LigaMX IA Analytics. It captures rules for prediction validation, bet validation, simulation, value evaluation, portfolio risk, authorization, auditability, versioning, competition logic, statistics, AI controls, and data quality.

All rules are designed to be enforceable by the domain model described in `02_DOMAIN_MODEL.md`, persisted by the database in `05_DATABASE.md`, and surfaced through the API in `07_API_SPEC.md`.

## 2. Rule Categories

- Bet validation rules
- Prediction validation rules
- Simulation validation rules
- Expected Value rules
- Kelly rules
- Portfolio rules
- Authentication rules
- Authorization rules
- Audit rules
- Versioning rules
- Competition rules
- Statistics rules
- AI rules
- Data quality rules

## 3. Bet Validation Rules

### 3.1 Market Validity

- Rule: A bet may only be placed on a `Market` with valid odds and supported market type.
- Rule: `odds` must be greater than 1.0.
- Rule: `market_type` must be one of `1X2`, `OverUnder`, `CorrectScore`, or `AsianHandicap`.

### 3.2 Timing Constraints

- Rule: A bet must be placed before `match.kickoff_at`.
- Rule: Bets on finished or cancelled matches must be rejected.

### 3.3 Portfolio Limits

- Rule: The sum of open `stake` values must not exceed `portfolio.max_risk_pct * current_balance`.
- Rule: Individual bet stakes must not exceed `portfolio.max_bet_pct * current_balance`.
- Rule: Stake recommendations must not exceed `portfolio.available_capital`.

### 3.4 Position Consistency

- Rule: A bet must reference a prediction generated from the same `match_id` and a live model version.
- Rule: Bets cannot be placed if the `Prediction` status is invalid or the associated model is retired.

## 4. Prediction Validation Rules

### 4.1 Probability Integrity

- Rule: `predicted_home_prob + predicted_draw_prob + predicted_away_prob == 1.0` after normalization.
- Rule: All prediction probabilities must be in the range [0, 1].

### 4.2 Expected Goals Constraints

- Rule: `expected_goals_home` and `expected_goals_away` must be non-negative.
- Rule: Expected goals are capped at a maximum plausible value defined by model settings.

### 4.3 Score Distribution Consistency

- Rule: Score distribution probabilities must sum to a value close to 1.0 after truncation of negligible probabilities.
- Rule: Scorelines with zero probability may be omitted, but sum of retained values must reflect total probability mass.

### 4.4 Model Reference and Status

- Rule: Every `Prediction` must reference an existing `ModelVersion`.
- Rule: Predictions using `retired` models may be persisted for reference, but not used in active portfolio recommendations.

### 4.5 Prediction Publication

- Rule: Predictions may only be published using a Production ModelVersion.
- Rule: Published predictions become immutable.
- Rule: Archived predictions remain queryable but cannot be recommended.

## 5. Simulation Validation Rules

### 5.1 Probability Mass Preservation

- Rule: Monte Carlo simulation outputs must preserve probability mass within acceptable numeric tolerance.
- Rule: Analytic distributions must produce totals that sum to 1.0.

### 5.2 Scenario Definition

- Rule: Scenario inputs must include explicit assumptions such as lineup changes, rest days, or weather conditions.
- Rule: Scenario descriptions must be recorded in audit payloads.

### 5.3 Simulation Stability

- Rule: Simulation must use deterministic seeds for reproducible audit runs when requested.
- Rule: Simulation results must include sample size, convergence metrics, and variance measures.

## 6. Expected Value Rules

### 6.1 Implied Probability Calculation

- Rule: `implied_probability = 1 / odds` for decimal odds.
- Rule: When multiple outcomes exist, normalize the implied probabilities to remove bookmaker overround.

### 6.2 Edge and EV

- Rule: `edge = predicted_probability - implied_probability`.
- Rule: `expected_value = (predicted_probability * odds) - 1`.
- Rule: EV values must be rounded to a consistent precision for storage.

### 6.3 Recommendation Thresholds

- Rule: A candidate bet must have EV >= configured threshold before recommendation.
- Rule: Default threshold is 0.02 (2%).
- Rule: Only supported markets are eligible for direct EV recommendation.

### 6.4 Transparency

- Rule: Store raw edge and implied probability alongside EV.
- Rule: Provide explanation metadata for positive EV decisions.

## 7. Kelly Rules

### 7.1 Kelly Fraction Calculation

- Rule: `kelly_fraction = ((predicted_probability * odds) - 1) / (odds - 1)`.
- Rule: If expected_value <= 0, kelly_fraction must be zero.
- Rule: `kelly_fraction` must be capped by `portfolio.max_risk_pct` and `portfolio.min_kelly_pct`.

### 7.2 Fractional Kelly

- Rule: The system supports fractional Kelly allocations such as 0.5x or 0.25x of full Kelly.
- Rule: Fractional Kelly is configurable per portfolio and used when volatility must be constrained.

### 7.3 Stake Recommendation

- Rule: `recommended_stake = portfolio.current_balance * kelly_fraction`.
- Rule: The recommended stake must not exceed the available capital or portfolio maximum bet percentage.

## 8. Portfolio Rules

### 8.1 Portfolio Definition

- Rule: `starting_capital` must be positive.
- Rule: `currency` must be defined and consistent for portfolio calculations.
- Rule: `max_risk_pct` and `min_kelly_pct` must be between 0.0 and 1.0.
- Rule: `max_bet_pct` must be defined to limit single bet size.

### 8.2 Risk Controls

- Rule: Portfolio exposure is defined as the sum of `stake` across open bets relative to `current_balance`.
- Rule: Portfolio concentration limits are enforced by match and correlated market grouping.
- Rule: Drawdown alerts are triggered when realized losses exceed configured thresholds.

### 8.3 Lifecycle Management

- Rule: Bets update portfolio balances only when settled.
- Rule: Proposed bets reserve capital but do not reduce settled balances until placement.
- Rule: Rejected bets release reserved capital immediately.

## 9. Authentication Rules

### 9.1 User Identity

- Rule: All platform operations require an authenticated user unless read-only public endpoints are added later.
- Rule: Users are uniquely identified by email.
- Rule: Authentication tokens must expire and support refresh semantics.

### 9.2 Credential Safety

- Rule: Passwords must be hashed securely.
- Rule: Session tokens and refresh tokens must be stored securely.
- Rule: Failed login attempts must be capturable in audit logs.

## 10. Authorization Rules

### 10.1 Role-Based Access

- Rule: `admin` can manage users, model promotions, and system configuration.
- Rule: `manager` can create portfolios, place bets, and ingest market data.
- Rule: `analyst` can generate predictions, run simulations, and run backtests.
- Rule: `auditor` can query audits, predictions, and governance reports.

### 10.2 Resource Enforcement

- Rule: Protected resources must validate role membership before execution.
- Rule: Model promotions and audit exports require `admin` or explicit governance authorization.

## 11. Audit Rules

### 11.1 Audit Coverage

- Rule: Every prediction generation, simulation run, bet placement, bet settlement, and model promotion must generate an `AuditRecord`.
- Rule: Audit records must include `entity_type`, `entity_id`, `action`, `payload`, `user_id`, and `created_at`.

### 11.2 Immutability

- Rule: Audit records cannot be updated or deleted.
- Rule: If data changes are required, a new audit record captures the alteration.

### 11.3 Searchability

- Rule: Audit payloads must include searchable metadata fields for compliance filtering.
- Rule: API endpoints must support search by entity type, action, user, and time range.

## 12. Versioning Rules

### 12.1 Model Lifecycle

- Rule: Model status transitions are `draft -> staging -> production -> retired`.
- Rule: Production models are immutable and may not be retrained in place.
- Rule: Retired models remain queryable for historical audits.

### 12.2 Dataset Versioning

- Rule: Every training and inference dataset must be captured as a `DatasetSnapshot`.
- Rule: Snapshots include source, hash, and metadata.
- Rule: Model versions must reference the dataset snapshot used for training.

### 12.3 API Versioning

- Rule: API endpoints must support versioning to maintain backward compatibility.
- Rule: Changes that break contract require a new version prefix such as `/v1/`.

## 13. Competition Rules

### 13.1 Fixture Uniqueness

- Rule: A `Match` is uniquely identified by `home_team_id`, `away_team_id`, and `kickoff_at`.
- Rule: Duplicate fixtures in the same competition and season are rejected.

### 13.2 Competition Context

- Rule: Competition stage and season context must be stored on matches.
- Rule: Model inputs must incorporate stage-specific weighting when available.

### 13.3 Match Lifecycle

- Rule: A Match transitions only through the following states:

  Scheduled
      ↓
      Live
      ↓
      Finished

- Rule: Cancelled and Postponed are terminal states.
- Rule: Finished matches cannot transition back to Live.
- Rule: Prediction recalculation is allowed only while Match status is Scheduled.

## 14. Statistics Rules

### 14.1 Data Aggregation

- Rule: Team and player statistics are aggregated consistently from source datasets.
- Rule: Historical statistics are versioned with dataset snapshots.

### 14.2 Derived Metrics

- Rule: Dynamic Elo, form indexes, and attack/defense ratings are recalculated with each ingest.
- Rule: Derived metrics used in prediction must be traceable to source data.

## 15. AI Rules

### 15.1 Training Discipline

- Rule: Models must be trained using reproducible pipelines.
- Rule: Feature engineering must be applied consistently across training and inference.

### 15.2 Calibration

- Rule: All probability models require calibration evaluation.
- Rule: Drift thresholds trigger model review.

### 15.3 Explainability

- Rule: Production predictions must expose explanation metadata.
- Rule: SHAP or equivalent measures are captured for audit.

### 15.4 Continuous Learning

- Rule: Retraining must be performed with a documented dataset snapshot and governance approval.
- Rule: New model versions are compared to baseline before promotion.

### 15.5 Feature Governance

- Rule: Feature definitions are immutable after publication.
- Rule: Feature versions must be traceable.
- Rule: Inference must use the same FeatureSet version used during training.

### 15.6 Model Drift

- Rule: Model drift above configured thresholds triggers review.
- Rule: Drift detection cannot automatically promote new models.
- Rule: Retraining requires governance approval.

## 16. Data Quality Rules

### 16.1 Source Integrity

- Rule: Data sources must be validated for completeness and format.
- Rule: Missing or inconsistent fields are rejected or flagged.

### 16.2 Data Freshness

- Rule: Match schedules, market feeds, and reference data must be refreshed according to configured ingestion intervals.
- Rule: Ingestion failures must generate alerts.

### 16.3 Error Handling

- Rule: Invalid rows in ingest pipelines must be logged and isolated.
- Rule: No partial writes may corrupt the core domain state.

### 16.4 Dataset Integrity

- Rule: Dataset checksums must be unique.
- Rule: DatasetSnapshots cannot be modified after creation.
- Rule: Every ModelVersion must reference exactly one DatasetSnapshot.

## 17. Implementation Notes

- Rule enforcement is implemented in domain services and database constraints.
- Validation rules must be mirrored in the API layer with explicit error messages.
- Cross-reference `02_DOMAIN_MODEL.md` for aggregate ownership and enforcement boundaries.
- Use `05_DATABASE.md` for schema-level enforcement of core invariants.

## 18. Traceability

| Rule Category | Primary Document | Enforcement Layer |
|---|---|---|
| Bet validation | `07_API_SPEC.md` | API and domain service |
| Prediction validation | `04_AI_ENGINE.md` | Prediction service and test suites |
| Simulation validation | `04_AI_ENGINE.md` | Simulation engine |
| EV and Kelly | `04_AI_ENGINE.md` | EV calculator and portfolio service |
| Audit | `05_DATABASE.md` | Audit table and service |
| Versioning | `06_ARCHITECTURE.md` | Model registry service |
| Data quality | `05_DATABASE.md` | Ingestion pipelines |
