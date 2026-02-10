# Week 1 - Learning Journal

## Session 1 (2026-02-10) - Django Project Setup & Employee Model

**Focus**: US-001 - Infrastructure setup + Employee model design

**What I built:**
- Complete Docker development environment (Django 5.1 + PostgreSQL 15)
- Django project "minijet" with employees app
- Employee model with soft delete pattern
- Django Admin configuration for Employee management

**What I learned:**
- Django Model = Python class that maps to a SQL CREATE TABLE
- TextChoices is preferred over FK table for small, fixed enum values (employee/manager/admin)
- auto_now_add = DEFAULT NOW() (set once), auto_now = ON UPDATE trigger (set on every save)
- blank=True + default='' for optional string fields (never use null=True on strings in Django)
- UNIQUE constraint > TRIGGER for enforcing uniqueness (declarative > imperative)
- Docker Compose healthcheck + depends_on condition prevents "connection refused" race conditions
- QuerySet.update() bypasses auto_now (common Django gotcha)
- Django validates at 3 levels: Serializer -> Model -> Database constraint

**Challenges faced:**
- Understanding when to normalize (FK table) vs denormalize (choices): resolved by analyzing
  if values change at runtime (FK) or are fixed in business rules (choices)
- Mapping SQL mental model to Django ORM: resolved by comparing generated SQL with handwritten DDL

**Resources used:**
- Django docs: https://docs.djangoproject.com/en/5.1/topics/db/models/
- DRF docs: https://www.django-rest-framework.org/
- Docker Compose docs: https://docs.docker.com/compose/

**Next steps:**
- [ ] Create DRF serializer for Employee model
- [ ] Implement API ViewSet with filtering and pagination
- [ ] Understand DRF request/response lifecycle
