#!/usr/bin/env python3
"""
Hybrid Demo Test Script - Enhanced with Structured Commands
Test the new hybrid approach with multiple options including structured commands
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_environment():
    """Check if required environment variables are set"""
    required_vars = {
        "E2B_API_KEY": "E2B Desktop Sandbox API key",
    }

    # Check for at least one LLM provider
    llm_providers = {
        "OPENAI_API_KEY": "OpenAI (GPT-4o)",
        "ANTHROPIC_API_KEY": "Anthropic (Claude)",
        "GROQ_API_KEY": "Groq (Llama)",
    }

    missing_vars = []

    # Check required E2B key
    if not os.getenv("E2B_API_KEY"):
        missing_vars.append("E2B_API_KEY")

    # Check for at least one LLM provider
    has_llm_provider = any(os.getenv(key) for key in llm_providers.keys())
    if not has_llm_provider:
        print("❌ No LLM provider API key found!")
        print("   You need at least one of:")
        for key, desc in llm_providers.items():
            print(f"   - {key} ({desc})")
        return False

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}: {required_vars.get(var, 'Required')}")
        return False

    print("✅ Environment variables configured correctly")

    # Show which LLM provider will be used
    for key, desc in llm_providers.items():
        if os.getenv(key):
            print(f"✅ Using LLM provider: {desc}")
            break

    return True


async def test_hybrid_demo():
    """Test the hybrid demo approach with enhanced options"""

    # Import here to avoid issues if environment isn't set up
    try:
        from os_computer_use.streaming import Sandbox
        from os_computer_use.demo_agent import DemoAgent
        from os_computer_use.demo_orchestrator import DemoOrchestrator
        from os_computer_use.decoupled_orchestrator import DecoupledDemoOrchestrator
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Try running: poetry install")
        return False

    # Test URLs - REPLACE THESE WITH YOUR REAL URLS
    github_url = "https://github.com/simarjeetss/simarjeetss.github.io"
    meet_link = "https://meet.google.com/bne-wrae-fdj"

    print(f"\n🚀 Starting hybrid demo test...")
    print(f"📦 GitHub Repository: {github_url}")
    print(f"📹 Google Meet Link: {meet_link}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n🔧 ARCHITECTURE OPTIONS:")
    print(f"   🔄 Traditional: Script + Agent (original hybrid)")
    print(f"   🚀 Decoupled: Independent services (repository ⚡ meeting)")
    print(f"   📦 Repository-only: Clone repos without meetings")
    print(f"   📹 Meeting-only: Join meetings without repos")
    print(f"   🎯 NEW: Structured Commands (no AI agent for meeting)")

    # Ask user for architecture choice
    print(f"\nChoose architecture:")
    print(f"   1. Traditional hybrid (original)")
    print(f"   2. Decoupled combined (recommended)")
    print(f"   3. Repository setup only")
    print(f"   4. Meeting setup only (with AI agent)")
    print(f"   5. Meeting setup with structured commands (NEW)")
    print(f"   6. Combined with structured commands (NEW)")

    try:
        choice = input(f"Enter choice (1-6, default=2): ").strip() or "2"
        choice = int(choice)
    except (ValueError, KeyboardInterrupt):
        choice = 2

    if choice not in [1, 2, 3, 4, 5, 6]:
        print("Invalid choice, using default (2)")
        choice = 2

    if "abc-defg-hij" in meet_link:
        print("\n⚠️  WARNING: You're using the example Google Meet link!")
        print(
            "   Create a real meeting at meet.google.com and update the meet_link variable"
        )
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != "y":
            return False

    try:
        # Create sandbox
        print("\n🏗️  Creating desktop sandbox...")
        sandbox = Sandbox()
        sandbox.set_timeout(300)  # 5 minutes

        # Start VNC stream
        sandbox.stream.start()
        vnc_url = sandbox.stream.get_url()

        print(f"🖥️  VNC URL: {vnc_url}")
        print("   👆 Open this URL in your browser to watch the demo live!")

        # Create output directory
        output_dir = f"./output/hybrid_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(output_dir, exist_ok=True)

        # Execute based on user choice
        if choice == 1:
            # Traditional hybrid approach
            print("\n🔄 Using TRADITIONAL hybrid approach...")
            agent = DemoAgent(sandbox, output_dir=output_dir, save_logs=True)
            orchestrator = DemoOrchestrator(agent)
            orchestrator.use_hybrid_approach = True
            result = await orchestrator.run_full_demo(github_url, meet_link)

        elif choice == 2:
            # Decoupled combined approach with AI agent
            print("\n🚀 Using DECOUPLED combined approach...")
            agent = DemoAgent(sandbox, output_dir=output_dir, save_logs=True)
            orchestrator = DecoupledDemoOrchestrator(agent)
            orchestrator.setup_services(sandbox)
            result = await orchestrator.setup_repository_and_meeting_with_agent(
                github_url, meet_link, agent
            )

        elif choice == 3:
            # Repository only
            print("\n📦 Repository setup ONLY...")
            orchestrator = DecoupledDemoOrchestrator()
            orchestrator.setup_services(sandbox)
            result = await orchestrator.setup_repository_only(github_url)

        elif choice == 4:
            # Meeting only with AI agent
            print("\n📹 Meeting setup ONLY with AI agent...")
            agent = DemoAgent(sandbox, output_dir=output_dir, save_logs=True)
            orchestrator = DecoupledDemoOrchestrator(agent)
            orchestrator.setup_services(sandbox)
            result = await orchestrator.setup_meeting_with_agent(meet_link, agent)

        elif choice == 5:
            # Meeting only with structured commands
            print("\n🎯 Meeting setup with STRUCTURED COMMANDS...")
            orchestrator = DecoupledDemoOrchestrator()
            orchestrator.setup_services(sandbox)
            result = await orchestrator.setup_meeting_with_commands(
                meet_link, "RAAY Agent"
            )

        elif choice == 6:
            # Combined with structured commands
            print("\n🚀 Combined setup with STRUCTURED COMMANDS...")
            orchestrator = DecoupledDemoOrchestrator()
            orchestrator.setup_services(sandbox)
            result = await orchestrator.setup_repository_and_meeting_with_commands(
                github_url, meet_link, "RAAY Agent"
            )

        print("\n🎬 Expected workflow:")
        if choice == 1:
            print("   1. 🔧 Script: Clone repository, setup terminal, open browser")
            print("   2. 🤖 Agent: Navigate to Google Meet URL")
            print("   3. 🤖 Agent: Join the Google Meet call")
            print("   4. 🤖 Agent: Start screen sharing")
        elif choice == 2:
            print("   1. 📦 Repository Service: Clone and setup repository")
            print("   2. 📹 Meeting Service: Setup browser environment")
            print("   3. 🤖 AI Agent: Navigate to Google Meet URL")
            print("   4. 🤖 AI Agent: Join the Google Meet call")
        elif choice == 3:
            print("   1. 📦 Repository Service: Clone and setup repository")
            print("   2. 📝 Code viewer ready for development")
        elif choice == 4:
            print("   1. 📹 Meeting Service: Setup browser environment")
            print("   2. 🤖 AI Agent: Navigate to Google Meet URL")
            print("   3. 🤖 AI Agent: Join the Google Meet call")
        elif choice == 5:
            print("   1. 📹 Meeting Service: Setup browser environment")
            print("   2. 🎯 Commands: Navigate to Google Meet URL")
            print("   3. 🎯 Commands: Enter name as 'RAAY Agent'")
            print("   4. 🎯 Commands: Join the Google Meet call")
        elif choice == 6:
            print("   1. 📦 Repository Service: Clone and setup repository")
            print("   2. 📹 Meeting Service: Setup browser environment")
            print("   3. 🎯 Commands: Navigate to Google Meet URL")
            print("   4. 🎯 Commands: Enter name as 'RAAY Agent'")
            print("   5. 🎯 Commands: Join the Google Meet call")

        print(f"\n   Watch the VNC URL to see the approach in action!")

        print("\n🎉 Demo execution completed!")
        print(f"📊 Final result: {result.get('success', 'Unknown')}")

        if result.get("success"):
            print(f"\n✅ SUCCESS: The chosen approach worked correctly!")
            if choice in [5, 6]:
                print("   🎯 Structured commands approach:")
                print("   - No AI agent required for meeting")
                print("   - Reliable command-based navigation")
                print("   - Joined as 'RAAY Agent' successfully")
                print("   - Fast and predictable execution")

            if choice == 6:
                print("   📦 Repository: VS Code opened with project")
                print("   📹 Meeting: Joined Google Meet as 'RAAY Agent'")
                print("   🎉 Complete demo environment ready!")

        else:
            print("\n❌ ISSUES DETECTED:")
            if "execution_log" in result:
                for log_entry in result["execution_log"][-5:]:
                    print(f"   - {log_entry}")
            elif "errors" in result:
                print(f"   - Errors: {result['errors']}")
            elif "error" in result:
                print(f"   - Error: {result['error']}")

        # Keep sandbox alive for interaction
        print(f"\n⏸️  Keeping sandbox active for interaction...")
        print(f"   🖥️  VNC URL: {vnc_url}")
        print(f"   Press Ctrl+C to exit")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Stopping sandbox...")

        # Cleanup
        sandbox.kill()
        return result.get("success", False)

    except Exception as e:
        print(f"\n❌ Error during demo execution: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


def main():
    """Main function to run the hybrid demo test"""
    print("=" * 60)
    print("🚀 HYBRID DEMO APPROACH - ENHANCED TEST")
    print("=" * 60)
    print("🔧 SCRIPT: Handles setup tasks reliably")
    print("🤖 AGENT: Focuses on interactive tasks")
    print("🎯 COMMANDS: Structured meeting join (NEW)")
    print("=" * 60)

    # Check environment
    if not check_environment():
        print("\n💡 Setup Instructions:")
        print("1. Get E2B API key from: https://e2b.dev")
        print("2. Get OpenAI API key from: https://platform.openai.com")
        print("3. Create .env file with your keys:")
        print("   E2B_API_KEY=your_e2b_key")
        print("   OPENAI_API_KEY=your_openai_key")
        print("4. Run: poetry install")
        return

    # Check if in correct directory
    if not os.path.exists("pyproject.toml"):
        print("❌ Please run this script from the open-computer-use directory")
        return

    # Run the hybrid demo test
    try:
        success = asyncio.run(test_hybrid_demo())

        if success:
            print("\n" + "=" * 60)
            print("🎉 DEMO TEST SUCCESSFUL!")
            print("   ✅ Chosen approach worked correctly")
            print("   ✅ Environment setup completed")
            print("   ✅ Services executed as expected")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ DEMO TEST FAILED")
            print("   Check the logs and VNC output for details")
            print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
