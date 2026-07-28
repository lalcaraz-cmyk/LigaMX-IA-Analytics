# LigaMX IA Analytics - Database Design

## 1. Purpose

This document defines the PostgreSQL persistence design for LigaMX IA Analytics. It is aligned with the aggregate boundaries in `02_DOMAIN_MODEL.md`, the invariants in `03_BUSINESS_RULES.md`, and the lineage requirements in `04_AI_ENGINE.md`.

The database is the system of record for domain state, model governance, market observations, and audit evidence. Model binaries and large raw source files are stored in object storage; PostgreSQL stores immutable references, hashes, and metadata.

## 2. Principles

- Use normalized relational tables for domain state and append-only records for evidence.
- Enforce structural invariants in PostgreSQL; enforce cross-aggregate policies in application transactions.
- Store timestamps as `TIMESTAMPTZ` in UTC and use UUID primary keys.
- Keep mutable operational records separate from immutable prediction, simulation, model, and audit records.
- Never overwrite historical odds, feature vectors, predictions, model artifacts, simulations, or backtest results.

## 3. Schemas and Naming

Use the `public` schema for Version 1.0. Tables use singular `snake_case` nouns; identifiers are `id`; foreign keys follow `<entity>_id`. The application-user table is named `app_user` to avoid a quoted SQL keyword.

All mutable tables include `created_at` and `updated_at`. Immutable tables include only `created_at` unless a lifecycle field is explicitly required. A shared trigger maintains `updated_at`.

## 4. Reference and Competition Data

### 4.1 `competition`

- `id UUID PRIMARY KEY`
- `name TEXT NOT NULL`
- `country_code CHAR(2) NOT NULL`
- `category TEXT NOT NULL`
- timestamps

Unique: `(name, country_code, category)`.

### 4.2 `season`

- `id UUID PRIMARY KEY`
- `competition_id UUID NOT NULL REFERENCES competition(id)`
- `name TEXT NOT NULL`
- `starts_on DATE NOT NULL`
- `ends_on DATE NOT NULL`
- timestamps

Check: `ends_on >= starts_on`. Unique: `(competition_id, name)`.

### 4.3 `round`

- `id UUID PRIMARY KEY`
- `season_id UUID NOT NULL REFERENCES season(id)`
- `number INTEGER NOT NULL CHECK (number > 0)`
- `stage TEXT NOT NULL`
- `name TEXT`
- timestamps

Unique: `(season_id, number, stage)`.

### 4.4 `team`, `venue`, `player`, and `team_membership`

`team` stores `name`, unique `short_code`, `country_code`, and timestamps. `venue` stores `name`, `city`, `country_code`, capacity, optional latitude/longitude, and timestamps; capacity is positive when present. `player` stores identity attributes, position, and timestamps.

Team assignment is historical. `team_membership` contains `player_id`, `team_id`, `starts_on`, optional `ends_on`, and `status` (`active`, `injured`, `suspended`, `transferred`). It checks dates and uses a partial unique index to allow at most one open membership per player.

## 5. Fixtures and Observations

### 5.1 `match`

- `id UUID PRIMARY KEY`
- `competition_id UUID NOT NULL REFERENCES competition(id)`
- `season_id UUID NOT NULL REFERENCES season(id)`
- `round_id UUID REFERENCES round(id)`
- `home_team_id UUID NOT NULL REFERENCES team(id)`
- `away_team_id UUID NOT NULL REFERENCES team(id)`
- `venue_id UUID REFERENCES venue(id)`
- `kickoff_at TIMESTAMPTZ NOT NULL`
- `status TEXT NOT NULL CHECK (status IN ('scheduled','live','finished','cancelled','postponed'))`
- `home_score SMALLINT`
- `away_score SMALLINT`
- `source_external_id TEXT`
- timestamps

Checks: home and away teams differ; scores are non-negative; scores are both null or both populated; populated scores require status `finished`. Unique: `(competition_id, season_id, home_team_id, away_team_id, kickoff_at)` and, where present, `source_external_id`.

Indexes: `(kickoff_at)`, `(status, kickoff_at)`, `(home_team_id, kickoff_at)`, and `(away_team_id, kickoff_at)`.

### 5.2 `lineup`, `lineup_player`, and statistics

`lineup` captures one team lineup for one match, including `team_id`, `match_id`, `status` (`predicted`, `confirmed`, `final`), `announced_at`, source metadata, and timestamps. `lineup_player` references a lineup and player and records role, starter state, and availability status.

