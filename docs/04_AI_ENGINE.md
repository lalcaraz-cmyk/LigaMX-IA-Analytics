# LigaMX IA Analytics - AI Engine

## 1. Purpose

This document defines the AI architecture for LigaMX IA Analytics: feature engineering, statistical models, training and inference pipelines, evaluation, simulation, explainability, and model governance.

It is the implementation contract for the AI context described in `02_DOMAIN_MODEL.md`. It must remain aligned with `03_BUSINESS_RULES.md`, `05_DATABASE.md`, `06_ARCHITECTURE.md`, and `07_API_SPEC.md`.

## 2. Objectives and Scope

The engine shall:

- Produce calibrated, auditable probabilities for Liga MX pre-match markets.
- Estimate home and away expected goals and derive a coherent score distribution.
- Identify positive expected-value opportunities by comparing model probabilities with independent market odds.
- Support reproducible simulations and backtests.
- Preserve complete lineage from source data to a published prediction.

The first production release is deliberately limited to pre-match predictions for Liga MX. In-play inference, player-level models, reinforcement learning, and additional leagues are future extensions, not Version 1.0 requirements.

## 3. Operating Principles

### 3.1 Reproducibility and lineage

Every training run, inference run, simulation, and backtest must record:

- `as_of_at`: the UTC cutoff time for data availability.
- `dataset_snapshot_id` and source hashes.
- `feature_set_id` and immutable feature-set version.
- Feature pipeline version and code revision.
- `model_version_id`, artifact digest, and model configuration.
- Random seed when randomness is used.
- Input scenario, output, and calculation timestamp.

Training and inference use the same versioned transformation definitions. A prediction cannot be published when any required lineage field is missing.

### 3.2 Temporal integrity

Features may use only information that was available strictly before `as_of_at`. Historical joins must preserve the original publication time of each match statistic, lineup, injury, weather observation, and odds quote.

The system must not use final score, post-kickoff information, revised statistics, or closing odds that were unavailable at prediction time. Missing data must be represented explicitly by an availability indicator and a documented imputation strategy; it must never silently become a numeric zero.

### 3.3 Separation of prediction and market comparison

The core probability model must not use the target bookmaker's contemporaneous odds as an input when those probabilities are later compared with that bookmaker to calculate edge or expected value. This prevents circularity and preserves a meaningful independent estimate.

Market-derived features may be used only in a separately identified market-aware model, for monitoring, or as a benchmark. Outputs from that model must be labelled as market-aware and must not drive direct EV recommendations against the same source unless an approved, documented policy explicitly allows it.

## 4. Release Scope

### 4.1 Version 1.0

- Match and team historical data with quality checks.
- Dynamic team Elo, recency-weighted form, attack/defense strength, rest days, home advantage, competition stage, and venue context.
- Poisson baseline and Dixon-Coles correction.
- Pre-match probabilities for 1X2, supported over/under lines, and correct score derived from one score distribution.
- Walk-forward backtesting, calibration, explainability, model registry, and audit lineage.
- Scenario simulation for explicit, auditable lineup, rest, and weather adjustments.

### 4.2 Post-Version 1.0

- Bivariate Poisson, gradient-boosted models, stacking, and approved market-aware experiments.
- Player-level ratings and lineup models once reliable player data is available.
- Automated retraining proposals, not automated promotion.
- In-play/event-based inference, additional leagues, and portfolio optimization research.

## 5. Feature Engineering

### 5.1 Feature categories

- **Fixture context:** home and away teams, season, competition stage, venue, kickoff time, rest days, and fixture congestion.
- **Team strength:** Elo, rolling attack and defense strength, home advantage, form, and opponent-adjusted historical performance.
- **Availability and context:** confirmed or estimated lineup availability, injuries, suspensions, travel, and weather, each with source and availability timestamps.
- **Derived features:** expected-goal inputs, recency-weighted aggregates, and feature availability flags.
- **Market features:** stored separately for monitoring, benchmarking, and expressly approved market-aware experiments.

### 5.2 Feature-set contract

A `FeatureSet` is an immutable, versioned collection of feature definitions. Each definition specifies its name, type, source, transformation, null-handling policy, availability rule, and owner.

A `FeatureVector` is generated for one match and one `as_of_at` timestamp. It must reference exactly one `FeatureSet`, one dataset snapshot, and the pipeline version used to generate it.

Changing a definition, transformation, source, or missing-value policy creates a new feature-set version. Published models and predictions retain references to their original versions.

### 5.3 Data quality gates

Before training or inference, the pipeline must validate schema, completeness, uniqueness, freshness, time ordering, and domain ranges. Invalid rows are quarantined with a reason; they do not silently enter features. A run is failed when configured quality thresholds are not met.

## 6. Statistical Prediction Models

### 6.1 Poisson baseline

The baseline estimates `expected_goals_home` and `expected_goals_away` from attack strength, defense strength, home advantage, and permitted contextual features. Independent Poisson score probabilities are computed over a configured score range with an explicit tail-mass policy.

### 6.2 Dixon-Coles correction

The Dixon-Coles model applies a time-weighted likelihood and low-score correction. It is evaluated against the Poisson baseline using the same temporal splits and promotion criteria.

### 6.3 Future model families

Bivariate Poisson and machine-learning models are experimental until promoted through the governance process. Gradient-boosted models may use non-market tabular features and must expose their feature set, calibration method, and reproducible training configuration.

## 7. Prediction Contract

### 7.1 Canonical score distribution

Each published prediction has one canonical probability distribution over scorelines plus documented residual tail mass. The engine derives all supported markets from this distribution:

