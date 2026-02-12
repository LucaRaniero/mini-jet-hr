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
         | psycopg2
         v
+------------------+
|  PostgreSQL 15   |   Database container
|                  |   Port 5432
+------------------+
```

## Scope (MVP)

### EPIC 1: Employee Management (done)
- CRUD operations via REST API
- Soft delete pattern
- Vue list view with role filtering and ordering

### EPIC 2: Contract Management (planned)
- One-to-many relation (Employee -> Contracts)
- PDF upload and preview
- Contract expiration alerts

### EPIC 3-7: See [USER_STORIES.md](USER_STORIES.md)

## Learning Approach

This project is built as a **learning exercise** by a Senior Data Engineer (5 years SQL/ETL experience) transitioning to full-stack development. Claude Code serves as a senior mentor, mapping new concepts to SQL equivalents.

Key methodology:
- **Concepts first, code second** — understand the "why" before writing
- **SQL analogies** — every new pattern mapped to familiar SQL concepts
- **Test-driven** — 13 backend tests + 1 frontend test covering all user stories
- **Production-quality** — code written as if deploying to production tomorrow

See [learning-journal/](../learning-journal/) for detailed session notes.

## Timeline

| Week | Focus | Status |
|---|---|---|
| 1 | Django + DRF + Vue setup | Complete |
| 2-3 | Contract management, Auth | Planned |
| 4-5 | Onboarding automation | Planned |
| 6-7 | Dashboard, Reports | Planned |
| 8 | Docker + AWS deployment | Planned |
