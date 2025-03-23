# AI Agent Project

A Python project for an AI agent that processes Jira tasks and makes code changes automatically.

## Setup

### Quick Start
The easiest way to run the project is using the dev-start script:
```bash
./dev-start.sh
```
This will:
1. Create a virtual environment if it doesn't exist
2. Activate the virtual environment
3. Run the program
4. Keep the environment active for development

After the initial setup, you can quickly run the program with:
```bash
./start.sh
```

### Manual Setup
If you prefer to set up manually:

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the project:
```bash
python src/main.py
```

## Project Structure

- `src/`: Source code directory
  - `main.py`: Main entry point of the application
  - `ai_service.py`: AI service for analyzing tasks and generating code changes
  - `github_client.py`: GitHub API client for making code changes
  - `jira_client.py`: Jira API client for fetching tasks
- `requirements.txt`: Project dependencies
- `dev-start.sh`: Development startup script (sets up and activates environment)
- `start.sh`: Quick run script (when environment is already set up)

## Jira Task Configuration

### Required Labels

The AI agent processes tasks based on specific labels in Jira. Here are the required and optional labels:

#### Required Labels
- `ai-task`: Marks a task for AI processing
  - This label is required for the AI agent to pick up the task
  - Tasks without this label will be ignored

#### Repository Labels
Tasks must include a repository label to specify which codebase to modify. Use one of these formats:
- `repo:owner/repo-name` (e.g., `repo:johanbyren/poker-tournament-app`)
- `repo-owner:owner/repo-name` (e.g., `repo-owner:johanbyren/poker-tournament-app`)

Note: The repository name must include both the owner and repository name (e.g., `owner/repo-name`).

#### Status
- Tasks must be in "To Do" status to be processed
- After processing, the status will be updated to "In Progress"

### Example Task Configuration

A properly configured Jira task should look like this:
```
Summary: Update default number of starting players from 10 to 8
Description: The game should start with 8 players by default instead of 10
Labels: 
  - ai-task
  - repo:johanbyren/poker-tournament-app
Status: To Do
```

## Environment Variables

Create a `.env` file in the project root with these variables:

```bash
# Jira Configuration
JIRA_EMAIL=your.email@example.com
JIRA_API_TOKEN=your_api_token

# GitHub Configuration
GITHUB_TOKEN=your_github_token

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key
```

## Running Tests

### AI Service Test
To test the AI service functionality:

1. Make sure you have set up your environment variables in `.env`:
```bash
GEMINI_API_KEY=your_api_key_here
```

2. Run the AI service test:
```bash
python test-files/test_ai_service.py
```

This test will:
- Create a sample task (counter feature)
- Use the AI service to analyze the task
- Generate potential code changes
- Display the results

The test output will show you how the AI service analyzes tasks and generates code changes.

## How It Works

1. The AI agent scans Jira for tasks with the `ai-task` label and "To Do" status
2. For each task:
   - Analyzes the task description and requirements
   - Identifies which files need to be modified
   - Generates appropriate code changes
   - Creates a pull request with the changes
   - Updates the task status to "In Progress"

3. The AI service:
   - Detects project type (React, Python, etc.)
   - Loads relevant codebase context
   - Generates changes following project conventions
   - Ensures changes are precise and maintainable

4. The GitHub client:
   - Creates branches for changes
   - Updates files with new code
   - Creates pull requests
   - Handles repository-specific operations

## Best Practices

1. Task Description:
   - Be specific about what needs to change
   - Include any relevant context or requirements
   - Mention specific files if known

2. Labels:
   - Always include the `ai-task` label
   - Use the correct repository label format
   - Add any relevant project-specific labels

3. Code Changes:
   - The AI will maintain existing code style
   - Changes are made with proper context
   - New files follow project conventions
