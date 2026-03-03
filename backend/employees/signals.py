"""Django signals per l'app employees.

SIGNALS = equivalente applicativo dei database trigger.
A differenza dei DB trigger (che scattano su qualsiasi INSERT/UPDATE),
i Django signals scattano solo quando si passa dall'ORM (.save(), .create()).
"""

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Contract, Employee, OnboardingStep
from .services import create_onboarding_steps_for_employee
from .tasks import send_welcome_email_task

# Stessa chiave usata in views.py — definita qui per evitare
# cross-import tra signals e views (fragilità ordine di import).
DASHBOARD_CACHE_KEY = "dashboard_stats"


@receiver(post_save, sender=Employee)
def auto_create_onboarding_steps(sender, instance, created, **kwargs):
    """Crea automaticamente gli step di onboarding e accoda l'email di benvenuto.

    Equivale a un AFTER INSERT trigger sulla tabella employees:
    - Onboarding steps: sincrono (INSERT veloce, deve completarsi prima dell'email)
    - Email: asincrono via Celery (.delay() = fire-and-forget in coda Redis)

    Args:
        sender: la classe del model (Employee). Fornito da Django.
        instance: l'oggetto Employee appena salvato.
        created: True se INSERT, False se UPDATE. Questo parametro
                 ci permette di NON scattare su:
                 - PATCH (aggiornamento dati)
                 - Soft delete (is_active=False + .save())
        **kwargs: convenzione Django per forward-compatibility.
                  Senza questo, il receiver si romperebbe se Django
                  aggiungesse nuovi parametri al signal in futuro.
    """
    if created:
        create_onboarding_steps_for_employee(instance)
        # .delay(pk) accoda il task su Redis e torna subito.
        # Il worker Celery lo eseguirà in un processo separato.
        # Passiamo il PK (int), non l'oggetto (non JSON-serializzabile).
        send_welcome_email_task.delay(instance.pk)


# ---------------------------------------------------------------------------
# Cache invalidation signals — equivalente di un AFTER INSERT/UPDATE/DELETE
# trigger che esegue REFRESH MATERIALIZED VIEW dashboard_stats.
#
# Ogni model che alimenta la dashboard (Employee, Contract, OnboardingStep)
# ha un signal che invalida la cache: il prossimo GET ricalcolerà i dati.
# ---------------------------------------------------------------------------


def invalidate_dashboard_cache(**kwargs):
    """Cancella la cache della dashboard.

    Chiamata da post_save/post_delete sui model che alimentano la dashboard.
    Equivale a: DELETE FROM staging_dashboard WHERE key = 'dashboard_stats'
    """
    cache.delete(DASHBOARD_CACHE_KEY)


# Employee: post_save copre INSERT e UPDATE (incluso soft delete via .save())
post_save.connect(invalidate_dashboard_cache, sender=Employee)

# Contract: post_save (INSERT/UPDATE) + post_delete (hard DELETE)
post_save.connect(invalidate_dashboard_cache, sender=Contract)
post_delete.connect(invalidate_dashboard_cache, sender=Contract)

# OnboardingStep: post_save copre toggle is_completed (PATCH)
post_save.connect(invalidate_dashboard_cache, sender=OnboardingStep)
