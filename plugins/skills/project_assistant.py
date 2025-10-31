"""
JARVIS AI - Project Assistant Bot Skill
AI-powered development assistance and project management.
"""

import os
import logging
import json
import subprocess
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from plugins.plugin_manager import PluginBase

class ProjectAssistantBot(PluginBase):
    """
    Project Assistant Bot for development assistance.
    Provides code analysis, documentation generation, project structure recommendations, and Git integration.
    """
    
    def __init__(self):
        """Initialize Project Assistant Bot."""
        super().__init__("ProjectAssistantBot", "1.0.0")
        
        # Update metadata
        self.metadata.update({
            'author': 'Jarvis AI Team',
            'description': 'AI-powered development assistance and project management',
            'category': 'development',
            'dependencies': ['git'],
            'compatibility': '1.0.0'
        })
        
        self.logger = logging.getLogger(f"skill.{self.name}")
        
        # Project analysis settings
        self.analysis_settings = {
            'supported_languages': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.go', '.rs'],
            'documentation_extensions': ['.md', '.txt', '.rst'],
            'config_extensions': ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'],
            'test_extensions': ['test_', '_test', '.test.', '.spec.']
        }
    
    def initialize(self, config: dict = None) -> bool:
        """Initialize the project assistant bot."""
        try:
            self.logger.info(f"Initializing {self.name} skill")
            
            # Load configuration if provided
            if config:
                self.analysis_settings.update(config.get('analysis_settings', {}))
            
            return super().initialize(config)
        except Exception as e:
            self.logger.error(f"Error initializing {self.name} skill: {e}")
            return False
    
    def process_command(self, command: str, context: dict = None) -> dict:
        """Process project assistance commands."""
        try:
            command_lower = command.lower()
            
            # Project analysis
            if any(keyword in command_lower for keyword in ['analyze', 'analysis', 'project']):
                return self._analyze_project(context.get('project_path', '.'))
            
            # Code analysis
            elif any(keyword in command_lower for keyword in ['code', 'review', 'quality']):
                return self._analyze_code(context.get('project_path', '.'))
            
            # Documentation generation
            elif any(keyword in command_lower for keyword in ['documentation', 'docs', 'generate']):
                return self._generate_documentation(context.get('project_path', '.'))
            
            # Project structure
            elif any(keyword in command_lower for keyword in ['structure', 'organize', 'layout']):
                return self._analyze_structure(context.get('project_path', '.'))
            
            # Git integration
            elif any(keyword in command_lower for keyword in ['git', 'commit', 'version']):
                return self._git_analysis(context.get('project_path', '.'))
            
            # Timeline estimation
            elif any(keyword in command_lower for keyword in ['timeline', 'estimate', 'schedule']):
                return self._estimate_timeline(context.get('project_path', '.'))
            
            # Dependencies analysis
            elif any(keyword in command_lower for keyword in ['dependencies', 'requirements', 'packages']):
                return self._analyze_dependencies(context.get('project_path', '.'))
            
            # Testing analysis
            elif any(keyword in command_lower for keyword in ['test', 'testing', 'coverage']):
                return self._analyze_testing(context.get('project_path', '.'))
            
            else:
                return {
                    'success': False,
                    'message': f'{self.name} cannot process: {command}',
                    'data': {},
                    'confidence': 0.0
                }
        
        except Exception as e:
            self.logger.error(f"Error processing command in {self.name}: {e}")
            return {
                'success': False,
                'message': f'Error in {self.name}: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _analyze_project(self, project_path: str) -> dict:
        """Comprehensive project analysis."""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    'success': False,
                    'message': f'Project path does not exist: {project_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Get project statistics
            stats = self._get_project_stats(project_dir)
            
            # Analyze code quality
            code_quality = self._analyze_code_quality(project_dir)
            
            # Analyze structure
            structure_analysis = self._analyze_project_structure(project_dir)
            
            # Analyze dependencies
            dependencies = self._analyze_dependencies(project_path)
            
            # Generate recommendations
            recommendations = self._generate_project_recommendations(stats, code_quality, structure_analysis)
            
            return {
                'success': True,
                'message': f'Project analysis completed for {project_dir.name}',
                'data': {
                    'project_name': project_dir.name,
                    'project_path': str(project_dir),
                    'statistics': stats,
                    'code_quality': code_quality,
                    'structure': structure_analysis,
                    'dependencies': dependencies.get('data', {}),
                    'recommendations': recommendations,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing project: {e}")
            return {
                'success': False,
                'message': f'Error analyzing project: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _analyze_code(self, project_path: str) -> dict:
        """Analyze code quality and structure."""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    'success': False,
                    'message': f'Project path does not exist: {project_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Find code files
            code_files = []
            for ext in self.analysis_settings['supported_languages']:
                code_files.extend(project_dir.rglob(f'*{ext}'))
            
            # Analyze each code file
            file_analysis = []
            total_lines = 0
            total_functions = 0
            total_classes = 0
            
            for file_path in code_files:
                try:
                    analysis = self._analyze_code_file(file_path)
                    file_analysis.append(analysis)
                    total_lines += analysis.get('lines', 0)
                    total_functions += analysis.get('functions', 0)
                    total_classes += analysis.get('classes', 0)
                except Exception as e:
                    self.logger.warning(f"Could not analyze {file_path}: {e}")
            
            # Calculate code metrics
            avg_lines_per_file = total_lines / len(code_files) if code_files else 0
            avg_functions_per_file = total_functions / len(code_files) if code_files else 0
            
            return {
                'success': True,
                'message': f'Analyzed {len(code_files)} code files',
                'data': {
                    'total_files': len(code_files),
                    'total_lines': total_lines,
                    'total_functions': total_functions,
                    'total_classes': total_classes,
                    'avg_lines_per_file': round(avg_lines_per_file, 2),
                    'avg_functions_per_file': round(avg_functions_per_file, 2),
                    'file_analysis': file_analysis,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing code: {e}")
            return {
                'success': False,
                'message': f'Error analyzing code: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _generate_documentation(self, project_path: str) -> dict:
        """Generate project documentation."""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    'success': False,
                    'message': f'Project path does not exist: {project_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Check existing documentation
            existing_docs = list(project_dir.rglob('README.md')) + list(project_dir.rglob('*.md'))
            
            # Generate documentation structure
            doc_structure = self._generate_doc_structure(project_dir)
            
            # Generate README content
            readme_content = self._generate_readme_content(project_dir)
            
            # Generate API documentation
            api_docs = self._generate_api_documentation(project_dir)
            
            return {
                'success': True,
                'message': f'Generated documentation structure for {project_dir.name}',
                'data': {
                    'existing_docs': [str(doc) for doc in existing_docs],
                    'doc_structure': doc_structure,
                    'readme_content': readme_content,
                    'api_docs': api_docs,
                    'recommendations': [
                        'Create comprehensive README.md',
                        'Add API documentation',
                        'Include setup instructions',
                        'Document dependencies',
                        'Add contribution guidelines'
                    ],
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error generating documentation: {e}")
            return {
                'success': False,
                'message': f'Error generating documentation: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _analyze_structure(self, project_path: str) -> dict:
        """Analyze project structure and organization."""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    'success': False,
                    'message': f'Project path does not exist: {project_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Analyze directory structure
            structure = self._get_directory_structure(project_dir)
            
            # Check for common project patterns
            patterns = self._detect_project_patterns(project_dir)
            
            # Generate structure recommendations
            recommendations = self._generate_structure_recommendations(structure, patterns)
            
            return {
                'success': True,
                'message': f'Analyzed project structure for {project_dir.name}',
                'data': {
                    'structure': structure,
                    'patterns': patterns,
                    'recommendations': recommendations,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing structure: {e}")
            return {
                'success': False,
                'message': f'Error analyzing structure: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _git_analysis(self, project_path: str) -> dict:
        """Analyze Git repository and version control."""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    'success': False,
                    'message': f'Project path does not exist: {project_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Check if it's a Git repository
            git_dir = project_dir / '.git'
            if not git_dir.exists():
                return {
                    'success': False,
                    'message': 'Not a Git repository',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Get Git information
            git_info = self._get_git_info(project_dir)
            
            # Analyze commit history
            commit_analysis = self._analyze_commit_history(project_dir)
            
            # Generate Git recommendations
            git_recommendations = self._generate_git_recommendations(git_info, commit_analysis)
            
            return {
                'success': True,
                'message': f'Git analysis completed for {project_dir.name}',
                'data': {
                    'git_info': git_info,
                    'commit_analysis': commit_analysis,
                    'recommendations': git_recommendations,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing Git: {e}")
            return {
                'success': False,
                'message': f'Error analyzing Git: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _estimate_timeline(self, project_path: str) -> dict:
        """Estimate project development timeline."""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    'success': False,
                    'message': f'Project path does not exist: {project_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Get project statistics
            stats = self._get_project_stats(project_dir)
            
            # Calculate complexity metrics
            complexity = self._calculate_complexity_metrics(project_dir)
            
            # Estimate timeline
            timeline = self._calculate_timeline_estimate(stats, complexity)
            
            return {
                'success': True,
                'message': f'Timeline estimation completed for {project_dir.name}',
                'data': {
                    'project_stats': stats,
                    'complexity_metrics': complexity,
                    'timeline_estimate': timeline,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.7
            }
        
        except Exception as e:
            self.logger.error(f"Error estimating timeline: {e}")
            return {
                'success': False,
                'message': f'Error estimating timeline: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _analyze_dependencies(self, project_path: str) -> dict:
        """Analyze project dependencies."""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    'success': False,
                    'message': f'Project path does not exist: {project_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Find dependency files
            dependency_files = []
            for pattern in ['requirements.txt', 'package.json', 'pom.xml', 'Cargo.toml', 'go.mod']:
                dependency_files.extend(project_dir.rglob(pattern))
            
            # Analyze each dependency file
            dependencies = {}
            for dep_file in dependency_files:
                try:
                    deps = self._parse_dependency_file(dep_file)
                    dependencies[str(dep_file)] = deps
                except Exception as e:
                    self.logger.warning(f"Could not parse {dep_file}: {e}")
            
            return {
                'success': True,
                'message': f'Analyzed dependencies in {len(dependency_files)} files',
                'data': {
                    'dependency_files': [str(f) for f in dependency_files],
                    'dependencies': dependencies,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing dependencies: {e}")
            return {
                'success': False,
                'message': f'Error analyzing dependencies: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _analyze_testing(self, project_path: str) -> dict:
        """Analyze testing coverage and quality."""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    'success': False,
                    'message': f'Project path does not exist: {project_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Find test files
            test_files = []
            for pattern in self.analysis_settings['test_extensions']:
                test_files.extend(project_dir.rglob(f'*{pattern}*'))
            
            # Analyze test coverage
            test_analysis = self._analyze_test_coverage(project_dir, test_files)
            
            return {
                'success': True,
                'message': f'Analyzed {len(test_files)} test files',
                'data': {
                    'test_files': [str(f) for f in test_files],
                    'test_analysis': test_analysis,
                    'recommendations': [
                        'Increase test coverage',
                        'Add integration tests',
                        'Implement automated testing',
                        'Add performance tests'
                    ],
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing testing: {e}")
            return {
                'success': False,
                'message': f'Error analyzing testing: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _get_project_stats(self, project_dir: Path) -> dict:
        """Get basic project statistics."""
        try:
            total_files = 0
            total_dirs = 0
            total_size = 0
            file_types = {}
            
            for item in project_dir.rglob('*'):
                if item.is_file():
                    total_files += 1
                    total_size += item.stat().st_size
                    ext = item.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                elif item.is_dir():
                    total_dirs += 1
            
            return {
                'total_files': total_files,
                'total_directories': total_dirs,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_types': file_types
            }
        except Exception as e:
            self.logger.error(f"Error getting project stats: {e}")
            return {}
    
    def _analyze_code_file(self, file_path: Path) -> dict:
        """Analyze individual code file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Count functions and classes (basic analysis)
                functions = content.count('def ')
                classes = content.count('class ')
                
                return {
                    'file': str(file_path),
                    'lines': len(lines),
                    'functions': functions,
                    'classes': classes,
                    'size_bytes': file_path.stat().st_size
                }
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {e}")
            return {'file': str(file_path), 'lines': 0, 'functions': 0, 'classes': 0, 'size_bytes': 0}
    
    def _get_directory_structure(self, project_dir: Path, max_depth: int = 3) -> dict:
        """Get directory structure."""
        structure = {}
        
        def build_structure(path: Path, depth: int = 0):
            if depth > max_depth:
                return
            
            items = []
            try:
                for item in path.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        items.append({
                            'name': item.name,
                            'type': 'directory',
                            'children': build_structure(item, depth + 1)
                        })
                    elif item.is_file():
                        items.append({
                            'name': item.name,
                            'type': 'file',
                            'size': item.stat().st_size
                        })
            except PermissionError:
                pass
            
            return items
        
        structure[project_dir.name] = build_structure(project_dir)
        return structure
    
    def _detect_project_patterns(self, project_dir: Path) -> list:
        """Detect common project patterns."""
        patterns = []
        
        # Check for common files
        common_files = {
            'README.md': 'Documentation',
            'requirements.txt': 'Python dependencies',
            'package.json': 'Node.js project',
            'Dockerfile': 'Containerization',
            '.gitignore': 'Git repository',
            'setup.py': 'Python package',
            'Makefile': 'Build automation'
        }
        
        for file_name, description in common_files.items():
            if (project_dir / file_name).exists():
                patterns.append(description)
        
        return patterns
    
    def _generate_structure_recommendations(self, structure: dict, patterns: list) -> list:
        """Generate structure recommendations."""
        recommendations = []
        
        if 'Documentation' not in patterns:
            recommendations.append("Add README.md for project documentation")
        
        if 'Git repository' not in patterns:
            recommendations.append("Initialize Git repository for version control")
        
        recommendations.append("Organize code into logical modules")
        recommendations.append("Separate source code from tests")
        recommendations.append("Add configuration files for dependencies")
        
        return recommendations
    
    def _get_git_info(self, project_dir: Path) -> dict:
        """Get Git repository information."""
        try:
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                 cwd=project_dir, capture_output=True, text=True)
            current_branch = result.stdout.strip()
            
            # Get commit count
            result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], 
                                 cwd=project_dir, capture_output=True, text=True)
            commit_count = int(result.stdout.strip()) if result.stdout.strip() else 0
            
            return {
                'current_branch': current_branch,
                'commit_count': commit_count,
                'is_git_repo': True
            }
        except Exception as e:
            self.logger.warning(f"Could not get Git info: {e}")
            return {'is_git_repo': False}
    
    def _analyze_commit_history(self, project_dir: Path) -> dict:
        """Analyze Git commit history."""
        try:
            # Get recent commits
            result = subprocess.run(['git', 'log', '--oneline', '-10'], 
                                 cwd=project_dir, capture_output=True, text=True)
            recent_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                'recent_commits': recent_commits,
                'commit_frequency': 'Regular' if len(recent_commits) > 5 else 'Infrequent'
            }
        except Exception as e:
            self.logger.warning(f"Could not analyze commit history: {e}")
            return {'recent_commits': [], 'commit_frequency': 'Unknown'}
    
    def _generate_git_recommendations(self, git_info: dict, commit_analysis: dict) -> list:
        """Generate Git recommendations."""
        recommendations = []
        
        if not git_info.get('is_git_repo'):
            recommendations.append("Initialize Git repository")
            return recommendations
        
        if commit_analysis.get('commit_frequency') == 'Infrequent':
            recommendations.append("Commit changes more frequently")
        
        recommendations.append("Use descriptive commit messages")
        recommendations.append("Create feature branches for new development")
        recommendations.append("Regularly push changes to remote repository")
        
        return recommendations
    
    def _calculate_complexity_metrics(self, project_dir: Path) -> dict:
        """Calculate project complexity metrics."""
        try:
            # Count code files
            code_files = []
            for ext in self.analysis_settings['supported_languages']:
                code_files.extend(project_dir.rglob(f'*{ext}'))
            
            total_lines = 0
            for file_path in code_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += len(f.readlines())
                except Exception:
                    continue
            
            return {
                'total_code_files': len(code_files),
                'total_lines_of_code': total_lines,
                'complexity_score': min(100, (total_lines / 1000) * 10)  # Simple complexity score
            }
        except Exception as e:
            self.logger.warning(f"Could not calculate complexity: {e}")
            return {'total_code_files': 0, 'total_lines_of_code': 0, 'complexity_score': 0}
    
    def _calculate_timeline_estimate(self, stats: dict, complexity: dict) -> dict:
        """Calculate timeline estimate."""
        try:
            # Simple estimation based on lines of code
            loc = complexity.get('total_lines_of_code', 0)
            
            # Rough estimates (these would be more sophisticated in practice)
            if loc < 1000:
                estimated_days = 1
                confidence = 'High'
            elif loc < 5000:
                estimated_days = 3
                confidence = 'Medium'
            elif loc < 10000:
                estimated_days = 7
                confidence = 'Medium'
            else:
                estimated_days = 14
                confidence = 'Low'
            
            return {
                'estimated_days': estimated_days,
                'confidence': confidence,
                'factors': [
                    'Lines of code',
                    'Project complexity',
                    'Team size',
                    'Requirements clarity'
                ]
            }
        except Exception as e:
            self.logger.warning(f"Could not calculate timeline: {e}")
            return {'estimated_days': 0, 'confidence': 'Unknown', 'factors': []}
    
    def _parse_dependency_file(self, dep_file: Path) -> list:
        """Parse dependency file."""
        try:
            dependencies = []
            with open(dep_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        dependencies.append(line)
            return dependencies
        except Exception as e:
            self.logger.warning(f"Could not parse {dep_file}: {e}")
            return []
    
    def _analyze_test_coverage(self, project_dir: Path, test_files: list) -> dict:
        """Analyze test coverage."""
        try:
            # Count test files vs total files
            total_files = len(list(project_dir.rglob('*.py')))  # Assuming Python project
            test_file_count = len(test_files)
            
            coverage_ratio = (test_file_count / total_files) * 100 if total_files > 0 else 0
            
            return {
                'test_files': test_file_count,
                'total_files': total_files,
                'coverage_ratio': round(coverage_ratio, 2),
                'coverage_status': 'Good' if coverage_ratio > 50 else 'Needs Improvement'
            }
        except Exception as e:
            self.logger.warning(f"Could not analyze test coverage: {e}")
            return {'test_files': 0, 'total_files': 0, 'coverage_ratio': 0, 'coverage_status': 'Unknown'}
    
    def _generate_doc_structure(self, project_dir: Path) -> dict:
        """Generate documentation structure."""
        return {
            'README.md': 'Main project documentation',
            'docs/': 'Detailed documentation folder',
            'API.md': 'API reference documentation',
            'CONTRIBUTING.md': 'Contribution guidelines',
            'CHANGELOG.md': 'Version history'
        }
    
    def _generate_readme_content(self, project_dir: Path) -> str:
        """Generate README content."""
        return f"""# {project_dir.name}

## Description
Brief description of the project.

## Installation
```bash
# Installation instructions
```

## Usage
```bash
# Usage examples
```

## Contributing
Guidelines for contributing to the project.

## License
Project license information.
"""
    
    def _generate_api_documentation(self, project_dir: Path) -> dict:
        """Generate API documentation."""
        return {
            'endpoints': 'API endpoint documentation',
            'authentication': 'Authentication methods',
            'examples': 'Usage examples',
            'error_codes': 'Error handling'
        }
    
    def _generate_project_recommendations(self, stats: dict, code_quality: dict, structure: dict) -> list:
        """Generate project recommendations."""
        recommendations = []
        
        if stats.get('total_files', 0) > 100:
            recommendations.append("Consider modularizing the project")
        
        if code_quality.get('avg_lines_per_file', 0) > 200:
            recommendations.append("Break down large files into smaller modules")
        
        recommendations.append("Add comprehensive documentation")
        recommendations.append("Implement automated testing")
        recommendations.append("Set up continuous integration")
        
        return recommendations
    
    def get_capabilities(self) -> list:
        """Get skill capabilities."""
        return [
            "Project analysis and statistics",
            "Code quality assessment",
            "Documentation generation",
            "Structure analysis",
            "Git repository analysis",
            "Timeline estimation",
            "Dependency analysis",
            "Testing coverage analysis",
            "Development recommendations",
            "Project management assistance"
        ]
