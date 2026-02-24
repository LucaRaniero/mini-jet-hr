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

### US-002: Create Employee (done — API + Frontend)
- [x] Custom field validation: validate_hire_date (no future dates)
- [x] Email uniqueness enforced by ModelSerializer UniqueValidator (auto from model)
- [x] API tests: 4 tests (valid create, duplicate email, future date, missing fields)
- [x] EmployeeForm.vue: create mode with all fields, HTML5 validation, server error display
- [x] Success message + redirect to list after creation

### US-003: Update Employee (done — API + Frontend; audit trail deferred)
- [x] Email immutability via validate_email() with self.instance check
- [x] PATCH support (partial update) already provided by ModelViewSet
- [x] API tests: 3 tests (patch field, email rejected, same email allowed)
- [x] EmployeeForm.vue: edit mode with pre-filled data, email disabled
- [x] EmployeeEditView.vue: fetches employee by route param, loading/error states

### US-004: Soft Delete (done — API + Frontend; restore deferred)
- [x] perform_destroy() override: sets is_active=False instead of deleting
- [x] API tests: 2 tests (soft delete preserves record, excluded from list)
- [x] ConfirmDialog.vue: reusable confirmation modal
- [x] Delete button in EmployeeList with confirm → re-fetch → success message

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

### EPIC 1 Frontend Completion (done)
- [x] Vue Router 4: 3 routes (/, /employees/new, /employees/:id/edit)
- [x] EmployeeForm.vue: dual-mode component (create/edit via props)
- [x] ConfirmDialog.vue: reusable modal for delete confirmation
- [x] 3 view components: EmployeeListView, EmployeeCreateView, EmployeeEditView
- [x] api.js expanded: fetchEmployee, createEmployee, updateEmployee, deleteEmployee
- [x] { data, error, status } pattern for structured error handling
- [x] Success messages via router query params + auto-clear after 3s
- [x] EmployeeList: action column (Modifica/Elimina), inline delete flow
- [x] Frontend tests: 19 total (2 App + 9 EmployeeForm + 8 EmployeeList)

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
- Vue Router: URL-based component dispatch, route params (:id), named routes
- RouterView: placeholder where router injects matched component
- RouterLink: SPA navigation without page reload
- Props: parent-to-child parameters (like SP arguments)
- computed(): derived auto-recalculating value (like computed column)
- watch() with immediate: true: reacts to prop changes, covers sync and async data arrival
- emit(): child-to-parent events (like RETURN from SP)
- v-model: two-way binding on inputs (reads AND writes)
- @submit.prevent: intercept form submission, prevent page reload
- PATCH vs PUT: partial update avoids immutable email conflict
- { data, error, status } pattern: 400 = business error (return), 500 = fatal (throw)
- Server-side per-field error display: map DRF errors to input borders + messages
- createMemoryHistory() in tests: needs explicit router.push('/') for isReady() to resolve

### Next steps:
- [x] EPIC 2: Contract management (US-005, US-006) — backend started in Week 2

---

## Week 2: EPIC 2 — Contract Management

### EPIC 2 Backend: Contract API (done)
- [x] Contract model: ForeignKey to Employee, TextChoices for contract_type + CCNL
- [x] DecimalField(10,2) for RAL (exact-precision NUMERIC, no floating-point issues)
- [x] end_date nullable: NULL = active contract (vs sentinel 9999-12-31 DWH pattern)
- [x] Migration 0002_contract: CREATE TABLE with FK, auto-index on employee_id
- [x] ContractSerializer: employee read-only (from URL), cross-field validate() for end_date > start_date
- [x] ContractViewSet: nested under Employee, get_queryset filters by employee_pk, perform_create injects employee
- [x] Nested URL routes: manual .as_view() mapping (no drf-nested-routers library)
- [x] API tests: 9 tests (CRUD + validation + isolation + 404)
- [x] Total backend tests: 22 (13 Employee + 9 Contract)

