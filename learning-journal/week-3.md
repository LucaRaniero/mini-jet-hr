# Week 3 - EPIC 3: Onboarding Automation

## Session 10 (2026-02-20) - Onboarding Checklist Full Stack (EPIC 3 Phase 1)

**Focus**: Lookup/bridge table pattern, bulk operations, idempotent API, interactive checklist

**What I built:**
- OnboardingTemplate model (lookup table): name, description, order, is_active soft delete
- OnboardingStep model (fact/bridge table): employee FK (CASCADE), template FK (PROTECT), unique_together
- OnboardingTemplateSerializer + OnboardingStepSerializer (denormalized fields via source="fk.field")
- OnboardingTemplateViewSet: standard CRUD with soft delete
- OnboardingStepViewSet: custom create() for idempotent bulk create, perform_update() auto-sets completed_at
- Nested URLs: /api/employees/{id}/onboarding/ and /api/onboarding-templates/
- Frontend: TemplateList, TemplateForm, Checklist (progress bar, toggle, "Avvia Onboarding" button)
- 46 new tests (16 backend + 30 frontend), total 131

**What I learned:**
- on_delete=PROTECT: equivalent to SQL RESTRICT — prevents parent deletion if children exist
- CASCADE vs PROTECT: different FK policies for different semantics (employee owns steps, template is referenced)
- unique_together: composite UNIQUE constraint at DB level — one step per (employee, template) pair
- bulk_create(): single INSERT query instead of N — like INSERT INTO ... SELECT ... FROM templates
- select_related("template"): SQL JOIN at query time to avoid N+1 problem (1 query vs N+1)
- source="template.name" on serializer: read through FK, equivalent to SELECT t.name FROM steps s JOIN templates t
- ViewSet create() override: custom bulk logic replacing standard single-resource creation
- perform_update() override: hook to auto-manage computed fields (completed_at) on state transitions
- http_method_names: restrict allowed HTTP methods (no PUT = no full replacement, no DELETE = steps persist)
- Idempotent POST: check existing records before insert — like INSERT ... ON CONFLICT DO NOTHING
- Defense in depth: PROTECT on FK + soft delete on template = two layers preventing data loss

**Key pattern: Lookup/bridge table (data modeling):**
| SQL Concept | Django Equivalent |
|---|---|
| Lookup/dimension table | OnboardingTemplate (reusable task definitions) |
| Fact/bridge table | OnboardingStep (employee-specific progress records) |
| Composite UNIQUE | unique_together = ["employee", "template"] |
| INSERT ... SELECT FROM lookup | bulk_create() with list comprehension from queryset |
| ON CONFLICT DO NOTHING | Check existing_template_ids set before creating |

**Frontend patterns:**
- computed() for derived progress: totalSteps, completedSteps, progressPercent — reactive recalculation
- Promise.all for parallel fetch: employee + steps loaded simultaneously
- Optimistic vs server-confirmed UI: toggle sends PATCH, waits for server response, updates local state
- Progress bar with dynamic width: :style="{ width: percent + '%' }" + Tailwind color classes
- @click.stop: prevent event bubbling from checkbox to parent li

---

## Session 11 (2026-02-23) - Django Signals + Service Layer (EPIC 3 Phase 2)

**Focus**: Django Signals (post_save), Service Layer pattern, DRY refactoring

**What I built:**
- services.py: create_onboarding_steps_for_employee() — extracted business logic from ViewSet
- signals.py: post_save receiver on Employee with created=True guard
- apps.py: ready() method to register signal module (side-effect import)
- Refactored OnboardingStepViewSet.create() to delegate to service function (DRY)
- 7 new signal tests + 1 existing test fixed, total 138 (56 backend + 82 frontend)

**What I learned:**
- Django Signals = application-level equivalent of SQL AFTER INSERT triggers
- post_save signal fires after .save() or .create() completes (INSERT or UPDATE)
- `created` parameter: True on INSERT, False on UPDATE — the reliable way to distinguish
- pre_save vs post_save: must use post_save because instance.pk may be None before save
- **kwargs in signal receivers: forward-compatibility convention (Django may add new params)
- @receiver decorator: connects handler to signal (alternative to signal.connect())
- AppConfig.ready(): official place for side-effect imports — runs once when app registry is loaded
- noqa: F401: tells linters "this import is intentionally unused — it's for side effects"
- Service Layer pattern: extract business logic from views/signals into reusable functions
  - Like a stored procedure called by both a trigger and an API endpoint
  - ViewSet handles HTTP concerns, service handles business logic
