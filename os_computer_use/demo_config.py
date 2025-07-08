"""
Demo Configuration - Demo-specific configuration and settings
Timeout settings, retry configurations, and environment-specific options
"""

import os
from typing import Dict, Any


class DemoConfig:
    """
    Configuration settings for demo agent functionality
    Includes timeouts, retry logic, and environment-specific settings
    """

    # Step timeout settings (in seconds)
    STEP_TIMEOUTS = {
        "open_terminal": 30,
        "clone_repository": 120,  # Git clone can take time
        "navigate_to_repo": 15,
        "open_code_viewer": 60,
        "open_browser": 45,
        "join_meet_call": 180,  # Meet joining can be slow
        "start_screen_share": 120,  # Screen share setup can take time
        "wait_for_instructions": 300,  # 5 minutes wait time
    }

    # Retry configurations
    MAX_RETRIES_PER_STEP = 3
    RETRY_DELAY_SECONDS = 2
    ERROR_RETRY_DELAY_SECONDS = 5

    # Sandbox settings
    SANDBOX_TIMEOUT_SECONDS = 1800  # 30 minutes
    SANDBOX_MAX_LIFETIME_MINUTES = 60  # 1 hour for demo sessions

    # Demo session limits
    MAX_CONCURRENT_DEMOS = int(os.getenv("MAX_CONCURRENT_DEMOS", "5"))
    DEMO_SESSION_TIMEOUT_MINUTES = 90  # 1.5 hours

    # GitHub repository validation
    GITHUB_URL_PATTERN = r"https://github\.com/[\w\-\.]+/[\w\-\.]+/?(?:\.git)?$"
    ALLOWED_GITHUB_HOSTS = ["github.com"]

    # Google Meet validation
    MEET_URL_PATTERN = r"https://meet\.google\.com/[a-z]{3}-[a-z]{4}-[a-z]{3}$"
    ALLOWED_MEET_HOSTS = ["meet.google.com"]

    # Browser preferences (in order of preference)
    PREFERRED_BROWSERS = ["firefox", "google-chrome", "chromium-browser", "chrome"]

    # Terminal preferences
    PREFERRED_TERMINALS = ["gnome-terminal", "terminal", "konsole", "xterm"]

    # Code editor preferences
    PREFERRED_EDITORS = ["code", "gedit", "nano", "vim"]

    # Logging configuration
    LOG_LEVEL = os.getenv("DEMO_LOG_LEVEL", "INFO")
    LOG_TO_FILE = True
    LOG_SCREENSHOTS = True

    # Error handling
    CONTINUE_ON_NON_CRITICAL_ERRORS = True
    CRITICAL_STEPS = ["clone_repository", "join_meet_call"]  # These must succeed

    # UI element detection timeouts
    ELEMENT_WAIT_TIMEOUT = 10  # seconds
    ELEMENT_RETRY_ATTEMPTS = 3

    # Network timeouts
    NETWORK_TIMEOUT_SECONDS = 30
    CLONE_TIMEOUT_SECONDS = 300  # 5 minutes for large repos

    # Screen sharing configuration
    SCREEN_SHARE_WAIT_TIME = 5  # seconds to wait after starting
    SCREEN_SHARE_RETRY_ATTEMPTS = 3

    # Demo validation settings
    VALIDATE_EACH_STEP = True
    SCREENSHOT_ON_ERROR = True

    @classmethod
    def get_step_timeout(cls, step_name: str) -> int:
        """
        Get timeout for a specific step

        Args:
            step_name: Name of the demo step

        Returns:
            Timeout in seconds
        """
        return cls.STEP_TIMEOUTS.get(step_name, 60)  # Default 1 minute

    @classmethod
    def get_retry_config(cls) -> Dict[str, int]:
        """
        Get retry configuration

        Returns:
            Dictionary with retry settings
        """
        return {
            "max_retries": cls.MAX_RETRIES_PER_STEP,
            "retry_delay": cls.RETRY_DELAY_SECONDS,
            "error_delay": cls.ERROR_RETRY_DELAY_SECONDS,
        }

    @classmethod
    def is_critical_step(cls, step_name: str) -> bool:
        """
        Check if a step is critical (demo must fail if this step fails)

        Args:
            step_name: Name of the demo step

        Returns:
            True if step is critical
        """
        return step_name in cls.CRITICAL_STEPS

    @classmethod
    def get_browser_config(cls) -> Dict[str, Any]:
        """
        Get browser-related configuration

        Returns:
            Browser configuration dictionary
        """
        return {
            "preferred_browsers": cls.PREFERRED_BROWSERS,
            "timeout": cls.get_step_timeout("open_browser"),
            "retry_attempts": cls.ELEMENT_RETRY_ATTEMPTS,
        }

    @classmethod
    def get_git_config(cls) -> Dict[str, Any]:
        """
        Get git-related configuration

        Returns:
            Git configuration dictionary
        """
        return {
            "clone_timeout": cls.CLONE_TIMEOUT_SECONDS,
            "network_timeout": cls.NETWORK_TIMEOUT_SECONDS,
            "retry_attempts": cls.MAX_RETRIES_PER_STEP,
            "depth_limit": 1,  # Use shallow clone for speed
        }

    @classmethod
    def get_meet_config(cls) -> Dict[str, Any]:
        """
        Get Google Meet related configuration

        Returns:
            Meet configuration dictionary
        """
        return {
            "join_timeout": cls.get_step_timeout("join_meet_call"),
            "screen_share_timeout": cls.get_step_timeout("start_screen_share"),
            "screen_share_wait": cls.SCREEN_SHARE_WAIT_TIME,
            "retry_attempts": cls.SCREEN_SHARE_RETRY_ATTEMPTS,
        }

    @classmethod
    def get_validation_config(cls) -> Dict[str, Any]:
        """
        Get validation configuration

        Returns:
            Validation configuration dictionary
        """
        return {
            "validate_steps": cls.VALIDATE_EACH_STEP,
            "screenshot_on_error": cls.SCREENSHOT_ON_ERROR,
            "github_pattern": cls.GITHUB_URL_PATTERN,
            "meet_pattern": cls.MEET_URL_PATTERN,
            "allowed_github_hosts": cls.ALLOWED_GITHUB_HOSTS,
            "allowed_meet_hosts": cls.ALLOWED_MEET_HOSTS,
        }


