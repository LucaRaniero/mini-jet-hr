"""Service layer per la business logic degli employees.

SERVICE LAYER PATTERN: separa la logica di business dalle view (HTTP)
e dai signal (eventi). Equivale a una stored procedure richiamabile
da contesti diversi (trigger, API, management command, ecc.).
"""

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