- Signal limitations vs DB triggers:
  - bulk_create(), update(), raw SQL all BYPASS signals
  - DB triggers fire on ANY INSERT regardless of origin
  - In enterprise, combine signals (standard flow) + integration tests (edge cases)

**Key pattern: Signal ≈ SQL AFTER INSERT trigger:**
```
-- SQL Trigger
CREATE TRIGGER trg_employee_onboarding
AFTER INSERT ON employees
FOR EACH ROW
    INSERT INTO onboarding_steps (employee_id, template_id)
    SELECT NEW.id, id FROM onboarding_templates WHERE is_active = 1;

-- Django Signal (equivalent)
@receiver(post_save, sender=Employee)
def auto_create_onboarding_steps(sender, instance, created, **kwargs):
    if created:
        create_onboarding_steps_for_employee(instance)
```

**Key pattern: Service Layer = Shared stored procedure:**
```
-- SQL: SP called by both trigger and API
CREATE PROCEDURE sp_create_onboarding_steps @employee_id INT AS ...

-- Python: function called by both signal and ViewSet
def create_onboarding_steps_for_employee(employee):
    ...  # Same logic, one place (DRY)
```

**Key pattern: Signal operations coverage:**
| Operation | Signal fires? | SQL trigger fires? |
|---|---|---|
| Employee.objects.create() | Yes | Yes |
| employee.save() | Yes | Yes |
| Employee.objects.bulk_create() | **No** | Yes |
| Employee.objects.update() | **No** | Yes |
| Raw SQL (cursor.execute) | **No** | Yes |

**Comprehension check answers:**
1. `created=True` vs `is_active`: using is_active would fire on every .save() of active employees (updates, not just inserts)
2. post_save not pre_save: need instance.pk to exist for FK, and need constraints validated first
3. bulk_create bypasses signals: key limitation vs SQL triggers

**Next steps:**
- [x] EPIC 3 Phase 3: Email di benvenuto — done in Session 12
- [x] EPIC 3 Phase 4: Celery + async tasks — done in Session 13
- [ ] EPIC 4: Dashboard & Analytics

---

## Session 12 (2026-02-24) - Welcome Email (EPIC 3 Phase 3)

**Focus**: Django email system, Strategy Pattern, mail.outbox testing

**What I built:**
- settings.py: EMAIL_BACKEND (console in dev) + DEFAULT_FROM_EMAIL via django-environ
- services.py: send_welcome_email() — plain text email with employee data
- signals.py: extended post_save to call send_welcome_email after onboarding steps
- .env.example: documented email environment variables
- 9 new email tests (content, recipient, from, update/soft-delete guards, API e2e)
- Total: 147 tests (65 backend + 82 frontend)

**What I learned:**
- Django Email Backend = Strategy Pattern: stessa send_mail(), backend diverso per ambiente
  - console → stdout (Docker logs), locmem → mail.outbox (test), smtp → reale (prod)
- send_mail(): equivale a SQL Server sp_send_dbmail — subject, body, from, recipients
- get_role_display(): metodo auto-generato per campi con choices (come JOIN a lookup table)
- mail.outbox: lista Python di email inviate in test (come tabella dbo.email_log)
  - Django TestCase auto-sostituisce il backend con locmem e svuota outbox tra i test
- mail.outbox.clear(): reset manuale DENTRO lo stesso test quando serve testare post-creazione
- fail_silently=False: errori espliciti — in produzione useremmo Celery con retry

**Bug scoperto e risolto:**
- hire_date arriva come stringa nel signal quando si usa `create(hire_date="2024-01-15")`
- Django `__init__` assegna il valore raw, la conversione str→date avviene solo nel DB adapter
- Il signal post_save riceve l'istanza in-memoria (con stringa), non quella dal DB (con date)
- Fix: `isinstance(hire_date, str)` guard + `date.fromisoformat()` conversion

**Key pattern: Django Email Backend = Strategy Pattern:**
| Ambiente | EMAIL_BACKEND | Effetto |
|----------|--------------|---------|
| Dev | console.EmailBackend | Stampa su stdout (Docker logs) |
| Test | locmem.EmailBackend (auto) | Popola mail.outbox (lista Python) |
| Prod | smtp.EmailBackend | Invia via server SMTP reale |

