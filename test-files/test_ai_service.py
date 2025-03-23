import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_service import AIService
import json

def test_ai_service():
    # Initialize the AI service
    ai_service = AIService()
    
    # Create a sample task
    task = {
        'key': 'JIRA-001',
        'summary': 'Add error handling for GitHub API rate limits',
        'description': '''
        Add proper error handling for GitHub API rate limits in our integration:
        1. Detect when we hit rate limits
        2. Add appropriate error messages
        3. Implement exponential backoff retry logic
        4. Log rate limit status
        ''',
        'status': 'To Do',
        'labels': ['enhancement', 'github-integration']
    }
    
    print("Testing AI Service with sample task...")
    print("\nTask details:")
    print(f"Key: {task['key']}")
    print(f"Summary: {task['summary']}")
    print(f"Description: {task['description']}")
    
    # Test the analysis
    print("\nAnalyzing task...")
    analysis = ai_service.analyze_task(task)
    if analysis:
        print("\nAnalysis result:")
        try:
            # Try to parse and pretty print the JSON
            analysis_json = json.loads(analysis)
            print(json.dumps(analysis_json, indent=2))
        except json.JSONDecodeError:
            # If not valid JSON, print as is
            print(analysis)
    else:
        print("Failed to get analysis")
    
    # Test code generation
    print("\nGenerating code changes...")
    code_changes = ai_service.generate_code_changes(task, analysis)
    if code_changes:
        print("\nCode changes result:")
        try:
            # Try to parse and pretty print the JSON
            changes_json = json.loads(code_changes)
            print(json.dumps(changes_json, indent=2))
        except json.JSONDecodeError:
            # If not valid JSON, print as is
            print(code_changes)
    else:
        print("Failed to generate code changes")

if __name__ == "__main__":
    test_ai_service() 