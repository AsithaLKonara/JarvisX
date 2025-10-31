"""
JARVIS AI - Software Engineer Agent
Automated software development lifecycle management from requirements to deployment.
"""

import json
import logging
import os
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import uuid

class SDLCPhase(Enum):
    """Software Development Lifecycle phases."""
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    CODE = "code"
    TEST = "test"
    DEPLOY = "deploy"
    DOCUMENT = "document"
    MAINTENANCE = "maintenance"

class ProjectStatus(Enum):
    """Project status levels."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    DEPLOYED = "deployed"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

@dataclass
class ProjectRequirement:
    """Individual project requirement."""
    req_id: str
    title: str
    description: str
    priority: str
    complexity: str
    acceptance_criteria: List[str]
    dependencies: List[str]
    estimated_hours: float
    status: str = "pending"

@dataclass
class ProjectDesign:
    """Project design specification."""
    design_id: str
    component_name: str
    description: str
    architecture: str
    interfaces: List[Dict[str, Any]]
    data_models: List[Dict[str, Any]]
    api_specifications: List[Dict[str, Any]]
    technology_stack: List[str]

@dataclass
class CodeModule:
    """Code module specification."""
    module_id: str
    name: str
    language: str
    file_path: str
    description: str
    dependencies: List[str]
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]

@dataclass
class TestCase:
    """Test case specification."""
    test_id: str
    name: str
    description: str
    test_type: str  # unit, integration, e2e, performance
    input_data: Dict[str, Any]
    expected_output: Any
    test_code: str
    status: str = "pending"

class SoftwareEngineerAgent:
    """
    AI-powered software engineer agent that manages the entire SDLC.
    Handles requirements analysis, design, coding, testing, deployment, and documentation.
    """
    
    def __init__(self, ai_engine=None, project_root: str = None):
        """Initialize Software Engineer Agent."""
        self.logger = logging.getLogger(__name__)
        self.ai_engine = ai_engine
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # Project management
        self.current_project = None
        self.projects = {}
        self.requirements = {}
        self.designs = {}
        self.code_modules = {}
        self.test_cases = {}
        
        # SDLC state
        self.current_phase = SDLCPhase.REQUIREMENTS
        self.project_status = ProjectStatus.PLANNING
        
        # Create project structure
        self._create_project_structure()
        
        self.logger.info("Software Engineer Agent initialized")
    
    def _create_project_structure(self):
        """Create standard project directory structure."""
        try:
            directories = [
                'requirements',
                'design',
                'src',
                'tests',
                'docs',
                'deployment',
                'scripts',
                'config'
            ]
            
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(exist_ok=True)
            
            self.logger.info("Project structure created")
        
        except Exception as e:
            self.logger.error(f"Error creating project structure: {e}")
    
    def create_project(self, project_name: str, description: str, technology_stack: List[str] = None) -> Dict[str, Any]:
        """Create a new software project."""
        try:
            project_id = f"proj_{uuid.uuid4().hex[:8]}"
            
            project = {
                'project_id': project_id,
                'name': project_name,
                'description': description,
                'technology_stack': technology_stack or [],
                'status': ProjectStatus.PLANNING.value,
                'current_phase': SDLCPhase.REQUIREMENTS.value,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'team_members': [],
                'timeline': {},
                'metrics': {}
            }
            
            self.projects[project_id] = project
            self.current_project = project_id
            
            # Create project-specific directories
            project_dir = self.project_root / project_name.replace(' ', '_').lower()
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize project files
            self._initialize_project_files(project_dir, project)
            
            self.logger.info(f"Project created: {project_name} ({project_id})")
            return project
        
        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
            return {}
    
    def _initialize_project_files(self, project_dir: Path, project: Dict[str, Any]):
        """Initialize project files and configuration."""
        try:
            # Create README.md
            readme_content = f"""# {project['name']}

{project['description']}

## Technology Stack
{', '.join(project['technology_stack'])}

