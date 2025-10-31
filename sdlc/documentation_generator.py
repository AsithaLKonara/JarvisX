"""
JARVIS AI - Documentation Generator
Automated documentation generation for projects, APIs, and technical specifications.
"""

import json
import logging
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import uuid
import ast

class DocumentationType(Enum):
    """Documentation types."""
    API_DOCS = "api_docs"
    USER_GUIDE = "user_guide"
    TECHNICAL_SPEC = "technical_spec"
    README = "readme"
    CHANGELOG = "changelog"
    CONTRIBUTING = "contributing"
    DEPLOYMENT = "deployment"

class DocumentationFormat(Enum):
    """Documentation formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    REST = "restructuredtext"

@dataclass
class CodeElement:
    """Code element for documentation."""
    name: str
    type: str  # function, class, module, variable
    description: str
    parameters: List[Dict[str, Any]]
    return_type: str
    examples: List[str]
    line_number: int
    file_path: str

@dataclass
class DocumentationSection:
    """Documentation section."""
    section_id: str
    title: str
    content: str
    subsections: List['DocumentationSection']
    code_examples: List[str]
    images: List[str]
    links: List[str]

@dataclass
class DocumentationProject:
    """Complete documentation project."""
    project_id: str
    title: str
    description: str
    version: str
    author: str
    sections: List[DocumentationSection]
    code_elements: List[CodeElement]
    metadata: Dict[str, Any]
    generated_at: datetime

class DocumentationGenerator:
    """
    AI-powered documentation generator for comprehensive project documentation.
    Generates API docs, user guides, technical specs, and more.
    """
    
    def __init__(self, ai_engine=None):
        """Initialize Documentation Generator."""
        self.logger = logging.getLogger(__name__)
        self.ai_engine = ai_engine
        
        # Documentation templates
        self.templates = self._load_templates()
        
        # Generated documentation
        self.documentation_projects = {}
        
        # Create documentation directories
        self._create_documentation_structure()
        
        self.logger.info("Documentation Generator initialized")
    
    def _create_documentation_structure(self):
        """Create documentation directory structure."""
        try:
            directories = [
                'docs',
                'docs/api',
                'docs/user',
                'docs/technical',
                'docs/images',
                'docs/examples',
                'templates',
                'output'
            ]
            
            for directory in directories:
                dir_path = Path(directory)
                dir_path.mkdir(exist_ok=True)
            
            self.logger.info("Documentation structure created")
        
        except Exception as e:
            self.logger.error(f"Error creating documentation structure: {e}")
    
    def _load_templates(self) -> Dict[str, str]:
        """Load documentation templates."""
        return {
            "api_docs": """# API Documentation

## Overview
{description}

## Base URL
{base_url}

## Authentication
{auth_info}

## Endpoints

{endpoints}

## Error Codes
{error_codes}

## Examples
{examples}
""",
            
            "user_guide": """# {title} - User Guide

## Table of Contents
{toc}

## Getting Started
{getting_started}

## Features
{features}

## Usage
{usage}

## Configuration
{configuration}

## Troubleshooting
{troubleshooting}

## Support
{support}
""",
            
            "technical_spec": """# {title} - Technical Specification

## Overview
{overview}

## Architecture
{architecture}

## Requirements
{requirements}

## Design
{design}

## Implementation
{implementation}

## Testing
{testing}

## Deployment
{deployment}
""",
            
            "readme": """# {title}

{description}

## Features
{features}

## Installation
{installation}

## Usage
{usage}

## Configuration
{configuration}

## API Reference
{api_reference}

## Contributing
{contributing}

