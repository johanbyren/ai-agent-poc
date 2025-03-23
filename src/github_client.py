from github import Github
from dotenv import load_dotenv
import os

class GitHubClient:
    def __init__(self):
        # Force reload environment variables
        load_dotenv(override=True)
        
        # Get environment variables
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_name = os.getenv('GITHUB_REPO')
        
        if not all([self.github_token, self.repo_name]):
            raise ValueError("Missing GitHub credentials. Please check your .env file.")
        
        try:
            # Create GitHub client
            self.client = Github(self.github_token)
            
            # Get the repository
            self.repo = self.client.get_repo(self.repo_name)
            print(f"Successfully connected to GitHub repository: {self.repo.full_name}")
            
        except Exception as e:
            print(f"GitHub Authentication failed: {str(e)}")
            raise
    
    def create_branch(self, branch_name, from_branch='main'):
        """Create a new branch from the specified base branch"""
        try:
            # Get the base branch
            source = self.repo.get_branch(from_branch)
            
            # Create new branch
            self.repo.create_git_ref(f"refs/heads/{branch_name}", source.commit.sha)
            print(f"Created new branch: {branch_name}")
            return True
        except Exception as e:
            print(f"Error creating branch: {str(e)}")
            return False
    
    def commit_changes(self, branch_name, file_path, content, commit_message):
        """Commit changes to a file in the specified branch"""
        try:
            # Get the current file if it exists
            try:
                file = self.repo.get_contents(file_path, ref=branch_name)
                # Update existing file
                self.repo.update_file(
                    file_path,
                    commit_message,
                    content,
                    file.sha,
                    branch=branch_name
                )
            except Exception:
                # File doesn't exist, create it
                self.repo.create_file(
                    file_path,
                    commit_message,
                    content,
                    branch=branch_name
                )
            
            print(f"Committed changes to {file_path} in branch {branch_name}")
            return True
        except Exception as e:
            print(f"Error committing changes: {str(e)}")
            return False
    
    def create_pull_request(self, branch_name, title, body):
        """Create a pull request from the specified branch to main"""
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base='main'
            )
            print(f"Created pull request: {pr.html_url}")
            return pr
        except Exception as e:
            print(f"Error creating pull request: {str(e)}")
            return None 