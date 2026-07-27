# LigaMX IA Analytics

## Project Charter

Version: 1.0

Status: Approved

---

# Vision

Build a professional football analytics platform focused on Liga MX that combines statistical models, machine learning and betting market analysis to identify positive Expected Value opportunities.

The platform must be modular, scalable, auditable and production-ready.

---

# Mission

Provide accurate probabilistic models and transparent betting recommendations based on mathematical evidence instead of intuition.

---

# Primary Goals

- Estimate match probabilities.
- Simulate football matches.
- Detect value bets.
- Calculate Expected Value.
- Apply Kelly Criterion.
- Track long-term ROI.
- Audit every prediction.
- Continuously improve model accuracy.

---

# Non-Goals

The system is not intended to:

- Guarantee winning bets.
- Predict every match correctly.
- Replace human judgment.
- Recommend bets without positive Expected Value.

---

# Technical Stack

## Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic v2

## Frontend

- Next.js 15
- React 19
- TypeScript
- TailwindCSS
- shadcn/ui

## Database

- PostgreSQL

## Cache

- Redis

## AI

- NumPy
- Pandas
- Scikit-Learn
- XGBoost
- LightGBM

---

# Architecture Principles

- Clean Architecture
- Domain Driven Design
- SOLID
- DRY
- KISS
- Repository Pattern
- Service Layer
- Dependency Injection
- Unit of Work

---

# Coding Standards

- English identifiers.
- Strong typing.
- Production-ready code only.
- Unit tests required.
- API documentation required.
- Docker-first development.

---

# Success Criteria

Sprint 1 is complete when:

- Backend starts successfully.
- Frontend starts successfully.
- Docker Compose works.
- PostgreSQL connects.
- Redis connects.
- Health endpoint returns HTTP 200.