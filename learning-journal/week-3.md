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
- [ ] EPIC 3 Phase 3: Email di benvenuto (console backend in dev)
- [ ] EPIC 3 Phase 4: Celery + async tasks
- [ ] EPIC 4: Dashboard & Analytics
