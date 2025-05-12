
# This code was created by Claude AI, a large language model trained by Anthropic.


#!/usr/bin/env python3
"""
GitHub Repository Creator
------------------------
This script creates a new GitHub repository based on parameters in a config file,
clones it locally, and adds a gitignore file.

Requirements:
- Python 3.6+
- requests library (pip install requests)
- PyYAML library (pip install pyyaml)
- GitPython library (pip install gitpython)
"""

import os
import sys
import json
import yaml
import requests
import shutil
import git
from pathlib import Path
import argparse
from typing import Dict, Any, Optional


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Create GitHub repo from config')
    parser.add_argument('-c', '--config', type=str, default='github_config.yml',
                        help='Path to config file (default: github_config.yml)')
    parser.add_argument('-d', '--directory', type=str,
                        help='Directory to clone repo into (default: same as repo name)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show verbose output')
    return parser.parse_args()


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Validate required fields
        required_fields = ['github_token', 'repo_name']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in config: {field}")
                
        return config
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config: {e}")
        sys.exit(1)


def create_github_repo(config: Dict[str, Any]) -> str:
    """Create a new GitHub repository using the GitHub API."""
    token = config['github_token']
    repo_name = config['repo_name']
    
    # Set up API request
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Build repository data
    repo_data = {
        "name": repo_name,
        "private": config.get('private', False),
    }
    
    # Optional fields
    if 'description' in config:
        repo_data["description"] = config['description']
    if 'homepage' in config:
        repo_data["homepage"] = config['homepage']
    if 'has_wiki' in config:
        repo_data["has_wiki"] = config['has_wiki']
    if 'has_issues' in config:
        repo_data["has_issues"] = config['has_issues']
    if 'auto_init' in config:
        repo_data["auto_init"] = config['auto_init']
    
    print(f"Creating GitHub repository: {repo_name}...")
    
    # Make API request
    try:
        response = requests.post(url, headers=headers, data=json.dumps(repo_data))
        response.raise_for_status()
        result = response.json()
        print(f"Repository created successfully: {result['html_url']}")
        return result['clone_url']
    except requests.exceptions.RequestException as e:
        if response.status_code == 422:
            print(f"Error: Repository '{repo_name}' may already exist.")
        else:
            print(f"Error creating repository: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
        sys.exit(1)


def clone_repo(clone_url: str, directory: Optional[str] = None) -> str:
    """Clone the repository to local machine."""
    if not directory:
        # Extract repo name from clone URL
        directory = clone_url.split('/')[-1].replace('.git', '')
    
    print(f"Cloning repository to {directory}...")
    
    try:
        repo = git.Repo.clone_from(clone_url, directory)
        print(f"Repository cloned successfully to {directory}")
        return directory
    except git.GitCommandError as e:
        print(f"Error cloning repository: {e}")
        sys.exit(1)


def add_gitignore(repo_dir: str, gitignore_type: str) -> None:
    """Add a .gitignore file to the repository."""
    print(f"Adding .gitignore file for {gitignore_type}...")
    
    # First, try to get the gitignore template from GitHub
    github_gitignore_url = f"https://raw.githubusercontent.com/github/gitignore/main/{gitignore_type}.gitignore"
    response = requests.get(github_gitignore_url)
    
    gitignore_path = os.path.join(repo_dir, '.gitignore')
    
    if response.status_code == 200:
        # Write the gitignore content to file
        with open(gitignore_path, 'w') as gitignore_file:
            gitignore_file.write(response.text)
        print(f"Added .gitignore file for {gitignore_type}")
    else:
        print(f"Could not find gitignore template for {gitignore_type}.")
        print("Creating a basic .gitignore file instead.")
        
        # Create a basic gitignore file based on the language/platform
        basic_gitignores = {
            "Python": """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.tox/
.venv/
venv/
ENV/
""",
            "Node": """
# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
package-lock.json
.npm
.node_repl_history
.env
.env.test
.cache
.next
.nuxt
dist/
""",
            "Java": """
# Java
*.class
*.log
*.jar
*.war
*.ear
*.zip
*.tar.gz
*.rar
hs_err_pid*
.mtj.tmp/
target/
.idea/
*.iml
.classpath
.project
.settings/
bin/
""",
        }
        
        default_gitignore = """
# IDE files
.idea/
.vscode/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db
"""
        
        content = basic_gitignores.get(gitignore_type, default_gitignore)
        with open(gitignore_path, 'w') as gitignore_file:
            gitignore_file.write(content)
        print("Created a basic .gitignore file")

    # Commit the .gitignore file
    try:
        repo = git.Repo(repo_dir)
        repo.git.add('.gitignore')
        repo.git.commit('-m', 'Add .gitignore file')
        
        # Push the changes to GitHub
        origin = repo.remote('origin')
        origin.push()
        print("Committed and pushed .gitignore file")
    except git.GitCommandError as e:
        print(f"Error committing .gitignore: {e}")


def main():
    """Main function to execute the script."""
    args = parse_arguments()
    
    # Load the configuration
    config = load_config(args.config)
    
    if args.verbose:
        print("Configuration loaded:")
        for key, value in config.items():
            if key == 'github_token':
                print(f"  github_token: {'*' * 10}")
            else:
                print(f"  {key}: {value}")
    
    # Create the GitHub repository
    clone_url = create_github_repo(config)
    
    # Clone the repository
    repo_dir = clone_repo(clone_url, args.directory)
    
    # Add .gitignore file if specified
    if 'gitignore_type' in config:
        add_gitignore(repo_dir, config['gitignore_type'])
    
    print("\nRepository setup completed successfully!")
    print(f"You can now work with your repo at: {os.path.abspath(repo_dir)}")


if __name__ == "__main__":
    main()
