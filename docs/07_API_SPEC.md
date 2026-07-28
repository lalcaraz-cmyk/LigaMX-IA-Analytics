# LigaMX IA Analytics - API Specification

## 1. Overview

This API specification defines the REST interface for LigaMX IA Analytics. It includes authentication, users, teams, players, matches, competitions, predictions, simulations, statistics, odds, portfolios, reports, error handling, versioning, pagination, filtering, sorting, and OpenAPI conventions.

The API is designed for frontend and integration clients with clear, production-ready resource contracts.

## 2. API Principles

- Use RESTful semantics and resource-oriented endpoints.
- Return JSON payloads with consistent schema conventions.
- Use HTTP status codes according to semantics.
- Support pagination, filtering, sorting, and versioning.
- Provide comprehensive OpenAPI documentation.
- Protect endpoints with OAuth2 and JWT.

## 3. Authentication and Authorization

### 3.1 Authentication

- OAuth2 password grant for internal users.
- JWT bearer tokens for API requests.
- Access tokens are short-lived; refresh tokens support session continuity.
- Tokens are signed with secure keys and rotated regularly.

### 3.2 Authorization

- Roles: `analyst`, `manager`, `auditor`, `admin`.
- RBAC enforced in middleware and service layers.
- Sensitive endpoints require explicit roles.

### 3.3 Headers

- `Authorization: Bearer <token>`
- `Accept: application/json`
- `Content-Type: application/json`
- `X-Correlation-ID`: optional request tracer

## 4. Error Handling and HTTP Codes

### 4.1 HTTP Status Codes

- `200 OK`: successful retrieval or action.
- `201 Created`: resource successfully created.
- `204 No Content`: action succeeded with no payload.
- `400 Bad Request`: validation or client error.
- `401 Unauthorized`: missing or invalid credentials.
- `403 Forbidden`: insufficient permissions.
- `404 Not Found`: resource unavailable.
- `409 Conflict`: duplicate or invalid state.
- `422 Unprocessable Entity`: semantic validation failure.
- `500 Internal Server Error`: unexpected server failure.

### 4.2 Error Response Schema

```json
{
  "code": "string",
  "message": "string",
  "details": [
    {
      "field": "string",
      "issue": "string"
    }
  ]
}
```

### 4.3 Common Error Codes

- `invalid_payload`
- `authentication_failed`
- `authorization_failed`
- `resource_not_found`
- `conflict`
- `validation_error`
- `model_not_production`
- `bet_not_allowed`

## 5. Versioning and OpenAPI

- API endpoints are prefixed with `/api/v1/`.
- Backward-incompatible changes create a new version path.
- Use OpenAPI 3.1 for schema definitions.
- Include example requests and responses in the API documentation.

## 6. Pagination, Filtering, Sorting

### 6.1 Pagination

- Use `page` and `page_size`.
- Response includes `meta` with `total`, `page`, `page_size`, `pages`.
- Default `page_size` is 25, maximum is 100.

### 6.2 Filtering

- Use query parameters for filters.
- Use ISO 8601 timestamp parameters.
- Support logical combinations where appropriate.

### 6.3 Sorting

- Use `sort` parameter with comma-separated fields.
- Prefix with `-` for descending order.
- Example: `sort=-created_at,odds`

## 7. Authentication Endpoints

### 7.1 POST /api/v1/auth/token

Request:
```json
{
  "username": "user@example.com",
  "password": "securePassword123"
}
```

Response:
```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "..."
}
```

### 7.2 POST /api/v1/auth/refresh

Request:
```json
{
  "refresh_token": "..."
}
```