### EPIC 2 Frontend: Contract CRUD (done)
- [x] api.js: 5 new functions (fetchContract, fetchContracts, createContract, updateContract, deleteContract)
- [x] ContractList.vue: table with active/closed badges, RAL currency formatting, delete with ConfirmDialog
- [x] ContractForm.vue: dual-mode (create/edit), dropdown choices matching backend, optional end_date
- [x] 3 View wrappers: ContractListView, ContractCreateView, ContractEditView
- [x] Vue Router: 3 nested routes with :employeeId and :contractId params
- [x] EmployeeList.vue: "Contratti" link per ogni dipendente
- [x] Frontend tests: 22 new (12 ContractList + 10 ContractForm)
- [x] Total tests: 63 (22 backend + 41 frontend)

### Concepts mastered (EPIC 2 Backend):
- ForeignKey: Django equivalent of SQL FOREIGN KEY REFERENCES, with on_delete behavior
- related_name: reverse accessor (employee.contracts.all() instead of explicit JOIN)
- on_delete=CASCADE: DB cascade delete (like ON DELETE CASCADE in SQL)
- null=True + blank=True: required together for optional non-string fields (DB + validation layers)
- DateField vs DateTimeField: date-only for contracts, timestamp for audit fields
- NULL vs sentinel value (9999-12-31): application DB uses NULL, DWH uses sentinel (different paradigms)
- DecimalField → PostgreSQL NUMERIC: exact arithmetic, no floating-point errors
- validate() vs validate_<field>(): cross-field validation needs validate() with access to all fields
- data.get() for optional fields in validate(): handles PATCH where not all fields are sent
- Nested ViewSet: get_queryset filters by URL param, perform_create injects parent from URL
- get_object_or_404: returns 404 if parent resource doesn't exist (security + UX)
- .as_view() manual mapping: {"get": "list", "post": "create"} for nested routes without library
- Django model naming: singular (Contract, not Contracts), Django pluralizes automatically
- sqlmigrate: shows actual SQL generated by Django migration (useful for learning)
- Django auto-creates INDEX on ForeignKey columns (unlike SQL Server where you must do it manually)

### Concepts mastered (EPIC 2 Frontend):
- Promise.all: parallel fetching of multiple API calls (employee + contracts simultaneously)
- Intl.NumberFormat('it-IT', { style: 'currency' }): native browser API for locale-aware currency formatting
- Derived state: active/closed badge computed from end_date === null (no redundant DB field)
- CSS capitalize: text-transform instead of JavaScript string manipulation
- Route params with two levels: :employeeId + :contractId in same URL (like JOIN on two FKs)
- Number() conversion: route.params are always strings, must convert to Number before passing as typed prop
- <input type="number"> + v-model: Vue auto-converts value to Number (not String)
- Frontend/backend choices alignment: <select> options must exactly match Django TextChoices values
- Optional field UX: remove HTML required + asterisk label for nullable backend fields
- Payload cleanup: delete empty string fields before API call ('' → omit, let backend default to null)
- Hard delete vs soft delete messaging: "irreversibile" for hard, "reversibile" for soft
- Guard clauses in API functions: fail-fast with explicit error when required params are missing

### EPIC 2 Phase 2: PDF Upload (done)
- [x] Django settings: MEDIA_ROOT, MEDIA_URL, media URL serving in development
- [x] Contract model: FileField(upload_to='contracts/%Y/%m/') with migration 0003
- [x] ContractSerializer: SerializerMethodField for document_url (absolute URL builder)
- [x] validate_document(): 3-level validation (extension, content-type, size 5MB)
- [x] api.js: FormData support (buildContractBody helper, detect FormData in apiRequest)
- [x] ContractForm.vue: file input, client-side PDF/size validation, existing document link
- [x] ContractList.vue: "PDF" column with Visualizza/dash
- [x] Backend tests: 7 new (upload, validation, document_url, PATCH add document)
- [x] Frontend tests: 8 new (file input, validation, preview link)
- [x] Total tests: 78 (29 backend + 49 frontend)

