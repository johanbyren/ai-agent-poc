from jira import JIRA
from dotenv import load_dotenv
import os

class JiraClient:
    def __init__(self):
        # Force reload environment variables
        load_dotenv(override=True)
        
        # Get environment variables
        self.jira_url = os.getenv('JIRA_URL')
        self.jira_email = os.getenv('JIRA_EMAIL')
        self.jira_api_token = os.getenv('JIRA_API_TOKEN')
        self.board_id = os.getenv('JIRA_BOARD_ID')
        
        if not all([self.jira_url, self.jira_email, self.jira_api_token]):
            raise ValueError("Missing Jira credentials. Please check your .env file.")
        
        print(f"Connecting to Jira at: {self.jira_url}")
        print(f"Using email: {self.jira_email}")
        print(f"API Token length: {len(self.jira_api_token)}")
        
        try:
            # Create JIRA client with basic auth
            self.client = JIRA(
                server=self.jira_url,
                basic_auth=(self.jira_email, self.jira_api_token)
            )
            
            # Verify authentication immediately
            current_user = self.client.current_user()
            print(f"Successfully authenticated as: {current_user}")
            
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            raise  # Stop execution if authentication fails
    
    def get_ai_tasks(self):
        """
        Fetch all tickets with the #ai-task tag from the specified board that are in the To Do lane
        """
        jql_query = 'project = "AIAGENTPOC" AND labels = "ai-task" AND status = "To Do" ORDER BY created DESC'
        print(f"\nFetching tasks using query: {jql_query}")
        
        try:
            issues = self.client.search_issues(jql_query)
            
            tasks = []
            for issue in issues:
                task = {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'description': issue.fields.description,
                    'status': issue.fields.status.name,
                    'labels': issue.fields.labels
                }
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            print(f"Error fetching tasks: {str(e)}")
            return [] 

    def update_task_status(self, issue_key, status):
        """Update the status of a Jira task"""
        try:
            # Get the issue
            issue = self.client.issue(issue_key)
            
            # Get the transition ID for the target status
            transitions = self.client.transitions(issue)
            for t in transitions:
                if status.lower() in t['name'].lower():
                    # Perform the transition
                    self.client.transition_issue(issue, t['id'])
                    print(f"Updated {issue_key} status to {status}")
                    return True
            
            print(f"No transition found for status: {status}")
            return False
            
        except Exception as e:
            print(f"Error updating task status: {str(e)}")
            return False 