## License
{license}
"""
        }
    
    def generate_project_documentation(self, project_path: str, project_name: str = None, 
                                     doc_types: List[DocumentationType] = None) -> DocumentationProject:
        """Generate comprehensive documentation for a project."""
        try:
            self.logger.info(f"Generating documentation for project: {project_path}")
            
            project_path = Path(project_path)
            if not project_path.exists():
                raise FileNotFoundError(f"Project path not found: {project_path}")
            
            # Set default documentation types
            if not doc_types:
                doc_types = [DocumentationType.README, DocumentationType.API_DOCS, DocumentationType.USER_GUIDE]
            
            # Analyze project
            project_info = self._analyze_project(project_path)
            code_elements = self._extract_code_elements(project_path)
            
            # Generate documentation project
            project_id = f"doc_{uuid.uuid4().hex[:8]}"
            
            doc_project = DocumentationProject(
                project_id=project_id,
                title=project_name or project_info.get('name', 'Project'),
                description=project_info.get('description', ''),
                version=project_info.get('version', '1.0.0'),
                author=project_info.get('author', 'Unknown'),
                sections=[],
                code_elements=code_elements,
                metadata=project_info,
                generated_at=datetime.now()
            )
            
            # Generate requested documentation types
            for doc_type in doc_types:
                section = self._generate_documentation_section(doc_type, project_info, code_elements)
                if section:
                    doc_project.sections.append(section)
            
            # Store documentation project
            self.documentation_projects[project_id] = doc_project
            
            # Save documentation files
            self._save_documentation_files(doc_project, project_path)
            
            self.logger.info(f"Documentation generated successfully: {project_id}")
            return doc_project
        
        except Exception as e:
            self.logger.error(f"Error generating project documentation: {e}")
            return None
    
    def _analyze_project(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project structure and extract metadata."""
        try:
            project_info = {
                'name': project_path.name,
                'description': '',
                'version': '1.0.0',
                'author': 'Unknown',
                'languages': [],
                'frameworks': [],
                'dependencies': [],
                'file_count': 0,
                'total_lines': 0
            }
            
            # Check for README.md
            readme_file = project_path / 'README.md'
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                    project_info['description'] = self._extract_description_from_readme(readme_content)
            
            # Check for package.json (Node.js)
            package_json = project_path / 'package.json'
            if package_json.exists():
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    project_info.update({
                        'name': package_data.get('name', project_info['name']),
                        'description': package_data.get('description', project_info['description']),
                        'version': package_data.get('version', project_info['version']),
                        'author': package_data.get('author', project_info['author']),
                        'dependencies': list(package_data.get('dependencies', {}).keys())
                    })
                    project_info['languages'].append('JavaScript')
            
            # Check for requirements.txt (Python)
            requirements_txt = project_path / 'requirements.txt'
            if requirements_txt.exists():
                with open(requirements_txt, 'r', encoding='utf-8') as f:
                    deps = [line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]
                    project_info['dependencies'].extend(deps)
                    project_info['languages'].append('Python')
            
            # Check for setup.py (Python)
            setup_py = project_path / 'setup.py'
            if setup_py.exists():
                project_info['languages'].append('Python')
            
            # Count files and lines
            file_count = 0
            total_lines = 0
            
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    file_count += 1
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                    except:
                        pass
            
            project_info['file_count'] = file_count
            project_info['total_lines'] = total_lines
            
            return project_info
        
        except Exception as e:
            self.logger.error(f"Error analyzing project: {e}")
            return {'name': project_path.name, 'description': '', 'version': '1.0.0', 'author': 'Unknown'}
    
    def _extract_description_from_readme(self, readme_content: str) -> str:
        """Extract project description from README content."""
        try:
            lines = readme_content.split('\n')
            
            # Look for description after title
            for i, line in enumerate(lines):
                if line.startswith('# ') and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('#'):
                        return next_line
            
            # Fallback: first non-empty line
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    return line.strip()
            
            return "No description available"
        
        except Exception as e:
            self.logger.error(f"Error extracting description: {e}")
            return "No description available"
    
    def _extract_code_elements(self, project_path: Path) -> List[CodeElement]:
        """Extract code elements for documentation."""
        try:
            code_elements = []
            
            # Find Python files
            python_files = list(project_path.rglob('*.py'))
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse AST
                    tree = ast.parse(content)
                    
                    # Extract elements
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            element = self._extract_function_element(node, str(file_path))
                            if element:
                                code_elements.append(element)
                        
                        elif isinstance(node, ast.ClassDef):
                            element = self._extract_class_element(node, str(file_path))
                            if element:
                                code_elements.append(element)
                
                except Exception as e:
                    self.logger.warning(f"Error parsing {file_path}: {e}")
                    continue
            
            return code_elements
        
        except Exception as e:
            self.logger.error(f"Error extracting code elements: {e}")
            return []
    
    def _extract_function_element(self, node: ast.FunctionDef, file_path: str) -> CodeElement:
        """Extract function element for documentation."""
        try:
            # Extract docstring
            docstring = ast.get_docstring(node) or ""
            
            # Extract parameters
            parameters = []
            for arg in node.args.args:
                param_info = {
                    'name': arg.arg,
                    'type': 'Any',  # Would need type hints analysis
                    'description': '',
                    'required': True
                }
                parameters.append(param_info)
            
            # Extract return type
            return_type = 'Any'
            if node.returns:
                return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else 'Any'
            
            return CodeElement(
                name=node.name,
                type='function',
                description=docstring,
                parameters=parameters,
                return_type=return_type,
                examples=[],
                line_number=node.lineno,
                file_path=file_path
            )
        
        except Exception as e:
            self.logger.error(f"Error extracting function element: {e}")
            return None
    
    def _extract_class_element(self, node: ast.ClassDef, file_path: str) -> CodeElement:
        """Extract class element for documentation."""
        try:
            # Extract docstring
            docstring = ast.get_docstring(node) or ""
            
            # Extract methods
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)
            
            return CodeElement(
                name=node.name,
                type='class',
                description=docstring,
                parameters=[],  # Classes don't have parameters
                return_type='',
                examples=[],
                line_number=node.lineno,
                file_path=file_path
            )
        
        except Exception as e:
            self.logger.error(f"Error extracting class element: {e}")
            return None
    
    def _generate_documentation_section(self, doc_type: DocumentationType, 
                                      project_info: Dict[str, Any], 
                                      code_elements: List[CodeElement]) -> DocumentationSection:
        """Generate a specific documentation section."""
        try:
            section_id = f"section_{uuid.uuid4().hex[:8]}"
            
            if doc_type == DocumentationType.API_DOCS:
                return self._generate_api_documentation(section_id, project_info, code_elements)
            
            elif doc_type == DocumentationType.USER_GUIDE:
                return self._generate_user_guide(section_id, project_info, code_elements)
            
            elif doc_type == DocumentationType.TECHNICAL_SPEC:
                return self._generate_technical_specification(section_id, project_info, code_elements)
            
            elif doc_type == DocumentationType.README:
                return self._generate_readme(section_id, project_info, code_elements)
            
            else:
                return None
        
        except Exception as e:
            self.logger.error(f"Error generating documentation section: {e}")
            return None
    
    def _generate_api_documentation(self, section_id: str, project_info: Dict[str, Any], 
                                  code_elements: List[CodeElement]) -> DocumentationSection:
        """Generate API documentation section."""
        try:
            # Filter functions and classes
            functions = [elem for elem in code_elements if elem.type == 'function']
            classes = [elem for elem in code_elements if elem.type == 'class']
            
            # Generate content
            content = f"""# API Documentation

## Overview
{project_info.get('description', 'API documentation for the project')}

## Base URL
`http://localhost:8000/api/v1`

## Authentication
This API uses Bearer token authentication.

## Endpoints

### Functions
"""
            
            for func in functions:
                content += f"""
#### {func.name}
{func.description}

**Parameters:**
"""
                for param in func.parameters:
                    content += f"- `{param['name']}` ({param['type']}): {param['description']}\n"
                
                content += f"**Returns:** {func.return_type}\n\n"
            
            content += "### Classes\n"
            
            for cls in classes:
                content += f"""
#### {cls.name}
{cls.description}

**Methods:**
- Available methods will be listed here
"""
            
            content += """
## Error Codes
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Examples
```python
# Example usage
from project import main_function

result = main_function(param1="value1", param2="value2")
print(result)
```
"""
            
            return DocumentationSection(
                section_id=section_id,
                title="API Documentation",
                content=content,
                subsections=[],
                code_examples=[],
                images=[],
                links=[]
            )
        
        except Exception as e:
            self.logger.error(f"Error generating API documentation: {e}")
            return None
    
    def _generate_user_guide(self, section_id: str, project_info: Dict[str, Any], 
                           code_elements: List[CodeElement]) -> DocumentationSection:
        """Generate user guide section."""
        try:
            content = f"""# {project_info.get('name', 'Project')} - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Features](#features)
3. [Usage](#usage)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Support](#support)

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

## Features
- Automated processing
- RESTful API
- Comprehensive logging
- Error handling
- Documentation generation

## Usage

### Basic Usage
1. Start the application
2. Follow the on-screen instructions
3. Use the API endpoints as needed

### Advanced Usage
For advanced usage, refer to the API documentation.

## Configuration
Configuration can be done through environment variables or configuration files.

### Environment Variables
- `API_KEY`: Your API key
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level

## Troubleshooting

### Common Issues
1. **Import Error**: Make sure all dependencies are installed
2. **Connection Error**: Check your network connection
3. **Permission Error**: Ensure proper file permissions

### Getting Help
- Check the logs for error messages
- Verify all dependencies are installed
- Ensure proper configuration

## Support
For support, please check the documentation or contact the development team.
"""
            
            return DocumentationSection(
                section_id=section_id,
                title="User Guide",
                content=content,
                subsections=[],
                code_examples=[],
                images=[],
                links=[]
            )
        
        except Exception as e:
            self.logger.error(f"Error generating user guide: {e}")
            return None
    
    def _generate_technical_specification(self, section_id: str, project_info: Dict[str, Any], 
                                        code_elements: List[CodeElement]) -> DocumentationSection:
        """Generate technical specification section."""
        try:
            content = f"""# {project_info.get('name', 'Project')} - Technical Specification

## Overview
{project_info.get('description', 'Technical specification for the project')}

## Architecture
The project follows a modular architecture with clear separation of concerns.

### Components
- **Core Module**: Main application logic
- **API Module**: REST API endpoints
- **Database Module**: Data persistence
- **Utils Module**: Utility functions

## Requirements

### Functional Requirements
- Process user requests
- Provide API endpoints
- Handle errors gracefully
- Generate documentation

### Non-Functional Requirements
- Performance: Handle 100+ concurrent requests
- Security: Secure authentication and authorization
- Scalability: Support horizontal scaling
- Maintainability: Clean, documented code

## Design

### Data Models
- User model for authentication
- Request model for API calls
- Response model for API responses

### API Design
- RESTful API design
- JSON request/response format
- HTTP status codes
- Error handling

## Implementation

### Technology Stack
- **Language**: {', '.join(project_info.get('languages', ['Python']))}
- **Framework**: FastAPI/Flask
- **Database**: SQLite/PostgreSQL
- **Testing**: pytest

### Code Structure
```
project/
├── src/
│   ├── main.py
│   ├── api/
│   ├── models/
│   └── utils/
├── tests/
├── docs/
└── requirements.txt
```

## Testing

### Test Strategy
- Unit tests for individual functions
- Integration tests for API endpoints
- End-to-end tests for complete workflows

### Test Coverage
- Target: 80%+ code coverage
- Automated testing in CI/CD pipeline

## Deployment

### Environment Setup
- Development environment
- Staging environment
- Production environment

### Deployment Process
1. Code review and testing
2. Build and package
3. Deploy to staging
4. Integration testing
5. Deploy to production
6. Monitor and maintain
"""
            
            return DocumentationSection(
                section_id=section_id,
                title="Technical Specification",
                content=content,
                subsections=[],
                code_examples=[],
                images=[],
                links=[]
            )
        
        except Exception as e:
            self.logger.error(f"Error generating technical specification: {e}")
            return None
    
    def _generate_readme(self, section_id: str, project_info: Dict[str, Any], 
                        code_elements: List[CodeElement]) -> DocumentationSection:
        """Generate README section."""
        try:
            content = f"""# {project_info.get('name', 'Project')}

{project_info.get('description', 'A Python project with automated documentation generation.')}

## Features
- Automated processing
- RESTful API
- Comprehensive logging
- Error handling
- Documentation generation

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup
1. Clone the repository
```bash
git clone <repository-url>
cd {project_info.get('name', 'project').lower().replace(' ', '-')}
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```

## Usage

### Basic Usage
```python
from project import main_function

result = main_function(param1="value1", param2="value2")
print(result)
```

### API Usage
```bash
curl -X GET "http://localhost:8000/api/v1/endpoint" \\
     -H "Authorization: Bearer your-token"
```

## Configuration
Configuration can be done through environment variables:

```bash
export API_KEY="your-api-key"
export DEBUG="true"
export LOG_LEVEL="INFO"
```

## API Reference
See [API Documentation](docs/api.md) for detailed API reference.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
"""
            
            return DocumentationSection(
                section_id=section_id,
                title="README",
                content=content,
                subsections=[],
                code_examples=[],
                images=[],
                links=[]
            )
        
        except Exception as e:
            self.logger.error(f"Error generating README: {e}")
            return None
    
    def _save_documentation_files(self, doc_project: DocumentationProject, project_path: Path):
        """Save documentation files to project."""
        try:
            docs_dir = project_path / 'docs'
            docs_dir.mkdir(exist_ok=True)
            
            # Save each section as a separate file
            for section in doc_project.sections:
                filename = f"{section.title.lower().replace(' ', '_')}.md"
                file_path = docs_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(section.content)
                
                self.logger.info(f"Documentation saved: {file_path}")
            
            # Save project metadata
            metadata_file = docs_dir / 'project_metadata.json'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'project_id': doc_project.project_id,
                    'title': doc_project.title,
                    'description': doc_project.description,
                    'version': doc_project.version,
                    'author': doc_project.author,
                    'generated_at': doc_project.generated_at.isoformat(),
                    'sections': [s.title for s in doc_project.sections],
                    'code_elements_count': len(doc_project.code_elements)
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Documentation metadata saved: {metadata_file}")
        
        except Exception as e:
            self.logger.error(f"Error saving documentation files: {e}")
    
    def export_documentation(self, project_id: str, output_format: DocumentationFormat = DocumentationFormat.MARKDOWN) -> bool:
        """Export documentation in specified format."""
        try:
            if project_id not in self.documentation_projects:
                self.logger.error(f"Documentation project not found: {project_id}")
                return False
            
            doc_project = self.documentation_projects[project_id]
            output_dir = Path("output") / project_id
            output_dir.mkdir(exist_ok=True)
            
            if output_format == DocumentationFormat.MARKDOWN:
                return self._export_markdown(doc_project, output_dir)
            elif output_format == DocumentationFormat.HTML:
                return self._export_html(doc_project, output_dir)
            else:
                self.logger.error(f"Unsupported output format: {output_format}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error exporting documentation: {e}")
            return False
    
    def _export_markdown(self, doc_project: DocumentationProject, output_dir: Path) -> bool:
        """Export documentation as Markdown files."""
        try:
            for section in doc_project.sections:
                filename = f"{section.title.lower().replace(' ', '_')}.md"
                file_path = output_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(section.content)
            
            self.logger.info(f"Markdown documentation exported to: {output_dir}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting Markdown: {e}")
            return False
    
    def _export_html(self, doc_project: DocumentationProject, output_dir: Path) -> bool:
        """Export documentation as HTML files."""
        try:
            # Simple HTML conversion (would need markdown library for proper conversion)
            for section in doc_project.sections:
                filename = f"{section.title.lower().replace(' ', '_')}.html"
                file_path = output_dir / filename
                
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{section.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; }}
    </style>
