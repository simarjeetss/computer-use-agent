# Docker Deployment Guide

This guide shows how to deploy the Open Computer Use API using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- E2B API key

## Quick Start

1. **Set up environment variables:**
   ```bash
   # Create .env file with your E2B API key
   echo "E2B_API_KEY=your_e2b_api_key_here" > .env
   ```

2. **Build and start the application:**
   ```bash
   docker-compose up -d
   ```

3. **Verify the deployment:**
   ```bash
   curl http://localhost:8000/status
   ```

## Docker Commands

### Start the application
```bash
docker-compose up -d
```

### Stop the application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Rebuild after code changes
```bash
docker-compose build
docker-compose up -d
```

### Check container status
```bash
docker-compose ps
```

## Configuration

- **Port**: The API runs on port 8000 by default
- **Logs**: Container logs are available via `docker-compose logs`
- **Output**: The `output/` directory is mounted as a volume for persistence
- **Health Check**: The container includes a health check that monitors the `/status` endpoint

## Accessing the API

Once deployed, your API will be available at:
- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/status

## Troubleshooting

### Check if containers are running
```bash
docker-compose ps
```

### View container logs
```bash
docker-compose logs open-computer-use-api
```

### Restart containers
```bash
docker-compose restart
```

### Clean rebuild
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Integration with Node.js

Your Node.js application can now connect to the always-available API at:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

The API will automatically restart if it crashes and persist across system reboots (when using `restart: unless-stopped` in docker-compose.yml).
