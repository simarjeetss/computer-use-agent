FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Configure poetry: don't create virtual environment, disable cache
RUN poetry config virtualenvs.create false \
    && poetry config cache-dir /tmp

# Copy poetry files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --only=main --no-cache

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/status || exit 1

# Run the application
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
