"""
Repository Setup Service - Handles git repository cloning and code viewing
Completely independent from meeting functionality
"""

import os
import time
from typing import Dict, Any, Optional
from pathlib import Path


class RepositorySetupService:
    """
    Handles all repository-related operations independently
    Can be used without any meeting functionality
    """

    def __init__(self, sandbox):
        self.sandbox = sandbox
        self.setup_log = []
        self.current_repo_path = None
        self.repo_name = None

    def log(self, message: str, status: str = "info"):
        """Log a message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.setup_log.append(
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

    def setup_terminal(self) -> bool:
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

    def clone_repository(self, github_url: str) -> bool:
        """Clone the GitHub repository"""
        self.log(f"🔄 Starting repository clone: {github_url}")

        # Extract repository name from URL
        repo_name = github_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        self.repo_name = repo_name

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

        # Set current repo path
        pwd_result = self.run_command("pwd")
        if pwd_result["success"]:
            self.current_repo_path = f"{pwd_result['stdout'].strip()}/{repo_name}"

        self.log(f"✅ Successfully cloned repository: {repo_name}", "success")
        return True

    def navigate_to_repository(self) -> bool:
        """Navigate to the cloned repository directory"""
        if not self.repo_name:
            self.log("❌ No repository cloned yet", "error")
            return False

        self.log(f"📁 Navigating to repository: {self.repo_name}")

        # Change to repository directory
        cd_result = self.run_command(f"cd {self.repo_name} && pwd")

        if not cd_result["success"]:
            self.log(f"❌ Failed to navigate to {self.repo_name}", "error")
            return False

        # Verify we're in the right directory
        if self.repo_name not in cd_result.get("stdout", ""):
            self.log(f"❌ Not in expected directory {self.repo_name}", "error")
            return False

        self.log(f"✅ Successfully navigated to {self.repo_name}", "success")
        return True

    def open_code_viewer(self) -> bool:
        """Open code viewer (try VS Code, fallback to file listing)"""
        if not self.repo_name:
            self.log("❌ No repository to view", "error")
            return False

        self.log("📝 Opening code viewer...")

        # Try to open VS Code
        code_result = self.run_command(
            f"cd {self.repo_name} && code . 2>/dev/null || echo 'VS Code not available'"
        )

        if "VS Code not available" in code_result.get("stdout", ""):
            self.log("⚠️ VS Code not available, showing file listing", "warning")

            # Fallback: show file structure
            ls_result = self.run_command(
                f"cd {self.repo_name} && find . -type f -name '*.py' -o -name '*.js' -o -name '*.md' | head -20"
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

    def get_repository_info(self) -> Dict[str, Any]:
        """Get information about the current repository"""
        if not self.repo_name:
            return {"error": "No repository loaded"}

        info = {
            "repo_name": self.repo_name,
            "repo_path": self.current_repo_path,
            "status": "loaded",
        }

        # Get file count
        file_count_result = self.run_command(
            f"cd {self.repo_name} && find . -type f | wc -l"
        )
        if file_count_result["success"]:
            info["file_count"] = file_count_result["stdout"].strip()

        # Get repository size
        size_result = self.run_command(f"du -sh {self.repo_name}")
        if size_result["success"]:
            info["size"] = size_result["stdout"].split()[0]

        return info

    def setup_repository_environment(self, github_url: str) -> Dict[str, Any]:
        """
        Complete repository setup process

        Args:
            github_url: GitHub repository URL to clone

        Returns:
            Setup results and status
        """
        self.log("🚀 Starting repository environment setup...", "info")
        self.log(f"📦 GitHub URL: {github_url}", "info")

        results = {
            "overall_success": True,
            "completed_tasks": [],
            "failed_tasks": [],
            "setup_log": self.setup_log,
            "repository_ready": False,
            "repository_info": {},
        }

        # Task 1: Setup terminal
        if self.setup_terminal():
            results["completed_tasks"].append("setup_terminal")
        else:
            results["failed_tasks"].append("setup_terminal")
            results["overall_success"] = False

        # Task 2: Clone repository
        if self.clone_repository(github_url):
            results["completed_tasks"].append("clone_repository")
        else:
            results["failed_tasks"].append("clone_repository")
            results["overall_success"] = False

        # Task 3: Navigate to repository
        if self.navigate_to_repository():
            results["completed_tasks"].append("navigate_to_repository")
        else:
            results["failed_tasks"].append("navigate_to_repository")
            results["overall_success"] = False

        # Task 4: Open code viewer
        if self.open_code_viewer():
            results["completed_tasks"].append("open_code_viewer")
        else:
            results["failed_tasks"].append("open_code_viewer")
            # Not critical for repository setup

        # Get repository info
        if results["overall_success"]:
            results["repository_info"] = self.get_repository_info()
            results["repository_ready"] = True
            self.log(
                "🎉 Repository environment setup completed successfully!", "success"
            )
        else:
            self.log("❌ Repository environment setup failed", "error")

        return results


def test_repository_service():
    """Test the repository service independently"""
    print("Repository Setup Service Test")
    print("This service handles:")
    print("✅ Terminal setup")
    print("✅ Git clone (reliable)")
    print("✅ Repository navigation")
    print("✅ Code viewer opening")
    print()
    print("Completely independent of meeting functionality!")


if __name__ == "__main__":
    test_repository_service()
