FROM python:3.10-slim

WORKDIR /app

# In a real-world scenario, smo-core would be installed from a package index.
# For local development, use multi-stage builds or Docker Compose volumes.
# COPY ../smo-core /app/smo-core
# RUN pip install --no-cache-dir -e /app/smo-core

COPY pyproject.toml .
# Install this package's dependencies
RUN pip install --no-cache-dir .

# Copy the application source code
COPY ./smo_web /app/smo_web
COPY ./config /app/config

# Set environment for production
ENV FLASK_ENV=production
ENV DOTENV_PATH=/app/config/flask.env

EXPOSE 8000

# Use gunicorn with the uvicorn worker for production
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4", "smo_web.app:connexion_app"]