Response:
```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## 8. User Endpoints

### 8.1 GET /api/v1/users

- Roles: `admin`
- Filters: `role`, `is_active`
- Sorting: `email`, `created_at`

Response meta includes pagination.

### 8.2 GET /api/v1/users/{user_id}

- Roles: `admin`
- Returns user details.

### 8.3 POST /api/v1/users

- Roles: `admin`
- Creates a user.

Request:
```json
{
  "email": "analyst@example.com",
  "full_name": "Liga MX Analyst",
  "role": "analyst"
}
```

### 8.4 PATCH /api/v1/users/{user_id}

- Roles: `admin`
- Updates user metadata and activation status.

## 9. Teams and Players

### 9.1 GET /api/v1/teams

- Returns teams.
- Filters: `country`, `short_code`
- Sorting: `name`

### 9.2 GET /api/v1/teams/{team_id}

- Returns team details.

### 9.3 GET /api/v1/players

- Filters: `team_id`, `position`, `status`

### 9.4 GET /api/v1/players/{player_id}

- Returns player details and status.

## 10. Competitions and Matches

### 10.1 GET /api/v1/competitions

- Filters: `season`, `category`
- Sorting: `name`, `season`

### 10.2 GET /api/v1/competitions/{competition_id}

- Returns competition metadata.

### 10.3 GET /api/v1/matches

- Filters: `competition_id`, `season`, `status`, `kickoff_from`, `kickoff_to`, `home_team_id`, `away_team_id`
- Sorting: `kickoff_at`, `status`

### 10.4 GET /api/v1/matches/{match_id}

- Returns match details, teams, competition context, and latest odds snapshots.

### 10.5 POST /api/v1/matches

- Roles: `admin`, `manager`
- Creates a match fixture.

Request:
```json
{
  "home_team_id": "uuid",
  "away_team_id": "uuid",
  "competition_id": "uuid",
  "venue_id": "uuid",
  "kickoff_at": "2026-08-01T20:00:00Z",
  "source": "schedule_feed"
}
```

### 10.6 PATCH /api/v1/matches/{match_id}

- Roles: `admin`, `manager`
- Updates match state, scores, or status.

## 11. Odds and Market Endpoints

### 11.1 GET /api/v1/odds

- Returns bookmaker market snapshots.
- Filters: `match_id`, `bookmaker_id`, `market_type`, `timestamp_from`, `timestamp_to`

### 11.2 GET /api/v1/odds/{odds_id}

- Returns a single odds snapshot.

### 11.3 POST /api/v1/odds

- Roles: `admin`, `manager`
- Ingests or updates market snapshot.

Request:
```json
{
  "match_id": "uuid",
  "bookmaker_id": "uuid",
  "market_type": "1X2",
  "odds_home": 2.12,
  "odds_draw": 3.20,
  "odds_away": 3.45,
  "timestamp": "2026-07-27T12:00:00Z"
}
```

## 12. Predictions

### 12.1 GET /api/v1/predictions

- Filters: `match_id`, `model_version_id`, `created_from`, `created_to`, `status`
- Sorting: `created_at`

### 12.2 GET /api/v1/predictions/{prediction_id}

- Returns prediction details, score distribution, calibration, and explanation.

### 12.3 POST /api/v1/predictions

- Roles: `analyst`, `manager`
- Generates or refreshes a prediction.

Request:
```json
{
  "match_id": "uuid",
  "model_version_id": "uuid",
  "scenario": {
    "player_adjustments": [
      {"player_id": "uuid", "status": "injured"}
    ],
    "weather": "rain"
  }
}
```

### 12.4 POST /api/v1/predictions/{prediction_id}/simulate

- Runs a simulation for the specified prediction.
- Returns simulation summary and scoreline probabilities.

## 13. Simulations

### 13.1 GET /api/v1/simulations

- Filters: `prediction_id`, `created_from`, `created_to`

### 13.2 GET /api/v1/simulations/{simulation_id}

- Returns simulation results and convergence metrics.

### 13.3 POST /api/v1/simulations

- Roles: `analyst`, `manager`
- Executes a Monte Carlo or analytic simulation.

Request:
```json
{
  "prediction_id": "uuid",
  "type": "monte_carlo",
  "iterations": 10000,
  "scenario": {"rest_days": 3}
}
```

## 14. Statistics and Reports

### 14.1 GET /api/v1/statistics/models

- Returns aggregate model performance metrics.
- Filters: `model_version_id`, `period`, `status`

### 14.2 GET /api/v1/statistics/portfolios

- Returns aggregated portfolio KPIs.
- Filters: `portfolio_id`, `period`

### 14.3 GET /api/v1/reports/backtests

- Returns backtest summaries and performance statistics.

### 14.4 GET /api/v1/reports/audit

- Roles: `auditor`, `admin`
- Returns audit report payloads.
- Filters: `entity_type`, `action`, `user_id`, `created_from`, `created_to`

## 15. Portfolios and Bets

### 15.1 GET /api/v1/portfolios

- Returns portfolios visible to the user.
- Filters: `owner_id`, `currency`, `status`

### 15.2 GET /api/v1/portfolios/{portfolio_id}

- Returns portfolio details, balances, exposure, and active bets.

### 15.3 POST /api/v1/portfolios

- Roles: `manager`
- Creates a portfolio.

Request:
```json
{
  "name": "Liga MX Growth",
  "currency": "MXN",
  "starting_capital": 100000.00,
  "max_risk_pct": 0.10,
  "min_kelly_pct": 0.02,
  "max_bet_pct": 0.03
}
```

### 15.4 PATCH /api/v1/portfolios/{portfolio_id}

- Updates portfolio settings.

### 15.5 GET /api/v1/portfolios/{portfolio_id}/summary

- Returns portfolio KPIs, drawdown, and risk exposure.

### 15.6 GET /api/v1/bets

- Filters: `portfolio_id`, `match_id`, `status`, `placed_from`, `placed_to`

### 15.7 GET /api/v1/bets/{bet_id}

- Returns bet details and settlement history.

### 15.8 POST /api/v1/bets

- Roles: `manager`
- Places a bet.

Request:
```json
{
  "portfolio_id": "uuid",
  "prediction_id": "uuid",
  "odds_snapshot_id": "uuid",
  "stake": 1500.00,
  "odds": 2.45,
  "expected_value": 0.032,
  "kelly_fraction": 0.06
}
```

### 15.9 PATCH /api/v1/bets/{bet_id}/settle

- Roles: `manager`
- Settles a bet.

Request:
```json
{
  "outcome": "won",
  "pnl": 2475.00,
  "settled_at": "2026-08-01T23:00:00Z"
}
```

### 15.10 PATCH /api/v1/bets/{bet_id}/reject

- Roles: `manager`
- Rejects a proposed bet.

## 16. Models and Governance

### 16.1 GET /api/v1/models

- Filters: `status`, `dataset_snapshot_id`, `created_from`

### 16.2 GET /api/v1/models/{model_version_id}

- Returns model metadata, metrics, and governance notes.

### 16.3 POST /api/v1/models

- Roles: `analyst`, `manager`
- Registers a model version.

Request:
```json
{
  "name": "lgmx-v1.0",
  "description": "Baseline combined analytics model.",
  "dataset_snapshot_id": "uuid",
  "training_parameters": {"max_depth": 6},
  "evaluation_metrics": {"log_loss": 0.88}
}
```

### 16.4 PATCH /api/v1/models/{model_version_id}/promote

- Roles: `admin`
- Promotes a model.

Request:
```json
{
  "status": "production",
  "release_notes": "Approved after backtesting and governance review."
}
```

### 16.5 PATCH /api/v1/models/{model_version_id}/retire

- Roles: `admin`
- Retires a model version.

## 17. Reporting Endpoints

### 17.1 GET /api/v1/dashboard/overview

- Returns KPIs for predictions, portfolios, and model health.

### 17.2 GET /api/v1/dashboard/prediction-performance

- Returns prediction accuracy, calibration, and EV distribution.

### 17.3 GET /api/v1/dashboard/portfolio-performance

- Returns portfolio ROI, drawdown, and exposure.

### 17.4 GET /api/v1/dashboard/model-health

- Returns model drift indicators and deployment metrics.

## 18. Swagger and Examples

### 18.1 Swagger Conventions

- Use `application/json` payloads.
- Include examples in schema definitions.
- Document required and optional fields explicitly.
- Use descriptive summary and description fields.

### 18.2 Example Response

```json
{
  "data": {
    "prediction_id": "uuid",
    "match_id": "uuid",
    "predicted_home_prob": 0.53,
    "predicted_draw_prob": 0.27,
    "predicted_away_prob": 0.20,
    "expected_goals_home": 1.45,
    "expected_goals_away": 0.95,
    "score_distribution": {"1-0": 0.18, "2-1": 0.12}
  },
  "meta": {
    "request_id": "abc-123",
    "generated_at": "2026-07-27T12:34:56Z"
  }
}
```

## 19. OpenAPI Conventions

- Use `components` for shared schemas.
- Reuse schemas across endpoints.
- Use tags for logical grouping.
- Include security schemes and server definitions.
- Provide example values for developer usability.

## 20. References

- `02_DOMAIN_MODEL.md`
- `03_BUSINESS_RULES.md`
- `04_AI_ENGINE.md`
- `05_DATABASE.md`
- `06_ARCHITECTURE.md`
- `08_UI_UX.md`
- `09_DEVELOPMENT_RULES.md`

## 14. Audit Endpoints

### 14.1 GET /audit

- Roles: `auditor`, `admin`
- Returns audit records with filtering.
- Filters: `entity_type`, `entity_id`, `action`, `user_id`, `created_from`, `created_to`.

### 14.2 GET /audit/{audit_id}

- Returns a single audit event record.

## 15. Backtesting Endpoints

### 15.1 POST /backtests

- Roles: `analyst`, `manager`
- Starts a backtest run.
- Input: `model_version_id`, `match_ids`, `start_date`, `end_date`, `portfolio_id`.

### 15.2 GET /backtests/{backtest_id}

- Returns backtest results, metrics, and recommendations.

### 15.3 GET /backtests

- Lists previous backtest runs and status.

## 16. Dashboard Endpoints

### 16.1 GET /dashboard/overview

- Returns high-level KPI metrics for predictions, portfolios, and model health.

### 16.2 GET /dashboard/prediction-performance

- Returns aggregated prediction metrics, accuracy, calibration, and EV distribution.

### 16.3 GET /dashboard/portfolio-performance

- Returns current portfolio performance and risk indicators.

### 16.4 GET /dashboard/model-health

- Returns model drift indicators, deployment status, and backtest summary.

## 17. Schema Examples

### 17.1 Prediction Result

```json
{
  "prediction_id": "uuid",
  "match_id": "uuid",
  "model_version_id": "uuid",
  "predicted_home_prob": 0.52,
  "predicted_draw_prob": 0.27,
  "predicted_away_prob": 0.21,
  "expected_goals_home": 1.31,
  "expected_goals_away": 0.92,
  "score_distribution": {
    "1-0": 0.18,
    "2-1": 0.10,
    "0-0": 0.06
  },
  "created_at": "2026-07-27T12:00:00Z"
}
```

### 17.2 Bet Recommendation

```json
{
  "portfolio_id": "uuid",
  "prediction_id": "uuid",
  "market_id": "uuid",
  "stake": 150.00,
  "recommended_stake": 180.00,
  "odds": 2.45,
  "expected_value": 0.032,
  "kelly_fraction": 0.06,
  "status": "proposed"
}
```

## 18. API Governance

- Endpoints must be documented in OpenAPI.
- Changes must be backward compatible or versioned.
- API contracts must follow the domain model in `02_DOMAIN_MODEL.md`.
- Security, validation, and pagination patterns are mandatory.

## 19. Notes and References

- `00_PROJECT_CHARTER.md` for business objectives and scope.
- `06_ARCHITECTURE.md` for service decomposition and integration.
- `05_DATABASE.md` for persistent model mappings.
- `08_UI_UX.md` for frontend usage of API responses.
- `09_DEVELOPMENT_RULES.md` for API coding standards.
