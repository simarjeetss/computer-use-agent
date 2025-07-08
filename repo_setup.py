#!/usr/bin/env python3
from os_computer_use.repo_agent import RepoAgent
from e2b_desktop import Sandbox

def main():
    # Initialize the sandbox
    sandbox = Sandbox()
    sandbox.stream.start()
    vnc_url = sandbox.stream.get_url()
    print(f"You can view the desktop at: {vnc_url}")
    # Get and print the VNC connection details
    # vnc = sandbox.get_vnc_connection()
    
    # Create the repo agent
    agent = RepoAgent(sandbox)
    
    # Example repository URL (you can replace this with any public GitHub repo)
    repo_url = input("Enter the GitHub repository URL: ")
    
    try:
        # Clone, setup and run the repository
        result = agent.setup_and_run(repo_url)
        print(f"Project setup complete: {result}")
        
        # Keep the script running to maintain the background process
        print("\nPress Ctrl+C to stop the application...")
        while True:
            pass
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up
        sandbox.kill()

if __name__ == "__main__":
    main() 