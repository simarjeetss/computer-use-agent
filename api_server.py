from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form,
    Depends,
    Header,
    status,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import asyncio
import base64
import io
import os
import tempfile
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
import threading

from os_computer_use.streaming import Sandbox
from os_computer_use.api_agent import APISandboxAgent
from os_computer_use.demo_agent import DemoAgent
from os_computer_use.demo_orchestrator import DemoOrchestrator
from os_computer_use.logging import Logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["E2B_API_KEY"] = os.getenv("E2B_API_KEY")

# Security Configuration
API_KEY = os.getenv("API_KEY")  # Add this to your Railway environment
ALLOWED_ORIGINS = (
    os.getenv("ALLOWED_ORIGINS", "").split(",")
    if os.getenv("ALLOWED_ORIGINS")
    else ["*"]
)
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "300"))  # 5 minutes
SANDBOX_MAX_LIFETIME_MINUTES = int(os.getenv("SANDBOX_MAX_LIFETIME_MINUTES", "30"))

app = FastAPI(title="Computer Use Agent API", version="1.0.0")

# Security: HTTPBearer for API key authentication
security = HTTPBearer(auto_error=False)

# Rate limiting storage
rate_limit_storage = defaultdict(list)
rate_limit_lock = threading.Lock()

# Sandbox cleanup tracking
sandbox_created_at = None
cleanup_timer = None

# Add CORS middleware with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Restricted to specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only necessary methods
    allow_headers=["Authorization", "Content-Type"],  # Specific headers only
)

# Global variables for sandbox and agent
sandbox = None
agent = None
logger = Logger()


# Security Functions
def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """Verify API key authentication"""
    if not API_KEY:
        # If no API key is set, allow access (for backward compatibility)
        return True

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


def rate_limit_check(client_ip: str = None):
    """Check rate limiting per IP"""
    if not client_ip:
        client_ip = "unknown"

    with rate_limit_lock:
        current_time = time.time()
        # Clean old entries (older than 1 minute)
        rate_limit_storage[client_ip] = [
            timestamp
            for timestamp in rate_limit_storage[client_ip]
            if current_time - timestamp < 60
        ]

        # Check if rate limit exceeded
        if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {RATE_LIMIT_PER_MINUTE} requests per minute.",
            )

        # Add current request
        rate_limit_storage[client_ip].append(current_time)


def schedule_sandbox_cleanup():
    """Schedule automatic sandbox cleanup"""
    global cleanup_timer, sandbox_created_at

    def cleanup_sandbox():
        global sandbox, agent, sandbox_created_at, cleanup_timer
        if sandbox:
            try:
                print(
                    f"🧹 Auto-cleanup: Shutting down sandbox after {SANDBOX_MAX_LIFETIME_MINUTES} minutes"
                )
                sandbox.kill()
                sandbox = None
                agent = None
                sandbox_created_at = None
                cleanup_timer = None
            except Exception as e:
                print(f"Error during auto-cleanup: {e}")

    if cleanup_timer:
        cleanup_timer.cancel()

    cleanup_timer = threading.Timer(SANDBOX_MAX_LIFETIME_MINUTES * 60, cleanup_sandbox)
    cleanup_timer.start()
    sandbox_created_at = datetime.now()


# Request/Response Models (keeping existing ones)
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
    sandbox_uptime_minutes: Optional[float] = None
    rate_limit_remaining: Optional[int] = None


class StreamResponse(BaseModel):
    stream_url: str
    timestamp: str


# Demo-specific models
class DemoSessionRequest(BaseModel):
    githubUrl: str
    meetLink: str


class DemoSessionResponse(BaseModel):
    sessionId: str
    sandboxUrl: str
    status: str
    currentStep: Optional[str] = None
    stepProgress: str
    logs: List[Dict[str, Any]] = []
    estimatedCompletion: Optional[str] = None
    timestamp: str


class DemoStatusResponse(BaseModel):
    sessionId: str
    status: str
    completedSteps: List[str]
    currentStep: Optional[str] = None
    stepProgress: str
    logs: List[Dict[str, Any]]
    sandboxUrl: Optional[str] = None
    runtimeMinutes: float
    timestamp: str


# Global variables for demo sessions
demo_sessions = {}  # Store active demo sessions
demo_agents = {}  # Store demo agents by session ID


