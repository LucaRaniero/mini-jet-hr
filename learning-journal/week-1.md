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
- [x] US-003: PUT/PATCH endpoint (update with immutable email)
- [x] US-004: DELETE endpoint (soft delete)
- [ ] Build EmployeeList.vue (Vue 3 frontend)

---

## Session 3b (2026-02-12) - Update & Soft Delete (US-003, US-004)

**Focus**: US-003 (PATCH with immutable email) + US-004 (soft delete via perform_destroy)

**What I built:**
- Email immutability validation: validate_email() checks self.instance to distinguish create vs update
- Soft delete: perform_destroy() override in ViewSet — sets is_active=False instead of deleting
- 5 new API tests (3 update + 2 delete)
- Total: 13 tests across all 4 user stories, all passing

**What I learned:**
- self.instance in Serializer: `None` during create, the existing object during update — allows conditional validation
- `=` in Python is assignment, not comparison (my SQL brain confused `SET is_active = False` with `IF is_active = False`)
- perform_destroy() is a ViewSet hook: DRF calls it when DELETE arrives, we override to change behavior
- refresh_from_db(): re-reads object from DB after changes — necessary in tests to verify UPDATE worked (like re-running SELECT)
- test_patch_same_email_allowed: edge case — sending same email in PATCH payload should NOT trigger immutability error

**Key insight:**
EPIC 1 backend complete! 4 user stories, 13 tests, only 3 files of actual code:
- models.py (data layer)
- serializers.py (validation + transformation)
- views.py (routing + business logic hooks)

**Architecture pattern:**
| Responsibility | File | SQL equivalent |
|---|---|---|
| Data structure | models.py | CREATE TABLE |
| Validation + transformation | serializers.py | CHECK constraints + triggers |
| Business logic hooks | views.py | Stored procedures |

**Next steps:**
- [x] Build EmployeeList.vue (Vue 3 frontend)
- [ ] EPIC 2: Contract management

---

## Session 4 (2026-02-12) - Vue 3 Frontend Setup & EmployeeList

**Focus**: First frontend — scaffold Vue 3 + Vite, Tailwind CSS, Docker, CORS, EmployeeList component

**What I built:**
- Vue 3 + Vite project with Tailwind CSS v4, Vitest, ESLint, Prettier
- EmployeeList.vue component: fetches employees from API, displays in a styled table
- Centralized API client (api.js) with configurable base URL via env vars
- Frontend Docker container (Node 20 Alpine, Vite dev server on port 5173)
- CORS configuration on Django backend (django-cors-headers)
- 1 frontend test (App renders header)

**What I learned:**
- Vue 3 Composition API: `ref()` creates reactive variables — when `.value` changes, the template auto-updates
- Without `ref()`, a plain `let` variable changes in memory but Vue doesn't know → UI stays stale
- `onMounted()` lifecycle hook: runs when component appears in DOM (like AFTER INSERT trigger)
- `v-for` = declarative loop in template (like CURSOR but without manual iteration)
- `v-if` / `v-else-if` / `v-else` = conditional rendering (like CASE WHEN in SQL)
- `:key` in v-for = PRIMARY KEY for Vue's DOM diffing algorithm (optimization)
- `{{ }}` = template interpolation (like CONCAT or PRINT — inserts values into HTML)
- `async/await` = sugar syntax for Promises (like WAITFOR in T-SQL)
- `fetch()` = native HTTP client (like requests.get() in Python)
- CORS = browser security policy blocking cross-origin requests (like a firewall rule)
- Middleware order matters: CorsMiddleware must come before CommonMiddleware in the pipeline
- Vite env vars: only `VITE_`-prefixed variables are exposed to the browser (security)
- Docker anonymous volume (`/app/node_modules`): preserves container's node_modules from being overwritten by Windows mount
- `--host 0.0.0.0`: required in Docker to expose Vite dev server outside the container
- Tailwind v4: no config files needed, just `@import "tailwindcss"` and Vite plugin
- `npm` = pip for JavaScript, `package.json` = requirements.txt

