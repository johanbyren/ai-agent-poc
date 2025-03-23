import json
from jira_client import JiraClient
from github_client import GitHubClient
from ai_service import AIService
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TaskProcessor:
    def __init__(self):
        self.jira = JiraClient()
        self.github = GitHubClient()
        self.working_dirs = {}  # Store working directories for each repo
    
    def __del__(self):
        # Clean up working directory when done
        if hasattr(self, 'github'):
            self.github.cleanup_working_directory()
    
    def process_ai_tasks(self):
        """Main workflow to process AI tasks"""
        try:
            # 1. Get AI tasks from Jira
            tasks = self.jira.get_ai_tasks()
            if not tasks:
                logging.info("No AI tasks found in Jira")
                return
            
            for task in tasks:
                try:
                    logging.info(f"Processing task: {task['key']} - {task['summary']}")
                    
                    # Set up working directory for this task's repository
                    working_dir = self.github.setup_working_directory(task['labels'])
                    self.working_dirs[task['key']] = working_dir
                    
                    # Initialize AI service with the correct working directory
                    ai = AIService(working_dir)
                    
                    # 2. Analyze task with AI
                    analysis = ai.analyze_task(task)
                    if not analysis:
                        logging.error(f"Failed to analyze task {task['key']}")
                        continue
                    
                    # Debug log the analysis
                    logging.info(f"AI Analysis response: {analysis}")
                    
                    # Parse the analysis
                    try:
                        analysis_data = json.loads(analysis)
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse AI analysis as JSON: {str(e)}")
                        logging.error(f"Raw analysis: {analysis}")
                        continue
                    
                    # 3. Generate code changes
                    code_changes = ai.generate_code_changes(task, analysis)
                    if not code_changes:
                        logging.error(f"Failed to generate code changes for task {task['key']}")
                        continue
                    
                    # Debug log the code changes
                    logging.info(f"AI Code Changes response: {code_changes}")
                    
                    # Parse the code changes
                    try:
                        changes_data = json.loads(code_changes)
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse code changes as JSON: {str(e)}")
                        logging.error(f"Raw code changes: {code_changes}")
                        continue
                    
                    # 4. Create GitHub branch
                    branch_name = f"feature/{task['key'].lower()}-{datetime.now().strftime('%Y%m%d')}"
                    branch_result = self.github.create_branch(task['labels'], branch_name)
                    
                    # If branch already exists, we can still update files on it
                    if branch_result is None:
                        logging.info(f"Using existing branch: {branch_name}")
                    
                    # 5. Apply code changes
                    for file_data in changes_data.get('files_to_modify', []):
                        if 'path' in file_data and 'changes' in file_data:
                            # If changes is a string, wrap it in a changes array
                            if isinstance(file_data['changes'], str):
                                changes = [{
                                    'type': 'update',
                                    'context': '',
                                    'old_code': '',
                                    'new_code': file_data['changes']
                                }]
                            else:
                                changes = file_data['changes']
                            
                            self.github.update_file(
                                labels=task['labels'],
                                path=file_data['path'],
                                message=f"Update {file_data['path']} for {task['key']}",
                                content={'changes': changes},  # Wrap changes in a dictionary
                                branch=branch_name
                            )
                    
                    # Create any new files
                    for new_file in changes_data.get('files_to_create', []):
                        if 'path' in new_file and 'content' in new_file:
                            self.github.update_file(
                                labels=task['labels'],
                                path=new_file['path'],
                                message=f"Create {new_file['path']} for {task['key']}",
                                content=new_file['content'],  # Direct content for new files
                                branch=branch_name
                            )
                    
                    # 6. Create pull request
                    pr_title = f"{task['key']}: {task['summary']}"
                    pr_body = f"""# {task['summary']}

## Description
{task['description']}

## Changes
{analysis_data['explanation']}

## Related Issue
- {task['key']}
"""
                    self.github.create_pull_request(
                        labels=task['labels'],
                        title=pr_title,
                        body=pr_body,
                        head_branch=branch_name
                    )
                    
                    # 7. Update Jira task status
                    self.jira.update_task_status(task['key'], 'In Progress')
                    
                    logging.info(f"Successfully processed task {task['key']}")
                    
                except Exception as e:
                    logging.error(f"Error processing task {task['key']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error in main workflow: {str(e)}")

def main():
    processor = TaskProcessor()
    processor.process_ai_tasks()

if __name__ == "__main__":
    main() 