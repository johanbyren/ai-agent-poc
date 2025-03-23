# AI Agent Project

A Python project for an AI agent.

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
- `requirements.txt`: Project dependencies
- `dev-start.sh`: Development startup script (sets up and activates environment)
- `start.sh`: Quick run script (when environment is already set up)

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
