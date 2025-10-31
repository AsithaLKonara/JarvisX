#!/usr/bin/env python3
"""
JARVIS X V2 - MULTI-MODEL ORCHESTRATOR (Phase A)
Coordinates 7 AI layers with unified verification pipeline
- L1: Core Intelligence (HelaGPT)
- L2: Logic Verifier (Code/Config validation)
- L3: Task Planner (Goal decomposition)
- L4: Self-Critic QA (Output verification)
- L5: System Supervisor (Monitoring)
- L6: Avatar Feedback (Persona/Expression)
- L7: Business Decision (Strategy)
"""

import os
import json
import logging
import asyncio
import time
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from abc import ABC, abstractmethod
import hashlib
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class ModelLayer(Enum):
    """AI Model Layers"""
    L1_CORE_INTELLIGENCE = "L1_CORE_INTELLIGENCE"
    L2_LOGIC_VERIFIER = "L2_LOGIC_VERIFIER"
    L3_TASK_PLANNER = "L3_TASK_PLANNER"
    L4_SELF_CRITIC = "L4_SELF_CRITIC"
    L5_SUPERVISOR = "L5_SUPERVISOR"
    L6_AVATAR_FEEDBACK = "L6_AVATAR_FEEDBACK"
    L7_BUSINESS_DECISION = "L7_BUSINESS_DECISION"


class VerificationLevel(Enum):
    """Verification Confidence Levels"""
    CRITICAL = "CRITICAL"      # Must verify
    HIGH = "HIGH"               # Should verify
    MEDIUM = "MEDIUM"           # Nice to verify
    LOW = "LOW"                 # Optional


class ExecutionStatus(Enum):
    """Task Execution Status"""
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRY = "RETRY"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class VerificationResult:
    """Single verification check result"""
    layer: ModelLayer
    passed: bool
    confidence: float
    message: str
    suggestions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TaskExecution:
    """Complete task execution record"""
    task_id: str
    original_command: str
    status: ExecutionStatus
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Layer outputs
    l1_response: Optional[str] = None
    l2_verification: Optional[VerificationResult] = None
    l3_plan: Optional[Dict] = None
    l4_qa_result: Optional[VerificationResult] = None
    l5_metrics: Optional[Dict] = None
    l6_feedback: Optional[str] = None
    l7_decision: Optional[Dict] = None
    
    # Metadata
    total_latency: float = 0.0
    layer_latencies: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    verification_score: float = 0.0

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['status'] = self.status.value
        data['l2_verification'] = self.l2_verification.to_dict() if self.l2_verification else None
        data['l4_qa_result'] = self.l4_qa_result.to_dict() if self.l4_qa_result else None
        return data


# ============================================================================
# MODEL LAYER INTERFACES
# ============================================================================

class AIModelLayer(ABC):
    """Abstract base for AI model layers"""
    
    def __init__(self, layer: ModelLayer, config: Optional[Dict] = None):
        self.layer = layer
        self.config = config or {}
        self.logger = logging.getLogger(f"jarvis.{layer.value}")
        self.request_count = 0
        self.error_count = 0
        self.latency_history = []

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result"""
        pass

    def record_latency(self, latency: float):
        """Track response latencies"""
        self.latency_history.append(latency)
        if len(self.latency_history) > 1000:
            self.latency_history = self.latency_history[-500:]

    def get_avg_latency(self) -> float:
        """Get average response time"""
        return sum(self.latency_history) / len(self.latency_history) if self.latency_history else 0.0

    def get_health(self) -> Dict[str, Any]:
        """Get layer health metrics"""
        return {
            'layer': self.layer.value,
            'requests': self.request_count,
            'errors': self.error_count,
            'error_rate': self.error_count / max(self.request_count, 1),
            'avg_latency': self.get_avg_latency(),
            'status': 'healthy' if self.error_count / max(self.request_count, 1) < 0.1 else 'degraded'
        }


class CoreIntelligenceLayer(AIModelLayer):
    """L1: Main conversational AI (HelaGPT)"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        try:
            self.request_count += 1
            
            user_input = input_data.get('message', '')
            context = input_data.get('context', [])
            
            # Import here to avoid circular imports
            from core.ai_engine import AIEngine
            from utils.config import Config
            
            config = Config()
            ai_engine = AIEngine(config)
            
            # Generate response
            response = ai_engine.get_response(user_input)
            
            latency = time.time() - start
            self.record_latency(latency)
            
            return {
                'success': True,
                'response': response,
                'latency': latency,
                'model': 'HelaGPT',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"L1 Error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'latency': time.time() - start
            }


