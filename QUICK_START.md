# Computer Use Agent API - Quick Start

## What was created

I've successfully wrapped your computer-use agent in a FastAPI server that exposes HTTP endpoints for integration with Node.js applications.

## Files Created/Modified

### Core API Files:
- `api_server.py` - Main FastAPI server with endpoints
- `os_computer_use/api_agent.py` - Enhanced agent with single-step execution
- `pyproject.toml` - Updated with FastAPI dependencies

### Documentation & Examples:
- `API_README.md` - Complete API documentation
- `nodejs_client_example.js` - Node.js client library
- `package.json` - Node.js dependencies
- `test_api.py` - Python test script

## How to Use

### 1. Start the API Server

```bash
poetry run api
```

The server runs on `http://localhost:8000`

### 2. From Node.js

```javascript
const ComputerUseClient = require('./nodejs_client_example.js');
const client = new ComputerUseClient();

// Execute an action
const result = await client.executeAction("Open Firefox browser");

// Get screenshot  
const screenshot = await client.getScreenshot();

// Click on something
const clickResult = await client.click("submit button");
```

### 3. Direct HTTP Calls

```bash
# Get status
curl http://localhost:8000/status

# Get screenshot
curl http://localhost:8000/screenshot

# Execute action
curl -X POST http://localhost:8000/act \
  -H "Content-Type: application/json" \
  -d '{"instruction": "Open terminal", "single_step": false}'

# Click on element
curl -X POST http://localhost:8000/click \
  -d "query=Firefox icon"
```

## Key Features

- **Single-step execution**: Set `single_step: true` to execute one action at a time
- **Full automation**: Set `single_step: false` to run complete instructions
- **Screenshot access**: Get current desktop screenshots as base64
- **Direct actions**: Click, type, key combinations, shell commands
- **Memory management**: Reset agent conversation history
- **CORS enabled**: Ready for web application integration

## API Endpoints

- `GET /status` - Check if agent is ready
- `GET /screenshot` - Get current screenshot  
- `POST /act` - Execute natural language instructions
- `POST /click` - Click on UI elements
- `POST /type` - Type text
- `POST /key` - Send key combinations  
- `POST /command` - Run shell commands
- `POST /reset` - Reset agent memory

## Testing

Test the API with the provided script:

```bash
python test_api.py
```

Or test the Node.js client:

```bash
npm install axios
node nodejs_client_example.js
```

The agent now runs as a proper HTTP API server that your Node.js application can communicate with!
