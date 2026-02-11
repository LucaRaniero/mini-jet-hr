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
- [x] Create DRF serializer for Employee model
- [x] Implement API ViewSet with filtering and pagination
- [x] Understand DRF request/response lifecycle

---

## Session 2 (2026-02-11) - DRF Serializer, ViewSet & REST API (US-001)

**Focus**: US-001 - Expose Employee model as REST API with filtering, ordering, pagination

**What I built:**
- EmployeeSerializer (ModelSerializer) for Python <-> JSON translation
- EmployeeViewSet (ModelViewSet) with role filtering and ordering
- URL routing with DefaultRouter (auto-generates list + detail endpoints)
- Global pagination config (20 items/page)
- 4 API tests covering all US-001 acceptance criteria

**What I learned:**
- ModelSerializer = SELECT column list for JSON: `fields` = columns to include, `read_only_fields` = IDENTITY/computed columns
- read_only_fields must be a SUBSET of fields (it marks them, doesn't add them)
- ModelViewSet = single class that handles 5 CRUD operations (list, create, retrieve, update, destroy)
- get_queryset() = the WHERE clause: base filtering (is_active=True) + dynamic filtering from query params
- Query params are ALWAYS strings: `?is_active=true` arrives as `"true"`, not Python `True`
- OrderingFilter with ordering_fields = whitelist of sortable columns (security: prevents ORDER BY on arbitrary columns)
- `?ordering=-hire_date` = ORDER BY hire_date DESC (minus prefix = descending)
- DefaultRouter auto-generates URL patterns from a ViewSet (like an API gateway)
- Django URL modularity: each app has its own urls.py, project includes them with path("api/", include("app.urls"))
- DRF global config in settings.py REST_FRAMEWORK dict, overridable per-ViewSet (like sp_configure vs SET)
- PageNumberPagination wraps response in {count, next, previous, results} instead of plain array
- Django test runner creates a temporary test database, runs migrations, destroys it after tests (like BEGIN TRAN/ROLLBACK)

**Key pattern: SQL -> DRF mapping:**
| SQL | DRF |
|---|---|
| SELECT col1, col2 | Serializer fields |
| CREATE VIEW / Stored Proc | ViewSet |
| WHERE role = 'x' | get_queryset() filtering |
| ORDER BY col DESC | OrderingFilter with `-` prefix |
| OFFSET/FETCH NEXT | PageNumberPagination |

**Next steps:**
- [ ] Build EmployeeList.vue (Vue 3 frontend)
- [x] US-002: POST endpoint with validation
- [ ] US-003: PUT/PATCH endpoint
- [ ] US-004: Soft delete endpoint

---

## Session 3 (2026-02-11) - POST Endpoint with Validation (US-002)

**Focus**: US-002 - POST /api/employees/ with hire_date and email validation

**What I built:**
- Custom field validator: validate_hire_date() to reject future dates
- 4 new API tests covering all US-002 acceptance criteria
- Total: 8 tests (4 US-001 + 4 US-002), all passing

**What I learned:**
- DRF validation cascade: validate_<field>() → validate() → model → DB (like layered CHECK constraints)
- validate_<field>() convention: DRF auto-discovers methods named `validate_<fieldname>`
- Pattern: `raise ValidationError("msg")` for invalid, `return value` for valid (like RAISERROR/THROW vs continue)
- ModelSerializer auto-generates UniqueValidator from model `unique=True` (no manual code needed)
- HTTP status semantics: 201 Created (POST success) vs 200 OK (GET) vs 204 No Content (DELETE)
- `python -c` vs `manage.py shell -c`: Django needs bootstrap (settings + app registry) before ORM works
- Never hardcode "future dates" in tests: use `date.today() + timedelta(days=30)` for reliability

**Key insight:**
ModelViewSet already handled POST — we only needed to add validation to the Serializer.
The ViewSet calls `serializer.is_valid()` automatically, and our `validate_hire_date()` runs as part of that cascade.
Zero changes to views.py!

**Next steps:**
- [ ] US-003: PUT/PATCH endpoint (update with immutable email)
- [ ] US-004: DELETE endpoint (soft delete)
- [ ] Build EmployeeList.vue (Vue 3 frontend)