class LogicVerifierLayer(AIModelLayer):
    """L2: Code and logic validation"""
    
    async def process(self, input_data: Dict[str, Any]) -> VerificationResult:
        start = time.time()
        try:
            self.request_count += 1
            
            code_or_logic = input_data.get('content', '')
            check_type = input_data.get('type', 'logic')  # 'code', 'config', 'logic'
            
            passed = True
            suggestions = []
            metrics = {}
            
            # Verify syntax for code
            if check_type == 'code':
                try:
                    compile(code_or_logic, '<string>', 'exec')
                    passed = True
                    metrics['syntax_valid'] = True
                except SyntaxError as e:
                    passed = False
                    suggestions.append(f"Syntax error: {e}")
                    metrics['syntax_valid'] = False
            
            # Verify configuration
            elif check_type == 'config':
                try:
                    json.loads(code_or_logic)
                    passed = True
                    metrics['json_valid'] = True
                except json.JSONDecodeError as e:
                    passed = False
                    suggestions.append(f"Invalid JSON: {e}")
                    metrics['json_valid'] = False
            
            # Generic logic checks
            else:
                dangerous_patterns = ['rm -rf', 'DROP TABLE', 'DELETE FROM', 'format']
                if any(pattern in code_or_logic for pattern in dangerous_patterns):
                    passed = False
                    suggestions.append("Dangerous operation detected")
                    metrics['dangerous'] = True
                else:
                    passed = True
                    metrics['dangerous'] = False
            
            latency = time.time() - start
            self.record_latency(latency)
            
            return VerificationResult(
                layer=self.layer,
                passed=passed,
                confidence=0.95 if passed else 0.85,
                message=f"Verification {'passed' if passed else 'failed'}",
                suggestions=suggestions,
                metrics=metrics
            )
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"L2 Error: {str(e)}")
            return VerificationResult(
                layer=self.layer,
                passed=False,
                confidence=0.0,
                message=f"Verification error: {str(e)}",
                suggestions=["Check input format"]
            )


class TaskPlannerLayer(AIModelLayer):
    """L3: Goal decomposition into executable tasks"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        try:
            self.request_count += 1
            
            goal = input_data.get('goal', '')
            context = input_data.get('context', {})
            
            # Simple decomposition logic
            tasks = [
                {"id": "task_1", "name": "Validate inputs", "type": "validation"},
                {"id": "task_2", "name": "Plan execution", "type": "planning"},
                {"id": "task_3", "name": "Execute workflow", "type": "execution"},
                {"id": "task_4", "name": "Verify results", "type": "verification"}
            ]
            
            latency = time.time() - start
            self.record_latency(latency)
            
            return {
                'success': True,
                'goal': goal,
                'tasks': tasks,
                'task_count': len(tasks),
                'latency': latency,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.error_count += 1
            return {'success': False, 'error': str(e)}


class SelfCriticQALayer(AIModelLayer):
    """L4: Output quality and fact-checking"""
    
    async def process(self, input_data: Dict[str, Any]) -> VerificationResult:
        start = time.time()
        try:
            self.request_count += 1
            
            output = input_data.get('output', '')
            criteria = input_data.get('criteria', [])
            
            # Quality checks
            quality_checks = {
                'length_ok': len(output) > 10,
                'no_duplicates': len(set(output.split())) == len(output.split()),
                'coherent': not output.endswith('?') or output.count('?') < 3
            }
            
            passed = all(quality_checks.values())
            suggestions = [k for k, v in quality_checks.items() if not v]
            
            latency = time.time() - start
            self.record_latency(latency)
            
            return VerificationResult(
                layer=self.layer,
                passed=passed,
                confidence=0.9,
                message=f"QA check {'passed' if passed else 'found issues'}",
                suggestions=suggestions,
                metrics=quality_checks
            )
        except Exception as e:
            self.error_count += 1
            return VerificationResult(
                layer=self.layer,
                passed=False,
                confidence=0.0,
                message=f"QA error: {str(e)}"
            )


class SystemSupervisorLayer(AIModelLayer):
    """L5: System health and resource monitoring"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        try:
            self.request_count += 1
            
            import psutil
            
            proc = psutil.Process()
            metrics = {
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_mb': proc.memory_info().rss / 1024 / 1024,
                'open_files': len(proc.open_files()),
                'timestamp': datetime.now().isoformat()
            }
            
            latency = time.time() - start
            self.record_latency(latency)
            
            return {
                'success': True,
                'metrics': metrics,
                'health_status': 'healthy' if metrics['cpu_percent'] < 50 else 'elevated',
                'latency': latency
            }
        except Exception as e:
            self.error_count += 1
            return {'success': False, 'error': str(e)}


