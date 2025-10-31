"""
JARVIS AI - AI Coding Assistant
Fine-tuned AI model for IDE integration with context-aware coding assistance.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import re

class AICodingAssistant:
    """
    AI-powered coding assistant with context awareness for IDE integration.
    Provides intelligent code suggestions, explanations, and automation.
    """
    
    def __init__(self, ai_engine=None):
        """Initialize AI coding assistant."""
        self.logger = logging.getLogger(__name__)
        self.ai_engine = ai_engine
        self.project_context = {}
        self.code_patterns = {}
        self.suggestion_history = []
        
        # Load coding patterns and best practices
        self._load_coding_patterns()
        
        self.logger.info("AI Coding Assistant initialized")
    
    def _load_coding_patterns(self):
        """Load coding patterns and best practices for different languages."""
        try:
            self.code_patterns = {
                'python': {
                    'imports': {
                        'standard': ['os', 'sys', 'json', 'datetime', 'pathlib', 'typing'],
                        'data_science': ['numpy', 'pandas', 'matplotlib', 'seaborn', 'scikit-learn'],
                        'web': ['flask', 'django', 'fastapi', 'requests', 'aiohttp'],
                        'ai_ml': ['tensorflow', 'pytorch', 'transformers', 'openai', 'langchain']
                    },
                    'patterns': {
                        'class_definition': 'class {name}:\n    def __init__(self):\n        pass',
                        'function_definition': 'def {name}({params}):\n    """{docstring}"""\n    pass',
                        'async_function': 'async def {name}({params}):\n    """{docstring}"""\n    pass',
                        'context_manager': 'with {resource} as {var}:\n    {code}',
                        'exception_handling': 'try:\n    {code}\nexcept {exception} as e:\n    {handle}'
                    },
                    'best_practices': [
                        'Use type hints for function parameters and return values',
                        'Follow PEP 8 style guidelines',
                        'Use meaningful variable and function names',
                        'Add docstrings to classes and functions',
                        'Use list comprehensions for simple transformations',
                        'Prefer f-strings over .format() or % formatting',
                        'Use pathlib.Path instead of os.path',
                        'Handle exceptions specifically, not bare except'
                    ]
                },
                'javascript': {
                    'imports': {
                        'standard': ['fs', 'path', 'http', 'url', 'crypto'],
                        'frontend': ['react', 'vue', 'angular', 'jquery', 'lodash'],
                        'backend': ['express', 'koa', 'hapi', 'socket.io', 'mongoose'],
                        'testing': ['jest', 'mocha', 'chai', 'cypress', 'puppeteer']
                    },
                    'patterns': {
                        'function_definition': 'function {name}({params}) {\n    {code}\n}',
                        'arrow_function': 'const {name} = ({params}) => {\n    {code}\n}',
                        'async_function': 'async function {name}({params}) {\n    {code}\n}',
                        'class_definition': 'class {name} {\n    constructor({params}) {\n        {code}\n    }\n}',
                        'promise_handling': 'Promise.resolve({value})\n    .then({handler})\n    .catch({error_handler})'
                    },
                    'best_practices': [
                        'Use const and let instead of var',
                        'Use arrow functions for short functions',
                        'Use template literals instead of string concatenation',
                        'Use destructuring for object and array assignment',
                        'Use async/await instead of Promise chains',
                        'Use meaningful variable and function names',
                        'Add JSDoc comments for functions',
                        'Use ESLint for code quality'
                    ]
                },
                'typescript': {
                    'imports': {
                        'standard': ['fs', 'path', 'http', 'url', 'crypto'],
                        'frontend': ['react', 'vue', 'angular', 'rxjs', 'lodash'],
                        'backend': ['express', 'koa', 'hapi', 'socket.io', 'mongoose'],
                        'testing': ['jest', 'mocha', 'chai', 'cypress', 'puppeteer']
                    },
                    'patterns': {
                        'interface_definition': 'interface {name} {\n    {properties}\n}',
                        'type_definition': 'type {name} = {definition}',
                        'generic_function': 'function {name}<T>({params}): {return_type} {\n    {code}\n}',
                        'class_with_types': 'class {name} {\n    private {property}: {type};\n    \n    constructor({params}: {param_types}) {\n        {code}\n    }\n}'
                    },
                    'best_practices': [
                        'Use strict type checking',
                        'Define interfaces for object shapes',
                        'Use union types for multiple possible values',
                        'Use generics for reusable code',
                        'Use enums for fixed sets of values',
                        'Use optional properties with ?',
                        'Use readonly for immutable properties',
                        'Use const assertions for literal types'
                    ]
                }
            }
            
            self.logger.info("Coding patterns loaded successfully")
        
        except Exception as e:
            self.logger.error(f"Error loading coding patterns: {e}")
    
    def analyze_code_context(self, file_path: str, cursor_position: int = 0) -> Dict[str, Any]:
        """Analyze code context around cursor position."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            current_line = 0
            char_count = 0
            
            # Find current line
            for i, line in enumerate(lines):
                if char_count + len(line) >= cursor_position:
                    current_line = i
                    break
                char_count += len(line) + 1  # +1 for newline
            
            # Get context around cursor
            context_lines = 5
            start_line = max(0, current_line - context_lines)
            end_line = min(len(lines), current_line + context_lines + 1)
            
            context = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_extension': file_path.suffix,
                'language': self._detect_language(file_path.suffix),
                'current_line': current_line,
                'cursor_position': cursor_position,
                'context_lines': lines[start_line:end_line],
                'current_line_content': lines[current_line] if current_line < len(lines) else '',
                'indentation_level': self._get_indentation_level(lines[current_line]) if current_line < len(lines) else 0,
                'surrounding_code': '\n'.join(lines[start_line:end_line]),
                'imports': self._extract_imports(content),
                'functions': self._extract_functions(content, file_path.suffix),
                'classes': self._extract_classes(content, file_path.suffix),
                'variables': self._extract_variables(content, current_line, file_path.suffix)
            }
            
            return context
        
        except Exception as e:
            self.logger.error(f"Error analyzing code context: {e}")
            return {}
    
    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.vue': 'vue',
            '.svelte': 'svelte',
            '.dart': 'dart',
            '.r': 'r',
            '.m': 'objective-c',
            '.mm': 'objective-cpp',
            '.sh': 'shell',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.md': 'markdown',
            '.tex': 'latex'
        }
        
        return language_map.get(file_extension.lower(), 'unknown')
    
    def _get_indentation_level(self, line: str) -> int:
        """Get indentation level of a line."""
        return len(line) - len(line.lstrip())
    
    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract import statements from code."""
        imports = []
        
        # Python imports
        python_imports = re.findall(r'^(?:from\s+(\S+)\s+)?import\s+(.+?)$', content, re.MULTILINE)
        for module, items in python_imports:
            imports.append({
                'type': 'python',
                'module': module,
                'items': items.strip(),
                'line': content[:content.find(f'import {items}')].count('\n') + 1
            })
        
        # JavaScript/TypeScript imports
        js_imports = re.findall(r'^import\s+(.+?)\s+from\s+[\'"](.+?)[\'"]', content, re.MULTILINE)
        for items, module in js_imports:
            imports.append({
                'type': 'javascript',
                'module': module,
                'items': items.strip(),
                'line': content[:content.find(f'import {items}')].count('\n') + 1
            })
        
        return imports
    
    def _extract_functions(self, content: str, file_extension: str) -> List[Dict[str, Any]]:
        """Extract function definitions from code."""
        functions = []
        
        if file_extension == '.py':
            # Python functions
            python_functions = re.findall(r'^def\s+(\w+)\s*\((.*?)\):', content, re.MULTILINE)
            for name, params in python_functions:
                functions.append({
                    'name': name,
                    'parameters': params,
                    'type': 'function',
                    'line': content[:content.find(f'def {name}')].count('\n') + 1
                })
        
        elif file_extension in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript functions
            js_functions = re.findall(r'^(?:async\s+)?(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)', content, re.MULTILINE)
            for match in js_functions:
                name = match[0] or match[1]
                functions.append({
                    'name': name,
                    'type': 'function',
                    'line': content[:content.find(name)].count('\n') + 1
                })
        
        return functions
    
    def _extract_classes(self, content: str, file_extension: str) -> List[Dict[str, Any]]:
        """Extract class definitions from code."""
        classes = []
        
        if file_extension == '.py':
            # Python classes
            python_classes = re.findall(r'^class\s+(\w+)(?:\([^)]*\))?:', content, re.MULTILINE)
            for name in python_classes:
                classes.append({
                    'name': name,
                    'type': 'class',
                    'line': content[:content.find(f'class {name}')].count('\n') + 1
                })
        
        elif file_extension in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript classes
            js_classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            for name in js_classes:
                classes.append({
                    'name': name,
                    'type': 'class',
                    'line': content[:content.find(f'class {name}')].count('\n') + 1
                })
        
        return classes
    
    def _extract_variables(self, content: str, current_line: int, file_extension: str) -> List[Dict[str, Any]]:
        """Extract variable declarations around current line."""
        variables = []
        
        # Get lines around current line
        lines = content.split('\n')
        start_line = max(0, current_line - 10)
        end_line = min(len(lines), current_line + 10)
        context_lines = lines[start_line:end_line]
        
        if file_extension == '.py':
            # Python variables
            for i, line in enumerate(context_lines):
                # Simple variable assignment
                var_match = re.match(r'^(\s*)(\w+)\s*=\s*(.+)$', line)
                if var_match:
                    variables.append({
                        'name': var_match.group(2),
                        'value': var_match.group(3).strip(),
                        'line': start_line + i + 1
                    })
        
        elif file_extension in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript variables
            for i, line in enumerate(context_lines):
                # const, let, var declarations
                var_match = re.match(r'^(\s*)(?:const|let|var)\s+(\w+)\s*=\s*(.+)$', line)
                if var_match:
                    variables.append({
                        'name': var_match.group(2),
                        'value': var_match.group(3).strip(),
                        'line': start_line + i + 1
                    })
        
        return variables
    
    def generate_code_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent code suggestions based on context."""
        try:
            suggestions = []
            
            if not context:
                return suggestions
            
            language = context.get('language', 'unknown')
            current_line = context.get('current_line_content', '')
            indentation = context.get('indentation_level', 0)
            
            # Get language-specific patterns
            patterns = self.code_patterns.get(language, {})
            
            # Suggest imports based on context
            import_suggestions = self._suggest_imports(context, patterns)
            suggestions.extend(import_suggestions)
            
            # Suggest code completions
            completion_suggestions = self._suggest_completions(context, patterns)
            suggestions.extend(completion_suggestions)
            
            # Suggest code patterns
            pattern_suggestions = self._suggest_patterns(context, patterns)
            suggestions.extend(pattern_suggestions)
            
            # Suggest best practices
            best_practice_suggestions = self._suggest_best_practices(context, patterns)
            suggestions.extend(best_practice_suggestions)
            
            # Store suggestions in history
            self.suggestion_history.extend(suggestions)
            
            return suggestions
        
        except Exception as e:
            self.logger.error(f"Error generating code suggestions: {e}")
            return []
    
    def _suggest_imports(self, context: Dict[str, Any], patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest relevant imports based on code context."""
        suggestions = []
        
        language = context.get('language', 'unknown')
        current_line = context.get('current_line_content', '')
        existing_imports = [imp['items'] for imp in context.get('imports', [])]
        
        if language == 'python':
            # Suggest standard library imports
            if 'os' in current_line.lower() and 'os' not in ' '.join(existing_imports):
                suggestions.append({
                    'type': 'import',
                    'suggestion': 'import os',
                    'description': 'Import os module for operating system interface',
                    'priority': 'high'
                })
            
            if 'json' in current_line.lower() and 'json' not in ' '.join(existing_imports):
                suggestions.append({
                    'type': 'import',
                    'suggestion': 'import json',
                    'description': 'Import json module for JSON data handling',
                    'priority': 'high'
                })
            
            if 'datetime' in current_line.lower() and 'datetime' not in ' '.join(existing_imports):
                suggestions.append({
                    'type': 'import',
                    'suggestion': 'from datetime import datetime',
                    'description': 'Import datetime for date and time operations',
                    'priority': 'high'
                })
        
        elif language in ['javascript', 'typescript']:
            # Suggest common imports
            if 'fetch' in current_line.lower() and 'fetch' not in ' '.join(existing_imports):
                suggestions.append({
                    'type': 'import',
                    'suggestion': 'import fetch from "node-fetch"',
                    'description': 'Import fetch for HTTP requests',
                    'priority': 'medium'
                })
        
        return suggestions
    
    def _suggest_completions(self, context: Dict[str, Any], patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest code completions based on context."""
        suggestions = []
        
        language = context.get('language', 'unknown')
        current_line = context.get('current_line_content', '')
        
        if language == 'python':
            # Suggest common Python patterns
            if current_line.strip().startswith('def '):
                suggestions.append({
                    'type': 'completion',
                    'suggestion': 'def {name}(self):\n    """{docstring}"""\n    pass',
                    'description': 'Complete function definition with docstring',
                    'priority': 'high'
                })
            
            if current_line.strip().startswith('class '):
                suggestions.append({
                    'type': 'completion',
                    'suggestion': 'class {name}:\n    def __init__(self):\n        pass',
                    'description': 'Complete class definition with constructor',
                    'priority': 'high'
                })
        
        return suggestions
    
    def _suggest_patterns(self, context: Dict[str, Any], patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest code patterns based on context."""
        suggestions = []
        
        language = context.get('language', 'unknown')
        current_line = context.get('current_line_content', '')
        
        if language == 'python':
            # Suggest context managers
            if 'open(' in current_line and 'with ' not in current_line:
                suggestions.append({
                    'type': 'pattern',
                    'suggestion': 'with open("{filename}", "r") as f:\n    {code}',
                    'description': 'Use context manager for file operations',
                    'priority': 'high'
                })
            
            # Suggest exception handling
            if 'try:' in current_line:
                suggestions.append({
                    'type': 'pattern',
                    'suggestion': 'try:\n    {code}\nexcept {Exception} as e:\n    {handle}',
                    'description': 'Complete try-except block',
                    'priority': 'medium'
                })
        
        return suggestions
    
    def _suggest_best_practices(self, context: Dict[str, Any], patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest best practices based on code analysis."""
        suggestions = []
        
        language = context.get('language', 'unknown')
        current_line = context.get('current_line_content', '')
        
        if language == 'python':
            # Check for string formatting
            if '.format(' in current_line or '%' in current_line:
                suggestions.append({
                    'type': 'best_practice',
                    'suggestion': 'Use f-strings instead of .format() or % formatting',
                    'description': 'f-strings are more readable and efficient',
                    'priority': 'medium'
                })
            
            # Check for type hints
            if current_line.strip().startswith('def ') and '->' not in current_line:
                suggestions.append({
                    'type': 'best_practice',
                    'suggestion': 'Add type hints to function parameters and return type',
                    'description': 'Type hints improve code readability and IDE support',
                    'priority': 'low'
                })
        
        return suggestions
    
    def explain_code(self, code: str, language: str = 'python') -> str:
        """Generate explanation for code snippet."""
        try:
            if not self.ai_engine:
                return "AI engine not available for code explanation"
            
            prompt = f"""
            Explain the following {language} code in simple terms:
            
            ```{language}
            {code}
            ```
            
            Provide:
            1. What the code does
            2. How it works
            3. Key concepts used
            4. Potential improvements
            """
            
            response = self.ai_engine.get_ai_response(prompt)
            return response
        
        except Exception as e:
            self.logger.error(f"Error explaining code: {e}")
            return f"Error explaining code: {e}"
    
    def refactor_suggestions(self, code: str, language: str = 'python') -> List[Dict[str, Any]]:
        """Generate refactoring suggestions for code."""
        try:
            suggestions = []
            
            if language == 'python':
                # Check for long functions
                lines = code.split('\n')
                if len(lines) > 20:
                    suggestions.append({
                        'type': 'refactor',
                        'suggestion': 'Consider breaking this function into smaller functions',
                        'description': 'Functions should ideally be 10-20 lines long',
                        'priority': 'medium'
                    })
                
                # Check for repeated code
                if 'if ' in code and code.count('if ') > 3:
                    suggestions.append({
                        'type': 'refactor',
                        'suggestion': 'Consider using a dictionary or switch statement for multiple conditions',
                        'description': 'Reduce repetitive if-else statements',
                        'priority': 'low'
                    })
            
            return suggestions
        
        except Exception as e:
            self.logger.error(f"Error generating refactor suggestions: {e}")
            return []
    
    def generate_tests(self, code: str, language: str = 'python') -> str:
        """Generate unit tests for code."""
        try:
            if not self.ai_engine:
                return "# AI engine not available for test generation"
            
            prompt = f"""
            Generate comprehensive unit tests for the following {language} code:
            
            ```{language}
            {code}
            ```
            
            Include:
            1. Test cases for normal operation
            2. Edge cases and error conditions
            3. Proper test structure and naming
            4. Assertions and expectations
            """
            
            response = self.ai_engine.get_ai_response(prompt)
            return response
        
        except Exception as e:
            self.logger.error(f"Error generating tests: {e}")
            return f"# Error generating tests: {e}"
    
    def get_suggestion_history(self) -> List[Dict[str, Any]]:
        """Get history of code suggestions."""
        return self.suggestion_history.copy()
    
    def clear_suggestion_history(self):
        """Clear suggestion history."""
        self.suggestion_history.clear()
        self.logger.info("Suggestion history cleared")
