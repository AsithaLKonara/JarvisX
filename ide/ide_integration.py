"""
JARVIS AI - IDE Integration
Integration with existing IDEs (Cursor IDE, VS Code) for AI-powered development assistance.
"""

import json
import logging
import os
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import re

class IDEIntegration:
    """
    Integrates Jarvis AI with existing IDEs for enhanced development experience.
    Supports Cursor IDE, VS Code, and other popular development environments.
    """
    
    def __init__(self):
        """Initialize IDE integration."""
        self.logger = logging.getLogger(__name__)
        self.supported_ides = {
            'cursor': self._detect_cursor_ide,
            'vscode': self._detect_vscode,
            'pycharm': self._detect_pycharm,
            'sublime': self._detect_sublime_text
        }
        self.active_ide = None
        self.project_context = {}
        
        self.logger.info("IDE Integration initialized")
    
    def detect_active_ide(self) -> Optional[str]:
        """Detect which IDE is currently active."""
        try:
            for ide_name, detector in self.supported_ides.items():
                if detector():
                    self.active_ide = ide_name
                    self.logger.info(f"Detected active IDE: {ide_name}")
                    return ide_name
            
            self.logger.info("No supported IDE detected")
            return None
        
        except Exception as e:
            self.logger.error(f"Error detecting IDE: {e}")
            return None
    
    def _detect_cursor_ide(self) -> bool:
        """Detect if Cursor IDE is running."""
        try:
            # Check for Cursor process
            result = subprocess.run(['pgrep', '-f', 'Cursor'], capture_output=True, text=True)
            if result.returncode == 0:
                return True
            
            # Check for Cursor in common locations
            cursor_paths = [
                '/Applications/Cursor.app',
                '~/Applications/Cursor.app',
                'C:\\Users\\{username}\\AppData\\Local\\Programs\\cursor'
            ]
            
            for path in cursor_paths:
                if Path(path).exists():
                    return True
            
            return False
        
        except Exception:
            return False
    
    def _detect_vscode(self) -> bool:
        """Detect if VS Code is running."""
        try:
            # Check for VS Code process
            result = subprocess.run(['pgrep', '-f', 'Code'], capture_output=True, text=True)
            if result.returncode == 0:
                return True
            
            # Check for VS Code in common locations
            vscode_paths = [
                '/Applications/Visual Studio Code.app',
                '~/Applications/Visual Studio Code.app',
                'C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code'
            ]
            
            for path in vscode_paths:
                if Path(path).exists():
                    return True
            
            return False
        
        except Exception:
            return False
    
    def _detect_pycharm(self) -> bool:
        """Detect if PyCharm is running."""
        try:
            result = subprocess.run(['pgrep', '-f', 'pycharm'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _detect_sublime_text(self) -> bool:
        """Detect if Sublime Text is running."""
        try:
            result = subprocess.run(['pgrep', '-f', 'Sublime Text'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def analyze_project_context(self, project_path: str) -> Dict[str, Any]:
        """Analyze the current project for context-aware assistance."""
        try:
            self.logger.info(f"Analyzing project context: {project_path}")
            
            project_path = Path(project_path)
            context = {
                'project_path': str(project_path),
                'project_name': project_path.name,
                'languages': [],
                'frameworks': [],
                'dependencies': {},
                'file_structure': {},
                'git_info': {},
                'ide_config': {},
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Analyze programming languages
            context['languages'] = self._detect_languages(project_path)
            
            # Detect frameworks and libraries
            context['frameworks'] = self._detect_frameworks(project_path)
            
            # Analyze dependencies
            context['dependencies'] = self._analyze_dependencies(project_path)
            
            # Analyze file structure
            context['file_structure'] = self._analyze_file_structure(project_path)
            
            # Get Git information
            context['git_info'] = self._get_git_info(project_path)
            
            # Get IDE-specific configuration
            context['ide_config'] = self._get_ide_config(project_path)
            
            self.project_context = context
            self.logger.info(f"Project context analyzed: {len(context['languages'])} languages, {len(context['frameworks'])} frameworks")
            
            return context
        
        except Exception as e:
            self.logger.error(f"Error analyzing project context: {e}")
            return {}
    
    def _detect_languages(self, project_path: Path) -> List[str]:
        """Detect programming languages used in the project."""
        try:
            languages = set()
            
            # Common file extensions and their languages
            language_extensions = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.jsx': 'React',
                '.tsx': 'React TypeScript',
                '.java': 'Java',
                '.cpp': 'C++',
                '.c': 'C',
                '.cs': 'C#',
                '.php': 'PHP',
                '.rb': 'Ruby',
                '.go': 'Go',
                '.rs': 'Rust',
                '.swift': 'Swift',
                '.kt': 'Kotlin',
                '.scala': 'Scala',
                '.html': 'HTML',
                '.css': 'CSS',
                '.scss': 'SCSS',
                '.sass': 'Sass',
                '.vue': 'Vue.js',
                '.svelte': 'Svelte',
                '.dart': 'Dart',
                '.r': 'R',
                '.m': 'Objective-C',
                '.mm': 'Objective-C++',
                '.sh': 'Shell',
                '.ps1': 'PowerShell',
                '.sql': 'SQL',
                '.yaml': 'YAML',
                '.yml': 'YAML',
                '.json': 'JSON',
                '.xml': 'XML',
                '.md': 'Markdown',
                '.tex': 'LaTeX'
            }
            
            # Scan project files
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    suffix = file_path.suffix.lower()
                    if suffix in language_extensions:
                        languages.add(language_extensions[suffix])
            
            return list(languages)
        
        except Exception as e:
            self.logger.error(f"Error detecting languages: {e}")
            return []
    
    def _detect_frameworks(self, project_path: Path) -> List[str]:
        """Detect frameworks and libraries used in the project."""
        try:
            frameworks = set()
            
            # Check package.json for Node.js frameworks
            package_json = project_path / 'package.json'
            if package_json.exists():
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    dependencies = data.get('dependencies', {})
                    dev_dependencies = data.get('devDependencies', {})
                    all_deps = {**dependencies, **dev_dependencies}
                    
                    # Common frameworks
                    framework_patterns = {
                        'react': 'React',
                        'vue': 'Vue.js',
                        'angular': 'Angular',
                        'express': 'Express.js',
                        'next': 'Next.js',
                        'nuxt': 'Nuxt.js',
                        'svelte': 'Svelte',
                        'django': 'Django',
                        'flask': 'Flask',
                        'fastapi': 'FastAPI',
                        'spring': 'Spring Boot',
                        'laravel': 'Laravel',
                        'symfony': 'Symfony',
                        'rails': 'Ruby on Rails',
                        'gin': 'Gin (Go)',
                        'fiber': 'Fiber (Go)',
                        'actix': 'Actix (Rust)',
                        'rocket': 'Rocket (Rust)'
                    }
                    
                    for dep_name in all_deps.keys():
                        for pattern, framework in framework_patterns.items():
                            if pattern in dep_name.lower():
                                frameworks.add(framework)
            
            # Check requirements.txt for Python frameworks
            requirements_txt = project_path / 'requirements.txt'
            if requirements_txt.exists():
                with open(requirements_txt, 'r', encoding='utf-8') as f:
                    content = f.read()
                    python_frameworks = {
                        'django': 'Django',
                        'flask': 'Flask',
                        'fastapi': 'FastAPI',
                        'tornado': 'Tornado',
                        'bottle': 'Bottle',
                        'cherrypy': 'CherryPy',
                        'pyramid': 'Pyramid'
                    }
                    
                    for pattern, framework in python_frameworks.items():
                        if pattern in content.lower():
                            frameworks.add(framework)
            
            # Check for other framework indicators
            if (project_path / 'manage.py').exists():
                frameworks.add('Django')
            if (project_path / 'app.py').exists() and 'flask' in (project_path / 'app.py').read_text().lower():
                frameworks.add('Flask')
            if (project_path / 'main.py').exists() and 'fastapi' in (project_path / 'main.py').read_text().lower():
                frameworks.add('FastAPI')
            
            return list(frameworks)
        
        except Exception as e:
            self.logger.error(f"Error detecting frameworks: {e}")
            return []
    
    def _analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies."""
        try:
            dependencies = {}
            
            # Python dependencies
            requirements_txt = project_path / 'requirements.txt'
            if requirements_txt.exists():
                with open(requirements_txt, 'r', encoding='utf-8') as f:
                    python_deps = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
                    dependencies['python'] = python_deps
            
            # Node.js dependencies
            package_json = project_path / 'package.json'
            if package_json.exists():
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    dependencies['nodejs'] = {
                        'dependencies': data.get('dependencies', {}),
                        'devDependencies': data.get('devDependencies', {})
                    }
            
            # Java dependencies
            pom_xml = project_path / 'pom.xml'
            if pom_xml.exists():
                dependencies['java'] = 'Maven project detected'
            
            build_gradle = project_path / 'build.gradle'
            if build_gradle.exists():
                dependencies['java'] = 'Gradle project detected'
            
            return dependencies
        
        except Exception as e:
            self.logger.error(f"Error analyzing dependencies: {e}")
            return {}
    
    def _analyze_file_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project file structure."""
        try:
            structure = {
                'total_files': 0,
                'total_directories': 0,
                'file_types': {},
                'largest_files': [],
                'recent_files': []
            }
            
            file_sizes = []
            file_times = []
            
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    structure['total_files'] += 1
                    
                    # File type analysis
                    suffix = file_path.suffix.lower()
                    structure['file_types'][suffix] = structure['file_types'].get(suffix, 0) + 1
                    
                    # File size analysis
                    try:
                        size = file_path.stat().st_size
                        file_sizes.append((str(file_path), size))
                        file_times.append((str(file_path), file_path.stat().st_mtime))
                    except OSError:
                        continue
                else:
                    structure['total_directories'] += 1
            
            # Get largest files
            file_sizes.sort(key=lambda x: x[1], reverse=True)
            structure['largest_files'] = file_sizes[:10]
            
            # Get most recent files
            file_times.sort(key=lambda x: x[1], reverse=True)
            structure['recent_files'] = [f[0] for f in file_times[:10]]
            
            return structure
        
        except Exception as e:
            self.logger.error(f"Error analyzing file structure: {e}")
            return {}
    
    def _get_git_info(self, project_path: Path) -> Dict[str, Any]:
        """Get Git repository information."""
        try:
            git_info = {}
            
            # Check if it's a Git repository
            git_dir = project_path / '.git'
            if not git_dir.exists():
                return {'is_git_repo': False}
            
            git_info['is_git_repo'] = True
            
            # Get current branch
            try:
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                     cwd=project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    git_info['current_branch'] = result.stdout.strip()
            except Exception:
                pass
            
            # Get recent commits
            try:
                result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                     cwd=project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    git_info['recent_commits'] = result.stdout.strip().split('\n')
            except Exception:
                pass
            
            # Get status
            try:
                result = subprocess.run(['git', 'status', '--porcelain'], 
                                     cwd=project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    git_info['modified_files'] = result.stdout.strip().split('\n') if result.stdout.strip() else []
            except Exception:
                pass
            
            return git_info
        
        except Exception as e:
            self.logger.error(f"Error getting Git info: {e}")
            return {}
    
    def _get_ide_config(self, project_path: Path) -> Dict[str, Any]:
        """Get IDE-specific configuration."""
        try:
            config = {}
            
            # VS Code configuration
            vscode_dir = project_path / '.vscode'
            if vscode_dir.exists():
                config['vscode'] = {
                    'settings': {},
                    'launch': {},
                    'tasks': {}
                }
                
                settings_file = vscode_dir / 'settings.json'
                if settings_file.exists():
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        config['vscode']['settings'] = json.load(f)
                
                launch_file = vscode_dir / 'launch.json'
                if launch_file.exists():
                    with open(launch_file, 'r', encoding='utf-8') as f:
                        config['vscode']['launch'] = json.load(f)
            
            # Cursor IDE configuration
            cursor_dir = project_path / '.cursor'
            if cursor_dir.exists():
                config['cursor'] = {'configured': True}
            
            # PyCharm configuration
            idea_dir = project_path / '.idea'
            if idea_dir.exists():
                config['pycharm'] = {'configured': True}
            
            return config
        
        except Exception as e:
            self.logger.error(f"Error getting IDE config: {e}")
            return {}
    
    def generate_ide_commands(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate IDE-specific commands based on project context."""
        try:
            commands = []
            
            if not context:
                return commands
            
            # Language-specific commands
            languages = context.get('languages', [])
            frameworks = context.get('frameworks', [])
            
            # Python-specific commands
            if 'Python' in languages:
                commands.extend([
                    {
                        'command': 'Run Python script',
                        'action': 'run_python_script',
                        'description': 'Execute the current Python file',
                        'shortcut': 'Ctrl+Shift+R'
                    },
                    {
                        'command': 'Debug Python script',
                        'action': 'debug_python_script',
                        'description': 'Debug the current Python file',
                        'shortcut': 'F5'
                    },
                    {
                        'command': 'Format Python code',
                        'action': 'format_python_code',
                        'description': 'Format Python code using black or autopep8',
                        'shortcut': 'Shift+Alt+F'
                    }
                ])
            
            # JavaScript/TypeScript commands
            if any(lang in languages for lang in ['JavaScript', 'TypeScript', 'React']):
                commands.extend([
                    {
                        'command': 'Run npm script',
                        'action': 'run_npm_script',
                        'description': 'Execute npm scripts from package.json',
                        'shortcut': 'Ctrl+Shift+P'
                    },
                    {
                        'command': 'Install dependencies',
                        'action': 'install_dependencies',
                        'description': 'Install project dependencies',
                        'shortcut': 'Ctrl+Shift+I'
                    },
                    {
                        'command': 'Start development server',
                        'action': 'start_dev_server',
                        'description': 'Start the development server',
                        'shortcut': 'Ctrl+Shift+D'
                    }
                ])
            
            # Framework-specific commands
            if 'Django' in frameworks:
                commands.extend([
                    {
                        'command': 'Run Django server',
                        'action': 'run_django_server',
                        'description': 'Start Django development server',
                        'shortcut': 'Ctrl+Shift+S'
                    },
                    {
                        'command': 'Django migrations',
                        'action': 'django_migrations',
                        'description': 'Run Django database migrations',
                        'shortcut': 'Ctrl+Shift+M'
                    }
                ])
            
            if 'React' in frameworks:
                commands.extend([
                    {
                        'command': 'Start React app',
                        'action': 'start_react_app',
                        'description': 'Start React development server',
                        'shortcut': 'Ctrl+Shift+R'
                    },
                    {
                        'command': 'Build React app',
                        'action': 'build_react_app',
                        'description': 'Build React application for production',
                        'shortcut': 'Ctrl+Shift+B'
                    }
                ])
            
            # Git commands
            git_info = context.get('git_info', {})
            if git_info.get('is_git_repo'):
                commands.extend([
                    {
                        'command': 'Git status',
                        'action': 'git_status',
                        'description': 'Show Git repository status',
                        'shortcut': 'Ctrl+Shift+G'
                    },
                    {
                        'command': 'Git commit',
                        'action': 'git_commit',
                        'description': 'Commit changes to Git',
                        'shortcut': 'Ctrl+Shift+C'
                    },
                    {
                        'command': 'Git push',
                        'action': 'git_push',
                        'description': 'Push changes to remote repository',
                        'shortcut': 'Ctrl+Shift+P'
                    }
                ])
            
            return commands
        
        except Exception as e:
            self.logger.error(f"Error generating IDE commands: {e}")
            return []
    
    def create_ide_workflow(self, workflow_name: str, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create an IDE workflow for automation."""
        try:
            workflow = {
                'name': workflow_name,
                'created_at': datetime.now().isoformat(),
                'commands': commands,
                'triggers': [],
                'conditions': []
            }
            
            self.logger.info(f"Created IDE workflow: {workflow_name}")
            return workflow
        
        except Exception as e:
            self.logger.error(f"Error creating IDE workflow: {e}")
            return {}
    
    def export_ide_config(self, output_file: str) -> bool:
        """Export IDE configuration and commands."""
        try:
            config = {
                'active_ide': self.active_ide,
                'project_context': self.project_context,
                'supported_ides': list(self.supported_ides.keys()),
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"IDE configuration exported: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting IDE config: {e}")
            return False
