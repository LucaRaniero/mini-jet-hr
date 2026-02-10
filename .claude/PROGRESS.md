# Progress Tracker

## Week 1: Django Fundamentals

### Setup & Infrastructure
- [x] Docker environment (PostgreSQL 15 + Django 5.1)
- [x] Django project scaffolding (minijet)
- [x] Environment variable management (django-environ)
- [x] Code quality tools aligned with CI (black, isort, flake8, pytest)

### US-001: Employee CRUD (in progress)
- [x] Employee model design (conceptual SQL -> Django)
- [x] Employee model implementation with soft delete (US-004)
- [x] Django Admin registration
- [x] Initial migration applied to PostgreSQL
- [ ] DRF Serializer
- [ ] API endpoint: GET /api/employees/
- [ ] Vue component: EmployeeList.vue

### Concepts mastered:
- Django Model to SQL mapping (CharField=VARCHAR, EmailField, DateField, BooleanField)
- TextChoices for enum-like fields (choices vs FK table trade-off)
- auto_now_add vs auto_now (DEFAULT NOW() vs ON UPDATE trigger)
- null=True vs blank=True (database vs validation layer)
- UNIQUE constraint vs TRIGGER for uniqueness
- Docker Compose service orchestration with healthchecks
- Django project vs app structure
- django-environ for environment variable management

### Next steps:
- [ ] Create DRF serializer for Employee
- [ ] Implement API ViewSet with filtering, pagination, ordering
- [ ] Build EmployeeList.vue frontend component

---

## Week 2: [Da compilare]
...
