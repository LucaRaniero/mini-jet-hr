# Mini Jet HR - Backend Dockerfile (Development)
#
# Base: python:3.11-slim (matches CI pipeline, good size/compatibility balance)
# Strategy: install dependencies first for Docker layer caching,
# then copy source code (overridden by volume mount in dev anyway).

FROM python:3.11-slim

# PYTHONDONTWRITEBYTECODE=1: no .pyc files in container (cleaner)
# PYTHONUNBUFFERED=1: print/logging output appears immediately in docker logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first → Docker caches this layer.
# If requirements.txt hasn't changed, pip install is skipped on rebuild.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (overridden by volume mount in docker-compose)
COPY . .

EXPOSE 8000

# 0.0.0.0 = accessible from outside the container (not just localhost inside it)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