# Environment-specific overrides
class DemoEnvironment:
    """
    Environment-specific configuration overrides
    """

    @staticmethod
    def is_production() -> bool:
        """Check if running in production environment"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"

    @staticmethod
    def is_development() -> bool:
        """Check if running in development environment"""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"

    @classmethod
    def get_config_overrides(cls) -> Dict[str, Any]:
        """
        Get environment-specific configuration overrides

        Returns:
            Configuration overrides for current environment
        """
        if cls.is_production():
            return {
                "MAX_RETRIES_PER_STEP": 2,  # Fewer retries in production
                "DEMO_SESSION_TIMEOUT_MINUTES": 60,  # Shorter timeout
                "LOG_LEVEL": "WARNING",  # Less verbose logging
                "CONTINUE_ON_NON_CRITICAL_ERRORS": False,  # Stricter error handling
            }
        elif cls.is_development():
            return {
                "MAX_RETRIES_PER_STEP": 5,  # More retries for testing
                "DEMO_SESSION_TIMEOUT_MINUTES": 120,  # Longer timeout for debugging
                "LOG_LEVEL": "DEBUG",  # Verbose logging
                "CONTINUE_ON_NON_CRITICAL_ERRORS": True,  # Permissive error handling
            }
        else:
            return {}


# Apply environment overrides
_env_overrides = DemoEnvironment.get_config_overrides()
for key, value in _env_overrides.items():
    if hasattr(DemoConfig, key):
        setattr(DemoConfig, key, value)
