# GitHubRepoCreator
Create a GitHub Repo based on a config file


A Python script that automates the GitHub repository setup process. Here's how it works:
Features

Creates a new GitHub repository via API
Clones the repository to your local machine
Adds a language-specific .gitignore file (downloads from GitHub's gitignore templates)
Commits and pushes the .gitignore to the remote repository

Requirements
You'll need to install the following Python packages:
pip install requests pyyaml gitpython


How to Use

Create a configuration file named github_config.yml with your repository settings (I've provided an example).
Make sure to add your GitHub personal access token (you can create one at https://github.com/settings/tokens). The token needs the repo scope permissions.

Run the script:
python github_repo_creator.py
Or with custom options:
python github_repo_creator.py --config custom_config.yml --directory my_project_dir --verbose
Command Line Arguments

-c, --config: Path to configuration file (default: github_config.yml)
-d, --directory: Custom directory to clone the repository into (default: same as repo name)
-v, --verbose: Show detailed output during execution