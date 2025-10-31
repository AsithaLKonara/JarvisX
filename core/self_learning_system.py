#!/usr/bin/env python3
"""
JARVIS X V2 - PHASE C: SELF-LEARNING SYSTEM
Continuous feedback collection, pattern learning, and autonomous improvement
- Feedback collection from execution results
- Pattern recognition from failures
- Confidence score optimization
- Adaptive model selection
- Learning analytics & reporting
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback collected"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    MANUAL = "manual"


@dataclass
class ExecutionFeedback:
    """Feedback record from single execution"""
    execution_id: str
    timestamp: str
    original_command: str
    feedback_type: FeedbackType
    
    # Scores
    l1_score: float  # L1 Intelligence
    l2_score: float  # L2 Logic Verifier
    l3_score: float  # L3 Task Planner
    l4_score: float  # L4 Self-Critic
    l5_score: float  # L5 Supervisor
    
    overall_score: float
    user_satisfaction: Optional[float] = None  # 1-5 scale
    
    # Pattern info
    command_category: str = ""
    response_quality: str = "neutral"  # good, neutral, poor
    execution_time: float = 0.0
    
    # Notes
    notes: str = ""
    improvement_suggestions: List[str] = field(default_factory=list)


@dataclass
class LearningMetrics:
    """Aggregate learning metrics"""
    total_feedbacks: int = 0
    success_rate: float = 0.0
    avg_satisfaction: float = 0.0
    
    l1_avg_score: float = 0.0
    l2_avg_score: float = 0.0
    l3_avg_score: float = 0.0
    l4_avg_score: float = 0.0
    l5_avg_score: float = 0.0
    
    common_failures: Dict[str, int] = field(default_factory=dict)
    improvement_areas: List[str] = field(default_factory=list)
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FeedbackCollector:
    """Collects feedback from executions"""
    
    def __init__(self, storage_path: str = "data/feedback"):
        self.logger = logging.getLogger("jarvis.feedback")
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.feedback_buffer: List[ExecutionFeedback] = []
        self.logger.info("Feedback Collector initialized")
    
    def collect(self, execution_data: Dict[str, Any], user_feedback: Optional[Dict] = None) -> ExecutionFeedback:
        """Collect feedback from execution"""
        
        feedback = ExecutionFeedback(
            execution_id=execution_data.get('task_id', 'unknown'),
            timestamp=datetime.now().isoformat(),
            original_command=execution_data.get('original_command', ''),
            feedback_type=self._determine_feedback_type(execution_data, user_feedback),
            
            l1_score=float(execution_data.get('l1_latency', 0) < 2),
            l2_score=float(execution_data.get('l2_verification', {}).get('passed', False)),
            l3_score=float(execution_data.get('l3_plan', {}).get('success', False)),
            l4_score=float(execution_data.get('l4_qa_result', {}).get('passed', False)),
            l5_score=float(execution_data.get('l5_metrics', {}).get('health_status') == 'healthy'),
            
            overall_score=execution_data.get('verification_score', 0.0),
            user_satisfaction=user_feedback.get('satisfaction', None) if user_feedback else None,
            execution_time=execution_data.get('total_latency', 0.0),
        )
        
        self.feedback_buffer.append(feedback)
        self.logger.debug(f"Feedback collected: {feedback.execution_id}")
        
        return feedback
    
    def _determine_feedback_type(self, execution_data: Dict, user_feedback: Optional[Dict]) -> FeedbackType:
        """Determine feedback type from execution"""
        
        if user_feedback:
            satisfaction = user_feedback.get('satisfaction', 3)
            if satisfaction >= 4:
                return FeedbackType.SUCCESS
            elif satisfaction >= 3:
                return FeedbackType.PARTIAL_SUCCESS
            else:
                return FeedbackType.FAILURE
        
        status = execution_data.get('status', '').upper()
        if status == 'SUCCESS':
            return FeedbackType.SUCCESS
        elif status == 'FAILED':
            return FeedbackType.FAILURE
        
        return FeedbackType.PARTIAL_SUCCESS
    
    def save_batch(self):
        """Save feedback buffer to disk"""
        if not self.feedback_buffer:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.storage_path / f"feedback_{timestamp}.jsonl"
        
        with open(filename, 'w') as f:
            for feedback in self.feedback_buffer:
                f.write(json.dumps(asdict(feedback), default=str) + '\n')
        
        self.logger.info(f"Saved {len(self.feedback_buffer)} feedbacks to {filename}")
        self.feedback_buffer.clear()


class PatternRecognizer:
    """Recognizes patterns from feedback"""
    
    def __init__(self):
        self.logger = logging.getLogger("jarvis.patterns")
        self.command_patterns: Dict[str, List] = {}
        self.failure_patterns: Dict[str, int] = {}
        self.logger.info("Pattern Recognizer initialized")
    
    def analyze_feedbacks(self, feedbacks: List[ExecutionFeedback]) -> Dict[str, Any]:
        """Analyze patterns in feedbacks"""
        
        patterns = {
            'command_categories': {},
            'failure_clusters': {},
            'success_patterns': {},
            'timing_patterns': {}
        }
        
        for feedback in feedbacks:
            # Categorize commands
            category = self._categorize_command(feedback.original_command)
            if category not in patterns['command_categories']:
                patterns['command_categories'][category] = {'count': 0, 'success_rate': 0}
            patterns['command_categories'][category]['count'] += 1
            
            # Track failures
            if feedback.feedback_type == FeedbackType.FAILURE:
                if category not in patterns['failure_clusters']:
                    patterns['failure_clusters'][category] = 0
                patterns['failure_clusters'][category] += 1
            
            # Timing patterns
            if feedback.execution_time > 5:
                patterns['timing_patterns']['slow'] = patterns['timing_patterns'].get('slow', 0) + 1
        
        self.logger.info(f"Pattern analysis complete: {len(feedbacks)} feedbacks analyzed")
        return patterns
    
    def _categorize_command(self, command: str) -> str:
        """Categorize command by type"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['code', 'python', 'script', 'function']):
            return 'coding'
        elif any(word in command_lower for word in ['create', 'generate', 'write', 'build']):
            return 'creation'
        elif any(word in command_lower for word in ['plan', 'schedule', 'organize', 'list']):
            return 'planning'
        elif any(word in command_lower for word in ['analyze', 'check', 'verify', 'test']):
            return 'analysis'
        else:
            return 'general'