</head>
<body>
{self._markdown_to_html(section.content)}
</body>
</html>"""
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            self.logger.info(f"HTML documentation exported to: {output_dir}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting HTML: {e}")
            return False
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """Simple markdown to HTML conversion."""
        try:
            # Basic markdown to HTML conversion
            html = markdown_content
            
            # Headers
            html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
            html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
            html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
            
            # Code blocks
            html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
            
            # Inline code
            html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
            
            # Bold
            html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
            
            # Italic
            html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
            
            # Line breaks
            html = html.replace('\n', '<br>\n')
            
            return html
        
        except Exception as e:
            self.logger.error(f"Error converting markdown to HTML: {e}")
            return markdown_content
    
    def get_documentation_projects(self) -> List[Dict[str, Any]]:
        """Get list of all documentation projects."""
        try:
            projects = []
            
            for project_id, doc_project in self.documentation_projects.items():
                projects.append({
                    'project_id': project_id,
                    'title': doc_project.title,
                    'description': doc_project.description,
                    'version': doc_project.version,
                    'author': doc_project.author,
                    'generated_at': doc_project.generated_at.isoformat(),
                    'sections_count': len(doc_project.sections),
                    'code_elements_count': len(doc_project.code_elements)
                })
            
            return sorted(projects, key=lambda x: x['generated_at'], reverse=True)
        
        except Exception as e:
            self.logger.error(f"Error getting documentation projects: {e}")
            return []
    
    def get_documentation_statistics(self) -> Dict[str, Any]:
        """Get documentation generation statistics."""
        try:
            total_projects = len(self.documentation_projects)
            total_sections = sum(len(p.sections) for p in self.documentation_projects.values())
            total_code_elements = sum(len(p.code_elements) for p in self.documentation_projects.values())
            
            return {
                'total_projects': total_projects,
                'total_sections': total_sections,
                'total_code_elements': total_code_elements,
                'average_sections_per_project': total_sections / total_projects if total_projects > 0 else 0,
                'average_code_elements_per_project': total_code_elements / total_projects if total_projects > 0 else 0
            }
        
        except Exception as e:
            self.logger.error(f"Error getting documentation statistics: {e}")
            return {}