`ingestion_run` records source, source version, started/finished timestamps, status, row counts, error summary, and source-file hash. `team_match_statistic` and `player_match_statistic` store normalized observations with `match_id`, `ingestion_run_id`, and `observed_at`, preserving the availability time needed for leakage-safe features.

## 6. Markets and Odds

### 6.1 `bookmaker`

- `id UUID PRIMARY KEY`
- `name TEXT NOT NULL UNIQUE`
- `website TEXT`
- `is_active BOOLEAN NOT NULL DEFAULT TRUE`
- timestamps

### 6.2 `market`

A market defines a betting offer for one match, independently of bookmaker quotes.

- `id UUID PRIMARY KEY`
- `match_id UUID NOT NULL REFERENCES match(id)`
- `market_type TEXT NOT NULL CHECK (market_type IN ('1X2','over_under','correct_score','asian_handicap','both_teams_to_score'))`
- `line_value NUMERIC(6,3)`
- `period TEXT NOT NULL DEFAULT 'full_time'`
- `settlement_rules_version TEXT NOT NULL`
- timestamps

Unique: `(match_id, market_type, line_value, period)` using a null-safe unique index. A line is required for over/under and Asian handicap; it is null for 1X2.

### 6.3 `market_selection`

Each possible outcome inside a market is a selection.

- `id UUID PRIMARY KEY`
- `market_id UUID NOT NULL REFERENCES market(id)`
- `code TEXT NOT NULL` (for example `home`, `draw`, `away`, `over`, `under`, `score_1_0`)
- `display_name TEXT NOT NULL`
- `outcome_payload JSONB NOT NULL`
- timestamps

Unique: `(market_id, code)`. Application schemas validate the payload according to the market type.

### 6.4 `odds_snapshot` and `odds_quote`

`odds_snapshot` represents one bookmaker capture for a match:

- `id UUID PRIMARY KEY`
- `match_id UUID NOT NULL REFERENCES match(id)`
- `bookmaker_id UUID NOT NULL REFERENCES bookmaker(id)`
- `captured_at TIMESTAMPTZ NOT NULL`
- `source_external_id TEXT`
- `ingestion_run_id UUID REFERENCES ingestion_run(id)`
- `raw_payload JSONB`
- `payload_hash TEXT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

Unique: `(bookmaker_id, source_external_id)` when available; otherwise `(match_id, bookmaker_id, captured_at, payload_hash)`.

`odds_quote` is one quote for one market selection in a snapshot:

- `id UUID PRIMARY KEY`
- `odds_snapshot_id UUID NOT NULL REFERENCES odds_snapshot(id)`
- `market_selection_id UUID NOT NULL REFERENCES market_selection(id)`
- `decimal_odds NUMERIC(10,4) NOT NULL CHECK (decimal_odds > 1)`
- `raw_implied_probability NUMERIC(10,8) NOT NULL CHECK (raw_implied_probability > 0 AND raw_implied_probability <= 1)`
- `normalized_implied_probability NUMERIC(10,8)`
- `is_available BOOLEAN NOT NULL DEFAULT TRUE`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

Unique: `(odds_snapshot_id, market_selection_id)`. Index snapshots by `(match_id, captured_at DESC)` and quotes by `market_selection_id`.

## 7. Feature and Dataset Lineage

### 7.1 `dataset_snapshot`

- `id UUID PRIMARY KEY`
- `version TEXT NOT NULL UNIQUE`
- `purpose TEXT NOT NULL CHECK (purpose IN ('training','inference','backtest','evaluation'))`
- `source_manifest JSONB NOT NULL`
- `content_hash TEXT NOT NULL UNIQUE`
- `row_count BIGINT`
- `as_of_at TIMESTAMPTZ NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

Dataset snapshots are immutable.

### 7.2 `feature`, `feature_set`, and `feature_set_feature`

`feature` stores the globally unique feature name, type, definition, source contract, owner, and creation timestamp.

`feature_set` stores name, immutable version, description, pipeline version, definition hash, status, and creation timestamp. Unique: `(name, version)` and `definition_hash`.

`feature_set_feature` joins a feature set to its features and stores feature order, transformation definition, null-handling policy, and availability rule. Unique: `(feature_set_id, feature_id)` and `(feature_set_id, ordinal)`.

### 7.3 `feature_vector`

