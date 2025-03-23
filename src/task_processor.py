from jira_client import JiraClient
from github_client import GitHubClient
from ai_service import AIService
import re
import json

class TaskProcessor:
    def __init__(self):
        self.jira = JiraClient()
        self.github = GitHubClient()
        self.ai = AIService()
    
    def process_tasks(self):
        """Process all AI tasks from Jira"""
        tasks = self.jira.get_ai_tasks()
        print(f"\nFound {len(tasks)} AI tasks to process")
        
        for task in tasks:
            print(f"\nProcessing task: {task['key']}")
            print(f"Summary: {task['summary']}")
            print(f"Status: {task['status']}")
            
            # Create branch name from task key and summary
            branch_name = self._create_branch_name(task['key'], task['summary'])
            
            # Create branch for the task
            if self.github.create_branch(branch_name):
                print(f"Created branch: {branch_name}")
                
                # Analyze task with AI
                print("\nAnalyzing task with AI...")
                analysis = self.ai.analyze_task(task)
                if analysis:
                    print("Task analysis completed")
                    
                    # Generate code changes
                    print("\nGenerating code changes...")
                    changes = self.ai.generate_code_changes(task, analysis)
                    if changes:
                        print("Code changes generated")
                        
                        try:
                            # Parse the changes
                            changes_data = json.loads(changes)
                            
                            # Apply changes to files
                            for file_path, content in changes_data.items():
                                if self.github.commit_changes(branch_name, file_path, content, f"Task {task['key']}: Update {file_path}"):
                                    print(f"Committed changes to {file_path}")
                            
                            # Create PR with task details and AI analysis
                            pr = self.github.create_pull_request(
                                branch_name,
                                f"Task {task['key']}: {task['summary']}",
                                f"""## Task Details
- **Key**: {task['key']}
- **Summary**: {task['summary']}
- **Status**: {task['status']}
- **Labels**: {', '.join(task['labels'])}

## Description
{task['description']}

## AI Analysis
{analysis}

## Changes
This PR implements the changes required for task {task['key']}. The changes were generated using AI analysis of the task requirements.
"""
                            )
                            if pr:
                                print(f"Created PR: {pr.html_url}")
                        except json.JSONDecodeError as e:
                            print(f"Error parsing AI response: {str(e)}")
                    else:
                        print("Failed to generate code changes")
                else:
                    print("Failed to analyze task")
    
    def _create_branch_name(self, task_key, summary):
        """Create a valid branch name from task key and summary"""
        # Convert summary to lowercase and replace spaces with hyphens
        summary_part = re.sub(r'[^a-z0-9-]', '', summary.lower().replace(' ', '-'))
        # Limit length and combine with task key
        return f"{task_key}-{summary_part[:30]}" 