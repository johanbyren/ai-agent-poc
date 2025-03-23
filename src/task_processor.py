from jira_client import JiraClient
from github_client import GitHubClient
import re

class TaskProcessor:
    def __init__(self):
        self.jira = JiraClient()
        self.github = GitHubClient()
    
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
                
                # TODO: Here we'll add AI processing to:
                # 1. Analyze the task description
                # 2. Determine what files need to be changed
                # 3. Generate the code changes
                # 4. Commit the changes
                
                # For now, let's just create a placeholder file
                content = f"""# Task: {task['key']}
## Summary
{task['summary']}

## Description
{task['description']}

## Status
{task['status']}

## Labels
{', '.join(task['labels'])}
"""
                if self.github.commit_changes(branch_name, f"tasks/{task['key']}.md", content, f"Task {task['key']}: {task['summary']}"):
                    # Create PR with task details
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

## Changes
This PR implements the changes required for task {task['key']}.
"""
                    )
                    if pr:
                        print(f"Created PR: {pr.html_url}")
    
    def _create_branch_name(self, task_key, summary):
        """Create a valid branch name from task key and summary"""
        # Convert summary to lowercase and replace spaces with hyphens
        summary_part = re.sub(r'[^a-z0-9-]', '', summary.lower().replace(' ', '-'))
        # Limit length and combine with task key
        return f"{task_key}-{summary_part[:30]}" 