"""Celery tasks per l'app employees.

TASK = unità di lavoro asincrono, equivalente a un job step di SQL Agent.
Ogni task viene serializzato in JSON, messo in coda su Redis (broker),
e poi eseguito da un worker Celery separato.

Pattern chiave:
    - Il task riceve un PK (integer), NON un oggetto Python.
      Motivo: l'oggetto non è JSON-serializzabile, il PK sì.
      Equivale a: un job step SQL Agent riceve @employee_id INT,
      non l'intera riga della tabella.
    - Il task fa la query per recuperare l'oggetto dal DB.
      Equivale a: SELECT * FROM employees WHERE id = @employee_id
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, employee_id):
    """Invia l'email di benvenuto in modo asincrono.

    Equivale a un job step di SQL Agent che:
    1. Riceve @employee_id come parametro
    2. Fa SELECT per caricare i dati del dipendente
    3. Chiama sp_send_dbmail
    4. Se fallisce, si rischedula (retry con backoff)

    Args:
        self: riferimento al task (bind=True). Necessario per self.retry().
              Come una SP che può richiamare sé stessa con EXEC sp_retry.
        employee_id: PK del dipendente (int, JSON-serializzabile).

    Raises:
        Employee.DoesNotExist: se il dipendente non esiste più nel DB.
            Non fa retry perché è un errore permanente (non transiente).
    """
    from .models import Employee
    from .services import send_welcome_email

    try:
        employee = Employee.objects.get(pk=employee_id)
    except Employee.DoesNotExist:
        logger.error("Employee %s not found, skipping welcome email.", employee_id)
        return

    try:
        send_welcome_email(employee)
        logger.info("Welcome email sent to %s", employee.email)
    except Exception as exc:
        logger.warning(
            "Failed to send welcome email to employee %s: %s. Retrying...",
            employee_id,
            exc,
        )
        raise self.retry(exc=exc)
