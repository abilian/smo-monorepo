FROM python:3.12-slim

# In a real-world scenario, smo-core would be installed from a package index.
# For local development, use multi-stage builds or Docker Compose volumes.
# COPY ../smo-core /app/smo-core
# RUN pip install --no-cache-dir -e /app/smo-core


COPY smo-core /smo-core
WORKDIR /smo-core
RUN pip install --no-cache-dir .

WORKDIR /app
COPY smo-web .
COPY config .

# RUN echo "--- Contents ---" && ls -la /app || true

RUN pip install --no-cache-dir .
RUN pip install --no-cache-dir gunicorn

# Set environment for production
ENV FLASK_ENV=production
ENV DOTENV_PATH=/app/config/flask.env

EXPOSE 8000

# Use gunicorn with the uvicorn worker for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "smo_web.app:create_app"]
