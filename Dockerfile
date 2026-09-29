# ==============================================================================
# Stage 1: Build & Dependency Resolution Stage
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools if necessary for native wheel compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt


# ==============================================================================
# Stage 2: Minimal Production Runtime Stage
# ==============================================================================
FROM python:3.11-slim AS runtime

# Security: Configure non-root system user
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=aiops_service_desk.settings \
    PORT=8000

WORKDIR /app

# Install compiled wheels from builder stage
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Copy application source code
COPY . /app

# Ensure proper permissions for non-root user and persistent SQLite directory
RUN mkdir -p /app/data && \
    chown -R appuser:appgroup /app

# Healthcheck validating login endpoint responsiveness
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; resp = urllib.request.urlopen('http://127.0.0.1:8000/login/'); exit(0 if resp.status == 200 else 1)"

USER appuser

EXPOSE 8000

# Default entrypoint: Run Django development server (or WSGI gunicorn in production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
