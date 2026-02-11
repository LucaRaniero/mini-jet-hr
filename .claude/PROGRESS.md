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
- [x] DRF Serializer (EmployeeSerializer with ModelSerializer)
- [x] API endpoint: GET /api/employees/ with filtering, ordering, pagination
- [x] API tests: 4 tests covering all US-001 acceptance criteria
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
- DRF ModelSerializer (fields = SELECT columns, read_only_fields = IDENTITY/computed)
- DRF ModelViewSet (single class handles all CRUD operations)
- get_queryset() for dynamic filtering (equivalent to WHERE clause)
- OrderingFilter with whitelist (ordering_fields for security)
- PageNumberPagination (OFFSET/FETCH NEXT equivalent)
- DRF DefaultRouter for automatic URL generation
- Django URL modularity: app urls.py + project include()
- DRF global settings vs per-ViewSet override (settings.py REST_FRAMEWORK)

### Next steps:
- [ ] Build EmployeeList.vue frontend component
- [ ] US-002: POST /api/employees/ (create with validation)
- [ ] US-003: PUT/PATCH /api/employees/{id}/ (update)
- [ ] US-004: DELETE /api/employees/{id}/ (soft delete)

---

## Week 2: [Da compilare]
...
