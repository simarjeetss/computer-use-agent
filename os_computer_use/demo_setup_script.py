#!/bin/bash
"""
Demo Setup Script - Handles initial setup tasks reliably
This script performs the basic setup tasks that don't require AI:
1. Clone the GitHub repository
2. Open terminal
3. Open browser to Google Meet
4. Open code viewer

The AI agent then takes over for interactive tasks:
- Navigate to Meet link
- Join the meeting
- Start screen sharing
- Interact with participants
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any


class DemoSetupScript:
    """Handles reliable setup of demo environment"""

    def __init__(self, sandbox):
        self.sandbox = sandbox
        self.setup_log = []

    def log(self, message: str, status: str = "info"):
        """Log a message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.setup_log.append(
            {"message": message, "status": status, "timestamp": timestamp}
        )

        # Color coding for different statuses
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

    def clone_repository(self, github_url: str) -> bool:
        """Clone the GitHub repository reliably"""
        self.log("🔄 Starting repository clone...")

        # Extract repository name from URL
        repo_name = github_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        # Check if directory already exists
        ls_result = self.run_command("ls -la")
        if repo_name in ls_result.get("stdout", ""):
            self.log(f"⚠️ Directory {repo_name} already exists, removing...", "warning")
            self.run_command(f"rm -rf {repo_name}")

        # Clone the repository
        clone_result = self.run_command(f"git clone {github_url}", timeout=60)

        if not clone_result["success"]:
            self.log(
                f"❌ Git clone failed: {clone_result.get('stderr', 'Unknown error')}",
                "error",
            )
            return False

        # Verify the clone worked
        ls_result = self.run_command("ls -la")
        if repo_name not in ls_result.get("stdout", ""):
            self.log(
                f"❌ Repository directory {repo_name} not found after clone", "error"
            )
            return False

        self.log(f"✅ Successfully cloned repository: {repo_name}", "success")
        return True

    def navigate_to_repository(self, github_url: str) -> bool:
        """Navigate to the cloned repository directory"""
        repo_name = github_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        self.log(f"📁 Navigating to repository: {repo_name}")

        # Change to repository directory
        cd_result = self.run_command(f"cd {repo_name} && pwd")

        if not cd_result["success"]:
            self.log(f"❌ Failed to navigate to {repo_name}", "error")
            return False

        # Verify we're in the right directory
        if repo_name not in cd_result.get("stdout", ""):
            self.log(f"❌ Not in expected directory {repo_name}", "error")
            return False

        self.log(f"✅ Successfully navigated to {repo_name}", "success")
        return True

    def open_terminal(self) -> bool:
        """Ensure terminal is open and responsive"""
        self.log("🖥️ Setting up terminal...")

        # Test terminal responsiveness
        test_result = self.run_command("echo 'Terminal test successful'")

        if not test_result["success"]:
            self.log("❌ Terminal not responsive", "error")
            return False

        if "Terminal test successful" not in test_result.get("stdout", ""):
            self.log("❌ Terminal output not as expected", "error")
            return False

        self.log("✅ Terminal is ready", "success")
        return True

    def open_code_viewer(self, github_url: str) -> bool:
        """Open code viewer (try VS Code, fallback to file listing)"""
        repo_name = github_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        self.log("📝 Opening code viewer...")

        # Try to open VS Code
        code_result = self.run_command(
            f"cd {repo_name} && code . 2>/dev/null || echo 'VS Code not available'"
        )

        if "VS Code not available" in code_result.get("stdout", ""):
            self.log("⚠️ VS Code not available, showing file listing", "warning")

            # Fallback: show file structure
            ls_result = self.run_command(
                f"cd {repo_name} && find . -type f -name '*.py' -o -name '*.js' -o -name '*.md' | head -20"
            )

            if ls_result["success"]:
                self.log("✅ File listing displayed", "success")
                return True
            else:
                self.log("❌ Failed to list files", "error")
                return False
        else:
            self.log("✅ VS Code opened", "success")
            return True

    def open_browser_to_meet(self, meet_link: str) -> bool:
        """Open browser and navigate to Google Meet (ready for agent interaction)"""
        self.log("🌐 Opening browser to Google Meet...")

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

        self.log(
            f"✅ Browser opened - ready for agent to navigate to: {meet_link}",
            "success",
        )
        return True

    def run_full_setup(self, github_url: str, meet_link: str) -> Dict[str, Any]:
        """
        Run the complete setup process

        Returns:
            Dictionary with setup results and status
        """
        self.log("🚀 Starting demo setup script...", "info")
        self.log(f"📦 GitHub URL: {github_url}", "info")
        self.log(f"📹 Meet URL: {meet_link}", "info")

        results = {
            "overall_success": True,
            "completed_tasks": [],
            "failed_tasks": [],
            "setup_log": self.setup_log,
            "ready_for_agent": False,
        }

        # Task 1: Open terminal
        if self.open_terminal():
            results["completed_tasks"].append("open_terminal")
        else:
            results["failed_tasks"].append("open_terminal")
            results["overall_success"] = False

        # Task 2: Clone repository
        if self.clone_repository(github_url):
            results["completed_tasks"].append("clone_repository")
        else:
            results["failed_tasks"].append("clone_repository")
            results["overall_success"] = False

        # Task 3: Navigate to repository
        if self.navigate_to_repository(github_url):
            results["completed_tasks"].append("navigate_to_repo")
        else:
            results["failed_tasks"].append("navigate_to_repo")
            results["overall_success"] = False

        # Task 4: Open code viewer
        if self.open_code_viewer(github_url):
            results["completed_tasks"].append("open_code_viewer")
        else:
            results["failed_tasks"].append("open_code_viewer")
            # Not critical, continue

        # Task 5: Open browser
        if self.open_browser_to_meet(meet_link):
            results["completed_tasks"].append("open_browser")
        else:
            results["failed_tasks"].append("open_browser")
            results["overall_success"] = False

        # Summary
        if results["overall_success"]:
            self.log("🎉 Setup completed successfully! Ready for AI agent.", "success")
            results["ready_for_agent"] = True

            self.log("🤖 Agent tasks remaining:", "info")
            self.log("  1. Navigate to Google Meet URL", "info")
            self.log("  2. Join the meeting", "info")
            self.log("  3. Start screen sharing", "info")
            self.log("  4. Interact with participants", "info")
        else:
            self.log("❌ Setup failed. Check the logs above.", "error")

        return results


def test_setup_script():
    """Test the setup script functionality"""
    # This would be called with a real sandbox in production
    print("Demo Setup Script Test")
    print("This script handles:")
    print("✅ Git clone (reliable)")
    print("✅ Terminal setup")
    print("✅ Browser opening")
    print("✅ Code viewer")
    print()
    print("AI Agent then handles:")
    print("🤖 Navigate to Meet URL")
    print("🤖 Join meeting")
    print("🤖 Screen sharing")
    print("🤖 User interaction")


if __name__ == "__main__":
    test_setup_script()
