"""Django signals per l'app employees.

SIGNALS = equivalente applicativo dei database trigger.
A differenza dei DB trigger (che scattano su qualsiasi INSERT/UPDATE),
i Django signals scattano solo quando si passa dall'ORM (.save(), .create()).
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Employee
from .services import create_onboarding_steps_for_employee
from .tasks import send_welcome_email_task


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
