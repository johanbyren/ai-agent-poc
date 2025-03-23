from jira_client import JiraClient

def main():
    try:
        # Initialize Jira client
        jira = JiraClient()
        
        # Fetch AI tasks
        print("Fetching AI tasks from Jira...")
        tasks = jira.get_ai_tasks()
        
        if not tasks:
            print("No AI tasks found.")
            return
        
        print(f"\nFound {len(tasks)} AI tasks:")
        for task in tasks:
            print(f"\nTask: {task['key']}")
            print(f"Summary: {task['summary']}")
            print(f"Status: {task['status']}")
            print(f"Labels: {', '.join(task['labels'])}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 