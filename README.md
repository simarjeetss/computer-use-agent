# Open Computer Use

A secure cloud Linux computer powered by [E2B Desktop Sandbox](https://github.com/e2b-dev/desktop/) and controlled by open-source LLMs.

https://github.com/user-attachments/assets/3837c4f6-45cb-43f2-9d51-a45f742424d4

## Features

- Uses [E2B](https://e2b.dev) for secure [Desktop Sandbox](https://github.com/e2b-dev/desktop)
- Operates the computer via the keyboard, mouse, and shell commands
- Supports 10+ LLMs, [OS-Atlas](https://osatlas.github.io/)/[ShowUI](https://github.com/showlab/ShowUI) and [any other models you want to integrate](#llm-support)!
- Live streams the display of the sandbox on the client computer
- User can pause and prompt the agent at any time
- Uses Ubuntu, but designed to work with any operating system
- Automatic repository setup and development environment configuration

## Design

![Open Computer Use Architecture](./assets/architecture.png#gh-dark-mode-only)
![Open Computer Use Architecture](./assets/architecture-light.png#gh-light-mode-only)

The details of the design are laid out in this article: [How I taught an AI to use a computer](https://blog.jamesmurdza.com/how-i-taught-an-ai-to-use-a-computer)

## LLM support

Open Computer Use is designed to make it easy to swap in and out new LLMs. The LLMs used by the agent are specified in [config.py](/os_computer_use/config.py) like this:

```
grounding_model = providers.OSAtlasProvider()
vision_model = providers.GroqProvider("llama3.2")
action_model = providers.GroqProvider("llama3.3")
```

The providers are imported from [providers.py](/os_computer_use/providers.py) and include:

- Fireworks, OpenRouter, Llama API:
  - Llama 3.2 (vision only), Llama 3.3 (action only)
- Groq:
  - Llama 3.2 (vision + action), Llama 3.3 (action only)
- DeepSeek:
  - DeepSeek (action only)
- Google:
  - Gemini 2.0 Flash (vision + action)
- OpenAI:
  - GPT-4o and GPT-4o mini (vision + action)
- Anthropic:
  - Claude (vision + action)
- HuggingFace Spaces:
  - OS-Atlas (grounding)
  - ShowUI (grounding)
- Moonshot
- Mistral AI (Pixtral for vision, Mistral Large for actions)

If you add a new model or provider, please [make a PR](../../pulls) to this repository with the updated providers.py!

## Repository Setup Feature

The project includes a specialized agent for automatically setting up and running GitHub repositories. This feature:

1. Clones any public GitHub repository
2. Automatically detects the technology stack
3. Installs required dependencies
4. Sets up a development environment with code-server
5. Runs the project if possible

### Using the Repository Setup Feature

1. Make sure you have the required environment variables set up in your `.env` file
2. Run the repository setup command:

```sh
poetry run python repo_setup.py https://github.com/username/repository
```

The agent will:
- Clone the repository
- Detect the technology stack (Python, Node.js, Ruby, Java, etc.)
- Install dependencies using the appropriate package manager
- Open the code in a web-based VS Code interface
- Start the project if a run command is detected

The web-based VS Code interface will be available at `http://localhost:8080` once the setup is complete.

### Supported Technology Stacks

The agent can automatically detect and set up:

- Python projects (pip, poetry)
- Node.js projects (npm, yarn)
- Ruby projects (bundler)
- Java/Kotlin projects (maven, gradle)

More technology stacks can be added by extending the `RepoSetupAgent` class.

## Get started

### Prerequisites

- Python 3.10 or later
- [git](https://git-scm.com/)
- [E2B API key](https://e2b.dev/dashboard?tab=keys)
- API key for an LLM provider (see above)

### 1. Install the prerequisites

In your terminal:

```sh
brew install poetry ffmpeg
```

### 2. Clone the repository

In your terminal:

```sh
git clone https://github.com/e2b-dev/open-computer-use/
```

### 3. Set the environment variables

Enter the project directory:

```
cd open-computer-use
```

Create a `.env` file in `open-computer-use` and set the following:

```sh
# Get your API key here: https://e2b.dev/
E2B_API_KEY="your-e2b-api-key"
```

Additionally, add API key(s) for any LLM providers you're using:
```
# You only need the API key for the provider(s) selected in config.py:
# Hugging Face Spaces do not require an API key.
FIREWORKS_API_KEY=...
OPENROUTER_API_KEY=...
LLAMA_API_KEY=...
GROQ_API_KEY=...
GEMINI_API_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
MOONSHOT_API_KEY=...
# Required: Provide your Hugging Face token to bypass Gradio rate limits.
HF_TOKEN=...
```

### 4. Start the web interface

Run the following command to start the agent:

```sh
poetry install
```

```sh
poetry run start
```

The agent will open and prompt you for its first instruction.

To start the agent with a specified prompt, run:

```sh
poetry run start --prompt "use the web browser to get the current weather in sf"
```

The display stream should be visible a few seconds after the Python program starts.

## API Mode

For integration with other applications (like Node.js backends), you can run the agent as a FastAPI server:

### Start the API server

```sh
poetry run api
```

This starts a FastAPI server on `http://localhost:8000` with the following endpoints:

- `GET /status` - Check if the agent is ready
- `GET /screenshot` - Get current screenshot
- `POST /act` - Execute actions with natural language instructions
- `POST /click` - Click on specific elements
- `POST /type` - Type text
- `POST /key` - Send key combinations
- `POST /command` - Run shell commands
- `POST /reset` - Reset agent memory

### Node.js Integration

Install the Node.js dependencies:

```sh
npm install axios
```

Use the provided client:

```javascript
const ComputerUseClient = require('./nodejs_client_secure.js');

const client = new ComputerUseClient();

// Execute an action
const result = await client.executeAction("Open Firefox browser");
console.log('Action completed:', result.success);

// Get a screenshot
const screenshot = await client.getScreenshot();
console.log('Screenshot:', screenshot.timestamp);
```

See [API_README.md](API_README.md) for complete API documentation and examples.