**Key pattern: SQL → Vue 3 mapping:**
| SQL / Backend | Vue 3 Equivalent |
|---|---|
| DECLARE @variable | ref() — reactive variable |
| EXEC sp_GetData | fetch() — HTTP call to API |
| CURSOR / WHILE | v-for — declarative loop |
| IF / CASE WHEN | v-if / v-else — conditional rendering |
| Trigger ON UPDATE (view refresh) | Reactivity — template auto-updates on ref change |

**Next steps:**
- [x] Complete EPIC 1 frontend (US-002, US-003, US-004)

---

## Session 5 (2026-02-16) - EPIC 1 Frontend Completion (US-002, US-003, US-004)

**Focus**: Vue Router, EmployeeForm (create/edit), ConfirmDialog (delete), full CRUD frontend

**What I built:**
- Vue Router with 3 routes: `/`, `/employees/new`, `/employees/:id/edit`
- EmployeeForm.vue: shared form for create and edit (dual-mode via props)
- ConfirmDialog.vue: reusable confirmation modal for delete
- 3 view components: EmployeeListView, EmployeeCreateView, EmployeeEditView
- Expanded api.js from 1 function (GET) to 5 (GET list, GET single, POST, PATCH, DELETE)
- 19 frontend tests (Vitest + Vue Test Utils), 32 total with backend

**What I learned:**
- Vue Router: URL-based component dispatch (like CASE WHEN @url = '/path' THEN EXEC component)
- Route params (`:id`): dynamic URL segments extracted as `route.params.id` (like WHERE id = @param)
- `<RouterView />`: placeholder where the router injects the matched component
- `<RouterLink>`: SPA navigation without page reload (unlike `<a href>`)
- `createWebHistory()` for clean URLs vs `createWebHashHistory()` for hash-based
- Named routes: navigate by name instead of hardcoded URLs (safer refactoring)
- Props: parameters passed from parent to child component (like stored procedure arguments)
- `computed()`: derived value that auto-recalculates (like a computed column in SQL)
- `watch()` with `immediate: true`: reacts to prop changes, covers both "data ready at mount" and "data arrives later"
- `emit()`: child-to-parent communication (like RETURN from a stored procedure)
- `v-model`: two-way binding on form inputs (reads AND writes, like a CURSOR)
- `@submit.prevent`: intercepts form submission, prevents page reload
- PATCH vs PUT: PATCH sends only changed fields, avoids immutable email conflict
- `{ data, error, status }` pattern: distinguish business errors (400) from fatal errors (throw)
- Server-side error display per field: map DRF validation errors to input borders + messages
- `createMemoryHistory()` in tests needs explicit `router.push('/')` before `router.isReady()` resolves
- Docker anonymous volume gotcha: `npm install` on host ≠ inside container, must do both

**Key pattern: SQL → Vue 3 mapping (new concepts):**
| SQL / Backend | Vue 3 Equivalent |
|---|---|
| WHERE id = @param | `route.params.id` — parameter from URL |
| INSERT INTO ... VALUES | `createEmployee(form)` — POST via fetch |
| UPDATE ... SET ... WHERE | `updateEmployee(id, payload)` — PATCH via fetch |
| DELETE ... WHERE id = @id | `deleteEmployee(id)` — DELETE via fetch (soft) |
| SP parameter @mode = 'INSERT' vs 'UPDATE' | `props.employee` — null = create, object = edit |
| CHECK CONSTRAINT violation message | Server 400 → `errors.field_name = ["msg"]` |
| RETURN from SP | `emit('saved')` — signals parent |
| CASE WHEN ... THEN ... END | Ternary: `condition ? valueA : valueB` |

**Architecture pattern: separation of concerns:**
| Layer | File | Responsibility |
|---|---|---|
| Routing | router/index.js | URL → component mapping |
| Views | views/*.vue | Orchestration (fetch data, handle navigation) |
| Components | components/*.vue | Presentation + user interaction |
| API client | api.js | HTTP calls + error normalization |

**Next steps:**
- [x] EPIC 2: Contract management (US-005, US-006) — backend started in Week 2