class ConfidenceOptimizer:
    """Optimizes confidence thresholds based on feedback"""
    
    def __init__(self):
        self.logger = logging.getLogger("jarvis.confidence")
        self.threshold_history: List[Dict] = []
        self.current_thresholds = {
            'l1_threshold': 0.80,
            'l2_threshold': 0.85,
            'l4_threshold': 0.90,
            'execute_threshold': 0.75,
            'review_threshold': 0.50
        }
        self.logger.info("Confidence Optimizer initialized")
    
    def optimize(self, feedbacks: List[ExecutionFeedback]) -> Dict[str, float]:
        """Optimize confidence thresholds"""
        
        if len(feedbacks) < 10:
            self.logger.warning("Insufficient feedbacks for optimization")
            return self.current_thresholds
        
        # Calculate layer performance
        l1_scores = [f.l1_score for f in feedbacks]
        l2_scores = [f.l2_score for f in feedbacks]
        l4_scores = [f.l4_score for f in feedbacks]
        
        success_feedbacks = [f for f in feedbacks if f.feedback_type == FeedbackType.SUCCESS]
        
        if success_feedbacks:
            avg_successful_score = statistics.mean([f.overall_score for f in success_feedbacks])
            # Adjust thresholds based on successful patterns
            self.current_thresholds['execute_threshold'] = min(avg_successful_score - 0.05, 0.85)
        
        self.logger.info(f"Thresholds optimized: {self.current_thresholds}")
        self.threshold_history.append({
            'timestamp': datetime.now().isoformat(),
            'thresholds': self.current_thresholds.copy()
        })
        
        return self.current_thresholds


