# Week 4 - EPIC 4: Dashboard & Analytics (continued)

## Session 16 (2026-03-03) - Django Cache Framework (EPIC 4 Phase 3)

**Focus**: Django low-level cache API, Redis as cache backend, signal-based invalidation, test isolation

**What I built:**
- settings.py: CACHES config (Redis DB 1, separate from Celery DB 0) + CACHE_DASHBOARD_TTL
- DashboardView: cache.get() / cache.set() wrapping existing aggregate queries
- signals.py: invalidate_dashboard_cache() connected to post_save/post_delete on 3 models
- conftest.py: use_local_cache fixture (LocMemCache for test isolation, like celery_eager_mode)
- 6 new cache tests: hit, miss, invalidation x3, data integrity
- Total: 176 tests (85 backend + 91 frontend)

**What I learned:**
- Django Cache Framework = application-level staging table
  - cache.get(key): SELECT FROM staging WHERE key = ? (returns None on MISS)
  - cache.set(key, data, ttl): INSERT INTO staging WITH EXPIRY
  - cache.delete(key): DELETE FROM staging WHERE key = ?
- `is not None` guard: critical for distinguishing cache MISS (None) from cached falsy values (0, {}, [])
  - `if cached:` would treat 0 as MISS — wrong! `if cached is not None:` is correct
  - SQL analogy: `IS NULL` (no value) vs `= 0` (has a value that happens to be zero)
- Redis DB isolation: DB 0 for Celery broker, DB 1 for cache
  - Like separate schemas in SQL Server — same server, logically isolated
  - Redis has 16 logical databases (0-15), no authentication between them
- RedisCache built-in since Django 4.0: no django-redis package needed
  - The `redis` Python package (already in requirements for Celery) is the only dependency
- Signal-based invalidation = AFTER trigger that does REFRESH MATERIALIZED VIEW
  - post_save on Employee, Contract, OnboardingStep → cache.delete()
  - post_delete on Contract (hard delete) → cache.delete()
  - Employee uses soft delete (no post_delete needed — is_active=False triggers post_save)
- post_save.connect() vs @receiver: imperative form allows connecting same handler to multiple senders
  - @receiver needs one decorator per model, connect() is one line per model
- Constant duplication (DASHBOARD_CACHE_KEY in views.py and signals.py):
  - Alternative: import from views in signals → creates cross-import dependency
  - Risk: if someone adds import from signals in views → circular ImportError
  - Rule: signals should not import from views (keep dependency graph acyclic)
- LocMemCache in tests: in-memory cache, no Redis dependency
  - Same pattern as CELERY_TASK_ALWAYS_EAGER: replace external service with in-process alternative
  - conftest.py fixture with autouse=True: applies to all tests automatically
  - cache.clear() in fixture: ensures test isolation (no stale data between tests)
- assertNumQueries(0): the definitive proof that cache works
  - Tests the BEHAVIOR (zero DB queries) not the IMPLEMENTATION (cache.get was called)
  - Better than mocking cache.get() because it proves end-to-end that the DB is actually spared

**Key pattern: Low-level cache API = staging table:**
```
Senza cache:  GET → 5 query DB → Response  (ogni volta)
Con cache:    GET → cache.get() → HIT?  → Response (0 query)
                                → MISS? → 5 query → cache.set() → Response

Invalidazione: Employee.save() → post_save signal → cache.delete()
               Prossimo GET → cache MISS → ricalcola
```

**Key pattern: Cache flow = materialized view lifecycle:**
| SQL Concept | Django Cache Equivalent |
|---|---|
| CREATE MATERIALIZED VIEW | First GET: cache.set(key, data, ttl) |
| SELECT FROM materialized_view | Subsequent GETs: cache.get(key) |
| REFRESH MATERIALIZED VIEW | Signal: cache.delete(key) |
| DROP MATERIALIZED VIEW | cache.clear() (test cleanup) |
| View expiry (hypothetical) | TTL: data auto-expires after N seconds |

