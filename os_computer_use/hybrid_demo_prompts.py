"""
Demo Prompts for Hybrid Approach - Script handles setup, Agent handles interaction
Optimized prompts for the new workflow where a script handles reliable setup tasks
and the AI agent focuses on interactive tasks requiring visual understanding
"""


class HybridDemoPrompts:
    """
    Prompts for the hybrid demo approach:
    - Script: Setup tasks (clone, terminal, browser opening)
    - Agent: Interactive tasks (navigation, joining meeting, screen sharing)
    """

    # System prompts for different contexts
    SYSTEM_PROMPT_INTERACTIVE = """You are an AI assistant performing interactive tasks in an automated developer demonstration. A setup script has already handled the basic setup tasks reliably:

✅ Terminal is open and ready
✅ GitHub repository has been cloned
✅ Repository directory is accessible 
✅ Code viewer is open
✅ Browser is open and ready

Your role is to handle the INTERACTIVE tasks that require visual understanding and user interface interaction:
- Navigate to Google Meet URL in the browser
- Join Google Meet calls
- Start screen sharing
- Interact with meeting participants

Always take a screenshot first to understand the current state, then take the appropriate action. Focus on UI elements, buttons, and visual cues that the setup script cannot handle."""

    SYSTEM_PROMPT_BROWSER = """You are working with web browser interactions for Google Meet. The browser is already open and ready. Your tasks:

- Navigate to the specific Google Meet URL
- Join the meeting (handle permission dialogs)
- Start screen sharing
- Manage meeting controls

Look for:
- Address bar to enter URLs
- Join meeting buttons
- Permission dialog boxes
- Screen sharing controls
- Meeting interface elements"""

    # Step-specific prompts for the hybrid approach

    SETUP_SCRIPT_PROMPT_TEMPLATE = """Run the automated setup script for demo preparation.

The setup script will reliably handle these tasks:
1. ✅ Open and configure terminal
2. ✅ Clone GitHub repository: {github_url}
3. ✅ Navigate to repository directory  
4. ✅ Open code viewer (VS Code or file listing)
5. ✅ Open browser ready for Google Meet

This is a scripted process that doesn't require AI interaction. The script will:
- Use direct git commands for reliable cloning
- Handle file system operations precisely
- Set up the development environment
- Prepare the browser for meeting navigation

GitHub URL: {github_url}
Meet URL: {meet_link}

Once the setup script completes successfully, the environment will be ready for AI-driven interactive tasks."""

    NAVIGATE_TO_MEET_PROMPT_TEMPLATE = """Navigate to the Google Meet URL in the browser.

The setup script has opened a browser window. Your task is to:
1. Take a screenshot to see the current browser state
2. Locate the address bar in the browser
3. Click on the address bar
4. Type or paste the Google Meet URL: {meet_link}
5. Press Enter to navigate to the meeting

Look for:
- Browser address bar (usually at the top)
- Any existing content that needs to be cleared
- Navigation controls

The Google Meet URL is: {meet_link}

Make sure to navigate to this exact URL. The browser should show the Google Meet interface once you navigate successfully."""

    JOIN_MEET_CALL_PROMPT_TEMPLATE = """Join the Google Meet call.

You should now be on the Google Meet page. Your task is to:
1. Take a screenshot to see the current Google Meet interface
2. Look for the "Join now" or similar button
3. Handle any permission requests for camera/microphone
4. Join the meeting

Common elements to look for:
- "Join now" button
- "Ask to join" button  
- Camera/microphone permission dialogs
- Meeting waiting room interface
- "Join with a meeting ID" options

Handle any permission dialogs by:
- Allowing camera access if requested
- Allowing microphone access if requested
- Clicking "Join" or "Allow" buttons

The goal is to successfully enter the Google Meet call."""

    START_SCREEN_SHARE_PROMPT_TEMPLATE = """Start screen sharing in the Google Meet call.

You should now be in the Google Meet call. Your task is to:
1. Take a screenshot to see the meeting interface
2. Look for the screen sharing button (usually looks like a monitor icon or says "Present now")
3. Click the screen sharing button
4. Select the appropriate screen/window to share
5. Confirm the screen sharing

Common screen sharing elements:
- "Present now" button
- Screen/monitor icon in meeting controls
- Window/screen selection dialog
- "Share" or "Present" confirmation button

The meeting controls are usually at the bottom of the screen. Look for icons related to:
- Screen sharing/presenting
- Monitor or desktop icons
- "Present" text

Goal: Successfully start sharing your screen so meeting participants can see the demo."""

    WAIT_FOR_INSTRUCTIONS_PROMPT_TEMPLATE = """Wait for further instructions and be ready to interact.

The demo setup is complete! You have successfully:
✅ Set up the development environment (via script)
✅ Navigated to Google Meet
✅ Joined the meeting 
✅ Started screen sharing

You are now ready to:
- Respond to participant questions
- Navigate through the code repository
- Demonstrate features as requested
- Take screenshots when needed
- Follow additional instructions

Stay alert and responsive to new instructions. The demo is live and participants may ask you to:
- Show specific files or code
- Explain functionality
- Navigate to different parts of the project
- Answer questions about the codebase

Be ready to take actions based on what participants want to see during the demonstration."""

    @classmethod
    def get_prompts_for_step(
        cls, step_name: str, github_url: str = "", meet_link: str = ""
    ) -> str:
        """
        Get the appropriate prompt for a demo step

        Args:
            step_name: The step to get prompt for
            github_url: GitHub repository URL
            meet_link: Google Meet URL

        Returns:
            Formatted prompt for the step
        """
        prompts = {
            "run_setup_script": cls.SETUP_SCRIPT_PROMPT_TEMPLATE.format(
                github_url=github_url, meet_link=meet_link
            ),
            "navigate_to_meet": cls.NAVIGATE_TO_MEET_PROMPT_TEMPLATE.format(
                meet_link=meet_link
            ),
            "join_meet_call": cls.JOIN_MEET_CALL_PROMPT_TEMPLATE,
            "start_screen_share": cls.START_SCREEN_SHARE_PROMPT_TEMPLATE,
            "wait_for_instructions": cls.WAIT_FOR_INSTRUCTIONS_PROMPT_TEMPLATE,
        }

        return prompts.get(step_name, f"Handle the {step_name} step of the demo.")

    @classmethod
    def get_system_prompt_for_step(cls, step_name: str) -> str:
        """Get the appropriate system prompt for a demo step"""
        if step_name == "run_setup_script":
            return "You are coordinating with a setup script to prepare the demo environment."
        elif step_name in ["navigate_to_meet", "join_meet_call", "start_screen_share"]:
            return cls.SYSTEM_PROMPT_BROWSER
        else:
            return cls.SYSTEM_PROMPT_INTERACTIVE
