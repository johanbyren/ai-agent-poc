import os
import time
from github import Github, RateLimitExceededException
import logging
from dotenv import load_dotenv
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GitHubClient:
    def __init__(self):
        # Force reload environment variables
        load_dotenv(override=True)
        
        # Get GitHub credentials
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("Missing GitHub token. Please check your .env file.")
            
        self.github = Github(self.github_token)
        self.working_dirs = {}  # Store working directories for each repo
        self.repos = {}  # Store repo objects

    def get_repo_from_label(self, labels):
        """Get repository based on repo label (e.g., 'repo:owner/repo-name' or 'repo-owner:owner/repo-name')"""
        # First try the standard format
        repo_label = next((label for label in labels if label.startswith('repo:')), None)
        if not repo_label:
            # Try alternative format with owner specified
            repo_label = next((label for label in labels if label.startswith('repo-owner:')), None)
            if not repo_label:
                raise ValueError(
                    "No repository label found. Task must have a label in one of these formats:\n"
                    "1. 'repo:owner/repo-name' (e.g., 'repo:johanbyren/poker-tournament-app')\n"
                    "2. 'repo-owner:owner/repo-name' (e.g., 'repo-owner:johanbyren/poker-tournament-app')"
                )
        
        # Remove the prefix (either 'repo:' or 'repo-owner:')
        repo_name = repo_label.split(':', 1)[1]
        
        # Validate the repository name format
        if '/' not in repo_name:
            raise ValueError(
                f"Invalid repository format in label '{repo_label}'. The repository must include both owner and name.\n"
                f"Expected format: 'owner/repo-name' (e.g., 'johanbyren/poker-tournament-app')\n"
                f"Received: '{repo_name}'"
            )
        
        # Cache and return the repository object
        if repo_name not in self.repos:
            try:
                self.repos[repo_name] = self.github.get_repo(repo_name)
            except Exception as e:
                raise ValueError(
                    f"Could not find repository '{repo_name}'. Please check:\n"
                    "1. The repository exists\n"
                    "2. You have access to it\n"
                    "3. The owner and repository names are correct\n"
                    f"Error: {str(e)}"
                ) from e
        
        return self.repos[repo_name]

    def setup_working_directory(self, labels):
        """Clone or update the repository to a temporary directory"""
        repo = self.get_repo_from_label(labels)
        repo_name = repo.full_name
        
        if repo_name in self.working_dirs:
            return self.working_dirs[repo_name]

        # Create a temporary directory
        working_dir = tempfile.mkdtemp(prefix='ai-agent-')
        logging.info(f"Created working directory for {repo_name}: {working_dir}")

        # Clone the repository
        repo_url = repo.clone_url
        # Replace the URL with one that includes the token
        repo_url = repo_url.replace('https://', f'https://{self.github_token}@')
        
        os.system(f'git clone {repo_url} {working_dir}')
        self.working_dirs[repo_name] = working_dir
        return working_dir

    def cleanup_working_directory(self):
        """Clean up all temporary working directories"""
        for working_dir in self.working_dirs.values():
            if working_dir and os.path.exists(working_dir):
                shutil.rmtree(working_dir)
        self.working_dirs = {}

    def get_working_directory(self, labels):
        """Get the path to the working directory for a specific repo"""
        repo = self.get_repo_from_label(labels)
        repo_name = repo.full_name
        if repo_name not in self.working_dirs:
            return self.setup_working_directory(labels)
        return self.working_dirs[repo_name]

    def get_rate_limit_remaining(self):
        """Get the number of remaining API requests"""
        return self.github.get_rate_limit().core.remaining

    def handle_rate_limit(self, reset_time):
        """Handle rate limit by sleeping until reset"""
        sleep_time = reset_time - time.time() + 1  # Add 1 second buffer
        logging.warning(f"GitHub API rate limit exceeded. Sleeping for {sleep_time:.2f} seconds.")
        time.sleep(sleep_time)

    def make_github_request(self, method, *args, **kwargs):
        """Make a GitHub API request with rate limit handling"""
        max_retries = 5
        retries = 0

        while retries < max_retries:
            try:
                result = method(*args, **kwargs)
                logging.info(f"GitHub API request successful. Remaining requests: {self.get_rate_limit_remaining()}")
                return result
            except RateLimitExceededException as e:
                reset_time = e.reset
                self.handle_rate_limit(reset_time)
                retries += 1
            except Exception as e:
                logging.error(f"GitHub API request failed: {e}")
                raise

        raise Exception(f"GitHub API request failed after {max_retries} retries due to rate limiting.")

    def create_branch(self, labels, branch_name, base_branch='main'):
        """Create a new branch with rate limit handling"""
        repo = self.get_repo_from_label(labels)
        def _create_branch():
            try:
                # Try to get the base branch
                base = repo.get_branch(base_branch)
                
                try:
                    # Check if branch already exists
                    repo.get_branch(branch_name)
                    logging.info(f"Branch {branch_name} already exists")
                    return None
                except Exception:
                    # Branch doesn't exist, create it
                    return repo.create_git_ref(
                        ref=f"refs/heads/{branch_name}",
                        sha=base.commit.sha
                    )
            except Exception as e:
                logging.error(f"Error creating branch: {str(e)}")
                raise
        return self.make_github_request(_create_branch)

    def create_pull_request(self, labels, title, body, head_branch, base_branch='main'):
        """Create a pull request with rate limit handling"""
        repo = self.get_repo_from_label(labels)
        def _create_pr():
            return repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
        return self.make_github_request(_create_pr)

    def get_file_content(self, labels, path, ref='main'):
        """Get file content with rate limit handling"""
        repo = self.get_repo_from_label(labels)
        def _get_content():
            return repo.get_contents(path, ref=ref)
        return self.make_github_request(_get_content)

    def update_file(self, labels, path, message, content, branch):
        """Update a file with rate limit handling"""
        repo = self.get_repo_from_label(labels)
        def _update_file():
            try:
                # Get the current file content
                try:
                    file_content = repo.get_contents(path, ref=branch)
                    current_content = file_content.decoded_content.decode('utf-8')
                    logging.info(f"Retrieved current content for {path}")
                except Exception as e:
                    # File doesn't exist
                    if "404" in str(e):
                        current_content = ""
                        file_content = None
                        logging.info(f"File {path} does not exist yet, will create it")
                    else:
                        raise
                
                # If content is a string, it's a complete file replacement
                if isinstance(content, str):
                    logging.info(f"Replacing entire content of {path}")
                    new_content = content
                
                # If content is a list of changes, apply them one by one
                elif isinstance(content, list):
                    logging.info(f"Applying list of changes to {path}")
                    new_content = current_content
                    for change in content:
                        if isinstance(change, dict) and all(k in change for k in ['type', 'context', 'old_code', 'new_code']):
                            # Find the old code in the context
                            context = change['context']
                            old_code = change['old_code']
                            new_code = change['new_code']
                            
                            logging.info(f"Applying change to {path}:")
                            logging.info(f"Context: {context}")
                            logging.info(f"Old code: {old_code}")
                            logging.info(f"New code: {new_code}")
                            
                            # Find the position of the context
                            context_pos = new_content.find(context)
                            if context_pos != -1:
                                # Find the position of the old code within the context
                                old_code_pos = new_content.find(old_code, context_pos)
                                if old_code_pos != -1:
                                    # Replace the old code with the new code
                                    new_content = (
                                        new_content[:old_code_pos] +
                                        new_code +
                                        new_content[old_code_pos + len(old_code):]
                                    )
                                    logging.info(f"Successfully applied change to {path}")
                                else:
                                    logging.error(f"Could not find old_code '{old_code}' within context in {path}")
                            else:
                                logging.error(f"Could not find context '{context}' in {path}")
                
                # If content is a dictionary with a changes array
                elif isinstance(content, dict) and 'changes' in content:
                    logging.info(f"Applying changes array to {path}")
                    new_content = current_content
                    for change in content['changes']:
                        if isinstance(change, dict) and all(k in change for k in ['type', 'context', 'old_code', 'new_code']):
                            # Find the old code in the context
                            context = change['context']
                            old_code = change['old_code']
                            new_code = change['new_code']
                            
                            logging.info(f"Applying change to {path}:")
                            logging.info(f"Context: {context}")
                            logging.info(f"Old code: {old_code}")
                            logging.info(f"New code: {new_code}")
                            
                            # Find the position of the context
                            context_pos = new_content.find(context)
                            if context_pos != -1:
                                # Find the position of the old code within the context
                                old_code_pos = new_content.find(old_code, context_pos)
                                if old_code_pos != -1:
                                    # Replace the old code with the new code
                                    new_content = (
                                        new_content[:old_code_pos] +
                                        new_code +
                                        new_content[old_code_pos + len(old_code):]
                                    )
                                    logging.info(f"Successfully applied change to {path}")
                                else:
                                    logging.error(f"Could not find old_code '{old_code}' within context in {path}")
                            else:
                                logging.error(f"Could not find context '{context}' in {path}")
                else:
                    raise ValueError(f"Invalid content format for {path}: {type(content)}")
                
                # Update or create the file
                if file_content:
                    logging.info(f"Updating existing file {path}")
                    return repo.update_file(
                        path=path,
                        message=message,
                        content=new_content,
                        sha=file_content.sha,
                        branch=branch
                    )
                else:
                    logging.info(f"Creating new file {path}")
                    return repo.create_file(
                        path=path,
                        message=message,
                        content=new_content,
                        branch=branch
                    )
                
            except Exception as e:
                logging.error(f"Error updating file {path}: {str(e)}")
                raise
        return self.make_github_request(_update_file)

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