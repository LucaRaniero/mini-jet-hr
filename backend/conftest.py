"""Pytest configuration and shared fixtures.

conftest.py è il punto centralizzato per fixture (setup/teardown)
condivise da tutti i test. Equivale a un setUp() globale.
"""

import pytest


@pytest.fixture(autouse=True)
def celery_eager_mode(settings):
    """Execute Celery tasks synchronously during tests.

    CELERY_TASK_ALWAYS_EAGER = True: i task vengono eseguiti subito
    nel processo chiamante, SENZA passare da Redis.
    Equivale a: eseguire la stored procedure inline invece di
    schedulare un job SQL Agent.

    CELERY_TASK_EAGER_PROPAGATES = True: se il task lancia un'eccezione,
    questa si propaga al chiamante (utile per debug nei test).

    autouse=True: si applica automaticamente a TUTTI i test,
    senza doverlo dichiarare come parametro del test.
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