- 1X2 from the total probability mass where home goals are greater than, equal to, or less than away goals.
- Over/under probabilities from total-goal outcomes for the requested line.
- Correct-score probabilities from individual scoreline probabilities.

The sum of the complete distribution, including retained tail mass, must equal 1 within the configured numerical tolerance. The derived 1X2 vector must also equal 1 within that tolerance.

### 7.2 Publication

Only predictions produced with a production `ModelVersion` may be published. A published prediction is immutable; a refresh creates a new prediction run with a new `as_of_at`, feature vector, and lineage record.

## 8. Market Comparison, EV, and Kelly

Market data is normalized per bookmaker, market, selection, and timestamp. The comparison uses the latest eligible odds snapshot available at or before the prediction's `as_of_at`.

For decimal odds:

- `implied_probability = 1 / odds`
- Multi-outcome markets are normalized to remove overround before comparison.
- `edge = model_probability - normalized_implied_probability`
- `expected_value = (model_probability * odds) - 1`

Kelly sizing is applied only after the business-rule thresholds, portfolio limits, model-production status, and audit requirements have passed. The result is a recommendation, never a guarantee of profit or an automatic placement instruction.

## 9. Training and Backtesting

### 9.1 Training pipeline

1. Ingest and validate source data.
2. Freeze a dataset snapshot and feature-set version.
3. Construct temporally valid feature vectors.
4. Train candidate models using fixed, recorded configurations.
5. Calibrate candidates using data that was not used to fit the base model.
6. Evaluate against the baseline and persist artifacts, metrics, and lineage.
7. Submit the candidate for governance review.

### 9.2 Temporal validation

Validation must use expanding-window or rolling-origin splits. For each fold, the training interval precedes the validation interval, and all feature availability rules are evaluated as of each match's cutoff time.

An untouched final holdout period is reserved for promotion evaluation. Randomly shuffled cross-validation is prohibited for time-dependent match data.

### 9.3 Backtesting

Backtests replay historical predictions chronologically using only data and odds known at each historical `as_of_at`. Each run records the model version, feature set, dataset snapshot, market-selection policy, odds-source policy, bankroll policy, and result metrics. Backtest results must never overwrite live prediction or portfolio records.

## 10. Evaluation and Promotion

### 10.1 Predictive metrics

- Multiclass log loss and Brier score for 1X2.
- Calibration error, reliability diagrams, and calibration slope/intercept.
- Market-specific log loss or Brier score for each supported binary market.
- Distribution-level checks for expected goals and scorelines.

Accuracy and ROC AUC may be reported as supplementary metrics, but they are not sufficient promotion metrics for calibrated probability models.

### 10.2 Betting and operational metrics

- Out-of-sample EV, ROI, yield, turnover, and maximum drawdown, with sample counts and confidence intervals.
- Closing-line value where a verified closing-odds source is available.
- Inference latency, task latency, throughput, error rate, and data freshness.

### 10.3 Promotion criteria

Threshold values are configuration, not hard-coded constants. A model may advance only when it:

- Completes all required temporal validation and final holdout tests.
- Meets configured calibration and reliability thresholds.
- Does not regress beyond the allowed tolerance against the current production baseline.
- Has complete reproducibility and data-quality lineage.
- Receives the required governance approval.

Drift detection can create a review or retraining proposal, but it cannot automatically promote a model.

## 11. Calibration and Explainability

Calibration is fitted only on data not used for model fitting. Isotonic regression or Platt scaling may be used when justified by validation evidence. The calibration method, fit period, and metrics are part of model metadata.

For eligible models, the engine stores a concise prediction explanation: top feature contributions, feature values or availability states, expected-goal drivers, model version, and limitation notices. SHAP values are appropriate for supported tree models; statistical models use an equivalent, documented attribution method.

## 12. Simulation and Scenarios

Simulation is used for scenarios and uncertainty analysis. A plain analytic Poisson result does not require Monte Carlo merely to calculate deterministic market probabilities.

Every scenario must include explicit assumptions, a source or manual-input flag, parameter changes, `as_of_at`, and random seed when sampling is used. Outputs include sample size, confidence intervals, convergence or error estimates, scoreline mass validation, and the base prediction reference.

## 13. Continuous Learning and Governance

The system monitors data quality, feature drift, calibration drift, predictive performance, and operational failures. Retraining creates a new candidate `ModelVersion`; production artifacts are never retrained in place.

`ModelVersion` lifecycle is `draft -> staging -> production -> retired`. Artifacts, configurations, metrics, approvals, release notes, and rollback decisions are immutable audit records. Retired models remain available for historical audit but cannot produce new active recommendations.

## 14. Integration Requirements

- `02_DOMAIN_MODEL.md` defines `FeatureSet`, `FeatureVector`, `DatasetSnapshot`, `ModelVersion`, `Prediction`, and `SimulationResult` ownership.
- `03_BUSINESS_RULES.md` defines probability, market, EV, Kelly, publication, audit, and model-lifecycle rules.
- `05_DATABASE.md` must persist all lineage, market-selection, simulation, and backtest records described here.
- `06_ARCHITECTURE.md` must run training, backtests, and simulations asynchronously while keeping inference bounded by API latency targets.
- `07_API_SPEC.md` must expose immutable prediction detail, asynchronous job status, model governance, simulation, and backtest contracts.

## 15. Future Extensions

- Player-level models after data-quality validation.
- Bivariate Poisson and approved ensemble models.
- Additional leagues through isolated feature pipelines and validation baselines.
- In-play inference only with dedicated latency, source-freshness, and responsible-use controls.
