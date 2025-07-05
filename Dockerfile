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

# Copy poetry files and README first for better caching
COPY pyproject.toml poetry.lock* README.md ./

# Install dependencies only (don't install the package itself)
RUN poetry install --only=main --no-root --no-cache

# Copy application code
COPY . .

# Now install the package itself so poetry scripts work
RUN poetry install --only-root

# Create output directory
RUN mkdir -p output

# Expose port (Railway will override with dynamic port)
EXPOSE 8000

# Health check (Railway will handle port mapping)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/status || exit 1

# Run the application using poetry script
CMD ["poetry", "run", "api"]
