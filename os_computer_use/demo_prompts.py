"""
Demo Prompts - Optimized prompts for each demo step
Includes fallback prompts and error recovery instructions
"""


class DemoPrompts:
    """
    Specialized prompts for each demo step
    Provides context-aware instructions and fallback strategies
    """

    # System prompts for different contexts
    SYSTEM_PROMPT_BASE = """You are an AI assistant performing an automated developer demonstration. You have computer use abilities including clicking, typing, taking screenshots, and running commands. 

Your goal is to execute each step precisely and efficiently. Always take a screenshot first to understand the current state, then take the appropriate action.

If you encounter any issues, try alternative approaches before giving up. Be methodical and patient."""

    SYSTEM_PROMPT_TERMINAL = (
        SYSTEM_PROMPT_BASE
        + """

You are currently working with terminal/command-line operations. Focus on:
- Finding and opening terminal applications
- Executing shell commands correctly
- Waiting for command completion
- Recognizing command success/failure indicators"""
    )

    SYSTEM_PROMPT_BROWSER = (
        SYSTEM_PROMPT_BASE
        + """

You are currently working with web browser operations. Focus on:
- Opening browser applications
- Navigating to web URLs
- Interacting with web page elements
- Handling browser permissions and dialogs"""
    )

    SYSTEM_PROMPT_GUI = (
        SYSTEM_PROMPT_BASE
        + """

You are currently working with GUI applications. Focus on:
- Finding application icons and menu items
- Clicking buttons and interface elements
- Typing text into input fields
- Recognizing application states and windows"""
    )

    # Step-specific detailed prompts
    TERMINAL_PROMPT = """Open the terminal application on this desktop.

Steps to follow:
1. Take a screenshot to see the current desktop
2. Look for a terminal icon on the desktop, taskbar, or in the applications menu
3. Common terminal applications: Terminal, Gnome Terminal, Console, Command Line
4. Click on the terminal icon to open it
5. Verify that a terminal window opened with a command prompt

If you don't see a terminal icon immediately:
- Try right-clicking on the desktop to see if there's a "Open Terminal" option
- Look in the applications menu (usually a grid icon or "Activities" button)
- Try pressing Ctrl+Alt+T as a keyboard shortcut
- Look for any command-line or shell applications

The terminal should show a command prompt (like user@hostname:~$ or similar) when successfully opened."""

    GIT_CLONE_PROMPT_TEMPLATE = """Clone the GitHub repository: {github_url}

You should now have a terminal window open. Execute these steps:
1. Take a screenshot to confirm terminal is open and ready
2. Use the run_command tool to execute: git clone {github_url}
3. Wait for the cloning process to complete
4. Look for success indicators like "Cloning into..." and "done"

CRITICAL: Always use the run_command tool for git commands - it waits for completion automatically and is more reliable.

The command will download the repository to the current directory. Expected output includes:
- "Cloning into 'repository-name'..."
- Progress information (objects, deltas)
- "done." message when complete

If the run_command fails:
- Check if git is installed by running: git --version
- Verify internet connectivity  
- Ensure the repository URL is correct and accessible
- Try with --depth=1 flag for faster clone: git clone --depth=1 {github_url}

IMPORTANT: If you must type manually (as absolute last resort):
- Use type_text to type the command: git clone {github_url}
- YOU MUST immediately press Enter with send_key("Return") to execute the command
- NEVER leave a command typed but not executed
- Wait 10-15 seconds for the command to complete before proceeding
- Take a screenshot to verify the cloning completed

Remember: The system will automatically press Enter if you type a git clone command and forget to execute it.

Wait for the command to complete before proceeding."""

    NAVIGATION_PROMPT_TEMPLATE = """Navigate into the cloned repository directory.

The git clone command should have created a directory. Now navigate into it:
1. Take a screenshot to see the current terminal state
2. Use the run_command tool to execute: cd {repo_name}
3. Verify you're in the repository directory

CRITICAL: Use run_command instead of typing manually for more reliable execution.

You can confirm successful navigation by:
- The command should complete without errors
- The command prompt should show the new directory name  
- You can run 'pwd' to confirm the working directory
- You can run 'ls' to see repository contents

If the directory doesn't exist or navigation fails:
- Run 'ls' to see what directories are available
- Look for the repository name (it might be slightly different)
- Check if the clone command actually succeeded
- The repo name is usually the last part of the GitHub URL

IMPORTANT: If you must type manually (as absolute last resort):
- Use type_text to type: cd {repo_name}
- YOU MUST immediately press Enter with send_key("Return") to execute the command
- NEVER leave a command typed but not executed
- The system will automatically press Enter if you forget

Remember: Always execute commands after typing them!"""

    CODE_VIEWER_PROMPT = """Open a code viewer in the current repository directory.

Try to open VS Code first, with fallback options:
1. Take a screenshot to see the current terminal
2. First try: code .
3. Wait a few seconds to see if VS Code opens
4. If VS Code doesn't open or command not found, try alternatives:
   - Run: ls -la (to list repository files)
   - Run: find . -name "*.py" -o -name "*.js" -o -name "*.md" | head -10 (to show code files)
   - Try: gedit . (if available)
   - Try: nano README.md (if README exists)

Success indicators:
- VS Code window opens showing the repository files
- OR terminal displays a detailed file listing
- OR alternative editor opens with repository content

The goal is to show the repository contents in some form - either graphically with VS Code or via terminal commands."""

    BROWSER_PROMPT = """Open a web browser application.

Find and launch a web browser:
1. Take a screenshot to see the desktop
2. Look for browser icons: Firefox, Chrome, Chromium, Safari
3. Check the desktop, taskbar, or applications menu
4. Click on a browser icon to launch it

Common browser locations:
- Desktop icons
- Taskbar/dock
- Applications menu (Activities, Start menu, etc.)
- File manager favorites

If no browser icons are visible:
- Open the applications menu and search for "browser", "firefox", or "chrome"
- Try keyboard shortcuts like Alt+F2 and type "firefox"
- Look in system applications folder

Success indicators:
- Browser window opens
- You can see the browser interface (address bar, tabs, etc.)
- Browser is ready to navigate to websites

Wait for the browser to fully load before proceeding to the next step."""

    MEET_JOIN_PROMPT_TEMPLATE = """Navigate to Google Meet and join the call as a guest.

You should now have a browser open. Execute these steps:
1. Take a screenshot to confirm browser is ready
2. Click on the address bar (URL bar)
3. Type: {meet_link}
4. Press Enter to navigate to the Meet link
5. Wait for the page to load
6. Look for "Join as guest" or similar option
7. Click "Join as guest" 
8. Enter "demo-agent" as the name when prompted
9. Click "Ask to join" or "Join" button

Expected sequence:
- Browser navigates to Google Meet
- Page shows meeting preview with camera/microphone options
- Option to join as guest is available
- Name input field appears
- Join button becomes available after entering name

If you encounter issues:
- Wait for page to fully load
- Look for alternative join options
- Check for browser permission dialogs (allow microphone/camera if prompted)
- Try refreshing the page if it doesn't load properly

The goal is to successfully join the Google Meet call as "demo-agent"."""

    SCREEN_SHARE_PROMPT = """Start screen sharing in the Google Meet call.

You should now be in the Google Meet call. Start screen sharing:
1. Take a screenshot to see the Meet interface
2. Look for "Present now" or screen share button (usually has a screen/monitor icon)
3. Click on "Present now" or the screen share button
4. Select "Your entire screen" from the sharing options
5. Click "Share" or "Start sharing" to confirm
6. Handle any browser permission dialogs by clicking "Allow"

Common screen share button locations:
- Bottom toolbar of the Meet interface
- May be in a "More options" menu (three dots)
- Could be labeled as "Present", "Share screen", or have a monitor icon

Expected flow:
- Screen share options appear (entire screen, window, tab)
- Select "Your entire screen" 
- Browser asks for screen sharing permission
- Click "Allow" or "Share" to grant permission
- Screen sharing starts and others can see your screen

If you don't see screen share options:
- Look for "More actions" or three-dot menu
- Ensure you've successfully joined the call
- Check if browser supports screen sharing
- Try refreshing the page and rejoining

Success indicator: Screen sharing should be active and visible to other participants."""

    WAIT_PROMPT = """Demo setup is complete. Maintain screen sharing and wait for instructions.

The demo presentation setup is now complete. You should:
1. Verify screen sharing is active (look for sharing indicator)
2. Ensure the Meet call is still connected
3. Keep all windows visible and organized
4. Wait for further instructions from the user

Current state should be:
- Terminal window open in the repository directory
- Code viewer (VS Code) or file listing visible
- Browser with Google Meet open and screen sharing active
- All demo components ready for presentation

Maintain this state and respond to any additional instructions for the demonstration."""

    # Error recovery prompts
    RECOVERY_PROMPTS = {
        "terminal_not_found": """Cannot find terminal application. Try these alternatives:
        - Right-click on desktop and look for "Open Terminal"
        - Press Ctrl+Alt+T keyboard shortcut
        - Open file manager and look for terminal option
        - Search applications for "terminal", "console", or "command"
        """,
        "git_not_installed": """Git is not installed or not found. Try:
        - Run: which git
        - Install git if needed: sudo apt-get install git
        - Use alternative: wget or curl to download repository
        """,
        "clone_failed": """Git clone failed. Try these alternatives:
        - Check internet connection
        - Verify repository URL is correct
        - Try with --depth=1 flag for faster clone
        - Download repository as ZIP if git clone fails
        """,
        "browser_not_found": """No browser found. Try:
        - Look in applications menu for Firefox, Chrome, or other browsers
        - Try command line: firefox, google-chrome, chromium-browser
        - Check if any web browser is installed
        """,
        "meet_join_failed": """Cannot join Meet call. Try:
        - Refresh the browser page
        - Check Meet link is valid and active
        - Look for different join options
        - Ensure browser allows microphone/camera access
        """,
        "screen_share_failed": """Screen sharing failed. Try:
        - Look for screen share button in Meet toolbar
        - Check browser permissions for screen sharing
        - Try different browser if current one doesn't support it
        - Look in "More options" menu for sharing options
        """,
    }

    @classmethod
    def get_step_prompt(cls, step_name: str, **kwargs) -> str:
        """
        Get the appropriate prompt for a demo step

        Args:
            step_name: Name of the demo step
            **kwargs: Additional parameters (github_url, meet_link, repo_name)

        Returns:
            Formatted prompt string
        """
        prompt_map = {
            "open_terminal": cls.TERMINAL_PROMPT,
            "clone_repository": cls.GIT_CLONE_PROMPT_TEMPLATE.format(
                github_url=kwargs.get("github_url", "")
            ),
            "navigate_to_repo": cls.NAVIGATION_PROMPT_TEMPLATE.format(
                repo_name=kwargs.get("repo_name", "")
            ),
            "open_code_viewer": cls.CODE_VIEWER_PROMPT,
            "open_browser": cls.BROWSER_PROMPT,
            "join_meet_call": cls.MEET_JOIN_PROMPT_TEMPLATE.format(
                meet_link=kwargs.get("meet_link", "")
            ),
            "start_screen_share": cls.SCREEN_SHARE_PROMPT,
            "wait_for_instructions": cls.WAIT_PROMPT,
        }

        return prompt_map.get(step_name, f"Execute step: {step_name}")

    @classmethod
    def get_system_prompt(cls, context: str = "base") -> str:
        """
        Get the appropriate system prompt for the context

        Args:
            context: Context type (base, terminal, browser, gui)

        Returns:
            System prompt string
        """
        prompt_map = {
            "base": cls.SYSTEM_PROMPT_BASE,
            "terminal": cls.SYSTEM_PROMPT_TERMINAL,
            "browser": cls.SYSTEM_PROMPT_BROWSER,
            "gui": cls.SYSTEM_PROMPT_GUI,
        }

        return prompt_map.get(context, cls.SYSTEM_PROMPT_BASE)

    @classmethod
    def get_recovery_prompt(cls, error_type: str) -> str:
        """
        Get error recovery prompt for specific error types

        Args:
            error_type: Type of error encountered

        Returns:
            Recovery instruction string
        """
        return cls.RECOVERY_PROMPTS.get(
            error_type,
            "An error occurred. Please take a screenshot and try an alternative approach.",
        )
