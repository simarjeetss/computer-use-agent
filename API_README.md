# Computer Use Agent API

This FastAPI server wraps the computer use agent functionality and exposes it via HTTP endpoints for integration with other services like Node.js applications.

## Installation

First, install the new dependencies:

```bash
poetry install
```

## Running the API Server

Start the API server:

```bash
poetry run api
```

The server will start on `http://localhost:8000` by default.

## API Endpoints

### GET /status
Get the current status of the agent and sandbox.

**Response:**
```json
{
  "status": "running",
  "sandbox_active": true,
  "agent_initialized": true
}
```

### GET /screenshot
Get the current screenshot from the sandbox.

**Response:**
```json
{
  "screenshot": "base64_encoded_image_data",
  "timestamp": "2025-07-02T10:30:00"
}
```

### POST /act
Execute an action based on natural language instruction.

**Request:**
```json
{
  "instruction": "Open Firefox browser",
  "screenshot": "optional_base64_screenshot",
  "single_step": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Action executed successfully",
  "actions": [
    {
      "action": "click",
      "parameters": {"query": "Firefox"},
      "result": "The mouse has clicked.",
      "timestamp": "2025-07-02T10:30:00"
    }
  ],
  "screenshot": "base64_encoded_current_screenshot",
  "completed": false
}
```

### POST /click
Click on a specific element.

**Form Data:**
- `query`: Description of element to click

**Response:**
```json
{
  "success": true,
  "message": "The mouse has clicked.",
  "screenshot": "base64_encoded_screenshot",
  "action": "click",
  "query": "submit button"
}
```

### POST /type
Type text into the current focus.

**Form Data:**
- `text`: Text to type

### POST /key
Send a key combination.

**Form Data:**
- `key`: Key combination (e.g., "Return", "Ctrl-C")

### POST /command
Run a shell command.

**Form Data:**
- `command`: Shell command to run
- `background`: Whether to run in background (default: false)

### POST /reset
Reset the agent's conversation memory.

## Node.js Integration Example

Here's how to integrate with a Node.js application:

```javascript
const axios = require('axios');

class ComputerUseClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async getStatus() {
    const response = await axios.get(`${this.baseUrl}/status`);
    return response.data;
  }

  async getScreenshot() {
    const response = await axios.get(`${this.baseUrl}/screenshot`);
    return response.data;
  }

  async executeAction(instruction, singleStep = false) {
    const response = await axios.post(`${this.baseUrl}/act`, {
      instruction,
      single_step: singleStep
    });
    return response.data;
  }

  async click(query) {
    const formData = new FormData();
    formData.append('query', query);
    
    const response = await axios.post(`${this.baseUrl}/click`, formData);
    return response.data;
  }

  async type(text) {
    const formData = new FormData();
    formData.append('text', text);
    
    const response = await axios.post(`${this.baseUrl}/type`, formData);
    return response.data;
  }

  async sendKey(key) {
    const formData = new FormData();
    formData.append('key', key);
    
    const response = await axios.post(`${this.baseUrl}/key`, formData);
    return response.data;
  }

  async runCommand(command, background = false) {
    const formData = new FormData();
    formData.append('command', command);
    formData.append('background', background.toString());
    
    const response = await axios.post(`${this.baseUrl}/command`, formData);
    return response.data;
  }

  async reset() {
    const response = await axios.post(`${this.baseUrl}/reset`);
    return response.data;
  }
}

// Usage example
async function example() {
  const client = new ComputerUseClient();
  
  // Check status
  const status = await client.getStatus();
  console.log('Status:', status);
  
  // Execute an action
  const result = await client.executeAction("Open the terminal application");
  console.log('Action result:', result);
  
  // Get screenshot
  const screenshot = await client.getScreenshot();
  console.log('Screenshot timestamp:', screenshot.timestamp);
}

module.exports = ComputerUseClient;
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 500: Internal server error (includes error details in response)

Error responses include a `detail` field with error information:
```json
{
  "detail": "Failed to execute action: Connection timeout"
}
```
