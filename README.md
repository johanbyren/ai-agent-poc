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
