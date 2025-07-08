FROM python:3.11-slim

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    nodejs \
    npm \
    x11vnc \
    xvfb \
    x11-xserver-utils \
    && rm -rf /var/lib/apt/lists/*

# Set up X11 virtual display
ENV DISPLAY=:0
RUN mkdir -p /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix

# Start Xvfb
RUN Xvfb :0 -screen 0 1024x768x16 &

# Install code-server
RUN curl -fsSL https://code-server.dev/install.sh | sh

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

# Install common package managers
RUN npm install -g yarn \
    && curl -fsSL https://raw.githubusercontent.com/rbenv/rbenv-installer/HEAD/bin/rbenv-installer | bash \
    && curl -s "https://get.sdkman.io" | bash

# Expose ports for the API, code-server, and VNC
EXPOSE 8000 8080 5900

# Health check (Railway will handle port mapping)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/status || exit 1

# Run the application using poetry script
CMD ["poetry", "run", "api"]
