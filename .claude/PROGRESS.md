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
- [x] Vue component: EmployeeList.vue

### US-002: Create Employee (done)
- [x] Custom field validation: validate_hire_date (no future dates)
- [x] Email uniqueness enforced by ModelSerializer UniqueValidator (auto from model)
- [x] API tests: 4 tests (valid create, duplicate email, future date, missing fields)
- [x] Manual verification via curl (POST valid, POST future date, POST duplicate email)

### US-003: Update Employee (done)
- [x] Email immutability via validate_email() with self.instance check
- [x] PATCH support (partial update) already provided by ModelViewSet
- [x] API tests: 3 tests (patch field, email rejected, same email allowed)

### US-004: Soft Delete (done)
- [x] perform_destroy() override: sets is_active=False instead of deleting
- [x] API tests: 2 tests (soft delete preserves record, excluded from list)

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
- DRF validation cascade: validate_<field>() → validate() → model → DB constraint
- validate_<field>() pattern: raise ValidationError or return value (like CHECK constraint)
- ModelSerializer auto-generates UniqueValidator from model unique=True
- HTTP status semantics: 200 OK (GET), 201 Created (POST), 204 No Content (DELETE), 400 Bad Request (validation error)
- manage.py shell vs python -c: Django needs bootstrap before ORM access
- self.instance in Serializer: None on create, existing object on update (conditional validation)
- perform_destroy() override: hook to customize DELETE behavior (soft delete pattern)
- refresh_from_db(): re-reads object from DB in tests (like re-running SELECT after UPDATE)

### Frontend Setup (done)
- [x] Vue 3 + Vite project scaffold (Vitest, ESLint, Prettier)
- [x] Tailwind CSS v4 integration (Vite plugin, no config files)
- [x] CORS configuration (django-cors-headers, whitelist localhost:5173)
- [x] Frontend Docker container (Node 20 Alpine, Vite dev server port 5173)
- [x] EmployeeList.vue component (fetch API, reactive table, loading/error states)
- [x] Centralized API client (api.js with VITE_API_URL env var)
- [x] Frontend test: 1 test (App renders header)

### Concepts mastered (Frontend):
- Vue 3 Composition API: ref() for reactive variables, onMounted() lifecycle hook
- Reactivity: ref() wraps values so Vue auto-updates template on change (vs plain let)
- Template directives: v-for (loop), v-if/v-else (conditional), :key (DOM diffing PK)
- Template interpolation: {{ }} for inserting values into HTML
- async/await for HTTP calls with fetch()
- CORS: browser security blocking cross-origin requests, django-cors-headers middleware
- Vite env vars: VITE_ prefix required to expose to browser (security)
- Docker anonymous volume: /app/node_modules preserved from host mount overwrite
- Tailwind CSS v4: utility-first, @import "tailwindcss" + Vite plugin (no config files)
- npm = pip, package.json = requirements.txt, node_modules = venv

### Next steps:
- [ ] EPIC 2: Contract management (US-005, US-006)

---

## Week 2: [Da compilare]
...