- `id UUID PRIMARY KEY`
- `match_id UUID NOT NULL REFERENCES match(id)`
- `feature_set_id UUID NOT NULL REFERENCES feature_set(id)`
- `dataset_snapshot_id UUID NOT NULL REFERENCES dataset_snapshot(id)`
- `as_of_at TIMESTAMPTZ NOT NULL`
- `pipeline_version TEXT NOT NULL`
- `values JSONB NOT NULL`
- `availability JSONB NOT NULL`
- `content_hash TEXT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

Unique: `(match_id, feature_set_id, dataset_snapshot_id, as_of_at, content_hash)`. Vectors are immutable and validated against the referenced feature set before insertion.

## 8. Model Governance and Predictions

### 8.1 `model_version`

- `id UUID PRIMARY KEY`
- `name TEXT NOT NULL`
- `version TEXT NOT NULL`
- `family TEXT NOT NULL`
- `status TEXT NOT NULL CHECK (status IN ('draft','staging','production','retired'))`
- `dataset_snapshot_id UUID NOT NULL REFERENCES dataset_snapshot(id)`
- `feature_set_id UUID NOT NULL REFERENCES feature_set(id)`
- `artifact_uri TEXT NOT NULL`
- `artifact_hash TEXT NOT NULL`
- `training_parameters JSONB NOT NULL`
- `evaluation_metrics JSONB NOT NULL`
- `calibration_metadata JSONB`
- `release_notes TEXT`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `promoted_at TIMESTAMPTZ`
- `retired_at TIMESTAMPTZ`

Unique: `(name, version)` and `artifact_hash`. A partial unique index permits one production model per approved scope. Model artifacts are never overwritten; lifecycle changes create an audit record.

### 8.2 `prediction`

`prediction` is an immutable run, not a mutable match summary.

- `id UUID PRIMARY KEY`
- `match_id UUID NOT NULL REFERENCES match(id)`
- `model_version_id UUID NOT NULL REFERENCES model_version(id)`
- `feature_vector_id UUID NOT NULL REFERENCES feature_vector(id)`
- `dataset_snapshot_id UUID NOT NULL REFERENCES dataset_snapshot(id)`
- `as_of_at TIMESTAMPTZ NOT NULL`
- `status TEXT NOT NULL CHECK (status IN ('draft','published','archived','failed'))`
- `expected_goals_home NUMERIC(10,6) NOT NULL CHECK (expected_goals_home >= 0)`
- `expected_goals_away NUMERIC(10,6) NOT NULL CHECK (expected_goals_away >= 0)`
- `home_probability NUMERIC(10,8) NOT NULL CHECK (home_probability BETWEEN 0 AND 1)`
- `draw_probability NUMERIC(10,8) NOT NULL CHECK (draw_probability BETWEEN 0 AND 1)`
- `away_probability NUMERIC(10,8) NOT NULL CHECK (away_probability BETWEEN 0 AND 1)`
- `score_distribution JSONB NOT NULL`
- `tail_probability NUMERIC(10,8) NOT NULL DEFAULT 0 CHECK (tail_probability BETWEEN 0 AND 1)`
- `calibration_metadata JSONB NOT NULL`
- `explanation_summary JSONB NOT NULL`
- `content_hash TEXT NOT NULL UNIQUE`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `published_at TIMESTAMPTZ`

Check: `home_probability + draw_probability + away_probability` is within the configured decimal tolerance of 1. A trigger rejects updates to published predictions; refreshing a prediction creates a new run.

### 8.3 `prediction_market_probability`

This table stores probabilities derived from the canonical prediction distribution:

- `prediction_id UUID NOT NULL REFERENCES prediction(id)`
- `market_selection_id UUID NOT NULL REFERENCES market_selection(id)`
- `probability NUMERIC(10,8) NOT NULL CHECK (probability BETWEEN 0 AND 1)`
- `derivation_version TEXT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

Primary key: `(prediction_id, market_selection_id)`.

## 9. Simulation and Backtesting

### 9.1 `simulation_run`

- `id UUID PRIMARY KEY`
- `prediction_id UUID NOT NULL REFERENCES prediction(id)`
- `scenario JSONB NOT NULL`
- `seed BIGINT`
- `method TEXT NOT NULL CHECK (method IN ('analytic','monte_carlo'))`
- `iterations INTEGER CHECK (iterations > 0)`
- `status TEXT NOT NULL CHECK (status IN ('queued','running','completed','failed','cancelled'))`
- `result JSONB`
- `convergence_metrics JSONB`
- `created_by_user_id UUID REFERENCES app_user(id)`
- `created_at`, `started_at`, `completed_at`

Completed runs are immutable. Index: `(prediction_id, created_at DESC)`.

### 9.2 `backtest_run` and `backtest_result`

`backtest_run` records `model_version_id`, `feature_set_id`, `dataset_snapshot_id`, date range, as-of and odds policies, bankroll policy, configuration, status, seed, creator, and timestamps.