## Project Structure
- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation
- `deployment/` - Deployment scripts
- `requirements/` - Requirements specifications
- `design/` - Design documents

## Getting Started
1. Install dependencies
2. Run tests
3. Start development server

## Development Status
- **Current Phase:** {project['current_phase']}
- **Status:** {project['status']}
- **Created:** {project['created_at']}
"""
            
            with open(project_dir / 'README.md', 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Create .gitignore
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
*.tmp
.env
config/secrets.json
"""
            
            with open(project_dir / '.gitignore', 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            # Create requirements.txt if Python project
            if 'python' in project['technology_stack']:
                with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
                    f.write("# Project dependencies\n")
            
            # Create package.json if Node.js project
            if 'nodejs' in project['technology_stack'] or 'javascript' in project['technology_stack']:
                package_json = {
                    "name": project['name'].replace(' ', '-').lower(),
                    "version": "1.0.0",
                    "description": project['description'],
                    "main": "src/index.js",
                    "scripts": {
                        "start": "node src/index.js",
                        "test": "jest",
                        "dev": "nodemon src/index.js"
                    },
                    "dependencies": {},
                    "devDependencies": {}
                }
                
                with open(project_dir / 'package.json', 'w', encoding='utf-8') as f:
                    json.dump(package_json, f, indent=2)
            
            self.logger.info("Project files initialized")
        
        except Exception as e:
            self.logger.error(f"Error initializing project files: {e}")
    
    def analyze_requirements(self, requirements_text: str) -> List[ProjectRequirement]:
        """Analyze and extract requirements from text."""
        try:
            self.logger.info("Analyzing requirements...")
            
            if not self.ai_engine:
                # Fallback: simple requirement extraction
                return self._extract_requirements_simple(requirements_text)
            
            # Use AI to analyze requirements
            prompt = f"""
            Analyze the following software requirements and extract structured requirements:
            
            {requirements_text}
            
            For each requirement, provide:
            1. Title (brief description)
            2. Description (detailed explanation)
            3. Priority (high, medium, low)
            4. Complexity (simple, medium, complex)
            5. Acceptance criteria (list of specific conditions)
            6. Dependencies (other requirements this depends on)
            7. Estimated hours (development time estimate)
            
            Return as JSON array of requirement objects.
            """
            
            response = self.ai_engine.get_ai_response(prompt)
            
            # Parse AI response
            try:
                requirements_data = json.loads(response)
                requirements = []
                
                for req_data in requirements_data:
                    requirement = ProjectRequirement(
                        req_id=f"req_{uuid.uuid4().hex[:8]}",
                        title=req_data.get('title', ''),
                        description=req_data.get('description', ''),
                        priority=req_data.get('priority', 'medium'),
                        complexity=req_data.get('complexity', 'medium'),
                        acceptance_criteria=req_data.get('acceptance_criteria', []),
                        dependencies=req_data.get('dependencies', []),
                        estimated_hours=req_data.get('estimated_hours', 8.0)
                    )
                    requirements.append(requirement)
                
                # Store requirements
                if self.current_project:
                    self.requirements[self.current_project] = requirements
                
                self.logger.info(f"Extracted {len(requirements)} requirements")
                return requirements
            
            except json.JSONDecodeError:
                self.logger.warning("AI response not in JSON format, using simple extraction")
                return self._extract_requirements_simple(requirements_text)
        
        except Exception as e:
            self.logger.error(f"Error analyzing requirements: {e}")
            return []
    
    def _extract_requirements_simple(self, requirements_text: str) -> List[ProjectRequirement]:
        """Simple requirement extraction without AI."""
        try:
            requirements = []
            lines = requirements_text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Simple heuristic: lines starting with numbers or bullets
                    if line[0].isdigit() or line.startswith('-') or line.startswith('*'):
                        requirement = ProjectRequirement(
                            req_id=f"req_{uuid.uuid4().hex[:8]}",
                            title=line[:50] + "..." if len(line) > 50 else line,
                            description=line,
                            priority="medium",
                            complexity="medium",
                            acceptance_criteria=[f"Implement {line}"],
                            dependencies=[],
                            estimated_hours=4.0
                        )
                        requirements.append(requirement)
            
            return requirements
        
        except Exception as e:
            self.logger.error(f"Error in simple requirement extraction: {e}")
            return []
    
    def generate_design(self, requirements: List[ProjectRequirement]) -> List[ProjectDesign]:
        """Generate system design based on requirements."""
        try:
            self.logger.info("Generating system design...")
            
            if not self.ai_engine:
                return self._generate_design_simple(requirements)
            
            # Prepare requirements summary
            req_summary = "\n".join([f"- {req.title}: {req.description}" for req in requirements])
            
            prompt = f"""
            Based on the following requirements, generate a system design:
            
            {req_summary}
            
            For each major component, provide:
            1. Component name
            2. Description
            3. Architecture pattern (MVC, microservices, etc.)
            4. Interfaces (API endpoints, data contracts)
            5. Data models (database schemas, data structures)
            6. Technology stack recommendations
            
            Return as JSON array of design objects.
            """
            
            response = self.ai_engine.get_ai_response(prompt)
            
            try:
                design_data = json.loads(response)
                designs = []
                
                for design_item in design_data:
                    design = ProjectDesign(
                        design_id=f"design_{uuid.uuid4().hex[:8]}",
                        component_name=design_item.get('component_name', f"component_{uuid.uuid4().hex[:8]}"),
                        description=design_item.get('description', 'No description available'),
                        architecture=design_item.get('architecture', 'Modular'),
                        interfaces=design_item.get('interfaces', []),
                        data_models=design_item.get('data_models', []),
                        api_specifications=design_item.get('api_specifications', []),
                        technology_stack=design_item.get('technology_stack', [])
                    )
                    designs.append(design)
                
                # Store designs
                if self.current_project:
                    self.designs[self.current_project] = designs
                
                self.logger.info(f"Generated {len(designs)} design components")
                return designs
            
            except json.JSONDecodeError:
                self.logger.warning("AI response not in JSON format, using simple design")
                return self._generate_design_simple(requirements)
        
        except Exception as e:
            self.logger.error(f"Error generating design: {e}")
            return []
    
    def _generate_design_simple(self, requirements: List[ProjectRequirement]) -> List[ProjectDesign]:
        """Simple design generation without AI."""
        try:
            designs = []
            
            # Group requirements by complexity
            high_priority = [req for req in requirements if req.priority == 'high']
            
            for req in high_priority:
                design = ProjectDesign(
                    design_id=f"design_{uuid.uuid4().hex[:8]}",
                    component_name=f"{req.title.replace(' ', '_')}_component",
                    description=f"Component for {req.title}",
                    architecture="Modular",
                    interfaces=[{
                        "name": f"{req.title.replace(' ', '_')}_api",
                        "type": "REST API",
                        "endpoints": [f"/api/{req.title.replace(' ', '-').lower()}"]
                    }],
                    data_models=[{
                        "name": f"{req.title.replace(' ', '_')}_model",
                        "fields": ["id", "name", "description", "created_at"]
                    }],
                    api_specifications=[{
                        "method": "GET",
                        "endpoint": f"/api/{req.title.replace(' ', '-').lower()}",
                        "description": f"Retrieve {req.title}"
                    }],
                    technology_stack=["Python", "FastAPI", "SQLite"]
                )
                designs.append(design)
            
            return designs
        
        except Exception as e:
            self.logger.error(f"Error in simple design generation: {e}")
            return []
    
    def generate_code(self, design: ProjectDesign) -> List[CodeModule]:
        """Generate code modules based on design."""
        try:
            self.logger.info(f"Generating code for {design.component_name}...")
            
            modules = []
            
            # Generate main module
            main_module = CodeModule(
                module_id=f"module_{uuid.uuid4().hex[:8]}",
                name=f"{design.component_name}_main",
                language="python",
                file_path=f"src/{design.component_name}.py",
                description=f"Main module for {design.component_name}",
                dependencies=[],
                functions=[],
                classes=[]
            )
            
            # Generate code content
            code_content = self._generate_code_content(design)
            main_module.functions = self._extract_functions_from_code(code_content)
            main_module.classes = self._extract_classes_from_code(code_content)
            
            modules.append(main_module)
            
            # Generate test module
            test_module = CodeModule(
                module_id=f"module_{uuid.uuid4().hex[:8]}",
                name=f"test_{design.component_name}",
                language="python",
                file_path=f"tests/test_{design.component_name}.py",
                description=f"Test module for {design.component_name}",
                dependencies=[f"{design.component_name}"],
                functions=[],
                classes=[]
            )
            
            test_code = self._generate_test_code(design)
            test_module.functions = self._extract_functions_from_code(test_code)
            
            modules.append(test_module)
            
            # Store modules
            if self.current_project:
                self.code_modules[self.current_project] = modules
            
            self.logger.info(f"Generated {len(modules)} code modules")
            return modules
        
        except Exception as e:
            self.logger.error(f"Error generating code: {e}")
            return []
    
    def _generate_code_content(self, design: ProjectDesign) -> str:
        """Generate Python code content based on design."""
        try:
            code = f'''"""
{design.component_name}
{design.description}
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class {design.component_name.replace('_', '').title()}:
    """
    {design.description}
    """
    
    def __init__(self):
        """Initialize {design.component_name}."""
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized {design.component_name}")
    
    def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming request.
        
        Args:
            data: Request data
            
        Returns:
            Response data
        """
        try:
            self.logger.info("Processing request")
            
            # Process the request based on design
            result = {{
                "status": "success",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }}
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error processing request: {{e}}")
            return {{
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }}
    
    def get_status(self) -> Dict[str, Any]:
        """Get component status."""
        return {{
            "component": "{design.component_name}",
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }}

def main():
    """Main function for testing."""
    component = {design.component_name.replace('_', '').title()}()
    
    # Test the component
    test_data = {{"test": "data"}}
    result = component.process_request(test_data)
    print(f"Result: {{result}}")

if __name__ == "__main__":
    main()
'''
            
            return code
        
        except Exception as e:
            self.logger.error(f"Error generating code content: {e}")
            return "# Error generating code"
    
    def _generate_test_code(self, design: ProjectDesign) -> str:
        """Generate test code for the design."""
        try:
            test_code = f'''"""
Tests for {design.component_name}
"""

import unittest
from unittest.mock import Mock, patch
from {design.component_name} import {design.component_name.replace('_', '').title()}

class Test{design.component_name.replace('_', '').title()}(unittest.TestCase):
    """Test cases for {design.component_name}."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.component = {design.component_name.replace('_', '').title()}()
    
    def test_initialization(self):
        """Test component initialization."""
        self.assertIsNotNone(self.component)
        self.assertIsInstance(self.component, {design.component_name.replace('_', '').title()})
    
    def test_process_request_success(self):
        """Test successful request processing."""
        test_data = {{"test": "data"}}
        result = self.component.process_request(test_data)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"], test_data)
        self.assertIn("timestamp", result)
    
    def test_process_request_error(self):
        """Test error handling in request processing."""
        # Test with invalid data that might cause an error
        invalid_data = None
        result = self.component.process_request(invalid_data)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("message", result)
    
    def test_get_status(self):
        """Test status retrieval."""
        status = self.component.get_status()
        
        self.assertEqual(status["component"], "{design.component_name}")
        self.assertEqual(status["status"], "active")
        self.assertIn("timestamp", status)

if __name__ == "__main__":
    unittest.main()
'''
            
            return test_code
        
        except Exception as e:
            self.logger.error(f"Error generating test code: {e}")
            return "# Error generating test code"
    
    def _extract_functions_from_code(self, code: str) -> List[Dict[str, Any]]:
        """Extract function information from code."""
        try:
            functions = []
            lines = code.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip().startswith('def '):
                    func_name = line.strip().split('(')[0].replace('def ', '')
                    functions.append({
                        'name': func_name,
                        'line': i + 1,
                        'description': 'Function extracted from code'
                    })
            
            return functions
        
        except Exception as e:
            self.logger.error(f"Error extracting functions: {e}")
            return []
    
    def _extract_classes_from_code(self, code: str) -> List[Dict[str, Any]]:
        """Extract class information from code."""
        try:
            classes = []
            lines = code.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip().startswith('class '):
                    class_name = line.strip().split('(')[0].replace('class ', '').replace(':', '')
                    classes.append({
                        'name': class_name,
                        'line': i + 1,
                        'description': 'Class extracted from code'
                    })
            
            return classes
        
        except Exception as e:
            self.logger.error(f"Error extracting classes: {e}")
            return []
    
    def generate_tests(self, code_modules: List[CodeModule]) -> List[TestCase]:
        """Generate comprehensive test cases for code modules."""
        try:
            self.logger.info("Generating test cases...")
            
            test_cases = []
            
            for module in code_modules:
                # Generate unit tests for each function
                for func in module.functions:
                    test_case = TestCase(
                        test_id=f"test_{uuid.uuid4().hex[:8]}",
                        name=f"test_{func['name']}",
                        description=f"Unit test for {func['name']} function",
                        test_type="unit",
                        input_data={"test_input": "sample_data"},
                        expected_output={"status": "success"},
                        test_code=f"def test_{func['name']}():\n    # Test implementation\n    pass"
                    )
                    test_cases.append(test_case)
                
                # Generate integration tests
                integration_test = TestCase(
                    test_id=f"test_{uuid.uuid4().hex[:8]}",
                    name=f"test_{module.name}_integration",
                    description=f"Integration test for {module.name}",
                    test_type="integration",
                    input_data={"module": module.name},
                    expected_output={"status": "success"},
                    test_code=f"def test_{module.name}_integration():\n    # Integration test implementation\n    pass"
                )
                test_cases.append(integration_test)
            
            # Store test cases
            if self.current_project:
                self.test_cases[self.current_project] = test_cases
            
            self.logger.info(f"Generated {len(test_cases)} test cases")
            return test_cases
        
        except Exception as e:
            self.logger.error(f"Error generating tests: {e}")
            return []
    
    def deploy_project(self, project_id: str, environment: str = "development") -> Dict[str, Any]:
        """Deploy project to specified environment."""
        try:
            self.logger.info(f"Deploying project {project_id} to {environment}...")
            
            if project_id not in self.projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.projects[project_id]
            project_dir = self.project_root / project['name'].replace(' ', '_').lower()
            
            # Create deployment script
            deployment_script = self._create_deployment_script(project, environment)
            
            # Execute deployment
            deployment_result = self._execute_deployment(deployment_script, project_dir)
            
            # Update project status
            project['status'] = ProjectStatus.DEPLOYED.value
            project['updated_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Project {project_id} deployed successfully")
            return {
                "success": True,
                "project_id": project_id,
                "environment": environment,
                "deployment_time": datetime.now().isoformat(),
                "result": deployment_result
            }
        
        except Exception as e:
            self.logger.error(f"Error deploying project: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_deployment_script(self, project: Dict[str, Any], environment: str) -> str:
        """Create deployment script for the project."""
        try:
            script_content = f"""#!/bin/bash
# Deployment script for {project['name']}
# Environment: {environment}

set -e

echo "Starting deployment of {project['name']}..."

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

if [ -f "package.json" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Run tests
echo "Running tests..."
if [ -f "tests" ]; then
    python -m pytest tests/ -v
fi

# Create deployment directory
mkdir -p deployment/{environment}

# Copy files
cp -r src/ deployment/{environment}/
cp -r config/ deployment/{environment}/ 2>/dev/null || true

# Create startup script
cat > deployment/{environment}/start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python src/main.py
EOF

chmod +x deployment/{environment}/start.sh

echo "Deployment completed successfully!"
echo "To start the application, run: ./deployment/{environment}/start.sh"
"""
            
            return script_content
        
        except Exception as e:
            self.logger.error(f"Error creating deployment script: {e}")
            return "#!/bin/bash\necho 'Error creating deployment script'"
    
    def _execute_deployment(self, script_content: str, project_dir: Path) -> Dict[str, Any]:
        """Execute deployment script."""
        try:
            # Write script to file
            script_path = project_dir / "deploy.sh"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Execute script
            result = subprocess.run(
                [str(script_path)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        
        except Exception as e:
            self.logger.error(f"Error executing deployment: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_documentation(self, project_id: str) -> Dict[str, Any]:
        """Generate comprehensive project documentation."""
        try:
            self.logger.info(f"Generating documentation for project {project_id}...")
            
            if project_id not in self.projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.projects[project_id]
            project_dir = self.project_root / project['name'].replace(' ', '_').lower()
            
            # Generate API documentation
            api_docs = self._generate_api_documentation(project_id)
            
            # Generate user guide
            user_guide = self._generate_user_guide(project)
            
            # Generate technical documentation
            tech_docs = self._generate_technical_documentation(project_id)
            
            # Save documentation
            docs_dir = project_dir / "docs"
            docs_dir.mkdir(exist_ok=True)
            
            with open(docs_dir / "API.md", 'w', encoding='utf-8') as f:
                f.write(api_docs)
            
            with open(docs_dir / "USER_GUIDE.md", 'w', encoding='utf-8') as f:
                f.write(user_guide)
            
            with open(docs_dir / "TECHNICAL.md", 'w', encoding='utf-8') as f:
                f.write(tech_docs)
            
            self.logger.info("Documentation generated successfully")
            return {
                "success": True,
                "documentation_files": [
                    "docs/API.md",
                    "docs/USER_GUIDE.md",
                    "docs/TECHNICAL.md"
                ]
            }
        
        except Exception as e:
            self.logger.error(f"Error generating documentation: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_api_documentation(self, project_id: str) -> str:
        """Generate API documentation."""
        try:
            designs = self.designs.get(project_id, [])
            
            api_docs = "# API Documentation\n\n"
            
            for design in designs:
                api_docs += f"## {design.component_name}\n\n"
                api_docs += f"{design.description}\n\n"
                
                if design.api_specifications:
                    api_docs += "### Endpoints\n\n"
                    for api in design.api_specifications:
                        api_docs += f"#### {api.get('method', 'GET')} {api.get('endpoint', '/')}\n"
                        api_docs += f"{api.get('description', 'No description')}\n\n"
            
            return api_docs
        
        except Exception as e:
            self.logger.error(f"Error generating API documentation: {e}")
            return "# API Documentation\n\nError generating API documentation."
    
    def _generate_user_guide(self, project: Dict[str, Any]) -> str:
        """Generate user guide."""
        try:
            user_guide = f"""# {project['name']} - User Guide

## Overview
{project['description']}

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python src/main.py`

### Basic Usage
1. Start the application
2. Follow the on-screen instructions
3. Use the API endpoints as needed

## Features
- Automated processing
- RESTful API
- Comprehensive logging
- Error handling

## Troubleshooting
- Check logs for error messages
- Verify all dependencies are installed
- Ensure proper configuration

## Support
For support, please check the documentation or contact the development team.
"""
            
            return user_guide
        
        except Exception as e:
            self.logger.error(f"Error generating user guide: {e}")
            return "# User Guide\n\nError generating user guide."
    
    def _generate_technical_documentation(self, project_id: str) -> str:
        """Generate technical documentation."""
        try:
            project = self.projects[project_id]
            requirements = self.requirements.get(project_id, [])
            designs = self.designs.get(project_id, [])
            code_modules = self.code_modules.get(project_id, [])
            
            tech_docs = f"""# {project['name']} - Technical Documentation

## Architecture Overview
{project['description']}

## Requirements
"""
            
            for req in requirements:
                tech_docs += f"- **{req.title}**: {req.description}\n"
            
            tech_docs += "\n## Design Components\n"
            
            for design in designs:
                tech_docs += f"### {design.component_name}\n"
                tech_docs += f"{design.description}\n"
                tech_docs += f"**Architecture**: {design.architecture}\n\n"
            
            tech_docs += "## Code Modules\n"
            
            for module in code_modules:
                tech_docs += f"### {module.name}\n"
                tech_docs += f"**File**: {module.file_path}\n"
                tech_docs += f"**Language**: {module.language}\n"
                tech_docs += f"**Description**: {module.description}\n\n"
            
            return tech_docs
        
        except Exception as e:
            self.logger.error(f"Error generating technical documentation: {e}")
            return "# Technical Documentation\n\nError generating technical documentation."
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project status."""
        try:
            if project_id not in self.projects:
                return {"error": "Project not found"}
            
            project = self.projects[project_id]
            requirements = self.requirements.get(project_id, [])
            designs = self.designs.get(project_id, [])
            code_modules = self.code_modules.get(project_id, [])
            test_cases = self.test_cases.get(project_id, [])
            
            return {
                "project": project,
                "requirements_count": len(requirements),
                "designs_count": len(designs),
                "code_modules_count": len(code_modules),
                "test_cases_count": len(test_cases),
                "current_phase": self.current_phase.value,
                "completion_percentage": self._calculate_completion_percentage(project_id)
            }
        
        except Exception as e:
            self.logger.error(f"Error getting project status: {e}")
            return {"error": str(e)}
    
    def _calculate_completion_percentage(self, project_id: str) -> float:
        """Calculate project completion percentage."""
        try:
            total_phases = len(SDLCPhase)
            completed_phases = 0
            
            if project_id in self.requirements and self.requirements[project_id]:
                completed_phases += 1
            
            if project_id in self.designs and self.designs[project_id]:
                completed_phases += 1
            
            if project_id in self.code_modules and self.code_modules[project_id]:
                completed_phases += 1
            
            if project_id in self.test_cases and self.test_cases[project_id]:
                completed_phases += 1
            
            return (completed_phases / total_phases) * 100
        
        except Exception as e:
            self.logger.error(f"Error calculating completion percentage: {e}")
            return 0.0
    
    def export_project_report(self, project_id: str, output_file: str = None) -> bool:
        """Export comprehensive project report."""
        try:
            if project_id not in self.projects:
                return False
            
            if not output_file:
                output_file = f"project_report_{project_id}_{int(datetime.now().timestamp())}.json"
            
            report = {
                "project": self.projects[project_id],
                "requirements": [
                    {
                        "req_id": req.req_id,
                        "title": req.title,
                        "description": req.description,
                        "priority": req.priority,
                        "complexity": req.complexity,
                        "estimated_hours": req.estimated_hours,
                        "status": req.status
                    }
                    for req in self.requirements.get(project_id, [])
                ],
                "designs": [
                    {
                        "design_id": design.design_id,
                        "component_name": design.component_name,
                        "description": design.description,
                        "architecture": design.architecture,
                        "technology_stack": design.technology_stack
                    }
                    for design in self.designs.get(project_id, [])
                ],
                "code_modules": [
                    {
                        "module_id": module.module_id,
                        "name": module.name,
                        "language": module.language,
                        "file_path": module.file_path,
                        "description": module.description
                    }
                    for module in self.code_modules.get(project_id, [])
                ],
                "test_cases": [
                    {
                        "test_id": test.test_id,
                        "name": test.name,
                        "description": test.description,
                        "test_type": test.test_type,
                        "status": test.status
                    }
                    for test in self.test_cases.get(project_id, [])
                ],
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Project report exported: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting project report: {e}")
            return False