**Key pattern: mail.outbox = dbo.email_log:**
```python
# Test: "verifica che l'email sia stata inviata"
from django.core import mail

Employee.objects.create(...)        # Signal → send_mail() → outbox
self.assertEqual(len(mail.outbox), 1)                    # COUNT(*)
self.assertEqual(mail.outbox[0].to, ["mario@example.com"])  # SELECT [to]
self.assertIn("Mario", mail.outbox[0].subject)           # WHERE subject LIKE '%Mario%'
```

**Comprehension check answers:**
1. Ordine nel signal: prima onboarding steps, poi email — l'email dice "checklist avviata" (deve essere vero), e se l'email fallisce gli step esistono comunque
2. mail.outbox.clear(): serve perché Employee.objects.create() nel test invia l'email di creazione — senza clear, l'assert `len(outbox) == 0` dopo update fallirebbe con 1 (l'email della creazione)
3. hire_date stringa nel signal: Django `__init__` non converte i tipi, il DB adapter lo fa. Il signal riceve l'istanza in-memoria con il valore originale passato a create()

**Next steps:**
- [x] EPIC 3 Phase 4: Celery + async tasks — done in Session 13
- [ ] EPIC 4: Dashboard & Analytics

---

## Session 13 (2026-02-24) - Celery + Async Tasks (EPIC 3 Phase 4)

**Focus**: Celery task queue, Redis broker, async email, retry logic, test isolation

**What I built:**
- docker-compose.yml: 2 nuovi servizi (Redis 7 Alpine + Celery worker)
- minijet/celery.py: Celery app config con autodiscover_tasks()
- minijet/__init__.py: import celery app all'avvio Django
- settings.py: CELERY_BROKER_URL, CELERY_RESULT_BACKEND, JSON serialization
- employees/tasks.py: send_welcome_email_task (shared_task, bind, retry)
- employees/signals.py: refactoring da chiamata sincrona a .delay(pk)
- conftest.py: CELERY_TASK_ALWAYS_EAGER fixture (autouse)
- 5 nuovi test Celery (task diretto, retry, PK inesistente, signal mock)
- Total: 152 tests (70 backend + 82 frontend)

**What I learned:**
- Celery = distributed task queue, equivalente di SQL Agent
  - Producer (Django): mette task in coda con .delay()
  - Broker (Redis): coda messaggi (come Service Broker queue)
  - Worker (celery worker): processo separato che esegue i task
- Redis: key-value store in-memory, NON un DB vettoriale — velocissimo per code messaggi
- shared_task: registra funzione come task senza import diretto dell'app Celery
- bind=True: dà accesso a self per self.retry() (come SP che richiama sé stessa)
- .delay(pk): fire-and-forget — accoda su Redis e torna subito
- Serializzazione JSON: i task ricevono PK (int), non oggetti Python (non serializzabili)
- Lazy imports in tasks.py: Django potrebbe non essere completamente caricato all'avvio del worker
- max_retries=3 + default_retry_delay=60: retry automatico su errori transienti (SMTP timeout)
- CELERY_TASK_ALWAYS_EAGER: esegue task inline (sincrono) nei test, senza Redis
- conftest.py con autouse=True: fixture globale che si applica a tutti i test automaticamente
- unittest.mock.patch: sostituire oggetti con mock per testare in isolamento

**Key pattern: Celery ≈ SQL Agent:**
```
-- SQL Agent: schedula job e torna subito
EXEC sp_start_job @job_name = 'SendWelcomeEmail', @step_name = 'Step1'

-- Celery: accoda task e torna subito
send_welcome_email_task.delay(employee_id)  # → Redis → Worker
```

**Key pattern: Task = thin wrapper around service function:**
```python
# tasks.py — riceve PK, carica oggetto, chiama service
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, employee_id):
    from .models import Employee       # Lazy import
    from .services import send_welcome_email
    employee = Employee.objects.get(pk=employee_id)  # SELECT
    try:
        send_welcome_email(employee)   # Chiama la business logic
    except Exception as exc:
        raise self.retry(exc=exc)      # Retry su errore
```

**Key pattern: CELERY_TASK_ALWAYS_EAGER = inline execution:**
| Modalità | Flusso | Uso |
|---|---|---|
| Normale (prod/dev) | .delay() → Redis → Worker → esecuzione | Runtime |
| Eager (test) | .delay() → esecuzione immediata inline | Test (no Redis) |

**Comprehension check answers:**
1. PK non oggetto: Celery serializza in JSON per metterlo in Redis. Un integer è JSON-serializzabile, un oggetto Employee no (TypeError)
2. Lazy imports: all'avvio del worker, Celery carica tasks.py ma Django potrebbe non aver finito di registrare tutti i modelli. Import dentro la funzione garantisce che Django sia pronto
3. CELERY_TASK_ALWAYS_EAGER: esegue il task inline nel processo chiamante, come una chiamata a funzione normale. Redis non serve, mail.outbox funziona

**Next steps:**
- [x] EPIC 4 Phase 1: Dashboard API — done in Session 14

---

## Session 14 (2026-02-25) - Dashboard API (EPIC 4 Phase 1)

**Focus**: Django aggregations, ORM GROUP BY, APIView vs ViewSet

**What I built:**
- DashboardView (APIView): single read-only endpoint aggregating data from 3 tables
- 5 aggregate queries: employee stats, contract expiration, onboarding progress, headcount trend, department distribution
- URL route: GET /api/dashboard/stats/
- 9 new tests covering every metric and edge case (empty state, active/inactive, boundary dates)
- Total: 161 tests (79 backend + 82 frontend)

**What I learned:**
- aggregate() = SELECT COUNT(*) FROM ... senza GROUP BY → ritorna UN dizionario (una riga)
- annotate() = SELECT col, COUNT(*) GROUP BY col → ritorna N righe (un QuerySet)
- Count("id", filter=Q(...)): aggregazione condizionale → equivale a COUNT(*) FILTER (WHERE ...)
- TruncMonth("hire_date"): database function → genera DATE_TRUNC('month', hire_date) in PostgreSQL
- values("month").annotate(count=Count("id")): la catena per GROUP BY — values() definisce le colonne di raggruppamento
- exclude(department=""): filtro negativo → WHERE department != ''
- APIView vs ViewSet: endpoint custom read-only vs CRUD auto-generato da modello
- pytest vs manage.py test: conftest.py con fixture autouse funziona solo con pytest (non Django test runner)

**Key pattern: Django aggregations = SQL GROUP BY:**

| SQL | Django ORM |
|-----|-----------|
| `SELECT COUNT(*) FROM employees` | `Employee.objects.aggregate(total=Count("id"))` |
| `COUNT(*) FILTER (WHERE is_active)` | `Count("id", filter=Q(is_active=True))` |
| `DATE_TRUNC('month', hire_date)` | `TruncMonth("hire_date")` |
| `SELECT col, COUNT(*) GROUP BY col` | `.values("col").annotate(count=Count("id"))` |
| `WHERE department != ''` | `.exclude(department="")` |

**Key pattern: aggregate() vs annotate():**
```
-- aggregate(): UNA riga
SELECT COUNT(*) AS total FROM employees;
→ Employee.objects.aggregate(total=Count("id"))
→ {'total': 42}

-- annotate(): N righe
SELECT department, COUNT(*) AS count FROM employees GROUP BY department;
→ Employee.objects.values("department").annotate(count=Count("id"))
→ QuerySet [{'department': 'Engineering', 'count': 15}, ...]
```

**Key pattern: APIView vs ViewSet:**
| | APIView | ViewSet |
|---|---------|---------|
| SQL equivalente | SP custom per report | CRUD auto-generate |
| Metodi | Solo quelli definiti (GET) | list, create, retrieve, update, destroy |
| Router | No (path manuale) | Sì (DefaultRouter) |
| Uso | Query aggregate, endpoint speciali | CRUD su un modello |

**Comprehension check answers:**
1. aggregate() non annotate() per employee stats: perché ci aspettiamo UN singolo dizionario (una riga totale), non una riga per ogni record
2. values("month") prima di annotate(): definisce la colonna del GROUP BY, esattamente come in SQL devi dichiarare GROUP BY prima di COUNT(*)
3. APIView non ViewSet: perché è solo lettura e non c'è un modello Dashboard — è una query aggregata su più tabelle

**Next steps:**
- [ ] EPIC 4 Phase 2: Frontend Dashboard + Chart.js (KPI cards, line chart, pie/bar chart)
- [ ] EPIC 4 Phase 3: Django Cache Framework (Redis cache backend, TTL)
- [ ] EPIC 4 Phase 4: Auto-refresh frontend (polling, onUnmounted cleanup)
