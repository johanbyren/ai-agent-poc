import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from pathlib import Path
import logging

class AIService:
    def __init__(self, working_directory):
        # Force reload environment variables
        load_dotenv(override=True)
        
        # Get Gemini API key
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Missing Gemini API key. Please check your .env file.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Set working directory
        self.working_directory = working_directory
        
        # Detect project type and load context
        self.project_type = self._detect_project_type()
        self.codebase_context = self._load_codebase_context()
    
    def _detect_project_type(self):
        """Detect the type of project based on key files and structure"""
        # Check for package.json (Node.js/React/Angular)
        if os.path.exists(os.path.join(self.working_directory, 'package.json')):
            with open(os.path.join(self.working_directory, 'package.json'), 'r') as f:
                package_json = json.load(f)
                dependencies = package_json.get('dependencies', {})
                
                # Check for React
                if 'react' in dependencies:
                    return 'react'
                # Check for Angular
                elif 'angular' in dependencies:
                    return 'angular'
                # Generic Node.js
                else:
                    return 'nodejs'
        
        # Check for Python files
        elif os.path.exists(os.path.join(self.working_directory, 'requirements.txt')):
            return 'python'
        
        # Check for Java/Maven
        elif os.path.exists(os.path.join(self.working_directory, 'pom.xml')):
            return 'java'
        
        # Default to unknown
        return 'unknown'
    
    def _get_file_patterns(self):
        """Get file patterns based on project type"""
        patterns = {
            'react': {
                'source_files': ['src/**/*.tsx', 'src/**/*.ts', 'src/**/*.jsx', 'src/**/*.js'],
                'config_files': ['package.json', 'tsconfig.json', 'vite.config.ts', '.env'],
                'key_files': ['src/App.tsx', 'src/main.tsx', 'src/index.tsx', 'src/constants.ts', 'src/config.ts']
            },
            'angular': {
                'source_files': ['src/**/*.ts', 'src/**/*.html', 'src/**/*.scss'],
                'config_files': ['package.json', 'angular.json', 'tsconfig.json'],
                'key_files': ['src/app/app.component.ts', 'src/app/app.module.ts']
            },
            'python': {
                'source_files': ['src/**/*.py'],
                'config_files': ['requirements.txt', 'setup.py', '.env'],
                'key_files': ['src/main.py', 'src/app.py', 'src/routes.py']
            },
            'java': {
                'source_files': ['src/**/*.java'],
                'config_files': ['pom.xml', 'application.properties'],
                'key_files': ['src/main/java/**/*.java']
            },
            'unknown': {
                'source_files': ['src/**/*'],
                'config_files': ['*'],
                'key_files': ['src/**/*']
            }
        }
        return patterns.get(self.project_type, patterns['unknown'])
    
    def _load_codebase_context(self):
        """Load and structure the codebase context"""
        context = {
            "project_type": self.project_type,
            "project_structure": self._get_project_structure(),
            "key_files": self._get_key_files_content()
        }
        return context
    
    def _get_project_structure(self):
        """Get the project's directory structure"""
        patterns = self._get_file_patterns()
        structure = []
        
        for pattern in patterns['source_files']:
            for path in Path(self.working_directory).glob(pattern):
                relative_path = str(path.relative_to(self.working_directory))
                level = relative_path.count(os.sep)
                indent = ' ' * 4 * level
                structure.append(f"{indent}{relative_path}")
        
        return "\n".join(structure)
    
    def _get_key_files_content(self):
        """Get content of key files that might be relevant"""
        key_files = {}
        patterns = self._get_file_patterns()
        
        try:
            # Add key source files
            for pattern in patterns['key_files']:
                for file_path in Path(self.working_directory).glob(pattern):
                    with open(file_path, 'r') as f:
                        key_files[str(file_path.relative_to(self.working_directory))] = f.read()
            
            # Add config files
            for pattern in patterns['config_files']:
                for file_path in Path(self.working_directory).glob(pattern):
                    with open(file_path, 'r') as f:
                        key_files[str(file_path.relative_to(self.working_directory))] = f.read()
            
        except Exception as e:
            print(f"Error loading key files: {str(e)}")
        
        return key_files
    
    def _clean_response(self, response_text):
        """Clean up the AI response by removing markdown formatting"""
        # Remove markdown code block if present
        if response_text.startswith('```'):
            # Find the first and last code block markers
            start_idx = response_text.find('\n') + 1
            end_idx = response_text.rfind('```')
            # Extract the content between the markers
            response_text = response_text[start_idx:end_idx].strip()
        return response_text

    def analyze_task(self, task):
        """Analyze a Jira task and determine what changes are needed"""
        # Get project-specific patterns
        patterns = self._get_file_patterns()
        
        # Get all source files in the project
        source_files = {}
        for pattern in patterns['source_files']:
            for path in Path(self.working_directory).glob(pattern):
                relative_path = str(path.relative_to(self.working_directory))
                try:
                    with open(path, 'r') as f:
                        source_files[relative_path] = f.read()
                except Exception as e:
                    print(f"Error reading file {relative_path}: {str(e)}")
        
        # Create a context-aware prompt
        prompt = f"""You are an expert software developer analyzing a task for a {self.project_type.upper()} application. 
Here is the current codebase structure and relevant files:

Project Type: {self.project_type.upper()}
Project Structure:
{self.codebase_context['project_structure']}

Source Files:
{json.dumps(source_files, indent=2)}

Project-specific patterns:
- Source files: {', '.join(patterns['source_files'])}
- Config files: {', '.join(patterns['config_files'])}
- Key files: {', '.join(patterns['key_files'])}

Now, analyze this Jira task and determine what code changes are needed:

Task Key: {task['key']}
Summary: {task['summary']}
Description: {task['description']}
Status: {task['status']}
Labels: {', '.join(task['labels'])}

Please provide:
1. A list of files that need to be modified (based on the existing codebase structure)
2. The specific changes needed for each file
3. Any new files that need to be created
4. A detailed explanation of the changes

Important:
- Follow {self.project_type.upper()} best practices and conventions
- Consider the project type when suggesting changes (e.g., React components, Python modules, etc.)
- Make the best architectural decision for implementing the changes
- You can either:
  a) Modify existing files if the functionality belongs there
  b) Create new files if it's better to separate the functionality
  c) Both modify existing files and create new ones if needed
- When modifying existing files, preserve their structure and style
- When creating new files, follow the project's patterns and conventions

Format your response in JSON like this:
{{
    "files_to_modify": [
        {{
            "path": "path/to/file",
            "changes": "detailed description of changes"
        }}
    ],
    "files_to_create": [
        {{
            "path": "path/to/new/file",
            "content": "file content",
            "reason": "explanation of why this new file is needed"
        }}
    ],
    "explanation": "detailed explanation of all changes and architectural decisions"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._clean_response(response.text)
            
        except Exception as e:
            print(f"Error analyzing task with Gemini: {str(e)}")
            return None
    
    def generate_code_changes(self, task, analysis):
        """Generate the actual code changes based on the analysis"""
        # Get project-specific patterns
        patterns = self._get_file_patterns()
        
        # Parse the analysis to get files we need to modify
        try:
            analysis_data = json.loads(analysis)
        except json.JSONDecodeError:
            logging.error("Failed to parse analysis as JSON")
            return None
        
        # Get the content of files that need to be modified
        files_content = {}
        for file_data in analysis_data.get('files_to_modify', []):
            if 'path' in file_data:
                try:
                    file_path = os.path.join(self.working_directory, file_data['path'])
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            files_content[file_data['path']] = f.read()
                    else:
                        logging.warning(f"File {file_data['path']} does not exist")
                        files_content[file_data['path']] = ""
                except Exception as e:
                    logging.error(f"Error reading file {file_data['path']}: {str(e)}")
                    files_content[file_data['path']] = ""
        
        prompt = f"""Based on this task analysis and the existing {self.project_type.upper()} codebase, generate the specific code changes needed.