`backtest_result` references a run and a match, and stores the generated prediction, selected market quote, recommendation decision, stake, outcome, PnL, and per-match metrics. Unique: `(backtest_run_id, match_id, market_selection_id)`.

Backtests are append-only and never modify live portfolios or bets.

## 10. Portfolio and Betting

### 10.1 `app_user`

- `id UUID PRIMARY KEY`
- `email TEXT NOT NULL UNIQUE`
- `full_name TEXT NOT NULL`
- `role TEXT NOT NULL CHECK (role IN ('analyst','manager','auditor','admin'))`
- `auth_provider TEXT NOT NULL`
- `provider_subject TEXT`
- `password_hash TEXT`
- `is_active BOOLEAN NOT NULL DEFAULT TRUE`
- timestamps

For local authentication, `password_hash` is required and passwords are never stored. For external identity providers, `(auth_provider, provider_subject)` is unique. The definitive authentication flow belongs in `07_API_SPEC.md`.

### 10.2 `portfolio`

`portfolio` references `owner_id`, has currency, starting/current/available capital, risk limits, timestamps, and non-negative amount checks. It has a unique `(owner_id, name)`.

### 10.3 `bet`

- `id UUID PRIMARY KEY`
- `portfolio_id UUID NOT NULL REFERENCES portfolio(id)`
- `match_id UUID NOT NULL REFERENCES match(id)`
- `prediction_id UUID NOT NULL REFERENCES prediction(id)`
- `market_selection_id UUID NOT NULL REFERENCES market_selection(id)`
- `odds_quote_id UUID NOT NULL REFERENCES odds_quote(id)`
- `stake NUMERIC(14,2) NOT NULL CHECK (stake > 0)`
- `recommended_stake NUMERIC(14,2) NOT NULL CHECK (recommended_stake >= 0)`
- `decimal_odds NUMERIC(10,4) NOT NULL CHECK (decimal_odds > 1)`
- `edge NUMERIC(12,8) NOT NULL`
- `expected_value NUMERIC(12,8) NOT NULL`
- `kelly_fraction NUMERIC(10,8) NOT NULL CHECK (kelly_fraction >= 0)`
- `status TEXT NOT NULL CHECK (status IN ('proposed','placed','settled','rejected','void'))`
- `outcome TEXT CHECK (outcome IN ('won','lost','void','pending'))`
- `pnl NUMERIC(14,2)`
- timestamps plus `placed_at` and `settled_at`

The application validates that the odds quote belongs to the same match and market selection as the bet. Index: `(portfolio_id, status)`, `(match_id)`, `(prediction_id)`, and `(market_selection_id)`.

## 11. Audit and Operational Integrity

### 11.1 `audit_record`

- `id UUID PRIMARY KEY`
- `entity_type TEXT NOT NULL`
- `entity_id UUID NOT NULL`
- `action TEXT NOT NULL`
- `actor_user_id UUID REFERENCES app_user(id)`
- `correlation_id UUID`
- `payload JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

`audit_record` is append-only. Database roles deny `UPDATE` and `DELETE` to application accounts. Index `(entity_type, entity_id, created_at DESC)`, `(actor_user_id, created_at DESC)`, `(correlation_id)`, and GIN on `payload` only where query evidence supports it.

### 11.2 Partitioning and retention

Partition `audit_record` by month once volume warrants it. Partition `odds_snapshot` by captured month or season only after validating query patterns. Do not partition small operational tables prematurely. Retention and archive policies must preserve audit and model lineage requirements.

## 12. Integrity, Indexes, and Migrations

- Create B-tree indexes on all foreign keys and stated time-based access paths.
- Use partial indexes for open bets, active portfolios, scheduled matches, and production-model lookup.
- Validate JSONB payloads at application boundaries and with targeted database checks for critical keys.
- Apply schema changes through focused Alembic migrations, including forward and rollback plans where safe.
- Test migrations against anonymized production-like data and verify indexes, constraints, and downgrade behavior.
- Seed only reference data required for local development; never seed production credentials or betting records.

## 13. References

- `02_DOMAIN_MODEL.md` for entities, aggregate ownership, and ubiquitous language.
- `03_BUSINESS_RULES.md` for state transitions, probability integrity, audit, and portfolio constraints.
- `04_AI_ENGINE.md` for feature lineage, prediction immutability, simulation, and model governance.
- `06_ARCHITECTURE.md` for object storage, workers, ingestion, and deployment.
- `07_API_SPEC.md` for resource contracts and asynchronous job behavior.
```