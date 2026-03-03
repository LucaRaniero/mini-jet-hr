# Mini Jet HR - Project Brief

## Overview

Mini Jet HR is a portfolio project simulating an HR automation platform, built to master the tech stack used at [Jet HR](https://jethr.it/) — an Italian startup simplifying HR management for SMEs.

## Problem Statement

HR departments in Italian SMEs still rely on spreadsheets, emails, and paper-based processes for employee management. This leads to:
- Data scattered across multiple systems
- Manual onboarding processes prone to errors
- No visibility on contract expirations
- Difficult compliance with Italian labor regulations

## Solution

A web-based HR management platform that:
1. **Centralizes employee data** in a single system
2. **Automates onboarding** with checklists and notifications
3. **Manages contracts** with expiration alerts
4. **Provides dashboards** for HR decision-making

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | Django 5.x + DRF | Matches Jet HR's stack, batteries-included framework |
| Frontend | Vue 3 (Composition API) | Matches Jet HR's stack, reactive UI |
| Database | PostgreSQL 15 | Production-grade RDBMS, matches Jet HR |
| Styling | Tailwind CSS v4 | Utility-first, fast prototyping |
| Containers | Docker + Docker Compose | Consistent dev/prod environments |
| CI/CD | GitHub Actions | Automated testing and quality checks |
| Cloud | AWS (EC2, RDS, S3) | Industry standard, planned |

## Architecture

```
Browser (localhost:5173)
    |
    v
+------------------+
|  Vue 3 + Vite    |   Frontend container (Node 20)
|  Tailwind CSS    |   Port 5173
+--------+---------+
         | fetch() + CORS
         v
+------------------+
|  Django + DRF    |   Backend container (Python 3.11)
|  REST API        |   Port 8000
+--------+---------+
         |                  |
         | psycopg2         | redis-py
         v                  v
+------------------+  +------------------+
|  PostgreSQL 15   |  |  Redis 7         |  DB 0: Celery broker
|  Database        |  |  (Alpine)        |  DB 1: Django cache
+------------------+  +--------+---------+
                               |
                               v
                      +------------------+
                      |  Celery Worker   |  Async tasks
                      |  (Python 3.11)  |  (welcome email)
                      +------------------+
```

## Scope (MVP)

### EPIC 1: Employee Management (done)
- CRUD operations via REST API + Vue frontend
- Soft delete pattern
- Role filtering and ordering

### EPIC 2: Contract Management (done)
- One-to-many relation (Employee -> Contracts)
- PDF upload and preview
- Contract expiration alerts (4-state badges)

### EPIC 3: Onboarding Automation (done)
- Configurable templates + interactive checklist
- Django Signals (auto-create steps on employee creation)
- Welcome email (Celery async task with retry logic)

### EPIC 4: Dashboard & Analytics (in progress)
- Aggregated KPIs (employees, contracts, onboarding)
- Chart.js visualizations (headcount trend, department distribution)
- Redis cache with signal-based invalidation

### EPIC 5-7: See [USER_STORIES.md](USER_STORIES.md)

## Learning Approach

This project is built as a **learning exercise** by a Senior Data Engineer (5 years SQL/ETL experience) transitioning to full-stack development. Claude Code serves as a senior mentor, mapping new concepts to SQL equivalents.

Key methodology:
- **Concepts first, code second** — understand the "why" before writing
- **SQL analogies** — every new pattern mapped to familiar SQL concepts
- **Test-driven** — 176 automated tests (85 backend + 91 frontend)
- **Production-quality** — code written as if deploying to production tomorrow

See [learning-journal/](../learning-journal/) for detailed session notes.

## Timeline

| Week | Focus | Status |
|---|---|---|
| 1 | Django + DRF + Vue setup, Employee CRUD | Complete |
| 2 | Contract management (CRUD + PDF upload) | Complete |
| 3 | Onboarding automation (signals, email, Celery) | Complete |
| 4 | Dashboard & Analytics (API, charts, cache) | In Progress |
| 5-6 | Auth & permissions, Reports | Planned |
| 7-8 | Docker production + AWS deployment | Planned |
