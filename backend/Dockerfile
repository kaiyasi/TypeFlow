FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy alembic configuration
COPY alembic.ini .
COPY alembic ./alembic

# Copy the application source code
COPY ./app /app/app

# Add the app directory to Python path
ENV PYTHONPATH=/app

# Create non-root user and set ownership
RUN useradd -m -u 1000 typeflow && chown -R typeflow:typeflow /app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/healthz || exit 1

# Expose port 80 (internal container port)
EXPOSE 80

# Run the application 
USER typeflow
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]