class AdaptiveModelSelector:
    """Selects models adaptively based on command type"""
    
    def __init__(self):
        self.logger = logging.getLogger("jarvis.model_selector")
        self.model_performance: Dict[str, Dict] = {}
        self.logger.info("Adaptive Model Selector initialized")
    
    def select_models(self, command: str, feedbacks: List[ExecutionFeedback]) -> Dict[str, Any]:
        """Select best models for command"""
        
        # Analyze command type
        command_lower = command.lower()
        is_code = any(word in command_lower for word in ['code', 'python', 'script'])
        is_analytical = any(word in command_lower for word in ['analyze', 'check', 'verify'])
        
        selection = {
            'primary': 'helagpt',
            'verification_models': ['mistral', 'deepseek'] if is_code else ['mistral'],
            'qa_model': 'gpt4o_mini',
            'reasoning': 'Specialized models selected based on command analysis'
        }
        
        self.logger.info(f"Models selected for command: {selection['verification_models']}")
        return selection


class LearningAnalytics:
    """Generates learning analytics and reports"""
    
    def __init__(self):
        self.logger = logging.getLogger("jarvis.analytics")
        self.logger.info("Learning Analytics initialized")
    
    def generate_report(self, feedbacks: List[ExecutionFeedback]) -> LearningMetrics:
        """Generate comprehensive learning report"""
        
        if not feedbacks:
            return LearningMetrics()
        
        success_count = len([f for f in feedbacks if f.feedback_type == FeedbackType.SUCCESS])
        
        metrics = LearningMetrics(
            total_feedbacks=len(feedbacks),
            success_rate=success_count / len(feedbacks) if feedbacks else 0,
            avg_satisfaction=statistics.mean([f.user_satisfaction for f in feedbacks if f.user_satisfaction]) if feedbacks else 0,
            
            l1_avg_score=statistics.mean([f.l1_score for f in feedbacks]) if feedbacks else 0,
            l2_avg_score=statistics.mean([f.l2_score for f in feedbacks]) if feedbacks else 0,
            l3_avg_score=statistics.mean([f.l3_score for f in feedbacks]) if feedbacks else 0,
            l4_avg_score=statistics.mean([f.l4_score for f in feedbacks]) if feedbacks else 0,
            l5_avg_score=statistics.mean([f.l5_score for f in feedbacks]) if feedbacks else 0,
        )
        
        # Identify improvement areas
        if metrics.l2_avg_score < 0.8:
            metrics.improvement_areas.append("L2 Logic Verification needs improvement")
        if metrics.l4_avg_score < 0.85:
            metrics.improvement_areas.append("L4 QA Verification needs enhancement")
        if metrics.success_rate < 0.85:
            metrics.improvement_areas.append("Overall success rate below target")
        
        self.logger.info(f"Analytics report generated: {metrics.total_feedbacks} feedbacks")
        return metrics


