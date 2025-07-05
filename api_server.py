from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import asyncio
import base64
import io
import os
import tempfile
import json
from datetime import datetime

from os_computer_use.streaming import Sandbox
from os_computer_use.api_agent import APISandboxAgent
from os_computer_use.logging import Logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["E2B_API_KEY"] = os.getenv("E2B_API_KEY")

app = FastAPI(title="Computer Use Agent API", version="1.0.0")

# Add CORS middleware for Node.js integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for sandbox and agent
sandbox = None
agent = None
logger = Logger()


# Request/Response Models
class ActionRequest(BaseModel):
    instruction: str
    screenshot: Optional[str] = None  # Base64 encoded screenshot
    single_step: bool = False  # If True, execute only one step


class ActionResponse(BaseModel):
    success: bool
    message: str
    actions: List[Dict[str, Any]]
    screenshot: Optional[str] = None  # Base64 encoded current screenshot
    completed: bool = False
    completion_reason: Optional[str] = None  # Why the task completed/stopped
    iterations: Optional[int] = None  # Number of steps taken


class ScreenshotResponse(BaseModel):
    screenshot: str  # Base64 encoded screenshot
    timestamp: str


class StatusResponse(BaseModel):
    status: str
    sandbox_active: bool
    agent_initialized: bool


class StreamResponse(BaseModel):
    stream_url: str
    timestamp: str


# Helper functions
def initialize_sandbox_and_agent():
    """Initialize the sandbox and agent if not already done"""
    global sandbox, agent

    if sandbox is None:
        try:
            sandbox = Sandbox()
            # Don't start VNC for API mode, just ensure sandbox is ready
            sandbox.set_timeout(1800)  # 30 minutes timeout instead of 1 minute

            # Start VNC stream to get the URL for viewing
            sandbox.stream.start()
            vnc_url = sandbox.stream.get_url()
            print(f"🖥️  Sandbox initialized successfully")
            print(f"🌐 View desktop at: {vnc_url}")
            print(f"📱 You can open this URL in your browser to see the desktop")

        except Exception as e:
            print(f"Error initializing sandbox: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to initialize sandbox: {str(e)}"
            )

    if agent is None:
        try:
            output_dir = f"./output/api_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(output_dir, exist_ok=True)
            agent = APISandboxAgent(sandbox, output_dir, save_logs=True)
            print("Agent initialized successfully")
        except Exception as e:
            print(f"Error initializing agent: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to initialize agent: {str(e)}"
            )


def screenshot_to_base64(screenshot_bytes: bytes) -> str:
    """Convert screenshot bytes to base64 string"""
    return base64.b64encode(screenshot_bytes).decode("utf-8")


def base64_to_bytes(base64_string: str) -> bytes:
    """Convert base64 string to bytes"""
    return base64.b64decode(base64_string)


# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize sandbox and agent on startup"""
    try:
        initialize_sandbox_and_agent()
        print("API server started successfully")
    except Exception as e:
        print(f"Failed to start API server: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global sandbox
    if sandbox:
        try:
            sandbox.kill()
            print("Sandbox stopped")
        except Exception as e:
            print(f"Error stopping sandbox: {e}")


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get the current status of the agent and sandbox"""
    return StatusResponse(
        status="running",
        sandbox_active=sandbox is not None,
        agent_initialized=agent is not None,
    )


@app.get("/screenshot", response_model=ScreenshotResponse)
async def get_screenshot():
    """Get current screenshot from the sandbox"""
    try:
        initialize_sandbox_and_agent()
        screenshot_bytes = agent.screenshot()
        screenshot_b64 = screenshot_to_base64(screenshot_bytes)

        return ScreenshotResponse(
            screenshot=screenshot_b64, timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get screenshot: {str(e)}"
        )


@app.get("/stream", response_model=StreamResponse)
async def get_stream_url():
    """Get the VNC stream URL for viewing the desktop"""
    try:
        initialize_sandbox_and_agent()

        # Get the VNC stream URL
        vnc_url = sandbox.stream.get_url()

        print(f"🌐 Stream URL requested: {vnc_url}")

        return StreamResponse(stream_url=vnc_url, timestamp=datetime.now().isoformat())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get stream URL: {str(e)}"
        )


@app.post("/act", response_model=ActionResponse)
async def execute_action(request: ActionRequest):
    """Execute an action based on instruction"""
    try:
        initialize_sandbox_and_agent()

        print(f"🚀 Executing action: '{request.instruction}'")
        print(f"📋 Single step mode: {request.single_step}")

        # If a screenshot is provided, we could potentially use it
        # For now, we'll always take a fresh screenshot

        actions_taken = []

        if request.single_step:
            # Execute only one step
            result = agent.execute_single_step(request.instruction)
            actions_taken.append(result)
            completed = result.get("completed", False)
            completion_reason = (
                "stop_tool_called" if completed else "single_step_incomplete"
            )
            iterations = 1
            print(f"✅ Single step completed: {result.get('action', 'unknown')}")
        else:
            # Execute the full instruction (may take multiple steps)
            actions_taken, completed = agent.run_with_tracking(request.instruction)
            iterations = len(
                [
                    a
                    for a in actions_taken
                    if a.get("action") not in ["error", "timeout"]
                ]
            )

            # Determine completion reason
            if completed:
                completion_reason = "stop_tool_called"
            elif any(a.get("action") == "timeout" for a in actions_taken):
                completion_reason = "max_iterations_reached"
            elif any(a.get("action") == "error" for a in actions_taken):
                completion_reason = "error_occurred"
            else:
                completion_reason = "unknown"

            print(f"✅ Full instruction completed with {len(actions_taken)} actions")

        # Get current screenshot
        screenshot_bytes = agent.screenshot()
        screenshot_b64 = screenshot_to_base64(screenshot_bytes)

        print(f"📸 Screenshot captured and returned")
        print(f"🏁 Task completed: {completed} ({completion_reason})")

        return ActionResponse(
            success=True,
            message="Action executed successfully",
            actions=actions_taken,
            screenshot=screenshot_b64,
            completed=completed,
            completion_reason=completion_reason,
            iterations=iterations,
        )

    except Exception as e:
        print(f"❌ Action failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to execute action: {str(e)}"
        )


@app.post("/click")
async def click_element(query: str = Form(...)):
    """Click on a specific element"""
    try:
        initialize_sandbox_and_agent()
        result = agent.click(query)

        screenshot_bytes = agent.screenshot()
        screenshot_b64 = screenshot_to_base64(screenshot_bytes)

        return {
            "success": True,
            "message": result,
            "screenshot": screenshot_b64,
            "action": "click",
            "query": query,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to click element: {str(e)}"
        )


@app.post("/type")
async def type_text(text: str = Form(...)):
    """Type text into the current focus"""
    try:
        initialize_sandbox_and_agent()
        result = agent.type_text(text)

        screenshot_bytes = agent.screenshot()
        screenshot_b64 = screenshot_to_base64(screenshot_bytes)

        return {
            "success": True,
            "message": result,
            "screenshot": screenshot_b64,
            "action": "type",
            "text": text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to type text: {str(e)}")


@app.post("/key")
async def send_key(key: str = Form(...)):
    """Send a key combination"""
    try:
        initialize_sandbox_and_agent()
        result = agent.send_key(key)

        screenshot_bytes = agent.screenshot()
        screenshot_b64 = screenshot_to_base64(screenshot_bytes)

        return {
            "success": True,
            "message": result,
            "screenshot": screenshot_b64,
            "action": "key",
            "key": key,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send key: {str(e)}")


@app.post("/command")
async def run_command(command: str = Form(...), background: bool = Form(False)):
    """Run a shell command"""
    try:
        initialize_sandbox_and_agent()

        if background:
            result = agent.run_background_command(command)
        else:
            result = agent.run_command(command)

        return {
            "success": True,
            "message": result,
            "action": "command",
            "command": command,
            "background": background,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run command: {str(e)}")


@app.post("/reset")
async def reset_agent():
    """Reset the agent's conversation memory"""
    try:
        initialize_sandbox_and_agent()
        agent.messages = []

        return {"success": True, "message": "Agent memory reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset agent: {str(e)}")


@app.post("/shutdown")
async def shutdown_sandbox():
    """Shutdown and kill the sandbox"""
    global sandbox, agent

    try:
        if sandbox:
            print("Shutting down sandbox...")
            sandbox.kill()
            print("Sandbox stopped successfully")

            # Reset global variables
            sandbox = None
            agent = None

            return {"success": True, "message": "Sandbox shutdown successfully"}
        else:
            return {"success": True, "message": "No active sandbox to shutdown"}
    except Exception as e:
        print(f"Error during shutdown: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to shutdown sandbox: {str(e)}"
        )


def main():
    """Start the FastAPI server"""
    port = int(os.getenv("PORT", 8000))  # Railway provides PORT env var
    uvicorn.run(
        "api_server:app", host="0.0.0.0", port=port, reload=False, log_level="info"
    )


if __name__ == "__main__":
    main()
