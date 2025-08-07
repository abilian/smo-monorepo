FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install build dependencies
RUN pip install --no-cache-dir uv-build

# Copy only what's needed for dependency installation
COPY pyproject.toml ./

# Install project dependencies
RUN uv pip install -e .

# --- Runtime stage ---
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY smo-ui/ ./smo-ui/
COPY config/ ./config/

# Set environment for production
ENV FLASK_ENV=production
ENV DOTENV_PATH=/app/config/flask.env

# Expose the FastAPI port
EXPOSE 8000

# Use gunicorn with uvicorn workers
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", \
     "--worker-class", "uvicorn.workers.UvicornWorker", "smo_ui.app:app"]
