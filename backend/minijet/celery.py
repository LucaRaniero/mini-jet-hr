"""Celery application configuration for Mini Jet HR.

CELERY = distributed task queue, equivalente applicativo di SQL Agent.
Tre componenti:
    1. Producer (Django): mette task in coda (.delay())
    2. Broker (Redis): coda messaggi (come Service Broker queue)
    3. Worker (celery worker): processo separato che esegue i task

Questo modulo configura il componente Producer e viene importato
all'avvio di Django tramite minijet/__init__.py.
"""

import os

from celery import Celery

# Imposta il modulo settings Django PRIMA di creare l'app Celery.
# Senza questo, il worker non saprebbe quale progetto Django usare.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "minijet.settings")

# Crea l'istanza Celery. Il nome "minijet" è convenzionale (= nome progetto).
app = Celery("minijet")

# Legge le impostazioni CELERY_* da settings.py.
# namespace="CELERY" significa: prendi solo le variabili che iniziano con CELERY_.
# Equivale a: SQL Agent legge la sua config dal registry di SQL Server.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-scopre tasks.py in ogni app Django installata (INSTALLED_APPS).
# Equivale a: SQL Agent scansiona le stored procedure marcate come "job step".
app.autodiscover_tasks()
