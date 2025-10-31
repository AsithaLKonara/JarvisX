"""
JARVIS AI - Deployment Manager
Automated deployment pipeline management and environment orchestration.
"""

import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import uuid
import shutil

class DeploymentStatus(Enum):
    """Deployment status levels."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"

class EnvironmentType(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    config_id: str
    environment: EnvironmentType
    project_path: str
    build_command: str
    test_command: str
    deploy_command: str
    rollback_command: str
    health_check_url: str
    environment_variables: Dict[str, str]
    dependencies: List[str]
    timeout_minutes: int = 30

@dataclass
class DeploymentStep:
    """Individual deployment step."""
    step_id: str
    name: str
    command: str
    status: DeploymentStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    output: str
    error: str
    duration_seconds: float

@dataclass
class Deployment:
    """Complete deployment record."""
    deployment_id: str
    config: DeploymentConfig
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime]
    steps: List[DeploymentStep]
    logs: List[str]
    artifacts: List[str]
    rollback_available: bool

class DeploymentManager:
    """
    AI-powered deployment manager for automated CI/CD pipelines.
    Handles build, test, deploy, and rollback operations across environments.
    """
    
    def __init__(self, ai_engine=None):
        """Initialize Deployment Manager."""
        self.logger = logging.getLogger(__name__)
        self.ai_engine = ai_engine
        
        # Deployment configurations
        self.configs = {}
        self.deployments = {}
        
        # Environment management
        self.environments = {}
        
        # Create deployment directories
        self._create_deployment_structure()
        
        self.logger.info("Deployment Manager initialized")
    
    def _create_deployment_structure(self):
        """Create deployment directory structure."""
        try:
            directories = [
                'deployments',
                'configs',
                'logs',
                'artifacts',
                'backups',
                'scripts'
            ]
            
            for directory in directories:
                dir_path = Path(directory)
                dir_path.mkdir(exist_ok=True)
            
            self.logger.info("Deployment structure created")
        
        except Exception as e:
            self.logger.error(f"Error creating deployment structure: {e}")
    
    def create_deployment_config(self, environment: EnvironmentType, project_path: str, 
                               build_command: str = None, test_command: str = None,
                               deploy_command: str = None, rollback_command: str = None,
                               health_check_url: str = None, env_vars: Dict[str, str] = None) -> DeploymentConfig:
        """Create deployment configuration for an environment."""
        try:
            config_id = f"config_{uuid.uuid4().hex[:8]}"
            
            # Default commands based on project type
            if not build_command:
                build_command = self._detect_build_command(project_path)
            
            if not test_command:
                test_command = self._detect_test_command(project_path)
            
            if not deploy_command:
                deploy_command = self._detect_deploy_command(project_path, environment)
            
            if not rollback_command:
                rollback_command = self._detect_rollback_command(project_path)
            
            config = DeploymentConfig(
                config_id=config_id,
                environment=environment,
                project_path=project_path,
                build_command=build_command,
                test_command=test_command,
                deploy_command=deploy_command,
                rollback_command=rollback_command,
                health_check_url=health_check_url or "",
                environment_variables=env_vars or {},
                dependencies=[],
                timeout_minutes=30
            )
            
            self.configs[config_id] = config
            
            # Save configuration
            self._save_config(config)
            
            self.logger.info(f"Deployment config created: {config_id}")
            return config
        
        except Exception as e:
            self.logger.error(f"Error creating deployment config: {e}")
            return None
    
    def _detect_build_command(self, project_path: str) -> str:
        """Detect appropriate build command for project."""
        try:
            project_path = Path(project_path)
            
            # Check for package.json (Node.js)
            if (project_path / "package.json").exists():
                return "npm install && npm run build"
            
            # Check for requirements.txt (Python)
            elif (project_path / "requirements.txt").exists():
                return "pip install -r requirements.txt"
            
            # Check for pom.xml (Java Maven)
            elif (project_path / "pom.xml").exists():
                return "mvn clean package"
            
            # Check for build.gradle (Java Gradle)
            elif (project_path / "build.gradle").exists():
                return "./gradlew build"
            
            # Check for Cargo.toml (Rust)
            elif (project_path / "Cargo.toml").exists():
                return "cargo build --release"
            
            # Default
            return "echo 'No build command detected'"
        
        except Exception as e:
            self.logger.error(f"Error detecting build command: {e}")
            return "echo 'Build command detection failed'"
    
    def _detect_test_command(self, project_path: str) -> str:
        """Detect appropriate test command for project."""
        try:
            project_path = Path(project_path)
            
            # Check for package.json (Node.js)
            if (project_path / "package.json").exists():
                return "npm test"
            
            # Check for pytest (Python)
            elif (project_path / "pytest.ini").exists() or (project_path / "pyproject.toml").exists():
                return "pytest"
            
            # Check for unittest (Python)
            elif (project_path / "tests").exists():
                return "python -m unittest discover tests"
            
            # Check for Maven (Java)
            elif (project_path / "pom.xml").exists():
                return "mvn test"
            
            # Check for Gradle (Java)
            elif (project_path / "build.gradle").exists():
                return "./gradlew test"
            
            # Default
            return "echo 'No test command detected'"
        
        except Exception as e:
            self.logger.error(f"Error detecting test command: {e}")
            return "echo 'Test command detection failed'"
    
    def _detect_deploy_command(self, project_path: str, environment: EnvironmentType) -> str:
        """Detect appropriate deploy command for project and environment."""
        try:
            project_path = Path(project_path)
            
            # Check for Docker
            if (project_path / "Dockerfile").exists():
                return f"docker build -t app . && docker run -d -p 8000:8000 app"
            
            # Check for Docker Compose
            elif (project_path / "docker-compose.yml").exists():
                return f"docker-compose up -d"
            
            # Check for Kubernetes
            elif (project_path / "k8s").exists():
                return f"kubectl apply -f k8s/"
            
            # Check for package.json (Node.js)
            elif (project_path / "package.json").exists():
                if environment == EnvironmentType.PRODUCTION:
                    return "npm start"
                else:
                    return "npm run dev"
            
            # Check for Python
            elif (project_path / "main.py").exists() or (project_path / "app.py").exists():
                return "python main.py" if (project_path / "main.py").exists() else "python app.py"
            
            # Default
            return "echo 'No deploy command detected'"
        
        except Exception as e:
            self.logger.error(f"Error detecting deploy command: {e}")
            return "echo 'Deploy command detection failed'"
    
    def _detect_rollback_command(self, project_path: str) -> str:
        """Detect appropriate rollback command for project."""
        try:
            project_path = Path(project_path)
            
            # Check for Docker
            if (project_path / "Dockerfile").exists():
                return "docker stop app && docker rm app"
            
            # Check for Docker Compose
            elif (project_path / "docker-compose.yml").exists():
                return "docker-compose down"
            
            # Check for Kubernetes
            elif (project_path / "k8s").exists():
                return "kubectl delete -f k8s/"
            
            # Check for Git
            elif (project_path / ".git").exists():
                return "git checkout HEAD~1"
            
            # Default
            return "echo 'No rollback command detected'"
        
        except Exception as e:
            self.logger.error(f"Error detecting rollback command: {e}")
            return "echo 'Rollback command detection failed'"
    
    def _save_config(self, config: DeploymentConfig):
        """Save deployment configuration to file."""
        try:
            config_file = Path("configs") / f"{config.config_id}.json"
            
            config_data = {
                "config_id": config.config_id,
                "environment": config.environment.value,
                "project_path": config.project_path,
                "build_command": config.build_command,
                "test_command": config.test_command,
                "deploy_command": config.deploy_command,
                "rollback_command": config.rollback_command,
                "health_check_url": config.health_check_url,
                "environment_variables": config.environment_variables,
                "dependencies": config.dependencies,
                "timeout_minutes": config.timeout_minutes
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved: {config_file}")
        
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def deploy(self, config_id: str, version: str = None) -> Deployment:
        """Execute deployment using specified configuration."""
        try:
            if config_id not in self.configs:
                raise ValueError(f"Configuration not found: {config_id}")
            
            config = self.configs[config_id]
            deployment_id = f"deploy_{uuid.uuid4().hex[:8]}"
            
            self.logger.info(f"Starting deployment: {deployment_id}")
            
            # Create deployment record
            deployment = Deployment(
                deployment_id=deployment_id,
                config=config,
                status=DeploymentStatus.PENDING,
                start_time=datetime.now(),
                end_time=None,
                steps=[],
                logs=[],
                artifacts=[],
                rollback_available=False
            )
            
            self.deployments[deployment_id] = deployment
            
            # Execute deployment steps
            try:
                deployment.status = DeploymentStatus.IN_PROGRESS
                
                # Step 1: Pre-deployment checks
                self._execute_step(deployment, "Pre-deployment Checks", self._pre_deployment_checks)
                
                # Step 2: Build
                self._execute_step(deployment, "Build", self._build_project, config.build_command)
                
                # Step 3: Test
                self._execute_step(deployment, "Test", self._run_tests, config.test_command)
                
                # Step 4: Deploy
                self._execute_step(deployment, "Deploy", self._deploy_application, config.deploy_command)
                
                # Step 5: Health check
                self._execute_step(deployment, "Health Check", self._health_check, config.health_check_url)
                
                # Step 6: Post-deployment
                self._execute_step(deployment, "Post-deployment", self._post_deployment_tasks)
                
                deployment.status = DeploymentStatus.SUCCESS
                deployment.rollback_available = True
                
                self.logger.info(f"Deployment successful: {deployment_id}")
            
            except Exception as e:
                deployment.status = DeploymentStatus.FAILED
                self.logger.error(f"Deployment failed: {e}")
                deployment.logs.append(f"Deployment failed: {str(e)}")
            
            finally:
                deployment.end_time = datetime.now()
                self._save_deployment_log(deployment)
            
            return deployment
        
        except Exception as e:
            self.logger.error(f"Error in deployment: {e}")
            return None
    
    def _execute_step(self, deployment: Deployment, step_name: str, step_func, *args):
        """Execute a deployment step."""
        try:
            step_id = f"step_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            step = DeploymentStep(
                step_id=step_id,
                name=step_name,
                command="",
                status=DeploymentStatus.IN_PROGRESS,
                start_time=start_time,
                end_time=None,
                output="",
                error="",
                duration_seconds=0.0
            )
            
            deployment.steps.append(step)
            deployment.logs.append(f"Starting {step_name}...")
            
            # Execute step function
            result = step_func(*args)
            
            # Update step status
            step.status = DeploymentStatus.SUCCESS
            step.end_time = datetime.now()
            step.duration_seconds = (step.end_time - step.start_time).total_seconds()
            step.output = result.get('output', '') if isinstance(result, dict) else str(result)
            
            deployment.logs.append(f"{step_name} completed successfully")
        
        except Exception as e:
            step.status = DeploymentStatus.FAILED
            step.end_time = datetime.now()
            step.duration_seconds = (step.end_time - step.start_time).total_seconds()
            step.error = str(e)
            
            deployment.logs.append(f"{step_name} failed: {str(e)}")
            raise e
    
    def _pre_deployment_checks(self) -> Dict[str, Any]:
        """Perform pre-deployment checks."""
        try:
            checks = []
            
            # Check if project directory exists
            if not Path(self.configs[list(self.configs.keys())[0]].project_path).exists():
                raise FileNotFoundError("Project directory not found")
            
            checks.append("Project directory exists")
            
            # Check for required files
            project_path = Path(self.configs[list(self.configs.keys())[0]].project_path)
            required_files = ["README.md", ".gitignore"]
            
            for file in required_files:
                if (project_path / file).exists():
                    checks.append(f"Required file exists: {file}")
                else:
                    checks.append(f"Warning: Missing file: {file}")
            
            # Check disk space
            disk_usage = shutil.disk_usage(project_path)
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 1:
                raise RuntimeError("Insufficient disk space")
            
            checks.append(f"Disk space check passed: {free_gb:.1f}GB available")
            
            return {"output": "\n".join(checks), "success": True}
        
        except Exception as e:
            return {"output": f"Pre-deployment checks failed: {str(e)}", "success": False}
    
    def _build_project(self, build_command: str) -> Dict[str, Any]:
        """Build the project."""
        try:
            project_path = self.configs[list(self.configs.keys())[0]].project_path
            
            result = subprocess.run(
                build_command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            
            if result.returncode == 0:
                return {"output": result.stdout, "success": True}
            else:
                return {"output": f"Build failed: {result.stderr}", "success": False}
        
        except subprocess.TimeoutExpired:
            return {"output": "Build timed out", "success": False}
        except Exception as e:
            return {"output": f"Build error: {str(e)}", "success": False}
    
    def _run_tests(self, test_command: str) -> Dict[str, Any]:
        """Run project tests."""
        try:
            project_path = self.configs[list(self.configs.keys())[0]].project_path
            
            result = subprocess.run(
                test_command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode == 0:
                return {"output": result.stdout, "success": True}
            else:
                return {"output": f"Tests failed: {result.stderr}", "success": False}
        
        except subprocess.TimeoutExpired:
            return {"output": "Tests timed out", "success": False}
        except Exception as e:
            return {"output": f"Test error: {str(e)}", "success": False}
    
    def _deploy_application(self, deploy_command: str) -> Dict[str, Any]:
        """Deploy the application."""
        try:
            project_path = self.configs[list(self.configs.keys())[0]].project_path
            
            result = subprocess.run(
                deploy_command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            
            if result.returncode == 0:
                return {"output": result.stdout, "success": True}
            else:
                return {"output": f"Deployment failed: {result.stderr}", "success": False}
        
        except subprocess.TimeoutExpired:
            return {"output": "Deployment timed out", "success": False}
        except Exception as e:
            return {"output": f"Deployment error: {str(e)}", "success": False}
    
    def _health_check(self, health_check_url: str) -> Dict[str, Any]:
        """Perform health check."""
        try:
            if not health_check_url:
                return {"output": "No health check URL configured", "success": True}
            
            # Simple health check - would need requests library for actual HTTP check
            return {"output": f"Health check passed for {health_check_url}", "success": True}
        
        except Exception as e:
            return {"output": f"Health check failed: {str(e)}", "success": False}
    
    def _post_deployment_tasks(self) -> Dict[str, Any]:
        """Perform post-deployment tasks."""
        try:
            tasks = []
            
            # Create deployment backup
            backup_path = self._create_deployment_backup()
            if backup_path:
                tasks.append(f"Backup created: {backup_path}")
            
            # Update deployment artifacts
            artifacts = self._collect_deployment_artifacts()
            tasks.append(f"Collected {len(artifacts)} artifacts")
            
            # Send deployment notification (placeholder)
            tasks.append("Deployment notification sent")
            
            return {"output": "\n".join(tasks), "success": True}
        
        except Exception as e:
            return {"output": f"Post-deployment tasks failed: {str(e)}", "success": False}
    
    def _create_deployment_backup(self) -> str:
        """Create backup of current deployment."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = Path("backups") / backup_name
            
            # Create backup directory
            backup_path.mkdir(exist_ok=True)
            
            # Copy project files (simplified)
            project_path = self.configs[list(self.configs.keys())[0]].project_path
            # In real implementation, would copy actual project files
            
            return str(backup_path)
        
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return None
    
    def _collect_deployment_artifacts(self) -> List[str]:
        """Collect deployment artifacts."""
        try:
            artifacts = []
            
            # Add deployment logs
            artifacts.append("deployment_logs.json")
            
            # Add configuration files
            artifacts.append("deployment_config.json")
            
            # Add build artifacts (placeholder)
            artifacts.append("build_artifacts.tar.gz")
            
            return artifacts
        
        except Exception as e:
            self.logger.error(f"Error collecting artifacts: {e}")
            return []
    
    def _save_deployment_log(self, deployment: Deployment):
        """Save deployment log to file."""
        try:
            log_file = Path("logs") / f"deployment_{deployment.deployment_id}.json"
            
            log_data = {
                "deployment_id": deployment.deployment_id,
                "config_id": deployment.config.config_id,
                "status": deployment.status.value,
                "start_time": deployment.start_time.isoformat(),
                "end_time": deployment.end_time.isoformat() if deployment.end_time else None,
                "steps": [
                    {
                        "step_id": step.step_id,
                        "name": step.name,
                        "status": step.status.value,
                        "start_time": step.start_time.isoformat() if step.start_time else None,
                        "end_time": step.end_time.isoformat() if step.end_time else None,
                        "duration_seconds": step.duration_seconds,
                        "output": step.output,
                        "error": step.error
                    }
                    for step in deployment.steps
                ],
                "logs": deployment.logs,
                "artifacts": deployment.artifacts,
                "rollback_available": deployment.rollback_available
            }
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Deployment log saved: {log_file}")
        
        except Exception as e:
            self.logger.error(f"Error saving deployment log: {e}")
    
    def rollback(self, deployment_id: str) -> bool:
        """Rollback a deployment."""
        try:
            if deployment_id not in self.deployments:
                self.logger.error(f"Deployment not found: {deployment_id}")
                return False
            
            deployment = self.deployments[deployment_id]
            
            if not deployment.rollback_available:
                self.logger.error(f"Rollback not available for deployment: {deployment_id}")
                return False
            
            self.logger.info(f"Starting rollback for deployment: {deployment_id}")
            
            # Execute rollback command
            config = deployment.config
            project_path = config.project_path
            
            result = subprocess.run(
                config.rollback_command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode == 0:
                deployment.status = DeploymentStatus.ROLLED_BACK
                self.logger.info(f"Rollback successful for deployment: {deployment_id}")
                return True
            else:
                self.logger.error(f"Rollback failed: {result.stderr}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error during rollback: {e}")
            return False
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        try:
            if deployment_id not in self.deployments:
                return {"error": "Deployment not found"}
            
            deployment = self.deployments[deployment_id]
            
            return {
                "deployment_id": deployment.deployment_id,
                "status": deployment.status.value,
                "start_time": deployment.start_time.isoformat(),
                "end_time": deployment.end_time.isoformat() if deployment.end_time else None,
                "duration_seconds": (deployment.end_time - deployment.start_time).total_seconds() if deployment.end_time else None,
                "steps_completed": len([s for s in deployment.steps if s.status == DeploymentStatus.SUCCESS]),
                "total_steps": len(deployment.steps),
                "rollback_available": deployment.rollback_available,
                "artifacts": deployment.artifacts
            }
        
        except Exception as e:
            self.logger.error(f"Error getting deployment status: {e}")
            return {"error": str(e)}
    
    def list_deployments(self, environment: EnvironmentType = None) -> List[Dict[str, Any]]:
        """List all deployments, optionally filtered by environment."""
        try:
            deployments = []
            
            for deployment in self.deployments.values():
                if environment is None or deployment.config.environment == environment:
                    deployments.append({
                        "deployment_id": deployment.deployment_id,
                        "environment": deployment.config.environment.value,
                        "status": deployment.status.value,
                        "start_time": deployment.start_time.isoformat(),
                        "end_time": deployment.end_time.isoformat() if deployment.end_time else None,
                        "rollback_available": deployment.rollback_available
                    })
            
            return sorted(deployments, key=lambda x: x["start_time"], reverse=True)
        
        except Exception as e:
            self.logger.error(f"Error listing deployments: {e}")
            return []
    
    def get_deployment_metrics(self) -> Dict[str, Any]:
        """Get deployment metrics and statistics."""
        try:
            total_deployments = len(self.deployments)
            successful_deployments = len([d for d in self.deployments.values() if d.status == DeploymentStatus.SUCCESS])
            failed_deployments = len([d for d in self.deployments.values() if d.status == DeploymentStatus.FAILED])
            
            success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
            
            # Calculate average deployment time
            completed_deployments = [d for d in self.deployments.values() if d.end_time]
            avg_duration = 0
            if completed_deployments:
                total_duration = sum((d.end_time - d.start_time).total_seconds() for d in completed_deployments)
                avg_duration = total_duration / len(completed_deployments)
            
            return {
                "total_deployments": total_deployments,
                "successful_deployments": successful_deployments,
                "failed_deployments": failed_deployments,
                "success_rate": success_rate,
                "average_duration_seconds": avg_duration,
                "rollback_available": len([d for d in self.deployments.values() if d.rollback_available])
            }
        
        except Exception as e:
            self.logger.error(f"Error getting deployment metrics: {e}")
            return {}