**Key pattern: Test fixture strategy (conftest.py):**
| External Service | Production Backend | Test Replacement | Fixture |
|---|---|---|---|
| Redis (Celery) | redis://redis:6379/0 | CELERY_TASK_ALWAYS_EAGER | celery_eager_mode |
| Redis (Cache) | RedisCache on DB 1 | LocMemCache | use_local_cache |
| SMTP (Email) | smtp.EmailBackend | locmem.EmailBackend (auto) | Django TestCase |

**Key pattern: assertNumQueries — testing behavior, not implementation:**
```python
# BAD: testing implementation (what functions are called)
with patch("django.core.cache.cache.get") as mock:
    mock.return_value = cached_data
    response = client.get(url)
    mock.assert_called_once()  # Proves cache.get was called, not that DB was spared

# GOOD: testing behavior (what actually happens)
with self.assertNumQueries(0):       # Zero SQL queries executed
    response = self.client.get(url)  # If this passes, cache WORKS — end of story
```

**Next steps:**
- [x] EPIC 4 Phase 4: Auto-refresh frontend (polling every 5 min, onUnmounted cleanup)

---

## Session 17 (2026-03-04) - Auto-refresh Polling (EPIC 4 Phase 4)

**Focus**: setInterval/clearInterval polling, Vue lifecycle cleanup (onUnmounted), fake timers in Vitest

**What I built:**
- DashboardPanel.vue: extracted loadStats() function, setInterval(5min), clearInterval on unmount
- Dashboard.spec.js: 4 new polling tests with vi.useFakeTimers() / vi.advanceTimersByTime()
- Total: 180 tests (85 backend + 95 frontend)

**What I learned:**
- Polling = periodic API call via setInterval(), like a SQL Agent Job on a schedule
  - setInterval returns an ID you must save to clear it later
  - clearInterval(id) stops the timer — like sp_stop_job
- onUnmounted lifecycle hook: cleanup code that runs when component is destroyed
  - Without it, navigating away leaves the timer running → memory leak
  - Like a trigger that disables an Agent Job when you close the report
- setInterval vs setTimeout ricorsivo:
  - setInterval: fires every N ms regardless of response time (fixed cadence)
  - setTimeout ricorsivo: fires N ms AFTER previous call completes (drift-free but variable cadence)
  - For 5-min dashboard refresh, fixed cadence is fine — no need for drift prevention
- `let intervalId` vs `ref(intervalId)`: timer ID isn't used in template → no reactivity needed
  - Rule: use ref() only for data that drives the UI, plain variables for internal bookkeeping
- vi.useFakeTimers(): replaces real setInterval/setTimeout with controllable versions
  - vi.advanceTimersByTime(ms): manually advance clock to trigger intervals
  - vi.useRealTimers(): restore real timers in afterEach (test isolation)
- Error recovery pattern: error.value = null in try block clears previous errors on successful refresh
  - If API fails → shows error → API recovers on next tick → error disappears automatically
  - Like an alerting system that auto-resolves when the issue is fixed

**Key pattern: Lifecycle cleanup = resource management:**
```
onMounted    → acquire resource (start timer, open connection, subscribe)
onUnmounted  → release resource (stop timer, close connection, unsubscribe)

SQL analogy:
BEGIN TRAN    → onMounted (acquire locks/resources)
COMMIT/ROLLBACK → onUnmounted (release locks/resources)
```

**Key pattern: Fake timers in tests:**
```javascript
// Instead of waiting 5 real minutes in a test:
vi.useFakeTimers()                    // Replace real timers
vi.advanceTimersByTime(5 * 60 * 1000) // Jump forward 5 min instantly
await flushPromises()                 // Let async callbacks resolve
// Assert that the interval callback fired
```

**Next steps:**
- [ ] EPIC 5: Authentication & Permissions (US-011, US-012)