### Concepts mastered (EPIC 2 Phase 2):
- FileField: stores path in DB (VARCHAR), file on disk — not a BLOB
- MEDIA_ROOT vs MEDIA_URL: physical storage path vs HTTP URL prefix
- upload_to with strftime: 'contracts/%Y/%m/' creates date-based subdirectories
- multipart/form-data vs application/json: binary data needs multipart encoding
- FormData: browser API for building multipart request body
- Content-Type auto-detection: never set Content-Type manually on FormData (browser adds boundary)
- SerializerMethodField: computed column pattern, read-only, uses request.build_absolute_uri()
- File validation cascade: extension → content-type → size (defense in depth)
- Client-side validation mirroring: fail-fast UX before server roundtrip
- SimpleUploadedFile: Django test utility for creating fake uploaded files
- override_settings(MEDIA_ROOT=tempdir): isolate test file storage from real MEDIA_ROOT
- if settings.DEBUG: urlpatterns +=: serve media files only in development

### EPIC 2 Phase 3: Expiration Indicator + Bug Fixes (done)
- [x] Backend: is_expiring SerializerMethodField (computed, no migration)
- [x] Frontend: 4-state badge (Pianificato/In Scadenza/Attivo/Scaduto) replacing 2-state (Attivo/Chiuso)
- [x] Bug fix: end_date clearing in edit mode (PATCH sends null, not omit)
- [x] Bug fix: isort import order in urls.py (CI green)
- [x] Backend tests: 4 new (expiration edge cases with timedelta)
- [x] Frontend tests: 3 new (Pianificato, In Scadenza, end_date null PATCH)
- [x] Total tests: 85 (33 backend + 52 frontend)

### Concepts mastered (EPIC 2 Phase 3):
- SerializerMethodField pattern reuse: is_expiring mirrors document_url (computed, read-only)
- Boundary condition testing: today-30, today+15, today+90 for expiration window
- PATCH semantics: omitting field = "don't change" vs sending null = "set to null"
- v-if/v-else-if/v-else chain: order matters (like SQL CASE WHEN — first match wins)
- String date comparison: YYYY-MM-DD lexicographic order matches chronological order
- isort: Python import sorting tool — alphabetical within groups (stdlib, third-party, local)

### Next steps:
- [x] EPIC 3: Onboarding automation — Phase 1 done in Week 3

---

## Week 3: EPIC 3 — Onboarding Automation (Phase 1)

### EPIC 3 Phase 1: Onboarding Checklist — Full Stack (done)

#### Backend: Models + API (done)
- [x] OnboardingTemplate model: lookup table (name, description, order, is_active soft delete)
- [x] OnboardingStep model: fact/bridge table (employee FK CASCADE, template FK PROTECT)
- [x] unique_together = ["employee", "template"] — composite UNIQUE constraint
- [x] Migration 0004_onboarding_models
- [x] OnboardingTemplateSerializer: standard CRUD
- [x] OnboardingStepSerializer: denormalized fields via source="template.name" (JOIN equivalent)
- [x] OnboardingTemplateViewSet: ModelViewSet with soft delete (is_active=False)
- [x] OnboardingStepViewSet: custom create() for idempotent bulk create, perform_update() auto-sets completed_at
- [x] Nested URLs: /api/employees/{id}/onboarding/ and /api/employees/{id}/onboarding/{step_id}/
- [x] select_related("template") for N+1 query prevention
- [x] http_method_names = ["get", "post", "patch"] — no PUT/DELETE on steps
- [x] Backend tests: 16 new (6 template + 10 steps)
- [x] Total backend tests: 49 (33 existing + 16 onboarding)