# Helper functions
def initialize_sandbox_and_agent():
    """Initialize the sandbox and agent if not already done"""
    global sandbox, agent

    if sandbox is None:
        try:
            sandbox = Sandbox()
            # Set reasonable timeout
            sandbox.set_timeout(REQUEST_TIMEOUT_SECONDS)

            # Start VNC stream to get the URL for viewing
            sandbox.stream.start()
            vnc_url = sandbox.stream.get_url()
            print(f"🖥️  Sandbox initialized successfully")
            print(f"🌐 View desktop at: {vnc_url}")

            # Schedule automatic cleanup
            schedule_sandbox_cleanup()

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
            print("✅ Agent initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing agent: {e}")
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
async def get_status(request: Request, _: bool = Depends(verify_api_key)):
    """Get the current status of the agent and sandbox"""
    try:
        # Get client IP for rate limiting
        client_ip = request.client.host if request.client else "unknown"

        # Apply rate limiting
        rate_limit_check(client_ip)

        uptime = None
        if sandbox_created_at:
            uptime = (
                datetime.now() - sandbox_created_at
            ).total_seconds() / 60  # in minutes

        rate_limit_remaining = None
        with rate_limit_lock:
            if client_ip in rate_limit_storage:
                # Clean old entries
                rate_limit_storage[client_ip] = [
                    timestamp
                    for timestamp in rate_limit_storage[client_ip]
                    if time.time() - timestamp < 60
                ]
                rate_limit_remaining = RATE_LIMIT_PER_MINUTE - len(
                    rate_limit_storage[client_ip]
                )

        return StatusResponse(
            status="running",
            sandbox_active=sandbox is not None,
            agent_initialized=agent is not None,
            sandbox_uptime_minutes=uptime,
            rate_limit_remaining=rate_limit_remaining,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@app.get("/screenshot", response_model=ScreenshotResponse)
async def get_screenshot(request: Request, _: bool = Depends(verify_api_key)):
    """Get current screenshot from the sandbox"""
    try:
        # Apply rate limiting
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_check(client_ip)

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
async def get_stream_url(request: Request, _: bool = Depends(verify_api_key)):
    """Get the VNC stream URL for viewing the desktop"""
    try:
        # Apply rate limiting
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_check(client_ip)

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
async def execute_action(
    action_request: ActionRequest, request: Request, _: bool = Depends(verify_api_key)
):
    """Execute an action based on instruction"""
    try:
        # Apply rate limiting
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_check(client_ip)

        initialize_sandbox_and_agent()

        print(f"🚀 Executing action: '{action_request.instruction}'")
        print(f"📋 Single step mode: {action_request.single_step}")

        # If a screenshot is provided, we could potentially use it
        # For now, we'll always take a fresh screenshot

        actions_taken = []

        if action_request.single_step:
            # Execute only one step
            result = agent.execute_single_step(action_request.instruction)
            actions_taken.append(result)
            completed = result.get("completed", False)
            completion_reason = (
                "stop_tool_called" if completed else "single_step_incomplete"
            )
            iterations = 1
            print(f"✅ Single step completed: {result.get('action', 'unknown')}")
        else:
            # Execute the full instruction (may take multiple steps)
            actions_taken, completed = agent.run_with_tracking(
                action_request.instruction
            )
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
async def click_element(
    query: str = Form(...), request: Request = None, _: bool = Depends(verify_api_key)
):
    """Click on a specific element"""
    try:
        # Apply rate limiting
        if request:
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_check(client_ip)

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
async def type_text(
    text: str = Form(...), request: Request = None, _: bool = Depends(verify_api_key)
):
    """Type text into the current focus"""
    try:
        # Apply rate limiting
        if request:
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_check(client_ip)

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
async def send_key(
    key: str = Form(...), request: Request = None, _: bool = Depends(verify_api_key)
):
    """Send a key combination"""
    try:
        # Apply rate limiting
        if request:
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_check(client_ip)

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
async def run_command(
    command: str = Form(...),
    background: bool = Form(False),
    request: Request = None,
    _: bool = Depends(verify_api_key),
):
    """Run a shell command"""
    try:
        # Apply rate limiting
        if request:
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_check(client_ip)

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
async def reset_agent(request: Request = None, _: bool = Depends(verify_api_key)):
    """Reset the agent's conversation memory"""
    try:
        # Apply rate limiting
        if request:
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_check(client_ip)

        initialize_sandbox_and_agent()
        agent.messages = []

        return {"success": True, "message": "Agent memory reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset agent: {str(e)}")


@app.post("/shutdown")
async def shutdown_sandbox(request: Request = None, _: bool = Depends(verify_api_key)):
    """Shutdown and kill the sandbox"""
    global sandbox, agent, cleanup_timer

    try:
        # Apply rate limiting
        if request:
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_check(client_ip)

        if sandbox:
            print("🧹 Manual shutdown: Shutting down sandbox...")
            sandbox.kill()
            print("✅ Sandbox stopped successfully")

            # Cancel cleanup timer and reset global variables
            if cleanup_timer:
                cleanup_timer.cancel()
                cleanup_timer = None

            sandbox = None
            agent = None

            return {"success": True, "message": "Sandbox shutdown successfully"}
        else:
            return {"success": True, "message": "No active sandbox to shutdown"}
    except Exception as e:
        print(f"❌ Error during shutdown: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to shutdown sandbox: {str(e)}"
        )


# Demo Session Endpoints
@app.post("/demo-session", response_model=DemoSessionResponse)
async def create_demo_session(
    demo_request: DemoSessionRequest,
    request: Request,
    _: bool = Depends(verify_api_key),
):
    """Create a new demo session with GitHub repository and Google Meet integration"""
    try:
        # Apply rate limiting
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_check(client_ip)

        # Initialize sandbox and create demo agent
        demo_sandbox = Sandbox()
        demo_sandbox.set_timeout(REQUEST_TIMEOUT_SECONDS)

        # Start VNC stream
        demo_sandbox.stream.start()
        sandbox_url = demo_sandbox.stream.get_url()

        # Create demo agent
        output_dir = f"./output/demo_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(output_dir, exist_ok=True)
        demo_agent = DemoAgent(demo_sandbox, output_dir, save_logs=True)

        # Initialize demo session
        session_id = demo_agent.initialize_demo_session(
            demo_request.githubUrl, demo_request.meetLink
        )

        # Store session for tracking
        demo_sessions[session_id] = {
            "agent": demo_agent,
            "sandbox": demo_sandbox,
            "orchestrator": DemoOrchestrator(demo_agent),
            "status": "initialized",
            "created_at": datetime.now(),
        }

        # Start demo execution in background
        import asyncio

        async def run_demo_background():
            try:
                orchestrator = demo_sessions[session_id]["orchestrator"]
                await orchestrator.run_full_demo(
                    demo_request.githubUrl, demo_request.meetLink
                )
                demo_sessions[session_id]["status"] = "completed"
            except Exception as e:
                logger.log(f"Demo execution error: {e}", "red")
                demo_sessions[session_id]["status"] = "failed"

        # Execute in background
        asyncio.create_task(run_demo_background())

        # Return immediate response
        return DemoSessionResponse(
            sessionId=session_id,
            sandboxUrl=sandbox_url,
            status="running",
            currentStep="open_terminal",
            stepProgress="0/8",
            logs=[],
            estimatedCompletion=(datetime.now() + timedelta(minutes=5)).isoformat(),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.log(f"Error creating demo session: {e}", "red")
        raise HTTPException(
            status_code=500, detail=f"Failed to create demo session: {str(e)}"
        )


@app.get("/demo-session/{session_id}/status", response_model=DemoStatusResponse)
async def get_demo_status(
    session_id: str, request: Request, _: bool = Depends(verify_api_key)
):
    """Get the current status of a demo session"""
    try:
        # Apply rate limiting
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_check(client_ip)

        # Check if session exists
        if session_id not in demo_sessions:
            raise HTTPException(
                status_code=404, detail=f"Demo session {session_id} not found"
            )

        session_data = demo_sessions[session_id]
        demo_agent = session_data["agent"]
        orchestrator = session_data["orchestrator"]

        # Get progress status from agent
        progress = demo_agent.get_progress_status()

        return DemoStatusResponse(
            sessionId=session_id,
            status=progress["status"],
            completedSteps=progress["completed_steps"],
            currentStep=progress["current_step"],
            stepProgress=progress["step_progress"],
            logs=orchestrator.execution_log,
            sandboxUrl=progress["sandbox_url"],
            runtimeMinutes=progress["runtime_minutes"],
            timestamp=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.log(f"Error getting demo status: {e}", "red")
        raise HTTPException(
            status_code=500, detail=f"Failed to get demo status: {str(e)}"
        )


@app.post("/demo-session/{session_id}/cleanup")
async def cleanup_demo_session(
    session_id: str, request: Request, _: bool = Depends(verify_api_key)
):
    """Clean up and terminate a demo session"""
    try:
        # Apply rate limiting
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_check(client_ip)

        # Check if session exists
        if session_id not in demo_sessions:
            raise HTTPException(
                status_code=404, detail=f"Demo session {session_id} not found"
            )

        session_data = demo_sessions[session_id]
        demo_agent = session_data["agent"]
        demo_sandbox = session_data["sandbox"]

        # Clean up resources
        demo_agent.cleanup_demo_session()
        demo_sandbox.kill()

        # Remove from active sessions
        del demo_sessions[session_id]

        logger.log(f"Demo session {session_id} cleaned up successfully", "green")

        return {
            "success": True,
            "message": f"Demo session {session_id} cleaned up successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.log(f"Error cleaning up demo session: {e}", "red")
        raise HTTPException(
            status_code=500, detail=f"Failed to cleanup demo session: {str(e)}"
        )


def main():
    """Start the FastAPI server"""
    port = int(os.getenv("PORT", 8000))  # Railway provides PORT env var
    uvicorn.run(
        "api_server:app", host="0.0.0.0", port=port, reload=False, log_level="info"
    )


if __name__ == "__main__":
    main()
