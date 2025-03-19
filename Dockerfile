FROM python:3.11-slim

WORKDIR /app

# Install PostgreSQL client and build dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=${FLASK_APP}
ENV PYTHONUNBUFFERED=${PYTHONUNBUFFERED}
ENV GUNICORN_WORKERS=${GUNICORN_WORKERS}
ENV GUNICORN_BIND=${GUNICORN_BIND}

# Run the application
CMD ["gunicorn", "--bind", "${GUNICORN_BIND}", "--workers", "${GUNICORN_WORKERS}", "app:app"]