#### Frontend: Components + Views (done)
- [x] api.js: 8 new functions (5 template CRUD + 3 onboarding steps)
- [x] Vue Router: 4 new routes (3 template + 1 checklist), total 10
- [x] OnboardingTemplateList.vue: CRUD table with soft delete, ConfirmDialog, success messages
- [x] OnboardingTemplateForm.vue: create/edit dual-mode (same pattern as EmployeeForm)
- [x] OnboardingChecklist.vue: progress bar, checkbox toggle, "Avvia Onboarding" button
- [x] 4 View wrappers: TemplateListView, TemplateCreateView, TemplateEditView, ChecklistView
- [x] App.vue: "Template Onboarding" nav link in header
- [x] EmployeeList.vue: "Onboarding" link per employee in actions column
- [x] Frontend tests: 30 new (9 TemplateList + 9 TemplateForm + 12 Checklist)
- [x] Total frontend tests: 82 (52 existing + 30 onboarding)

#### Total tests: 131 (49 backend + 82 frontend)

### Concepts mastered (EPIC 3 Phase 1 Backend):
- on_delete=PROTECT: equivalent to SQL RESTRICT — prevents parent deletion if children exist
- on_delete=CASCADE vs PROTECT: different policies for different FK semantics (employee owns steps, template is referenced)
- unique_together: composite UNIQUE constraint — one step per (employee, template) pair
- bulk_create(): single INSERT query instead of N queries — like INSERT INTO ... SELECT ... FROM templates
- select_related(): SQL JOIN at query time to avoid N+1 problem (1 query instead of N+1)
- source="template.name" on serializer: read through FK — equivalent to SELECT t.name FROM steps s JOIN templates t
- ViewSet create() override: custom bulk logic replacing standard single-resource create
- perform_update() override: hook to auto-manage computed fields (completed_at) on state transitions
- http_method_names: restrict allowed HTTP methods at ViewSet level (no PUT = no full replacement, no DELETE = steps persist)
- Idempotent POST: check existing records before insert, skip duplicates (like INSERT ... ON CONFLICT DO NOTHING)
- Defense in depth: PROTECT on FK + soft delete on template = two layers preventing data loss

### Concepts mastered (EPIC 3 Phase 1 Frontend):
- computed() for derived progress: totalSteps, completedSteps, progressPercent — reactive recalculation
- Promise.all for parallel fetch: employee + steps loaded simultaneously (like parallel SQL queries)
- Conditional rendering chains: v-if (loading) → v-else-if (error) → v-if (no steps) → v-else (checklist)
- Optimistic vs server-confirmed UI: toggle sends PATCH, waits for server response, updates local state with server data
- Progress bar with dynamic width: :style="{ width: percent + '%' }" + Tailwind classes for color
- @click.stop on nested clickable elements: prevent event bubbling from checkbox to parent li

### EPIC 3 Phase 2: Django Signals — Auto-Create Onboarding (done)
- [x] Service Layer: `services.py` with `create_onboarding_steps_for_employee()` (extracted from ViewSet)
- [x] Signal: `signals.py` with `post_save` receiver on Employee (`created=True` guard)
- [x] Registration: `apps.py` `ready()` method to import signals module
- [x] Refactoring: `OnboardingStepViewSet.create()` delegates to service (DRY)
- [x] Tests: 7 new signal tests + 1 existing test fixed
- [x] Total backend tests: 56 (49 existing + 7 signal)

### Concepts mastered (EPIC 3 Phase 2):
- Django Signals: application-level equivalent of database triggers (post_save ≈ AFTER INSERT)
- `created` parameter: True on INSERT, False on UPDATE — reliable way to distinguish operations
- `**kwargs` in signal receivers: forward-compatibility convention (Django may add new params)
- `ready()` in AppConfig: official place for side-effect imports (signal registration)
- `@receiver` decorator: cleaner alternative to `signal.connect()` for connecting handlers
- Service Layer pattern: extract business logic from views/signals into reusable functions (like stored procedures)
- DRY refactoring: ViewSet + Signal both call the same service function
- Signal limitations vs DB triggers: `bulk_create()`, `update()`, raw SQL bypass signals entirely
- `noqa: F401`: tells linters to ignore "unused import" when import is for side effects

