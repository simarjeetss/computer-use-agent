const axios = require('axios');

class ComputerUseClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async getStatus() {
    try {
      const response = await axios.get(`${this.baseUrl}/status`);
      return response.data;
    } catch (error) {
      throw new Error(`Status request failed: ${error.message}`);
    }
  }

  async getScreenshot() {
    try {
      const response = await axios.get(`${this.baseUrl}/screenshot`);
      return response.data;
    } catch (error) {
      throw new Error(`Screenshot request failed: ${error.message}`);
    }
  }

  async executeAction(instruction, singleStep = false) {
    try {
      const response = await axios.post(`${this.baseUrl}/act`, {
        instruction,
        single_step: singleStep
      });
      return response.data;
    } catch (error) {
      throw new Error(`Action request failed: ${error.message}`);
    }
  }

  async click(query) {
    try {
      const formData = new URLSearchParams();
      formData.append('query', query);
      
      const response = await axios.post(`${this.baseUrl}/click`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Click request failed: ${error.message}`);
    }
  }

  async type(text) {
    try {
      const formData = new URLSearchParams();
      formData.append('text', text);
      
      const response = await axios.post(`${this.baseUrl}/type`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Type request failed: ${error.message}`);
    }
  }

  async sendKey(key) {
    try {
      const formData = new URLSearchParams();
      formData.append('key', key);
      
      const response = await axios.post(`${this.baseUrl}/key`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Key request failed: ${error.message}`);
    }
  }

  async runCommand(command, background = false) {
    try {
      const formData = new URLSearchParams();
      formData.append('command', command);
      formData.append('background', background.toString());
      
      const response = await axios.post(`${this.baseUrl}/command`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Command request failed: ${error.message}`);
    }
  }

  async reset() {
    try {
      const response = await axios.post(`${this.baseUrl}/reset`);
      return response.data;
    } catch (error) {
      throw new Error(`Reset request failed: ${error.message}`);
    }
  }
}

// Usage example
async function example() {
  const client = new ComputerUseClient();
  
  try {
    // Check status
    console.log('Checking API status...');
    const status = await client.getStatus();
    console.log('Status:', status);
    
    if (!status.sandbox_active || !status.agent_initialized) {
      console.log('Sandbox or agent not ready, waiting...');
      return;
    }
    
    // Get initial screenshot
    console.log('\nGetting screenshot...');
    const screenshot = await client.getScreenshot();
    console.log('Screenshot captured at:', screenshot.timestamp);
    
    // Execute an action step by step
    console.log('\nExecuting action: Open terminal...');
    const result = await client.executeAction("Open the terminal application", true);
    console.log('Action result:', {
      success: result.success,
      message: result.message,
      completed: result.completed,
      actions: result.actions.length
    });
    
    // Run a simple command
    console.log('\nRunning command...');
    const cmdResult = await client.runCommand('echo "Hello from Node.js!"');
    console.log('Command result:', cmdResult.message);
    
    console.log('\nExample completed successfully!');
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Export for use in other modules
module.exports = ComputerUseClient;

// Run example if this file is executed directly
if (require.main === module) {
  example();
}
