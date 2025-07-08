"""
Demo Orchestrator - Manages sequential execution of demo steps
Handles retries, error recovery, and progress tracking for demo sessions
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from os_computer_use.demo_agent import DemoAgent
from os_computer_use.demo_prompts import DemoPrompts
from os_computer_use.hybrid_demo_prompts import HybridDemoPrompts
from os_computer_use.demo_config import DemoConfig
from os_computer_use.logging import logger


class DemoOrchestrator:
    """
    Manages the sequential execution of demo steps
    Handles retries, error recovery, and progress tracking
    """

    def __init__(self, agent: DemoAgent):
        self.agent = agent
        self.max_retries = DemoConfig.MAX_RETRIES_PER_STEP
        self.step_timeout = 180  # 3 minutes per step
        self.execution_log = []
        self.current_step_start_time = None
        self.use_hybrid_approach = True  # Use hybrid setup script + agent approach

    async def run_full_demo(self, github_url: str, meet_link: str) -> Dict:
        """
        Execute the complete demo workflow from start to finish

        Args:
            github_url: GitHub repository URL to clone
            meet_link: Google Meet URL to join

        Returns:
            Complete execution summary
        """
        try:
            # Initialize demo session
            session_id = self.agent.initialize_demo_session(github_url, meet_link)
            logger.log(f"Starting full demo execution: {session_id}", "blue")

            # Execute each step in sequence with hybrid approach
            if self.use_hybrid_approach:
                demo_steps = [
                    (
                        "run_setup_script",
                        f"Run setup script for {github_url} and {meet_link}",
                    ),
                    ("navigate_to_meet", f"Navigate to Google Meet: {meet_link}"),
                    ("join_meet_call", "Join the Google Meet call"),
                    ("start_screen_share", "Start screen sharing"),
                    ("wait_for_instructions", "Wait for further instructions"),
                ]
            else:
                # Original approach (fallback)
                demo_steps = [
                    ("open_terminal", "Open terminal application"),
                    ("clone_repository", f"Clone repository: {github_url}"),
                    ("navigate_to_repo", f"Navigate to repository directory"),
                    ("open_code_viewer", "Open code viewer (VS Code or file listing)"),
                    ("open_browser", "Open web browser"),
                    ("join_meet_call", f"Join Google Meet: {meet_link}"),
                    ("start_screen_share", "Start screen sharing"),
                    ("wait_for_instructions", "Wait for further instructions"),
                ]

            for step_name, step_description in demo_steps:
                success = await self.execute_step_with_retry(
                    step_name, step_description, github_url, meet_link
                )

                if not success:
                    logger.log(f"Demo failed at step: {step_name}", "red")
                    break

                # Check if we should continue
                if step_name == "wait_for_instructions":
                    logger.log(
                        "Demo setup complete - waiting for user instructions", "green"
                    )
                    break

            # Generate final summary
            return self.get_execution_summary()

        except Exception as e:
            logger.log(f"Critical error during demo execution: {e}", "red")
            return {
                "success": False,
                "error": str(e),
                "execution_log": self.execution_log,
                "timestamp": datetime.now().isoformat(),
            }

    async def execute_step_with_retry(
        self, step_name: str, step_description: str, github_url: str, meet_link: str
    ) -> bool:
        """
        Execute a single step with retry logic and error recovery

        Args:
            step_name: Internal step name
            step_description: Human-readable step description
            github_url: GitHub repository URL
            meet_link: Google Meet URL

        Returns:
            True if step completed successfully
        """
        self.current_step_start_time = datetime.now()
        self.agent.current_step = step_name

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.log(
                    f"Executing step {step_name} (attempt {attempt}/{self.max_retries})",
                    "blue",
                )

                # Get step-specific instruction
                instruction = self._get_step_instruction(
                    step_name, github_url, meet_link
                )

                # Execute step with verification
                if hasattr(self.agent, "execute_step_with_verification"):
                    result = self.agent.execute_step_with_verification(
                        instruction, step_name
                    )
                else:
                    result = self.agent.execute_single_step(instruction)

                # Check verification result
                verification_success = result.get("verification") == "success"
                step_completed = result.get("completed", False)
                validation_success = self._validate_step_success(step_name, result)

                # Log step execution
                step_log = {
                    "step": step_name,
                    "description": step_description,
                    "attempt": attempt,
                    "instruction": instruction,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                    "success": step_completed
                    or verification_success
                    or validation_success,
                }

                self.execution_log.append(step_log)

                # Check if step completed successfully
                if step_log["success"]:
                    self.agent.mark_step_completed(step_name, True)
                    logger.log(f"Step {step_name} completed successfully", "green")
                    return True
                elif result.get("action") == "stop":
                    # If AI thinks task is done but we haven't validated success
                    if self._validate_step_success(step_name, result):
                        self.agent.mark_step_completed(step_name, True)
                        logger.log(f"Step {step_name} completed (validated)", "green")
                        return True

                # Step failed, prepare for retry
                logger.log(
                    f"Step {step_name} failed, attempt {attempt}/{self.max_retries}",
                    "yellow",
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(2)  # Brief pause before retry

            except Exception as e:
                error_report = self.agent.handle_demo_error(step_name, e)
                step_log = {
                    "step": step_name,
                    "description": step_description,
                    "attempt": attempt,
                    "error": error_report,
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                }
                self.execution_log.append(step_log)

                if attempt < self.max_retries:
                    logger.log(f"Retrying step {step_name} after error: {e}", "yellow")
                    await asyncio.sleep(5)  # Longer pause after error
                else:
                    logger.log(
                        f"Step {step_name} failed after {self.max_retries} attempts",
                        "red",
                    )

        # All retries exhausted
        self.agent.mark_step_completed(step_name, False)
        return False

    def _get_step_instruction(
        self, step_name: str, github_url: str, meet_link: str
    ) -> str:
        """
        Get the appropriate instruction for each demo step using HybridDemoPrompts

        Args:
            step_name: The step to get instruction for
            github_url: GitHub repository URL
            meet_link: Google Meet URL

        Returns:
            Instruction string for the AI agent
        """
        if self.use_hybrid_approach:
            # Use hybrid prompts for new approach
            return HybridDemoPrompts.get_prompts_for_step(
                step_name, github_url=github_url, meet_link=meet_link
            )
        else:
            # Fallback to original prompts
            repo_name = self.agent.extract_repo_name(github_url)
            return DemoPrompts.get_step_prompt(
                step_name,
                github_url=github_url,
                meet_link=meet_link,
                repo_name=repo_name,
            )

    def _validate_step_success(self, step_name: str, result: Dict) -> bool:
        """
        Validate if a step completed successfully based on the result

        Args:
            step_name: Name of the step to validate
            result: Result from step execution

        Returns:
            True if step appears to have succeeded
        """
        action = result.get("action", "")
        result_text = str(result.get("result", "")).lower()

        # Check if the agent explicitly said it was completed
        if result.get("completed", False):
            return True

        # Handle new hybrid approach steps
        if step_name == "run_setup_script":
            # Setup script success is determined by the script itself
            return result.get("verification") == "success"

        elif step_name == "navigate_to_meet":
            # Navigation to Meet successful if we see meet-related content
            return any(
                indicator in result_text
                for indicator in [
                    "meet.google.com",
                    "google meet",
                    "join",
                    "meeting",
                    "navigated",
                    "loaded",
                ]
            )

        elif step_name == "join_meet_call":
            # Meeting join successful if we see meeting interface
            return any(
                indicator in result_text
                for indicator in [
                    "joined",
                    "meeting",
                    "participants",
                    "in call",
                    "camera",
                    "microphone",
                    "present",
                ]
            )

        elif step_name == "start_screen_share":
            # Screen sharing successful if we see sharing interface
            return any(
                indicator in result_text
                for indicator in [
                    "sharing",
                    "screen",
                    "present",
                    "presenting",
                    "shared",
                ]
            )

        # Legacy validation for old approach (fallback)
        elif step_name == "open_terminal":
            # Terminal is open if we see terminal-related indicators
            return any(
                indicator in result_text
                for indicator in [
                    "terminal",
                    "command prompt",
                    "shell",
                    "$",
                    "user@",
                    "opened",
                ]
            )

        elif step_name == "clone_repository":
            # Git clone is successful if we see cloning indicators
            # Also check if run_command was used (more reliable than typing)
            if action == "run_command" and "git clone" in str(
                result.get("parameters", {})
            ):
                # run_command was used, check output
                return any(
                    indicator in result_text
                    for indicator in [
                        "cloning into",
                        "clone",
                        "done",
                        "complete",
                        "success",
                        "receiving objects",
                        "resolving deltas",
                    ]
                )
            elif action in ["type_text", "send_key"] or result.get("follow_up_action"):
                # Manual typing was used, but we may have auto-pressed Enter
                # Check if we typed a git clone command
                parameters = result.get("parameters", {})
                if (
                    "git clone" in str(parameters)
                    or result.get("follow_up_action") == "send_key"
                ):
                    # We typed a git clone command and pressed Enter, check for directory creation
                    # This is more reliable than checking command output for manual typing
                    return True  # Let verification step handle detailed checking
                # Check output for any cloning indicators
                return any(
                    indicator in result_text
                    for indicator in ["cloning", "clone", "typed", "entered", "pressed"]
                )
            else:
                # Other actions
                return any(
                    indicator in result_text
                    for indicator in ["cloning", "clone", "done", "complete", "success"]
                )

        elif step_name == "navigate_to_repo":
            # Navigation successful if directory changed
            if action == "run_command" and "cd " in str(result.get("parameters", {})):
                # run_command cd should complete without error
                return "error" not in result_text and "not found" not in result_text
            elif action in ["type_text", "send_key"] or result.get("follow_up_action"):
                # Manual typing was used, check if we typed cd command and pressed Enter
                parameters = result.get("parameters", {})
                if (
                    "cd " in str(parameters)
                    or result.get("follow_up_action") == "send_key"
                ):
                    # We typed cd command and pressed Enter
                    return True  # Let verification step handle detailed checking
                return any(
                    indicator in result_text
                    for indicator in [
                        "changed",
                        "directory",
                        "moved",
                        "cd",
                        "typed",
                        "pressed",
                    ]
                )
            else:
                return any(
                    indicator in result_text
                    for indicator in ["changed", "directory", "moved", "cd"]
                )

        elif step_name == "open_code_viewer":
            return any(
                indicator in result_text
                for indicator in [
                    "code",
                    "vs code",
                    "vscode",
                    "opened",
                    "files",
                    "listed",
                    "editor",
                ]
            )

        elif step_name == "open_browser":
            return any(
                indicator in result_text
                for indicator in [
                    "browser",
                    "firefox",
                    "chrome",
                    "opened",
                    "launched",
                    "web",
                ]
            )

        elif step_name == "join_meet_call":
            return any(
                indicator in result_text
                for indicator in [
                    "meet",
                    "joined",
                    "call",
                    "connected",
                    "guest",
                    "video",
                ]
            )

        elif step_name == "start_screen_share":
            return any(
                indicator in result_text
                for indicator in ["screen", "sharing", "present", "share", "started"]
            )

        elif step_name == "wait_for_instructions":
            return any(
                indicator in result_text
                for indicator in ["waiting", "ready", "complete", "active"]
            )

        # Default: look for general success indicators
        return any(
            indicator in result_text
            for indicator in [
                "success",
                "complete",
                "done",
                "finished",
                "opened",
                "started",
            ]
        )

    def log_step_completion(self, step: str, success: bool, details: str) -> None:
        """
        Log the completion of a demo step

        Args:
            step: Step name
            success: Whether step succeeded
            details: Additional details about the step execution
        """
        log_entry = {
            "step": step,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": None,
        }

        if self.current_step_start_time:
            duration = (datetime.now() - self.current_step_start_time).total_seconds()
            log_entry["duration_seconds"] = round(duration, 2)

        self.execution_log.append(log_entry)
        logger.log(
            f"Step logged: {step} - {'Success' if success else 'Failed'}",
            "green" if success else "red",
        )

    def get_execution_summary(self) -> Dict:
        """
        Generate a comprehensive execution summary

        Returns:
            Summary of the demo execution
        """
        total_steps = len(self.execution_log)
        successful_steps = sum(
            1 for log in self.execution_log if log.get("success", False)
        )

        return {
            "session_id": self.agent.demo_session_id,
            "success": self.agent.is_demo_complete(),
            "steps_completed": successful_steps,
            "total_steps": total_steps,
            "completion_rate": round(
                (successful_steps / total_steps * 100) if total_steps > 0 else 0, 1
            ),
            "execution_log": self.execution_log,
            "progress_status": self.agent.get_progress_status(),
            "sandbox_url": self.agent.get_sandbox_url(),
            "timestamp": datetime.now().isoformat(),
        }