### EPIC 3 Phase 3: Welcome Email — Email di Benvenuto (done)
- [x] Django settings: EMAIL_BACKEND (console in dev, env-configurable), DEFAULT_FROM_EMAIL
- [x] Service function: `send_welcome_email()` in services.py (plain text, Italian body)
- [x] Signal extended: post_save calls both `create_onboarding_steps` + `send_welcome_email`
- [x] .env.example: documented email variables
- [x] Tests: 9 new email tests (content, recipient, from, guards for update/soft-delete, API e2e)
- [x] Total backend tests: 65 (56 existing + 9 email)

### Concepts mastered (EPIC 3 Phase 3):
- `send_mail()`: Django built-in, equivalent to SQL Server `sp_send_dbmail`
- EMAIL_BACKEND Strategy Pattern: same `send_mail()` call, different backend per environment
- `console.EmailBackend`: prints email to stdout (visible in Docker logs)
- `locmem.EmailBackend`: Django TestCase auto-uses this, populates `mail.outbox` list
- `mail.outbox`: in-memory list of sent emails in tests (like a `dbo.email_log` table)
- `get_role_display()`: auto-generated method for TextChoices fields (like JOIN to lookup table)
- `date.fromisoformat()`: handles string-to-date when signal receives in-memory instance
- Signal receives in-memory instance: `create(hire_date="...")` keeps string, DB adapter converts
- `fail_silently=False`: explicit errors vs silent swallowing (like RAISERROR vs TRY/CATCH with no re-throw)
- `mail.outbox.clear()`: manual reset within same test when testing post-creation behavior

### EPIC 3 Phase 4: Celery + Async Tasks (done)
- [x] Docker: Redis 7 Alpine service + Celery worker service (5 services total)
- [x] Celery app config: `celery.py` with autodiscover + `__init__.py` import
- [x] Django settings: `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, JSON serialization
- [x] Task: `send_welcome_email_task` with `shared_task`, `bind=True`, `max_retries=3`
- [x] Signal refactored: onboarding steps sync, email async via `.delay(pk)`
- [x] Test config: `conftest.py` with `CELERY_TASK_ALWAYS_EAGER=True` fixture
- [x] Tests: 5 new Celery tests (task execution, retry, nonexistent PK, signal mock)
- [x] Total backend tests: 70 (65 existing + 5 Celery)

### Concepts mastered (EPIC 3 Phase 4):
- Celery: distributed task queue — equivalent to SQL Agent (Producer/Broker/Worker)
- Redis: in-memory key-value store used as message broker (like Service Broker queue)
- `shared_task`: decorator that registers function as async task (like SP registered as Agent job step)
- `bind=True`: gives task access to `self` for `self.retry()` (self-referencing SP)
- `.delay(pk)`: fire-and-forget — queues task on Redis and returns immediately
- Pass PK not object: Celery serializes params as JSON, model instances aren't serializable
- `max_retries` + `default_retry_delay`: automatic retry on transient failures (SMTP timeouts)
- Lazy imports in tasks: prevent circular imports at worker startup (Django may not be fully loaded)
- `CELERY_TASK_ALWAYS_EAGER`: execute tasks inline during tests (no Redis needed)
- `CELERY_TASK_EAGER_PROPAGATES`: exceptions bubble up to caller in eager mode (for test debugging)
- `conftest.py` with `autouse=True` fixture: applies settings to all tests automatically
- `patch.object(task, "retry")`: mock retry method to test retry behavior without actually retrying
- `autodiscover_tasks()`: scans INSTALLED_APPS for `tasks.py` modules (like Agent scanning for SPs)

### Next steps:
- [ ] EPIC 4: Dashboard & Analytics
