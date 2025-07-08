"""
Demo Agent - Specialized agent for automated developer demonstrations
Extends APISandboxAgent with demo-specific capabilities for GitHub repo demos via Google Meet
"""

from os_computer_use.api_agent import APISandboxAgent
from os_computer_use.logging import logger
from os_computer_use.demo_setup_script import DemoSetupScript
from datetime import datetime
import re
import asyncio
from typing import Dict, List, Optional, Tuple


class DemoAgent(APISandboxAgent):
    """
    Specialized agent for automated demo presentations
    Extends APISandboxAgent with demo-specific capabilities
    """

    def __init__(self, sandbox, output_dir=".", save_logs=True):
        super().__init__(sandbox, output_dir, save_logs)
        self.demo_session_id = None
        self.demo_start_time = None
        self.current_step = None
        self.demo_progress = {
            "total_steps": 5,  # Reduced from 8 since script handles setup
            "completed_steps": [],
            "current_step_index": 0,
            "status": "initialized",
        }
        # Updated steps - script handles initial setup, agent handles interaction
        self.demo_steps = [
            "run_setup_script",  # Script handles: terminal, clone, navigate, code viewer, browser
            "navigate_to_meet",  # Agent: Navigate to Meet URL in browser
            "join_meet_call",  # Agent: Join the Google Meet
            "start_screen_share",  # Agent: Start screen sharing
            "wait_for_instructions",  # Agent: Wait for further instructions
        ]
        self.setup_script = DemoSetupScript(sandbox)

    def initialize_demo_session(self, github_url: str, meet_link: str) -> str:
        """
        Initialize a new demo session with validation

        Args:
            github_url: Valid HTTPS GitHub repository URL
            meet_link: Valid Google Meet URL

        Returns:
            Session ID for tracking
        """
        # Validate inputs
        if not self.validate_inputs(github_url, meet_link):
            raise ValueError("Invalid GitHub URL or Meet link provided")

        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.demo_session_id = f"demo_{timestamp}"
        self.demo_start_time = datetime.now()

        # Reset progress tracking
        self.demo_progress = {
            "total_steps": 8,
            "completed_steps": [],
            "current_step_index": 0,
            "status": "running",
            "github_url": github_url,
            "meet_link": meet_link,
            "session_id": self.demo_session_id,
            "start_time": self.demo_start_time.isoformat(),
        }

        logger.log(f"Demo session initialized: {self.demo_session_id}", "green")
        logger.log(f"GitHub URL: {github_url}", "blue")
        logger.log(f"Meet Link: {meet_link}", "blue")

        return self.demo_session_id

    def validate_inputs(self, github_url: str, meet_link: str) -> bool:
        """
        Validate GitHub URL and Google Meet link formats

        Args:
            github_url: GitHub repository URL to validate
            meet_link: Google Meet URL to validate

        Returns:
            True if both inputs are valid
        """
        # Validate GitHub URL format
        github_pattern = r"https://github\.com/[\w\-\.]+/[\w\-\.]+/?(?:\.git)?$"
        if not re.match(github_pattern, github_url):
            logger.log(f"Invalid GitHub URL format: {github_url}", "red")
            return False

        # Validate Google Meet URL format
        meet_pattern = r"https://meet\.google\.com/[a-z]{3}-[a-z]{4}-[a-z]{3}$"
        if not re.match(meet_pattern, meet_link):
            logger.log(f"Invalid Google Meet URL format: {meet_link}", "red")
            return False

        return True

    def get_sandbox_url(self) -> str:
        """
        Get the VNC URL for sandbox monitoring

        Returns:
            VNC stream URL for real-time monitoring
        """
        if self.sandbox and hasattr(self.sandbox, "stream"):
            return self.sandbox.stream.get_url()
        return None

    def get_progress_status(self) -> Dict:
        """
        Get detailed progress status of the demo session

        Returns:
            Dictionary containing progress information
        """
        if self.demo_start_time:
            runtime_seconds = (datetime.now() - self.demo_start_time).total_seconds()
            runtime_minutes = runtime_seconds / 60
        else:
            runtime_minutes = 0

        return {
            "session_id": self.demo_session_id,
            "status": self.demo_progress.get("status", "unknown"),
            "current_step": self.current_step,
            "step_progress": f"{len(self.demo_progress['completed_steps'])}/{self.demo_progress['total_steps']}",
            "completed_steps": self.demo_progress["completed_steps"],
            "runtime_minutes": round(runtime_minutes, 2),
            "sandbox_url": self.get_sandbox_url(),
            "github_url": self.demo_progress.get("github_url"),
            "meet_link": self.demo_progress.get("meet_link"),
            "start_time": self.demo_progress.get("start_time"),
        }

    def mark_step_completed(self, step_name: str, success: bool = True) -> None:
        """
        Mark a demo step as completed and update progress

        Args:
            step_name: Name of the completed step
            success: Whether the step completed successfully
        """
        if success and step_name not in self.demo_progress["completed_steps"]:
            self.demo_progress["completed_steps"].append(step_name)
            self.demo_progress["current_step_index"] = len(
                self.demo_progress["completed_steps"]
            )

        logger.log(
            f"Step {'completed' if success else 'failed'}: {step_name}",
            "green" if success else "red",
        )

    def extract_repo_name(self, github_url: str) -> str:
        """
        Extract repository name from GitHub URL

        Args:
            github_url: GitHub repository URL

        Returns:
            Repository name for directory navigation
        """
        # Remove .git suffix and extract repo name
        repo_name = github_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        return repo_name

    def is_demo_complete(self) -> bool:
        """
        Check if all demo steps have been completed

        Returns:
            True if demo is complete
        """
        return (
            len(self.demo_progress["completed_steps"])
            >= self.demo_progress["total_steps"]
        )

    def get_next_step(self) -> Optional[str]:
        """
        Get the next step that needs to be executed

        Returns:
            Next step name or None if demo is complete
        """
        current_index = len(self.demo_progress["completed_steps"])
        if current_index < len(self.demo_steps):
            return self.demo_steps[current_index]
        return None

    def handle_demo_error(self, step_name: str, error: Exception) -> Dict:
        """
        Handle errors during demo execution with recovery strategies

        Args:
            step_name: Name of the step that failed
            error: Exception that occurred

        Returns:
            Error report with recovery suggestions
        """
        error_report = {
            "step": step_name,
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
            "recovery_suggestions": [],
        }

        # Add specific recovery suggestions based on step
        if step_name == "clone_repository":
            error_report["recovery_suggestions"] = [
                "Check internet connectivity",
                "Verify repository exists and is public",
                "Try cloning with --depth=1 flag",
            ]
        elif step_name == "join_meet_call":
            error_report["recovery_suggestions"] = [
                "Check Meet link validity",
                "Verify browser permissions",
                "Try refreshing the page",
            ]
        elif step_name == "start_screen_share":
            error_report["recovery_suggestions"] = [
                "Check browser screen share permissions",
                "Try using a different browser",
                "Manually grant screen share access",
            ]
        else:
            error_report["recovery_suggestions"] = [
                "Take screenshot to analyze current state",
                "Retry the step with modified approach",
                "Skip to next step if non-critical",
            ]

        logger.log(f"Demo error in {step_name}: {error}", "red")
        return error_report

    def cleanup_demo_session(self) -> None:
        """
        Clean up demo session resources and reset state
        """
        if self.demo_session_id:
            logger.log(f"Cleaning up demo session: {self.demo_session_id}", "yellow")

        # Update final status
        if self.demo_progress:
            self.demo_progress["status"] = (
                "completed" if self.is_demo_complete() else "terminated"
            )

        # Reset session state
        self.demo_session_id = None
        self.demo_start_time = None
        self.current_step = None

        logger.log("Demo session cleanup completed", "green")

    def execute_step_with_verification(self, instruction: str, step_name: str) -> Dict:
        """
        Execute a step with post-execution verification
        Now handles hybrid approach: script for setup, agent for interaction

        Args:
            instruction: The instruction to execute
            step_name: Name of the step for verification

        Returns:
            Enhanced result with verification status
        """
        # Handle setup script step differently
        if step_name == "run_setup_script":
            # Extract URLs from instruction
            import re

            github_url_match = re.search(r"https://github\.com/[^\s]+", instruction)
            meet_url_match = re.search(r"https://meet\.google\.com/[^\s]+", instruction)

            if not github_url_match:
                return {
                    "action": "setup_script",
                    "result": "Error: No GitHub URL found in instruction",
                    "verification": "failed",
                    "verification_details": "GitHub URL required for setup",
                }

            github_url = github_url_match.group(0)
            meet_url = (
                meet_url_match.group(0)
                if meet_url_match
                else "https://meet.google.com/unknown"
            )

            # Run setup script
            setup_result = self.run_setup_script(github_url, meet_url)

            return {
                "action": "setup_script",
                "parameters": {"github_url": github_url, "meet_url": meet_url},
                "result": setup_result["message"],
                "verification": "success" if setup_result["success"] else "failed",
                "verification_details": setup_result.get("setup_results", {}),
                "completed": setup_result["success"],
                "timestamp": datetime.now().isoformat(),
            }

        # For interactive agent steps, use the original logic
        # Execute the base step
        result = self.execute_single_step(instruction)

        # Add a brief pause for command completion
        import time

        time.sleep(2)

        # Take a verification screenshot
        try:
            screenshot_data = self.screenshot()
            logger.log("📸 Verification screenshot taken", "gray")
        except Exception as e:
            logger.log(f"Failed to take verification screenshot: {e}", "yellow")

        # Enhanced verification based on step type
        if step_name == "navigate_to_meet":
            # For navigation to Meet, check if browser shows Google Meet
            try:
                # Take screenshot and check for Meet-related content
                # This is where the agent should navigate to the Meet URL
                result["verification"] = "manual"
                result["verification_details"] = (
                    "Agent should navigate to Google Meet URL"
                )
            except Exception as e:
                result["verification"] = "error"
                result["verification_details"] = f"Could not verify: {e}"

        elif step_name == "join_meet_call":
            # For joining meeting, look for meeting interface
            try:
                result["verification"] = "manual"
                result["verification_details"] = (
                    "Agent should join the Google Meet call"
                )
            except Exception as e:
                result["verification"] = "error"
                result["verification_details"] = f"Could not verify: {e}"

        elif step_name == "start_screen_share":
            # For screen sharing, check for sharing interface
            try:
                result["verification"] = "manual"
                result["verification_details"] = "Agent should start screen sharing"
            except Exception as e:
                result["verification"] = "error"
                result["verification_details"] = f"Could not verify: {e}"
        else:
            # For other steps, just mark as needs manual verification
            result["verification"] = "manual"
            result["verification_details"] = "Requires manual verification"

        return result

    def run_setup_script(self, github_url: str, meet_link: str) -> Dict:
        """
        Run the automated setup script to handle basic tasks

        This script reliably handles:
        - Opening terminal
        - Cloning the GitHub repository
        - Navigating to repository directory
        - Opening code viewer
        - Opening browser to Google Meet

        Args:
            github_url: GitHub repository URL to clone
            meet_link: Google Meet URL for later navigation

        Returns:
            Setup results and status
        """
        logger.log("🔧 Running automated setup script...", "blue")

        try:
            # Run the setup script
            setup_results = self.setup_script.run_full_setup(github_url, meet_link)

            if setup_results["ready_for_agent"]:
                logger.log("✅ Setup script completed successfully!", "green")
                logger.log("🤖 Environment ready for AI agent interaction", "blue")

                # Mark setup tasks as completed
                self.demo_progress["completed_steps"].extend(["run_setup_script"])

                return {
                    "success": True,
                    "message": "Setup script completed successfully",
                    "setup_results": setup_results,
                    "next_step": "navigate_to_meet",
                }
            else:
                logger.log("❌ Setup script failed", "red")
                failed_tasks = setup_results.get("failed_tasks", [])
                logger.log(f"Failed tasks: {failed_tasks}", "red")

                return {
                    "success": False,
                    "message": f"Setup script failed. Failed tasks: {failed_tasks}",
                    "setup_results": setup_results,
                    "next_step": None,
                }

        except Exception as e:
            logger.log(f"❌ Setup script error: {e}", "red")
            return {
                "success": False,
                "message": f"Setup script error: {str(e)}",
                "setup_results": None,
                "next_step": None,
            }
