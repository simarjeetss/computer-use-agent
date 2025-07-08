from os_computer_use.sandbox_agent import SandboxAgent, tools
from os_computer_use.logging import logger
import os
import json
import re

class RepoAgent(SandboxAgent):
    def __init__(self, sandbox, output_dir=".", save_logs=True):
        super().__init__(sandbox, output_dir, save_logs)
        self.repo_url = None
        self.repo_name = None
        self.tech_stack = {
            'python': False,
            'node': False,
            'java': False,
            'go': False,
            'rust': False
        }

    @SandboxAgent.tool(
        description="Clone a git repository",
        params={"url": "Git repository URL to clone"}
    )
    def clone_repo(self, url):
        self.repo_url = url
        self.repo_name = url.split('/')[-1].replace('.git', '')
        result = self.run_command(f"git clone {url}")
        return f"Repository cloned: {result}"

    @SandboxAgent.tool(
        description="Detect the technology stack of the repository",
        params={"path": "Path to the repository"}
    )
    def detect_stack(self, path):
        # Check for Python
        if os.path.exists(f"{path}/requirements.txt") or os.path.exists(f"{path}/pyproject.toml"):
            self.tech_stack['python'] = True
        
        # Check for Node.js
        if os.path.exists(f"{path}/package.json"):
            self.tech_stack['node'] = True
        
        # Check for Java
        if os.path.exists(f"{path}/pom.xml") or os.path.exists(f"{path}/build.gradle"):
            self.tech_stack['java'] = True
        
        # Check for Go
        if os.path.exists(f"{path}/go.mod"):
            self.tech_stack['go'] = True
        
        # Check for Rust
        if os.path.exists(f"{path}/Cargo.toml"):
            self.tech_stack['rust'] = True
        
        return f"Detected tech stack: {json.dumps(self.tech_stack, indent=2)}"

    @SandboxAgent.tool(
        description="Install project dependencies based on detected tech stack",
        params={"path": "Path to the repository"}
    )
    def install_dependencies(self, path):
        results = []
        
        if self.tech_stack['python']:
            if os.path.exists(f"{path}/requirements.txt"):
                results.append(self.run_command(f"cd {path} && pip install -r requirements.txt"))
            elif os.path.exists(f"{path}/pyproject.toml"):
                results.append(self.run_command(f"cd {path} && pip install poetry && poetry install"))
        
        if self.tech_stack['node']:
            results.append(self.run_command(f"cd {path} && npm install"))
        
        if self.tech_stack['java']:
            if os.path.exists(f"{path}/pom.xml"):
                results.append(self.run_command(f"cd {path} && mvn install"))
            else:
                results.append(self.run_command(f"cd {path} && gradle build"))
        
        if self.tech_stack['go']:
            results.append(self.run_command(f"cd {path} && go mod download"))
        
        if self.tech_stack['rust']:
            results.append(self.run_command(f"cd {path} && cargo build"))
        
        return "Dependencies installed:\n" + "\n".join(results)

    @SandboxAgent.tool(
        description="Run the project based on detected tech stack",
        params={"path": "Path to the repository"}
    )
    def run_project(self, path):
        # Read package.json for Node.js projects
        if self.tech_stack['node'] and os.path.exists(f"{path}/package.json"):
            with open(f"{path}/package.json") as f:
                package_json = json.loads(f.read())
                if 'scripts' in package_json and 'start' in package_json['scripts']:
                    return self.run_background_command(f"cd {path} && npm start")
                elif 'scripts' in package_json and 'dev' in package_json['scripts']:
                    return self.run_background_command(f"cd {path} && npm run dev")
        
        # Look for Python main files
        if self.tech_stack['python']:
            python_files = ['main.py', 'app.py', 'run.py']
            for file in python_files:
                if os.path.exists(f"{path}/{file}"):
                    return self.run_background_command(f"cd {path} && python {file}")
        
        # For Java projects
        if self.tech_stack['java']:
            if os.path.exists(f"{path}/pom.xml"):
                return self.run_background_command(f"cd {path} && mvn spring-boot:run")
            else:
                return self.run_background_command(f"cd {path} && gradle bootRun")
        
        # For Go projects
        if self.tech_stack['go']:
            return self.run_background_command(f"cd {path} && go run .")
        
        # For Rust projects
        if self.tech_stack['rust']:
            return self.run_background_command(f"cd {path} && cargo run")
        
        return "Could not determine how to run the project. Please check the project documentation."

    def setup_and_run(self, repo_url):
        """Main method to clone, setup and run a repository"""
        self.clone_repo(repo_url)
        repo_path = self.repo_name
        
        # Detect the tech stack
        self.detect_stack(repo_path)
        
        # Install dependencies
        self.install_dependencies(repo_path)
        
        # Run the project
        return self.run_project(repo_path) 