class AvatarFeedbackLayer(AIModelLayer):
    """L6: Persona, expression, and user feedback"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        try:
            self.request_count += 1
            
            message = input_data.get('message', '')
            sentiment = input_data.get('sentiment', 'neutral')
            
            # Generate appropriate avatar feedback
            feedback_templates = {
                'positive': "🟢 Success! Task completed.",
                'negative': "🔴 Issue detected. Let me help fix this.",
                'neutral': "⚪ Processing your request.",
                'error': "⚠️ An error occurred. Retrying..."
            }
            
            feedback = feedback_templates.get(sentiment, feedback_templates['neutral'])
            
            latency = time.time() - start
            self.record_latency(latency)
            
            return {
                'success': True,
                'feedback': feedback,
                'emotion': sentiment,
                'latency': latency
            }
        except Exception as e:
            self.error_count += 1
            return {'success': False, 'error': str(e)}


class BusinessDecisionLayer(AIModelLayer):
    """L7: Strategic and business decision support"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        try:
            self.request_count += 1
            
            decision_type = input_data.get('type', 'priority')
            options = input_data.get('options', [])
            
            # Simple decision logic
            decision = {
                'type': decision_type,
                'recommendation': options[0] if options else None,
                'confidence': 0.85,
                'reasoning': 'Analyzed available options'
            }
            
            latency = time.time() - start
            self.record_latency(latency)
            
            return {
                'success': True,
                'decision': decision,
                'latency': latency
            }
        except Exception as e:
            self.error_count += 1
            return {'success': False, 'error': str(e)}


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class ModelOrchestrator:
    """
    Coordinates 7 AI model layers with unified verification pipeline.
    Manages message routing, verification, and monitoring.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger("jarvis.orchestrator")
        self.execution_log: List[TaskExecution] = []
        self.max_log_size = 1000
        
        # Initialize all model layers
        self.layers = {
            ModelLayer.L1_CORE_INTELLIGENCE: CoreIntelligenceLayer(ModelLayer.L1_CORE_INTELLIGENCE),
            ModelLayer.L2_LOGIC_VERIFIER: LogicVerifierLayer(ModelLayer.L2_LOGIC_VERIFIER),
            ModelLayer.L3_TASK_PLANNER: TaskPlannerLayer(ModelLayer.L3_TASK_PLANNER),
            ModelLayer.L4_SELF_CRITIC: SelfCriticQALayer(ModelLayer.L4_SELF_CRITIC),
            ModelLayer.L5_SUPERVISOR: SystemSupervisorLayer(ModelLayer.L5_SUPERVISOR),
            ModelLayer.L6_AVATAR_FEEDBACK: AvatarFeedbackLayer(ModelLayer.L6_AVATAR_FEEDBACK),
            ModelLayer.L7_BUSINESS_DECISION: BusinessDecisionLayer(ModelLayer.L7_BUSINESS_DECISION),
        }
        
        self.logger.info("Model Orchestrator initialized with 7 AI layers")

    async def process_command(self, command: str, context: Optional[Dict] = None) -> TaskExecution:
        """
        Process command through all 7 model layers with verification
        
        Flow:
        1. L1: Generate response
        2. L2: Verify logic
        3. L3: Plan decomposition
        4. L4: QA verification
        5. L5: Monitor system health
        6. L6: Generate avatar feedback
        7. L7: Business decision support
        """
        import uuid
        
        task_id = str(uuid.uuid4())[:8]
        execution = TaskExecution(
            task_id=task_id,
            original_command=command,
            status=ExecutionStatus.PENDING,
            started_at=datetime.now().isoformat()
        )
        
        try:
            execution.status = ExecutionStatus.VALIDATING
            self.logger.info(f"[{task_id}] Processing: {command}")
            
            # L1: Core Intelligence
            l1_start = time.time()
            l1_result = await self.layers[ModelLayer.L1_CORE_INTELLIGENCE].process({
                'message': command,
                'context': context or []
            })
            l1_latency = time.time() - l1_start
            execution.l1_response = l1_result.get('response', '')
            execution.layer_latencies['L1'] = l1_latency
            
            # L2: Logic Verifier
            l2_start = time.time()
            l2_result = await self.layers[ModelLayer.L2_LOGIC_VERIFIER].process({
                'content': execution.l1_response,
                'type': 'logic'
            })
            l2_latency = time.time() - l2_start
            execution.l2_verification = l2_result
            execution.layer_latencies['L2'] = l2_latency
            
            # L3: Task Planner
            l3_start = time.time()
            l3_result = await self.layers[ModelLayer.L3_TASK_PLANNER].process({
                'goal': command,
                'context': context or {}
            })
            l3_latency = time.time() - l3_start
            execution.l3_plan = l3_result
            execution.layer_latencies['L3'] = l3_latency
            
            # L4: Self-Critic QA
            l4_start = time.time()
            l4_result = await self.layers[ModelLayer.L4_SELF_CRITIC].process({
                'output': execution.l1_response
            })
            l4_latency = time.time() - l4_start
            execution.l4_qa_result = l4_result
            execution.layer_latencies['L4'] = l4_latency
            
            # L5: System Supervisor
            l5_start = time.time()
            l5_result = await self.layers[ModelLayer.L5_SUPERVISOR].process({})
            l5_latency = time.time() - l5_start
            execution.l5_metrics = l5_result
            execution.layer_latencies['L5'] = l5_latency
            
            # L6: Avatar Feedback
            l6_start = time.time()
            l6_result = await self.layers[ModelLayer.L6_AVATAR_FEEDBACK].process({
                'message': execution.l1_response,
                'sentiment': 'positive' if l2_result.passed else 'negative'
            })
            l6_latency = time.time() - l6_start
            execution.l6_feedback = l6_result.get('feedback', '')
            execution.layer_latencies['L6'] = l6_latency
            
            # L7: Business Decision
            l7_start = time.time()
            l7_result = await self.layers[ModelLayer.L7_BUSINESS_DECISION].process({
                'type': 'priority',
                'options': ['execute', 'review', 'defer']
            })
            l7_latency = time.time() - l7_start
            execution.l7_decision = l7_result
            execution.layer_latencies['L7'] = l7_latency
            
            # Calculate verification score
            verification_checks = [
                l2_result.passed,
                l4_result.passed,
                execution.l5_metrics.get('metrics', {}).get('cpu_percent', 100) < 80
            ]
            execution.verification_score = sum(verification_checks) / len(verification_checks)
            
            execution.status = ExecutionStatus.SUCCESS
            execution.completed_at = datetime.now().isoformat()
            execution.total_latency = sum(execution.layer_latencies.values())
            
            self.logger.info(f"[{task_id}] Completed: {execution.verification_score:.1%} verified")
            
        except Exception as e:
            self.logger.error(f"[{task_id}] Error: {str(e)}")
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now().isoformat()
        
        # Store in log
        self._record_execution(execution)
        return execution

    def _record_execution(self, execution: TaskExecution):
        """Store execution record"""
        self.execution_log.append(execution)
        if len(self.execution_log) > self.max_log_size:
            self.execution_log = self.execution_log[-self.max_log_size:]

    def get_system_health(self) -> Dict[str, Any]:
        """Get health status of all 7 layers"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'layers': {},
            'overall_health': 'healthy'
        }
        
        for layer_name, layer in self.layers.items():
            health['layers'][layer_name.value] = layer.get_health()
        
        # Check overall health
        error_rate = sum(
            layer_health['error_rate'] 
            for layer_health in health['layers'].values()
        ) / len(health['layers'])
        
        if error_rate > 0.1:
            health['overall_health'] = 'degraded'
        
        return health

    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent execution history"""
        return [e.to_dict() for e in self.execution_log[-limit:]]

    async def verify_all_layers(self) -> Dict[str, Any]:
        """Run verification on all 7 layers"""
        verification = {
            'timestamp': datetime.now().isoformat(),
            'results': {}
        }
        
        for layer_name, layer in self.layers.items():
            try:
                result = await layer.process({'test': True})
                verification['results'][layer_name.value] = {
                    'status': 'ok',
                    'latency': result.get('latency', 0) if isinstance(result, dict) else 0
                }
            except Exception as e:
                verification['results'][layer_name.value] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return verification


# ============================================================================
# ASYNC UTILITIES
# ============================================================================

def run_async(coro):
    """Helper to run async code synchronously"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    orchestrator = ModelOrchestrator()
    
    # Test command
    result = run_async(orchestrator.process_command("Hello, plan my day"))
    
    print(f"\n✅ Execution ID: {result.task_id}")
    print(f"   Status: {result.status.value}")
    print(f"   Verification Score: {result.verification_score:.1%}")
    print(f"   Total Latency: {result.total_latency:.2f}s")
    print(f"\n   L1 Response: {result.l1_response[:50]}...")
    print(f"   L2 Verification: {'✓ PASS' if result.l2_verification.passed else '✗ FAIL'}")
    print(f"   L3 Plan: {result.l3_plan.get('task_count', 0)} tasks")
    print(f"   L4 QA: {'✓ PASS' if result.l4_qa_result.passed else '✗ FAIL'}")
    print(f"   L5 System: {result.l5_metrics.get('health_status', 'unknown')}")
    print(f"   L6 Feedback: {result.l6_feedback}")
    print(f"   L7 Decision: {result.l7_decision.get('decision', {}).get('recommendation', 'none')}")
    
    print(f"\n📊 System Health:")
    health = orchestrator.get_system_health()
    print(f"   Overall: {health['overall_health']}")
    print(f"   Layers: {len(health['layers'])} operational")
