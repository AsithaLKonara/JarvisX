"""
JARVIS AI - Code Reviewer
Automated code review, quality assurance, and security analysis.
"""

import ast
import json
import logging
import os
import re
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import uuid

class ReviewSeverity(Enum):
    """Code review severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ReviewCategory(Enum):
    """Code review categories."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    READABILITY = "readability"
    BEST_PRACTICES = "best_practices"
    BUG_POTENTIAL = "bug_potential"
    DOCUMENTATION = "documentation"

@dataclass
class CodeIssue:
    """Individual code issue found during review."""
    issue_id: str
    file_path: str
    line_number: int
    column: int
    severity: ReviewSeverity
    category: ReviewCategory
    title: str
    description: str
    suggestion: str
    code_snippet: str
    rule_id: str

@dataclass
class CodeMetrics:
    """Code quality metrics."""
    file_path: str
    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    code_duplication: float
    test_coverage: float
    security_score: float
    performance_score: float

@dataclass
class ReviewReport:
    """Complete code review report."""
    report_id: str
    project_path: str
    review_timestamp: datetime
    total_files: int
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_category: Dict[str, int]
    code_metrics: List[CodeMetrics]
    recommendations: List[str]
    overall_score: float

class CodeReviewer:
    """
    AI-powered code reviewer for automated quality assurance.
    Analyzes code for security, performance, maintainability, and best practices.
    """
    
    def __init__(self, ai_engine=None):
        """Initialize Code Reviewer."""
        self.logger = logging.getLogger(__name__)
        self.ai_engine = ai_engine
        
        # Review rules and patterns
        self.security_patterns = self._load_security_patterns()
        self.performance_patterns = self._load_performance_patterns()
        self.best_practice_patterns = self._load_best_practice_patterns()
        
        # Review history
        self.review_history = []
        
        self.logger.info("Code Reviewer initialized")
    
    def _load_security_patterns(self) -> List[Dict[str, Any]]:
        """Load security vulnerability patterns."""
        return [
            {
                "pattern": r"eval\s*\(",
                "title": "Use of eval() function",
                "description": "eval() can execute arbitrary code and is a security risk",
                "severity": ReviewSeverity.CRITICAL,
                "category": ReviewCategory.SECURITY,
                "suggestion": "Use safer alternatives like ast.literal_eval() or json.loads()"
            },
            {
                "pattern": r"exec\s*\(",
                "title": "Use of exec() function",
                "description": "exec() can execute arbitrary code and is a security risk",
                "severity": ReviewSeverity.CRITICAL,
                "category": ReviewCategory.SECURITY,
                "suggestion": "Avoid using exec() or ensure input is properly sanitized"
            },
            {
                "pattern": r"subprocess\.call\s*\(\s*[^,)]*shell\s*=\s*True",
                "title": "Shell injection vulnerability",
                "description": "Using shell=True with subprocess can lead to shell injection",
                "severity": ReviewSeverity.HIGH,
                "category": ReviewCategory.SECURITY,
                "suggestion": "Avoid shell=True or properly sanitize input"
            },
            {
                "pattern": r"pickle\.loads?\s*\(",
                "title": "Unsafe pickle usage",
                "description": "pickle can execute arbitrary code during deserialization",
                "severity": ReviewSeverity.HIGH,
                "category": ReviewCategory.SECURITY,
                "suggestion": "Use safer serialization like json or ensure trusted source"
            },
            {
                "pattern": r"password\s*=\s*['\"][^'\"]*['\"]",
                "title": "Hardcoded password",
                "description": "Password should not be hardcoded in source code",
                "severity": ReviewSeverity.HIGH,
                "category": ReviewCategory.SECURITY,
                "suggestion": "Use environment variables or secure configuration"
            }
        ]
    
    def _load_performance_patterns(self) -> List[Dict[str, Any]]:
        """Load performance issue patterns."""
        return [
            {
                "pattern": r"for\s+\w+\s+in\s+range\s*\(\s*len\s*\(",
                "title": "Inefficient loop with range(len())",
                "description": "Using range(len()) is less efficient than enumerate()",
                "severity": ReviewSeverity.MEDIUM,
                "category": ReviewCategory.PERFORMANCE,
                "suggestion": "Use enumerate() instead of range(len())"
            },
            {
                "pattern": r"\.append\s*\(\s*\.join\s*\(",
                "title": "Inefficient string concatenation",
                "description": "Repeated string concatenation is inefficient",
                "severity": ReviewSeverity.MEDIUM,
                "category": ReviewCategory.PERFORMANCE,
                "suggestion": "Use join() for multiple string concatenations"
            },
            {
                "pattern": r"import\s+\*",
                "title": "Wildcard import",
                "description": "Wildcard imports can slow down module loading",
                "severity": ReviewSeverity.LOW,
                "category": ReviewCategory.PERFORMANCE,
                "suggestion": "Import only specific functions/classes needed"
            }
        ]
    
    def _load_best_practice_patterns(self) -> List[Dict[str, Any]]:
        """Load best practice patterns."""
        return [
            {
                "pattern": r"except\s*:",
                "title": "Bare except clause",
                "description": "Bare except clauses catch all exceptions including system exits",
                "severity": ReviewSeverity.MEDIUM,
                "category": ReviewCategory.BEST_PRACTICES,
                "suggestion": "Specify exception types to catch"
            },
            {
                "pattern": r"def\s+\w+\s*\(\s*\)\s*:\s*pass",
                "title": "Empty function",
                "description": "Empty functions should have docstrings or be removed",
                "severity": ReviewSeverity.LOW,
                "category": ReviewCategory.BEST_PRACTICES,
                "suggestion": "Add docstring or implement functionality"
            },
            {
                "pattern": r"class\s+\w+\s*:\s*pass",
                "title": "Empty class",
                "description": "Empty classes should have docstrings or be removed",
                "severity": ReviewSeverity.LOW,
                "category": ReviewCategory.BEST_PRACTICES,
                "suggestion": "Add docstring or implement functionality"
            }
        ]
    
    def review_file(self, file_path: str) -> List[CodeIssue]:
        """Review a single file for issues."""
        try:
            self.logger.info(f"Reviewing file: {file_path}")
            
            if not os.path.exists(file_path):
                return []
            
            issues = []
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Pattern-based analysis
            issues.extend(self._analyze_patterns(file_path, lines))
            
            # AST-based analysis
            issues.extend(self._analyze_ast(file_path, content))
            
            # AI-powered analysis
            if self.ai_engine:
                issues.extend(self._analyze_with_ai(file_path, content))
            
            self.logger.info(f"Found {len(issues)} issues in {file_path}")
            return issues
        
        except Exception as e:
            self.logger.error(f"Error reviewing file {file_path}: {e}")
            return []
    
    def _analyze_patterns(self, file_path: str, lines: List[str]) -> List[CodeIssue]:
        """Analyze code using pattern matching."""
        try:
            issues = []
            all_patterns = self.security_patterns + self.performance_patterns + self.best_practice_patterns
            
            for line_num, line in enumerate(lines, 1):
                for pattern_info in all_patterns:
                    matches = re.finditer(pattern_info["pattern"], line, re.IGNORECASE)
                    
                    for match in matches:
                        issue = CodeIssue(
                            issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                            file_path=file_path,
                            line_number=line_num,
                            column=match.start(),
                            severity=pattern_info["severity"],
                            category=pattern_info["category"],
                            title=pattern_info["title"],
                            description=pattern_info["description"],
                            suggestion=pattern_info["suggestion"],
                            code_snippet=line.strip(),
                            rule_id=f"pattern_{pattern_info['pattern'][:20]}"
                        )
                        issues.append(issue)
            
            return issues
        
        except Exception as e:
            self.logger.error(f"Error in pattern analysis: {e}")
            return []
    
    def _analyze_ast(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze code using Abstract Syntax Tree."""
        try:
            issues = []
            
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                # Handle syntax errors
                issue = CodeIssue(
                    issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                    file_path=file_path,
                    line_number=e.lineno or 1,
                    column=e.offset or 0,
                    severity=ReviewSeverity.CRITICAL,
                    category=ReviewCategory.BUG_POTENTIAL,
                    title="Syntax Error",
                    description=f"Syntax error: {e.msg}",
                    suggestion="Fix the syntax error",
                    code_snippet=content.split('\n')[e.lineno - 1] if e.lineno else "",
                    rule_id="syntax_error"
                )
                issues.append(issue)
                return issues
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                issues.extend(self._analyze_ast_node(file_path, node))
            
            return issues
        
        except Exception as e:
            self.logger.error(f"Error in AST analysis: {e}")
            return []
    
    def _analyze_ast_node(self, file_path: str, node: ast.AST) -> List[CodeIssue]:
        """Analyze individual AST node."""
        try:
            issues = []
            
            # Check for long functions
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:  # More than 50 lines
                    issue = CodeIssue(
                        issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity=ReviewSeverity.MEDIUM,
                        category=ReviewCategory.MAINTAINABILITY,
                        title="Long function",
                        description=f"Function '{node.name}' has {len(node.body)} lines",
                        suggestion="Consider breaking into smaller functions",
                        code_snippet=f"def {node.name}(...):",
                        rule_id="long_function"
                    )
                    issues.append(issue)
                
                # Check for missing docstring
                if not (node.body and isinstance(node.body[0], ast.Expr) and 
                       isinstance(node.body[0].value, ast.Constant) and
                       isinstance(node.body[0].value.value, str)):
                    issue = CodeIssue(
                        issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity=ReviewSeverity.LOW,
                        category=ReviewCategory.DOCUMENTATION,
                        title="Missing docstring",
                        description=f"Function '{node.name}' lacks docstring",
                        suggestion="Add a docstring describing the function's purpose",
                        code_snippet=f"def {node.name}(...):",
                        rule_id="missing_docstring"
                    )
                    issues.append(issue)
            
            # Check for long classes
            elif isinstance(node, ast.ClassDef):
                if len(node.body) > 20:  # More than 20 methods/attributes
                    issue = CodeIssue(
                        issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity=ReviewSeverity.MEDIUM,
                        category=ReviewCategory.MAINTAINABILITY,
                        title="Large class",
                        description=f"Class '{node.name}' has {len(node.body)} members",
                        suggestion="Consider splitting into smaller classes",
                        code_snippet=f"class {node.name}:",
                        rule_id="large_class"
                    )
                    issues.append(issue)
            
            return issues
        
        except Exception as e:
            self.logger.error(f"Error analyzing AST node: {e}")
            return []
    
    def _analyze_with_ai(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze code using AI engine."""
        try:
            if not self.ai_engine:
                return []
            
            # Prepare code for AI analysis
            lines = content.split('\n')
            code_sample = '\n'.join(lines[:50])  # First 50 lines
            
            prompt = f"""
            Analyze the following Python code for potential issues:
            
            File: {file_path}
            
            Code:
            {code_sample}
            
            Look for:
            1. Security vulnerabilities
            2. Performance issues
            3. Code quality problems
            4. Best practice violations
            5. Potential bugs
            
            For each issue found, provide:
            - Title
            - Description
            - Severity (critical, high, medium, low)
            - Category (security, performance, maintainability, readability, best_practices, bug_potential)
            - Suggestion for improvement
            - Line number (if applicable)
            
            Return as JSON array of issues.
            """
            
            response = self.ai_engine.get_ai_response(prompt)
            
            try:
                ai_issues = json.loads(response)
                issues = []
                
                for issue_data in ai_issues:
                    issue = CodeIssue(
                        issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                        file_path=file_path,
                        line_number=issue_data.get('line_number', 1),
                        column=0,
                        severity=ReviewSeverity(issue_data.get('severity', 'low')),
                        category=ReviewCategory(issue_data.get('category', 'best_practices')),
                        title=issue_data.get('title', 'AI Detected Issue'),
                        description=issue_data.get('description', ''),
                        suggestion=issue_data.get('suggestion', ''),
                        code_snippet=lines[issue_data.get('line_number', 1) - 1] if issue_data.get('line_number', 1) <= len(lines) else "",
                        rule_id="ai_analysis"
                    )
                    issues.append(issue)
                
                return issues
            
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(f"AI analysis response not parseable: {e}")
                return []
        
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")
            return []
    
    def calculate_metrics(self, file_path: str) -> CodeMetrics:
        """Calculate code quality metrics for a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            lines_of_code = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Calculate cyclomatic complexity
            complexity = self._calculate_cyclomatic_complexity(content)
            
            # Calculate maintainability index (simplified)
            maintainability = max(0, 100 - (complexity * 2) - (lines_of_code / 10))
            
            # Calculate code duplication (simplified)
            duplication = self._calculate_code_duplication(lines)
            
            # Calculate test coverage (placeholder)
            test_coverage = 0.0  # Would need test runner integration
            
            # Calculate security score
            security_score = self._calculate_security_score(content)
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(content)
            
            return CodeMetrics(
                file_path=file_path,
                lines_of_code=lines_of_code,
                cyclomatic_complexity=complexity,
                maintainability_index=maintainability,
                code_duplication=duplication,
                test_coverage=test_coverage,
                security_score=security_score,
                performance_score=performance_score
            )
        
        except Exception as e:
            self.logger.error(f"Error calculating metrics for {file_path}: {e}")
            return CodeMetrics(
                file_path=file_path,
                lines_of_code=0,
                cyclomatic_complexity=0,
                maintainability_index=0,
                code_duplication=0,
                test_coverage=0,
                security_score=0,
                performance_score=0
            )
    
    def _calculate_cyclomatic_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity."""
        try:
            complexity = 1  # Base complexity
            
            # Count decision points
            decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'except', 'and', 'or']
            
            for keyword in decision_keywords:
                complexity += content.count(f' {keyword} ')
                complexity += content.count(f' {keyword}\n')
            
            return complexity
        
        except Exception as e:
            self.logger.error(f"Error calculating cyclomatic complexity: {e}")
            return 1
    
    def _calculate_code_duplication(self, lines: List[str]) -> float:
        """Calculate code duplication percentage."""
        try:
            # Simple duplication detection based on identical lines
            line_counts = {}
            
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    line_counts[stripped] = line_counts.get(stripped, 0) + 1
            
            duplicated_lines = sum(count - 1 for count in line_counts.values() if count > 1)
            total_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            return (duplicated_lines / total_lines * 100) if total_lines > 0 else 0.0
        
        except Exception as e:
            self.logger.error(f"Error calculating code duplication: {e}")
            return 0.0
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score (0-100)."""
        try:
            score = 100.0
            
            # Deduct points for security issues
            security_issues = [
                'eval(', 'exec(', 'pickle.loads', 'shell=True',
                'password =', 'secret =', 'key ='
            ]
            
            for issue in security_issues:
                if issue in content:
                    score -= 20
            
            return max(0.0, score)
        
        except Exception as e:
            self.logger.error(f"Error calculating security score: {e}")
            return 0.0
    
    def _calculate_performance_score(self, content: str) -> float:
        """Calculate performance score (0-100)."""
        try:
            score = 100.0
            
            # Deduct points for performance issues
            performance_issues = [
                'range(len(', 'import *', '.append(',
                'global ', 'nonlocal '
            ]
            
            for issue in performance_issues:
                if issue in content:
                    score -= 10
            
            return max(0.0, score)
        
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {e}")
            return 0.0
    
    def review_project(self, project_path: str) -> ReviewReport:
        """Review entire project and generate comprehensive report."""
        try:
            self.logger.info(f"Starting project review: {project_path}")
            
            project_path = Path(project_path)
            if not project_path.exists():
                raise FileNotFoundError(f"Project path not found: {project_path}")
            
            # Find all Python files
            python_files = list(project_path.rglob("*.py"))
            
            all_issues = []
            all_metrics = []
            
            # Review each file
            for file_path in python_files:
                issues = self.review_file(str(file_path))
                all_issues.extend(issues)
                
                metrics = self.calculate_metrics(str(file_path))
                all_metrics.append(metrics)
            
            # Generate report
            report = self._generate_review_report(project_path, all_issues, all_metrics)
            
            # Store in history
            self.review_history.append(report)
            
            self.logger.info(f"Project review completed: {len(all_issues)} issues found")
            return report
        
        except Exception as e:
            self.logger.error(f"Error reviewing project: {e}")
            return ReviewReport(
                report_id=f"report_{uuid.uuid4().hex[:8]}",
                project_path=str(project_path),
                review_timestamp=datetime.now(),
                total_files=0,
                total_issues=0,
                issues_by_severity={},
                issues_by_category={},
                code_metrics=[],
                recommendations=[],
                overall_score=0.0
            )
    
    def _generate_review_report(self, project_path: Path, issues: List[CodeIssue], metrics: List[CodeMetrics]) -> ReviewReport:
        """Generate comprehensive review report."""
        try:
            # Count issues by severity
            issues_by_severity = {}
            for severity in ReviewSeverity:
                issues_by_severity[severity.value] = len([i for i in issues if i.severity == severity])
            
            # Count issues by category
            issues_by_category = {}
            for category in ReviewCategory:
                issues_by_category[category.value] = len([i for i in issues if i.category == category])
            
            # Calculate overall score
            total_issues = len(issues)
            critical_issues = issues_by_severity.get(ReviewSeverity.CRITICAL.value, 0)
            high_issues = issues_by_severity.get(ReviewSeverity.HIGH.value, 0)
            medium_issues = issues_by_severity.get(ReviewSeverity.MEDIUM.value, 0)
            low_issues = issues_by_severity.get(ReviewSeverity.LOW.value, 0)
            
            # Weighted score calculation
            weighted_score = (critical_issues * 0) + (high_issues * 0.2) + (medium_issues * 0.5) + (low_issues * 0.8)
            overall_score = max(0, 100 - (weighted_score * 10))
            
            # Generate recommendations
            recommendations = self._generate_recommendations(issues, metrics)
            
            return ReviewReport(
                report_id=f"report_{uuid.uuid4().hex[:8]}",
                project_path=str(project_path),
                review_timestamp=datetime.now(),
                total_files=len(metrics),
                total_issues=total_issues,
                issues_by_severity=issues_by_severity,
                issues_by_category=issues_by_category,
                code_metrics=metrics,
                recommendations=recommendations,
                overall_score=overall_score
            )
        
        except Exception as e:
            self.logger.error(f"Error generating review report: {e}")
            return ReviewReport(
                report_id=f"report_{uuid.uuid4().hex[:8]}",
                project_path=str(project_path),
                review_timestamp=datetime.now(),
                total_files=0,
                total_issues=0,
                issues_by_severity={},
                issues_by_category={},
                code_metrics=[],
                recommendations=[],
                overall_score=0.0
            )
    
    def _generate_recommendations(self, issues: List[CodeIssue], metrics: List[CodeMetrics]) -> List[str]:
        """Generate improvement recommendations based on issues and metrics."""
        try:
            recommendations = []
            
            # Security recommendations
            security_issues = [i for i in issues if i.category == ReviewCategory.SECURITY]
            if security_issues:
                recommendations.append(f"Address {len(security_issues)} security issues, especially critical ones")
            
            # Performance recommendations
            performance_issues = [i for i in issues if i.category == ReviewCategory.PERFORMANCE]
            if performance_issues:
                recommendations.append(f"Optimize {len(performance_issues)} performance issues")
            
            # Maintainability recommendations
            avg_complexity = sum(m.cyclomatic_complexity for m in metrics) / len(metrics) if metrics else 0
            if avg_complexity > 10:
                recommendations.append("Reduce cyclomatic complexity - consider breaking down complex functions")
            
            # Documentation recommendations
            doc_issues = [i for i in issues if i.category == ReviewCategory.DOCUMENTATION]
            if doc_issues:
                recommendations.append(f"Improve documentation - {len(doc_issues)} functions/classes lack docstrings")
            
            # Test coverage recommendations
            avg_coverage = sum(m.test_coverage for m in metrics) / len(metrics) if metrics else 0
            if avg_coverage < 80:
                recommendations.append("Increase test coverage - aim for at least 80%")
            
            return recommendations
        
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    def export_report(self, report: ReviewReport, output_file: str = None) -> bool:
        """Export review report to file."""
        try:
            if not output_file:
                output_file = f"code_review_report_{report.report_id}_{int(report.review_timestamp.timestamp())}.json"
            
            report_data = {
                "report_id": report.report_id,
                "project_path": report.project_path,
                "review_timestamp": report.review_timestamp.isoformat(),
                "total_files": report.total_files,
                "total_issues": report.total_issues,
                "issues_by_severity": report.issues_by_severity,
                "issues_by_category": report.issues_by_category,
                "code_metrics": [
                    {
                        "file_path": m.file_path,
                        "lines_of_code": m.lines_of_code,
                        "cyclomatic_complexity": m.cyclomatic_complexity,
                        "maintainability_index": m.maintainability_index,
                        "code_duplication": m.code_duplication,
                        "test_coverage": m.test_coverage,
                        "security_score": m.security_score,
                        "performance_score": m.performance_score
                    }
                    for m in report.code_metrics
                ],
                "recommendations": report.recommendations,
                "overall_score": report.overall_score
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Review report exported: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            return False
    
    def get_review_history(self) -> List[ReviewReport]:
        """Get review history."""
        return self.review_history
    
    def get_issue_statistics(self) -> Dict[str, Any]:
        """Get overall issue statistics from all reviews."""
        try:
            all_issues = []
            for report in self.review_history:
                # This would need to be stored in the report
                pass
            
            return {
                "total_reviews": len(self.review_history),
                "average_score": sum(r.overall_score for r in self.review_history) / len(self.review_history) if self.review_history else 0,
                "total_files_reviewed": sum(r.total_files for r in self.review_history),
                "total_issues_found": sum(r.total_issues for r in self.review_history)
            }
        
        except Exception as e:
            self.logger.error(f"Error getting issue statistics: {e}")
            return {}
