"""Service layer per la business logic degli employees.

SERVICE LAYER PATTERN: separa la logica di business dalle view (HTTP)
e dai signal (eventi). Equivale a una stored procedure richiamabile
da contesti diversi (trigger, API, management command, ecc.).
"""

from datetime import date

from django.conf import settings
from django.core.mail import send_mail

from .models import OnboardingStep, OnboardingTemplate


def create_onboarding_steps_for_employee(employee):
    """Crea gli step di onboarding da tutti i template attivi.

    Idempotente: gli step esistenti vengono preservati, solo quelli
    mancanti vengono creati. Se non ci sono template attivi, non fa nulla.

    SQL equivalente:
        INSERT INTO onboarding_steps (employee_id, template_id)
        SELECT %s, id FROM onboarding_templates
        WHERE is_active = 1
          AND id NOT IN (
              SELECT template_id FROM onboarding_steps
              WHERE employee_id = %s
          );

    Args:
        employee: istanza Employee per cui creare gli step.

    Returns:
        list[OnboardingStep]: gli step appena creati (può essere vuota).
    """
    templates = OnboardingTemplate.objects.filter(is_active=True)

    # Trova template per cui lo step esiste già (evita duplicati)
    existing_template_ids = set(
        OnboardingStep.objects.filter(employee=employee).values_list(
            "template_id", flat=True
        )
    )

    # Crea step solo per i template mancanti
    new_steps = [
        OnboardingStep(employee=employee, template=t)
        for t in templates
        if t.id not in existing_template_ids
    ]

    if new_steps:
        OnboardingStep.objects.bulk_create(new_steps)

    return new_steps


def send_welcome_email(employee):
    """Invia l'email di benvenuto a un nuovo dipendente.

    SQL equivalente:
        EXEC msdb.dbo.sp_send_dbmail
            @profile_name = 'HR_Profile',
            @recipients = @employee_email,
            @subject = 'Benvenuto!',
            @body = '...';

    Sincrona: blocca finché il backend non ha processato l'email.
    Con console backend è istantaneo (stampa su stdout).
    In produzione si userebbe Celery per renderla asincrona.

    Args:
        employee: istanza Employee a cui inviare l'email.

    Returns:
        int: numero di email inviate con successo (0 o 1).
    """
    subject = f"Benvenuto in Mini Jet HR, {employee.first_name}!"

    # hire_date può essere str ("2024-01-15") o date, a seconda di come
    # l'Employee è stato creato. Il signal riceve l'istanza in-memoria,
    # dove il valore potrebbe non essere ancora convertito da Django.
    # Analogo a: il trigger SQL riceve il tipo DATE dal DB, ma il signal
    # Django riceve il valore Python originale passato a .create().
    hire_date = employee.hire_date
    if isinstance(hire_date, str):
        hire_date = date.fromisoformat(hire_date)

    body = (
        f"Ciao {employee.first_name} {employee.last_name},\n"
        f"\n"
        f"Benvenuto/a nel team di Mini Jet HR!\n"
        f"\n"
        f"Ecco i tuoi dati:\n"
        f"  - Ruolo: {employee.get_role_display()}\n"
        f"  - Data di assunzione: {hire_date.strftime('%d/%m/%Y')}\n"
        f"\n"
        f"Il tuo processo di onboarding è già stato avviato. "
        f"Controlla la tua checklist per i prossimi passi.\n"
        f"\n"
        f"A presto,\n"
        f"Il team HR"
    )

    return send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[employee.email],
        fail_silently=False,
    )