class SelfLearningSystem:
    """Main Phase C Self-Learning System"""
    
    def __init__(self):
        self.logger = logging.getLogger("jarvis.phase_c")
        self.feedback_collector = FeedbackCollector()
        self.pattern_recognizer = PatternRecognizer()
        self.confidence_optimizer = ConfidenceOptimizer()
        self.model_selector = AdaptiveModelSelector()
        self.analytics = LearningAnalytics()
        
        self.feedbacks: List[ExecutionFeedback] = []
        self.logger.info("Self-Learning System initialized (Phase C)")
    
    async def record_execution(self, execution_data: Dict[str, Any], user_feedback: Optional[Dict] = None):
        """Record execution result"""
        
        feedback = self.feedback_collector.collect(execution_data, user_feedback)
        self.feedbacks.append(feedback)
        
        # Save periodically
        if len(self.feedbacks) % 10 == 0:
            self.feedback_collector.save_batch()
    
    async def analyze_and_improve(self):
        """Analyze feedbacks and optimize system"""
        
        if len(self.feedbacks) < 5:
            self.logger.warning("Insufficient feedbacks for analysis")
            return
        
        # Pattern analysis
        patterns = self.pattern_recognizer.analyze_feedbacks(self.feedbacks)
        
        # Optimize thresholds
        thresholds = self.confidence_optimizer.optimize(self.feedbacks)
        
        # Generate report
        report = self.analytics.generate_report(self.feedbacks)
        
        return {
            'patterns': patterns,
            'thresholds': thresholds,
            'metrics': asdict(report)
        }
    
    async def get_next_model_selection(self, command: str) -> Dict[str, Any]:
        """Get adaptive model selection for command"""
        return self.model_selector.select_models(command, self.feedbacks)
    
    async def generate_learning_report(self) -> Dict[str, Any]:
        """Generate comprehensive learning report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_executions': len(self.feedbacks),
            'analytics': asdict(self.analytics.generate_report(self.feedbacks)),
            'patterns': self.pattern_recognizer.analyze_feedbacks(self.feedbacks),
            'confidence_thresholds': self.confidence_optimizer.current_thresholds,
            'improvement_recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if len(self.feedbacks) > 0:
            success_rate = len([f for f in self.feedbacks if f.feedback_type == FeedbackType.SUCCESS]) / len(self.feedbacks)
            
            if success_rate < 0.80:
                recommendations.append("Focus on improving L2 Logic Verification accuracy")
            if success_rate < 0.75:
                recommendations.append("Consider retraining L4 QA model")
            
            avg_time = statistics.mean([f.execution_time for f in self.feedbacks])
            if avg_time > 5:
                recommendations.append("Optimize for faster execution (current avg: {:.1f}s)".format(avg_time))
        
        return recommendations


# ============================================================================
# PHASE C EXECUTION
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        system = SelfLearningSystem()
        
        print("\n" + "="*80)
        print("JARVIS X V2 - PHASE C: SELF-LEARNING SYSTEM")
        print("="*80 + "\n")
        
        # Simulate feedback collection
        print("📋 Simulating execution feedback collection...")
        
        test_executions = [
            {
                'task_id': f'task_{i:03d}',
                'original_command': f'Test command {i}',
                'verification_score': 0.85 + (i % 10) * 0.01,
                'l1_latency': 1.5,
                'l2_verification': {'passed': True},
                'l3_plan': {'success': True},
                'l4_qa_result': {'passed': True},
                'l5_metrics': {'health_status': 'healthy'},
                'total_latency': 1.8,
                'status': 'SUCCESS'
            }
            for i in range(20)
        ]
        
        for exec_data in test_executions:
            await system.record_execution(exec_data, {'satisfaction': 4})
        
        print(f"✅ Recorded {len(test_executions)} executions\n")
        
        # Analyze
        print("📋 Analyzing patterns and optimizing...")
        analysis = await system.analyze_and_improve()
        print(f"✅ Analysis complete: {analysis['metrics']['total_feedbacks']} feedbacks analyzed\n")
        
        # Generate report
        print("📋 Generating learning report...")
        report = await system.generate_learning_report()
        
        print(f"✅ SUCCESS RATE: {report['analytics']['success_rate']:.1%}")
        print(f"✅ AVG SATISFACTION: {report['analytics']['avg_satisfaction']:.1f}/5.0")
        print(f"✅ L4 QUALITY SCORE: {report['analytics']['l4_avg_score']:.2f}")
        print(f"\n📊 IMPROVEMENT AREAS:")
        for area in report['analytics']['improvement_areas']:
            print(f"   • {area}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['improvement_recommendations']:
            print(f"   • {rec}")
        
        print("\n" + "="*80)
        print("✅ PHASE C SELF-LEARNING SYSTEM OPERATIONAL")
        print("="*80 + "\n")
    
    asyncio.run(main())
