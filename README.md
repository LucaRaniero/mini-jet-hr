# Mini Jet HR - Learning Project

> An HR automation platform built to learn Django, Vue.js, Docker, and AWS while preparing for a Software Engineer role.

[![Project Status](https://img.shields.io/badge/status-in%20progress-yellow)]()
[![Tech Stack](https://img.shields.io/badge/stack-Django%20%7C%20Vue%20%7C%20Docker%20%7C%20AWS-blue)]()
[![CI](https://github.com/LucaRaniero/mini-jet-hr/workflows/CI%20Pipeline/badge.svg)](https://github.com/LucaRaniero/mini-jet-hr/actions)

## Project Goal

This is a portfolio project that demonstrates:
- **Full-stack development** capabilities (Django + Vue.js)
- Understanding of **HR automation domain**
- **Enterprise-ready** code practices
- **Cloud deployment** skills (AWS)

Built as preparation for a Software Engineer role at [Jet HR](https://jethr.it/), focusing on their tech stack and problem domain.

## Architecture

**Current**: Monolithic architecture (matching Jet HR's current approach for speed)  
**Future-ready**: Designed to be split into microservices

### Tech Stack
- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: Vue 3 (Composition API) + Vite
- **Database**: PostgreSQL 15
- **Containerization**: Docker + Docker Compose
- **Cloud**: AWS (EC2, RDS, S3)
- **CI/CD**: GitHub Actions (planned)

### Architecture Diagram
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Vue 3     │─────▶│  Django API  │─────▶│ PostgreSQL  │
│  Frontend   │      │   (DRF)      │      │   Database  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   AWS S3    │
                     │  (Storage)  │
                     └─────────────┘
```

## Features

### Completed
- [x] Employee CRUD operations (API + full frontend: list, create, edit, delete)
- [x] Contract management (API + full frontend: nested CRUD under employees)
- [x] PDF upload for contracts (FileField, multipart, preview in browser)
- [x] Contract status badges (Pianificato/In Scadenza/Attivo/Scaduto) with expiration indicator
- [x] Vue Router with 6 routes (3 employee + 3 contract)
- [x] Docker containerization (PostgreSQL + Django + Vue)
- [x] 85 automated tests (33 backend + 52 frontend)

### In Progress
- [ ] Authentication & role-based permissions

### Planned
- [ ] Onboarding automation
- [ ] Dashboard & analytics
- [ ] PDF report generation
- [ ] Email notifications
- [ ] AWS deployment
- [ ] CI/CD pipeline

Full user stories available in [`docs/USER_STORIES.md`](docs/USER_STORIES.md)

## Project Structure
```
mini-jet-hr/
├── .claude/                # AI learning configuration
│   ├── CLAUDE.md          # Project manifesto
│   ├── LEARNING_MODE.md   # How Claude mentors me
│   ├── ARCHITECTURE.md    # Architecture decisions
│   └── PROGRESS.md        # Learning tracker
├── backend/               # Django application
├── frontend/              # Vue.js application
├── docs/                  # Documentation
│   ├── USER_STORIES.md
│   ├── PROJECT_BRIEF.md
│   └── API_DESIGN.md
├── learning-journal/      # Weekly learning notes
└── docker/                # Docker configurations
```

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15

### Quick Start
```bash
# Clone the repository
git clone https://github.com/LucaRaniero/mini-jet-hr.git
cd mini-jet-hr

# Start with Docker Compose
docker-compose up

# Application will be available at:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Manual Setup (without Docker)
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## Learning Journey

This project is part of my transition from **Senior Data Engineer** to **Software Engineer**.

**Background**: 5 years of SQL expertise (T-SQL, PL/pgSQL, PL/SQL), data pipelines, ETL  
**Goal**: Master full-stack web development with Django and Vue.js  
**Approach**: Build production-ready code while documenting the learning process

See [`learning-journal/`](learning-journal/) for detailed weekly progress.

## Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test

# Coverage report
pytest --cov=. --cov-report=html
```

## Deployment

Deployment instructions for AWS will be added once the containerization is complete.

Target architecture:
- **Compute**: AWS EC2 (Docker containers)
- **Database**: AWS RDS (PostgreSQL)
- **Storage**: AWS S3
- **CDN**: CloudFront (optional)

## Contributing

This is a personal learning project, but I'm open to feedback and suggestions!

Feel free to open issues if you spot:
- Bugs or security issues
- Better architectural patterns
- Optimization opportunities
- Learning resources recommendations

## Built with AI-Assisted Learning

This project leverages **Claude Code** as a senior engineering mentor to accelerate learning while ensuring deep understanding of concepts. 

The `.claude/` folder contains my learning methodology and how I've structured the AI collaboration.

**Key principle**: AI explains concepts and guides architecture decisions, I implement and internalize the knowledge through hands-on coding.

Check out `learning-journal/` for my weekly progress and concepts mastered.

## License

MIT License - This is a portfolio/learning project, feel free to use it for your own learning.

## Contact

- **LinkedIn**: https://www.linkedin.com/in/luca-raniero/

---

**Current Status**: Week 2 of 8 | Last updated: 2026/02/19

*"The best way to learn is to build."*