Task: {task['key']} - {task['summary']}
Analysis: {analysis}

Files to modify:
{json.dumps(files_content, indent=2)}

Project-specific patterns:
- Source files: {', '.join(patterns['source_files'])}
- Config files: {', '.join(patterns['config_files'])}
- Key files: {', '.join(patterns['key_files'])}

Important:
- Follow {self.project_type.upper()} best practices and conventions
- Maintain the existing code style
- Use appropriate patterns for the project type
- Consider the project's architecture when making changes
- For existing files:
  - Only modify the specific parts that need to change
  - Preserve all other code
  - Include enough context around changes to locate them
  - Make sure the context string EXACTLY matches a part of the file content
  - The old_code must EXACTLY match what's in the file
- For new files:
  - Follow the project's file structure and naming conventions
  - Include all necessary imports and dependencies
  - Add proper documentation and types
  - Make sure the new file integrates well with existing code

Please provide the code changes in this format:
{{
    "files_to_modify": [
        {{
            "path": "path/to/file",
            "changes": [
                {{
                    "type": "update",
                    "context": "exact string from the file that helps locate where to make the change",
                    "old_code": "exact code to replace",
                    "new_code": "new code to insert"
                }}
            ]
        }}
    ],
    "files_to_create": [
        {{
            "path": "path/to/new/file",
            "content": "complete file content with imports, types, and documentation"
        }}
    ]
}}

Example of a good change:
{{
    "files_to_modify": [
        {{
            "path": "src/pages/SettingsPage.tsx",
            "changes": [
                {{
                    "type": "update",
                    "context": "const SettingsPage: React.FC = () => {{\n  const [playerCount, setPlayerCount] = useState(10);",
                    "old_code": "useState(10)",
                    "new_code": "useState(8)"
                }}
            ]
        }}
    ]
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._clean_response(response.text)
            
        except Exception as e:
            print(f"Error generating code changes with Gemini: {str(e)}")
            return None 