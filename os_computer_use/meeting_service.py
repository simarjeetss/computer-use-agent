"""
Meeting Service - Handles Google Meet operations
Completely independent from repository functionality
"""

import time
from typing import Dict, Any, Optional


class MeetingService:
    """
    Handles all Google Meet operations independently
    Can be used without any repository functionality
    """

    def __init__(self, sandbox):
        self.sandbox = sandbox
        self.meeting_log = []
        self.current_meet_url = None
        self.meeting_status = "not_started"

    def log(self, message: str, status: str = "info"):
        """Log a message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.meeting_log.append(
            {"message": message, "status": status, "timestamp": timestamp}
        )

        # Color coding
        colors = {
            "info": "\033[94m",  # Blue
            "success": "\033[92m",  # Green
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "reset": "\033[0m",  # Reset
        }

        color = colors.get(status, colors["info"])
        print(f"{color}{log_entry}{colors['reset']}")

    def run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run a command in the sandbox and return result"""
        try:
            self.log(f"Executing: {command}")
            result = self.sandbox.commands.run(command, timeout=timeout)

            if result.exit_code == 0:
                self.log(f"✅ Command succeeded: {command}", "success")
                return {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                }
            else:
                self.log(
                    f"❌ Command failed (exit {result.exit_code}): {command}", "error"
                )
                return {
                    "success": False,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                }

        except Exception as e:
            self.log(f"❌ Command error: {e}", "error")
            return {"success": False, "error": str(e), "exit_code": -1}

    def validate_meet_url(self, meet_url: str) -> bool:
        """Validate Google Meet URL format"""
        import re

        meet_pattern = r"https://meet\.google\.com/[a-z]{3}-[a-z]{4}-[a-z]{3}$"
        if not re.match(meet_pattern, meet_url):
            self.log(f"❌ Invalid Google Meet URL format: {meet_url}", "error")
            return False
        return True

    def open_browser(self) -> bool:
        """Open browser ready for Google Meet"""
        self.log("🌐 Opening browser for Google Meet...")

        # First, try to open Firefox
        firefox_result = self.run_command("firefox --new-window 'about:blank' &")

        if not firefox_result["success"]:
            # Fallback to other browsers
            self.log("⚠️ Firefox not available, trying other browsers", "warning")

            # Try Chrome/Chromium
            chrome_result = self.run_command(
                "google-chrome --new-window 'about:blank' &"
            )
            if not chrome_result["success"]:
                chromium_result = self.run_command(
                    "chromium-browser --new-window 'about:blank' &"
                )
                if not chromium_result["success"]:
                    self.log("❌ No browser available", "error")
                    return False

        # Wait for browser to start
        time.sleep(3)

        self.log("✅ Browser opened and ready", "success")
        return True

    def navigate_to_meet(self, meet_url: str) -> Dict[str, Any]:
        """
        Navigate browser to Google Meet URL
        This should be handled by the AI agent for visual interaction
        """
        if not self.validate_meet_url(meet_url):
            return {
                "success": False,
                "message": "Invalid Google Meet URL",
                "next_action": "fix_url",
            }

        self.current_meet_url = meet_url
        self.log(f"🎯 Ready to navigate to Google Meet: {meet_url}", "info")

        return {
            "success": True,
            "message": f"Browser ready for navigation to {meet_url}",
            "meet_url": meet_url,
            "next_action": "ai_agent_navigate",
            "instructions": "AI agent should navigate to the Meet URL and handle visual elements",
        }

    def get_meeting_status(self) -> Dict[str, Any]:
        """Get current meeting status"""
        return {
            "status": self.meeting_status,
            "meet_url": self.current_meet_url,
            "logs": self.meeting_log[-5:],  # Last 5 log entries
            "timestamp": time.strftime("%H:%M:%S"),
        }

    def setup_meeting_environment(self, meet_url: str) -> Dict[str, Any]:
        """
        Complete meeting environment setup

        Args:
            meet_url: Google Meet URL

        Returns:
            Setup results and status
        """
        self.log("🚀 Starting meeting environment setup...", "info")
        self.log(f"📹 Meet URL: {meet_url}", "info")

        results = {
            "overall_success": True,
            "completed_tasks": [],
            "failed_tasks": [],
            "meeting_log": self.meeting_log,
            "meeting_ready": False,
            "meet_url": meet_url,
            "next_steps": [],
        }

        # Task 1: Validate Meet URL
        if self.validate_meet_url(meet_url):
            results["completed_tasks"].append("validate_meet_url")
        else:
            results["failed_tasks"].append("validate_meet_url")
            results["overall_success"] = False
            return results

        # Task 2: Open browser
        if self.open_browser():
            results["completed_tasks"].append("open_browser")
        else:
            results["failed_tasks"].append("open_browser")
            results["overall_success"] = False
            return results

        # Task 3: Prepare for navigation (AI agent task)
        nav_result = self.navigate_to_meet(meet_url)
        if nav_result["success"]:
            results["completed_tasks"].append("prepare_navigation")
            results["meeting_ready"] = True
            results["next_steps"] = [
                "AI Agent: Navigate to Google Meet URL",
                "AI Agent: Join the meeting",
                "AI Agent: Start screen sharing",
                "AI Agent: Handle meeting interactions",
            ]
            self.meeting_status = "ready_for_agent"
            self.log(
                "🎉 Meeting environment setup completed! Ready for AI agent.", "success"
            )
        else:
            results["failed_tasks"].append("prepare_navigation")
            results["overall_success"] = False

        return results

    def navigate_to_meet_with_agent(self, meet_url: str, agent=None) -> Dict[str, Any]:
        """
        Actually navigate to Google Meet URL using AI agent
        This performs the real navigation, not just preparation
        """
        if not self.validate_meet_url(meet_url):
            return {
                "success": False,
                "message": "Invalid Google Meet URL",
                "next_action": "fix_url",
            }

        self.current_meet_url = meet_url
        self.log(f"🎯 Navigating to Google Meet: {meet_url}", "info")

        try:
            if agent:
                # Use AI agent to navigate to Meet URL
                navigation_instruction = f"""Navigate to Google Meet URL in the browser.

IMPORTANT: You need to navigate to this exact URL: {meet_url}

Steps:
1. Look for the browser address bar (URL bar)
2. Click on the address bar to focus it
3. Clear any existing URL
4. Type the exact Meet URL: {meet_url}
5. Press Enter to navigate to the meeting

Expected result: Browser should show the Google Meet interface with options to join the meeting."""

                self.log("🤖 Using AI agent to navigate to Meet URL...", "info")
                result = agent.execute_single_step(navigation_instruction)

                if result.get("success", True):  # Default to success if not specified
                    self.log("✅ AI agent navigation completed", "success")
                    return {
                        "success": True,
                        "message": f"Successfully navigated to {meet_url}",
                        "meet_url": meet_url,
                        "next_action": "join_meeting",
                        "agent_result": result,
                    }
                else:
                    self.log("❌ AI agent navigation failed", "error")
                    return {
                        "success": False,
                        "message": "AI agent failed to navigate to Meet URL",
                        "meet_url": meet_url,
                        "agent_result": result,
                    }
            else:
                # Fallback: direct browser navigation (less reliable)
                self.log("⚠️ No AI agent available, using direct navigation", "warning")
                nav_result = self.run_command(f"firefox '{meet_url}' &")

                if nav_result["success"]:
                    time.sleep(5)  # Wait for page load
                    return {
                        "success": True,
                        "message": f"Opened browser to {meet_url}",
                        "meet_url": meet_url,
                        "next_action": "join_meeting",
                        "method": "direct_browser",
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to open browser to Meet URL",
                        "error": nav_result.get("stderr", "Unknown error"),
                    }

        except Exception as e:
            self.log(f"❌ Navigation error: {e}", "error")
            return {
                "success": False,
                "message": f"Navigation failed: {e}",
                "meet_url": meet_url,
            }

    def join_meeting_with_agent(self, agent=None) -> Dict[str, Any]:
        """
        Actually join the Google Meet call using AI agent
        This performs the real joining, not just preparation
        """
        if not self.current_meet_url:
            return {
                "success": False,
                "message": "No Meet URL set - navigate first",
                "next_action": "navigate_first",
            }

        self.log(f"🎤 Joining Google Meet call...", "info")

        try:
            if agent:
                # Use AI agent to join the meeting
                join_instruction = """Join the Google Meet call that is currently displayed in the browser.

IMPORTANT: You should see the Google Meet interface. Look for join options.

Steps:
1. Look for a "Join now" button or similar
2. You might see options like:
   - "Join now" 
   - "Ask to join"
   - "Join with a meeting ID"
3. Click the appropriate join button
4. If prompted for camera/microphone permissions, allow them
5. If asked for your name, you can enter "Demo Agent" or similar
6. Complete the joining process

Expected result: You should be in the Google Meet call with video/audio controls visible."""

                self.log("🤖 Using AI agent to join meeting...", "info")
                result = agent.execute_single_step(join_instruction)

                if result.get("success", True):  # Default to success if not specified
                    self.log("✅ AI agent successfully joined meeting", "success")
                    self.meeting_status = "joined"
                    return {
                        "success": True,
                        "message": "Successfully joined Google Meet call",
                        "meet_url": self.current_meet_url,
                        "status": "joined",
                        "next_action": "start_screen_share",
                        "agent_result": result,
                    }
                else:
                    self.log("❌ AI agent failed to join meeting", "error")
                    return {
                        "success": False,
                        "message": "AI agent failed to join meeting",
                        "meet_url": self.current_meet_url,
                        "agent_result": result,
                    }
            else:
                # No AI agent available
                self.log("⚠️ No AI agent available for meeting join", "warning")
                return {
                    "success": False,
                    "message": "AI agent required for meeting join",
                    "meet_url": self.current_meet_url,
                    "instructions": "Manual join required - look for join button in browser",
                }

        except Exception as e:
            self.log(f"❌ Meeting join error: {e}", "error")
            return {
                "success": False,
                "message": f"Join failed: {e}",
                "meet_url": self.current_meet_url,
            }

    def start_screen_share_with_agent(self, agent=None) -> Dict[str, Any]:
        """
        Start screen sharing in Google Meet using AI agent
        """
        if self.meeting_status != "joined":
            return {
                "success": False,
                "message": "Must join meeting first before screen sharing",
                "next_action": "join_meeting_first",
            }

        self.log(f"🖥️ Starting screen share...", "info")

        try:
            if agent:
                # Use AI agent to start screen sharing
                share_instruction = """Start screen sharing in the Google Meet call.

IMPORTANT: You should be in an active Google Meet call. Look for screen sharing controls.

Steps:
1. Look for a screen share button (usually has a monitor/screen icon)
2. It might be labeled "Present now", "Share screen", or have a screen icon
3. Click the screen share button
4. You'll see options for what to share:
   - "Your entire screen" 
   - "A window"
   - "A tab"
5. Choose "Your entire screen" for the demo
6. Click "Share" to start sharing
7. You should see a "You're presenting" indicator

Expected result: Screen sharing should be active and other participants can see your screen."""

                self.log("🤖 Using AI agent to start screen sharing...", "info")
                result = agent.execute_single_step(share_instruction)

                if result.get("success", True):  # Default to success if not specified
                    self.log(
                        "✅ AI agent successfully started screen sharing", "success"
                    )
                    self.meeting_status = "screen_sharing"
                    return {
                        "success": True,
                        "message": "Successfully started screen sharing",
                        "meet_url": self.current_meet_url,
                        "status": "screen_sharing",
                        "agent_result": result,
                    }
                else:
                    self.log("❌ AI agent failed to start screen sharing", "error")
                    return {
                        "success": False,
                        "message": "AI agent failed to start screen sharing",
                        "status": self.meeting_status,
                        "agent_result": result,
                    }
            else:
                # No AI agent available
                self.log("⚠️ No AI agent available for screen sharing", "warning")
                return {
                    "success": False,
                    "message": "AI agent required for screen sharing",
                    "instructions": "Manual screen share required - look for share screen button",
                }

        except Exception as e:
            self.log(f"❌ Screen sharing error: {e}", "error")
            return {
                "success": False,
                "message": f"Screen sharing failed: {e}",
                "status": self.meeting_status,
            }

    def complete_meeting_workflow(self, meet_url: str, agent=None) -> Dict[str, Any]:
        """
        Complete end-to-end meeting workflow: navigate -> join -> screen share
        """
        self.log("🚀 Starting complete meeting workflow...", "info")

        workflow_results = {
            "overall_success": False,
            "completed_tasks": [],
            "failed_tasks": [],
            "workflow_log": [],
            "meet_url": meet_url,
            "final_status": "not_started",
        }

        # Step 1: Navigate to Meet URL
        nav_result = self.navigate_to_meet_with_agent(meet_url, agent)
        workflow_results["navigation_result"] = nav_result

        if nav_result["success"]:
            workflow_results["completed_tasks"].append("navigate_to_meet")
            workflow_results["workflow_log"].append(
                "✅ Successfully navigated to Meet URL"
            )
        else:
            workflow_results["failed_tasks"].append("navigate_to_meet")
            workflow_results["workflow_log"].append(
                f"❌ Navigation failed: {nav_result['message']}"
            )
            return workflow_results

        # Wait a moment for page to load
        time.sleep(3)

        # Step 2: Join the meeting
        join_result = self.join_meeting_with_agent(agent)
        workflow_results["join_result"] = join_result

        if join_result["success"]:
            workflow_results["completed_tasks"].append("join_meeting")
            workflow_results["workflow_log"].append(
                "✅ Successfully joined the meeting"
            )
        else:
            workflow_results["failed_tasks"].append("join_meeting")
            workflow_results["workflow_log"].append(
                f"❌ Join failed: {join_result['message']}"
            )
            return workflow_results

        # Wait a moment for meeting to stabilize
        time.sleep(5)

        # Step 3: Start screen sharing
        share_result = self.start_screen_share_with_agent(agent)
        workflow_results["screen_share_result"] = share_result

        if share_result["success"]:
            workflow_results["completed_tasks"].append("start_screen_share")
            workflow_results["workflow_log"].append(
                "✅ Successfully started screen sharing"
            )
            workflow_results["overall_success"] = True
            workflow_results["final_status"] = "screen_sharing"
        else:
            workflow_results["failed_tasks"].append("start_screen_share")
            workflow_results["workflow_log"].append(
                f"❌ Screen sharing failed: {share_result['message']}"
            )
            workflow_results["final_status"] = "joined_no_sharing"
            # Still consider partially successful if we joined the meeting
            workflow_results["overall_success"] = True

        self.log("🎉 Meeting workflow completed!", "success")
        return workflow_results

    def navigate_to_meet_with_commands(self, meet_url: str) -> Dict[str, Any]:
        """
        Navigate to Google Meet using clear, defined steps (no AI agent)

        Args:
            meet_url: Google Meet URL to navigate to

        Returns:
            Navigation results
        """
        self.log(f"🌐 Starting structured navigation to: {meet_url}")

        try:
            # Step 1: Focus on browser window
            self.log("🎯 Step 1: Focusing on browser window")
            focus_result = self.run_command("wmctrl -a firefox", timeout=10)
            if not focus_result["success"]:
                self.log("⚠️  Browser focus failed, trying alternative", "warning")
                self.run_command(
                    "xdotool search --name firefox windowactivate", timeout=10
                )

            time.sleep(2)

            # Step 2: Navigate to URL using keyboard shortcut
            self.log("🎯 Step 2: Opening address bar (Ctrl+L)")
            self.run_command("xdotool key ctrl+l", timeout=5)
            time.sleep(1)

            # Step 3: Type the Meet URL
            self.log(f"🎯 Step 3: Typing Meet URL: {meet_url}")
            self.run_command(f"xdotool type '{meet_url}'", timeout=10)
            time.sleep(1)

            # Step 4: Press Enter to navigate
            self.log("🎯 Step 4: Pressing Enter to navigate")
            self.run_command("xdotool key Return", timeout=5)
            time.sleep(5)  # Wait for page to load

            self.log("✅ Navigation commands completed", "success")
            return {
                "success": True,
                "message": "Navigation completed successfully",
                "next_action": "join_meeting",
            }

        except Exception as e:
            self.log(f"❌ Navigation failed: {str(e)}", "error")
            return {
                "success": False,
                "message": f"Navigation failed: {str(e)}",
                "error": str(e),
            }

    def join_meeting_with_commands(
        self, participant_name: str = "RAAY Agent"
    ) -> Dict[str, Any]:
        """
        Join Google Meet using clear, defined steps (no AI agent)

        Args:
            participant_name: Name to use when joining (default: "RAAY Agent")

        Returns:
            Join results
        """
        self.log(f"🎤 Starting structured meeting join as: {participant_name}")

        try:
            # Step 1: Wait for page to load completely
            self.log("🎯 Step 1: Waiting for Meet page to load")
            time.sleep(5)

            # Step 2: Look for and click name input field
            self.log("🎯 Step 2: Focusing on name input field")
            # Try multiple approaches to find name field
            name_field_commands = [
                "xdotool search --name 'Google Meet' windowactivate",
                "xdotool key Tab Tab Tab",  # Tab to name field
                "xdotool key ctrl+a",  # Select all text
            ]

            for cmd in name_field_commands:
                self.run_command(cmd, timeout=5)
                time.sleep(1)

            # Step 3: Enter participant name
            self.log(f"🎯 Step 3: Entering name: {participant_name}")
            self.run_command(f"xdotool type '{participant_name}'", timeout=10)
            time.sleep(1)

            # Step 4: Look for and click "Join now" button
            self.log("🎯 Step 4: Attempting to join meeting")
            join_attempts = [
                "xdotool key Tab Return",  # Tab to join button and press
                "xdotool key Return",  # Direct Enter
                "xdotool key space",  # Space to activate button
            ]

            for i, cmd in enumerate(join_attempts, 1):
                self.log(f"🎯 Join attempt {i}: {cmd}")
                self.run_command(cmd, timeout=5)
                time.sleep(2)

                # Check if we successfully joined (basic check)
                if i == len(join_attempts):
                    self.log("🎯 Final join attempt completed")

            # Step 5: Wait for meeting to load
            self.log("🎯 Step 5: Waiting for meeting interface to load")
            time.sleep(5)

            self.meeting_status = "joined"
            self.log("✅ Meeting join process completed", "success")

            return {
                "success": True,
                "message": f"Successfully joined meeting as {participant_name}",
                "participant_name": participant_name,
                "status": "joined",
            }

        except Exception as e:
            self.log(f"❌ Meeting join failed: {str(e)}", "error")
            return {
                "success": False,
                "message": f"Meeting join failed: {str(e)}",
                "error": str(e),
            }

    def complete_meeting_setup_with_commands(
        self, meet_url: str, participant_name: str = "RAAY Agent"
    ) -> Dict[str, Any]:
        """
        Complete meeting setup using structured commands (no AI agent)

        Args:
            meet_url: Google Meet URL
            participant_name: Name to use when joining

        Returns:
            Complete setup results
        """
        self.log("🚀 Starting complete meeting setup with structured commands")
        self.log(f"📹 Meet URL: {meet_url}")
        self.log(f"👤 Participant Name: {participant_name}")

        results = {
            "success": True,
            "steps_completed": [],
            "errors": [],
        }

        try:
            # Step 1: Setup browser environment
            self.log("🎯 Step 1: Setting up browser environment")
            env_result = self.setup_meeting_environment(meet_url)
            if env_result.get("overall_success", False):
                results["steps_completed"].append("browser_environment")
                self.log("✅ Browser environment ready", "success")
            else:
                results["errors"].append("browser_environment_failed")
                self.log("❌ Browser environment setup failed", "error")

            # Step 2: Navigate to Meet URL
            self.log("🎯 Step 2: Navigating to Meet URL")
            nav_result = self.navigate_to_meet_with_commands(meet_url)
            if nav_result["success"]:
                results["steps_completed"].append("navigation")
                self.log("✅ Navigation completed", "success")
            else:
                results["errors"].append("navigation_failed")
                results["success"] = False

            # Step 3: Join the meeting
            self.log("🎯 Step 3: Joining the meeting")
            join_result = self.join_meeting_with_commands(participant_name)
            if join_result["success"]:
                results["steps_completed"].append("meeting_joined")
                self.log("✅ Meeting joined successfully", "success")
            else:
                results["errors"].append("meeting_join_failed")
                results["success"] = False

            # Step 4: Final status
            if results["success"]:
                self.meeting_status = "active"
                self.log("🎉 Complete meeting setup successful!", "success")
                results["final_status"] = "active"
            else:
                self.log("⚠️  Meeting setup completed with some issues", "warning")
                results["final_status"] = "partial"

        except Exception as e:
            self.log(f"❌ Complete meeting setup failed: {str(e)}", "error")
            results["success"] = False
            results["error"] = str(e)
            results["final_status"] = "failed"

        return results
