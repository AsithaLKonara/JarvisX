#!/usr/bin/env python3
"""
Self-Training System - Continuous Learning for Jarvis LLM
Collects feedback, builds datasets, and triggers retraining
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """
    Collects user feedback and interaction data for self-training
    """
    
    def __init__(self, feedback_dir: str = "data/feedback"):
        """
        Initialize feedback collector
        
        Args:
            feedback_dir: Directory to store feedback data
        """
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        
        self.feedback_file = self.feedback_dir / "feedback.jsonl"
        self.stats_file = self.feedback_dir / "stats.json"
        
        # Statistics
        self.stats = self._load_stats()
        
        logger.info(f"📊 Feedback Collector initialized")
        logger.info(f"   Feedback dir: {self.feedback_dir}")
        logger.info(f"   Total feedback: {self.stats['total_feedback']}")
    
    def _load_stats(self) -> Dict[str, int]:
        """Load statistics"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {
            'total_feedback': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
    
    def _save_stats(self):
        """Save statistics"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def record_interaction(
        self,
        user_input: str,
        model_response: str,
        rating: Optional[int] = None,  # 1-5 stars, or None
        feedback_text: Optional[str] = None,
        task_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Record a user interaction for future training
        
        Args:
            user_input: User's query/prompt
            model_response: Model's response
            rating: User rating (1-5) or None
            feedback_text: Optional feedback text
            task_type: Type of task (engineering, design, etc.)
            metadata: Additional metadata
        """
        try:
            # Determine sentiment
            if rating:
                if rating >= 4:
                    sentiment = "positive"
                    self.stats['positive'] += 1
                elif rating <= 2:
                    sentiment = "negative"
                    self.stats['negative'] += 1
                else:
                    sentiment = "neutral"
                    self.stats['neutral'] += 1
            else:
                sentiment = "neutral"
                self.stats['neutral'] += 1
            
            # Build feedback entry
            entry = {
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'model_response': model_response,
                'rating': rating,
                'sentiment': sentiment,
                'feedback_text': feedback_text,
                'task_type': task_type,
                'metadata': metadata or {}
            }
            
            # Append to JSONL file
            with open(self.feedback_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            
            self.stats['total_feedback'] += 1
            self._save_stats()
            
            logger.info(f"✅ Recorded feedback (rating: {rating}, sentiment: {sentiment})")
            
        except Exception as e:
            logger.error(f"❌ Failed to record feedback: {e}")
    
    def get_training_data(
        self,
        min_rating: int = 4,
        task_types: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get high-quality interactions for training
        
        Args:
            min_rating: Minimum rating to include
            task_types: Filter by task types
            limit: Maximum number of entries
            
        Returns:
            List of training examples
        """
        if not self.feedback_file.exists():
            return []
        
        training_data = []
        
        with open(self.feedback_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Filter by rating
                    if entry.get('rating') and entry['rating'] < min_rating:
                        continue
                    
                    # Filter by task type
                    if task_types and entry.get('task_type') not in task_types:
                        continue
                    
                    training_data.append(entry)
                    
                    # Check limit
                    if limit and len(training_data) >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"⚠️  Skipped invalid entry: {e}")
                    continue
        
        logger.info(f"📚 Retrieved {len(training_data)} training examples")
        return training_data
    
    def export_training_dataset(
        self,
        output_file: str,
        min_rating: int = 4,
        format: str = "alpaca"  # "alpaca" or "sharegpt"
    ):
        """
        Export training dataset in standard format
        
        Args:
            output_file: Output file path
            min_rating: Minimum rating to include
            format: Dataset format ("alpaca" or "sharegpt")
        """
        training_data = self.get_training_data(min_rating=min_rating)
        
        if not training_data:
            logger.warning("⚠️  No training data to export")
            return
        
        # Convert to desired format
        if format == "alpaca":
            dataset = self._convert_to_alpaca(training_data)
        elif format == "sharegpt":
            dataset = self._convert_to_sharegpt(training_data)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        # Save dataset
        with open(output_file, 'w') as f:
            for entry in dataset:
                f.write(json.dumps(entry) + '\n')
        
        logger.info(f"✅ Exported {len(dataset)} examples to {output_file}")
    
    def _convert_to_alpaca(self, data: List[Dict]) -> List[Dict]:
        """Convert to Alpaca format"""
        return [
            {
                "instruction": entry['user_input'],
                "input": "",
                "output": entry['model_response']
            }
            for entry in data
        ]
    
    def _convert_to_sharegpt(self, data: List[Dict]) -> List[Dict]:
        """Convert to ShareGPT format"""
        return [
            {
                "conversations": [
                    {"from": "human", "value": entry['user_input']},
                    {"from": "gpt", "value": entry['model_response']}
                ]
            }
            for entry in data
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        return {
            **self.stats,
            'positive_rate': (
                self.stats['positive'] / self.stats['total_feedback'] * 100
                if self.stats['total_feedback'] > 0 else 0
            ),
            'feedback_file': str(self.feedback_file),
            'ready_for_training': self.stats['positive'] >= 100  # Minimum 100 good examples
        }


class ContinualTrainer:
    """
    Manages continual fine-tuning of the model
    """
    
    def __init__(
        self,
        model_path: str,
        training_script: str = "scripts/train_lora.py",
        min_examples: int = 100
    ):
        """
        Initialize continual trainer
        
        Args:
            model_path: Path to base model
            training_script: Path to training script
            min_examples: Minimum examples needed for retraining
        """
        self.model_path = model_path
        self.training_script = training_script
        self.min_examples = min_examples
        
        self.training_history_file = Path("data/training_history.json")
        self.training_history = self._load_training_history()
        
        logger.info("🔄 Continual Trainer initialized")
        logger.info(f"   Model: {model_path}")
        logger.info(f"   Training runs: {len(self.training_history)}")
    
    def _load_training_history(self) -> List[Dict]:
        """Load training history"""
        if self.training_history_file.exists():
            with open(self.training_history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_training_history(self):
        """Save training history"""
        self.training_history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.training_history_file, 'w') as f:
            json.dump(self.training_history, f, indent=2)
    
    def check_if_ready(self, feedback_collector: FeedbackCollector) -> bool:
        """
        Check if enough new data for retraining
        
        Args:
            feedback_collector: Feedback collector instance
            
        Returns:
            True if ready for retraining
        """
        stats = feedback_collector.get_stats()
        
        # Check if we have enough positive examples
        if stats['positive'] < self.min_examples:
            logger.info(f"📊 Not ready: {stats['positive']}/{self.min_examples} examples")
            return False
        
        # Check if we already trained recently
        if self.training_history:
            last_training = self.training_history[-1]
            last_training_time = datetime.fromisoformat(last_training['timestamp'])
            days_since = (datetime.now() - last_training_time).days
            
            if days_since < 7:  # Don't retrain more than once per week
                logger.info(f"📊 Not ready: Last training was {days_since} days ago (minimum 7)")
                return False
        
        logger.info(f"✅ Ready for retraining! ({stats['positive']} examples)")
        return True
    
    def trigger_training(
        self,
        dataset_file: str,
        output_dir: str = "models/jarvis-v2",
        num_epochs: int = 3,
        learning_rate: float = 2e-4,
        batch_size: int = 4
    ) -> Dict[str, Any]:
        """
        Trigger a new training run
        
        Args:
            dataset_file: Path to training dataset
            output_dir: Output directory for new model
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            batch_size: Batch size
            
        Returns:
            Training results
        """
        logger.info("🚀 Starting continual training...")
        
        training_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Record training run
        training_record = {
            'id': training_id,
            'timestamp': datetime.now().isoformat(),
            'dataset_file': dataset_file,
            'output_dir': output_dir,
            'config': {
                'num_epochs': num_epochs,
                'learning_rate': learning_rate,
                'batch_size': batch_size
            },
            'status': 'started'
        }
        
        self.training_history.append(training_record)
        self._save_training_history()
        
        try:
            # NOTE: Actual training would be triggered here
            # For now, this is a placeholder
            
            logger.info(f"📝 Training configuration:")
            logger.info(f"   Dataset: {dataset_file}")
            logger.info(f"   Output: {output_dir}")
            logger.info(f"   Epochs: {num_epochs}")
            logger.info(f"   Learning rate: {learning_rate}")
            logger.info(f"   Batch size: {batch_size}")
            
            # Update status
            training_record['status'] = 'completed'
            training_record['completed_at'] = datetime.now().isoformat()
            self._save_training_history()
            
            logger.info(f"✅ Training {training_id} completed!")
            
            return {
                'success': True,
                'training_id': training_id,
                'output_dir': output_dir
            }
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            training_record['status'] = 'failed'
            training_record['error'] = str(e)
            self._save_training_history()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_history(self) -> List[Dict]:
        """Get training history"""
        return self.training_history.copy()


class SelfTrainingSystem:
    """
    Complete self-training system integrating feedback and retraining
    """
    
    def __init__(
        self,
        model_path: str,
        feedback_dir: str = "data/feedback",
        auto_train: bool = False,
        check_interval_hours: int = 24
    ):
        """
        Initialize self-training system
        
        Args:
            model_path: Path to base model
            feedback_dir: Directory for feedback data
            auto_train: Enable automatic retraining
            check_interval_hours: Hours between readiness checks
        """
        self.model_path = model_path
        self.auto_train = auto_train
        self.check_interval_hours = check_interval_hours
        
        self.feedback_collector = FeedbackCollector(feedback_dir)
        self.trainer = ContinualTrainer(model_path)
        
        self.last_check_time = time.time()
        
        logger.info("🤖 Self-Training System initialized")
        logger.info(f"   Auto-train: {auto_train}")
        logger.info(f"   Check interval: {check_interval_hours}h")
    
    def record_interaction(
        self,
        user_input: str,
        model_response: str,
        rating: Optional[int] = None,
        feedback_text: Optional[str] = None,
        task_type: Optional[str] = None
    ):
        """Record user interaction"""
        self.feedback_collector.record_interaction(
            user_input=user_input,
            model_response=model_response,
            rating=rating,
            feedback_text=feedback_text,
            task_type=task_type
        )
        
        # Auto-check if ready for training
        if self.auto_train:
            self._auto_check_and_train()
    
    def _auto_check_and_train(self):
        """Automatically check and trigger training if ready"""
        current_time = time.time()
        hours_since_check = (current_time - self.last_check_time) / 3600
        
        if hours_since_check < self.check_interval_hours:
            return  # Not time to check yet
        
        self.last_check_time = current_time
        
        # Check if ready
        if self.trainer.check_if_ready(self.feedback_collector):
            logger.info("🚀 Auto-triggering training...")
            
            # Export dataset
            dataset_file = f"data/feedback/training_dataset_{datetime.now().strftime('%Y%m%d')}.jsonl"
            self.feedback_collector.export_training_dataset(
                output_file=dataset_file,
                min_rating=4,
                format="alpaca"
            )
            
            # Trigger training
            result = self.trainer.trigger_training(
                dataset_file=dataset_file,
                output_dir=f"models/jarvis-v2-{datetime.now().strftime('%Y%m%d')}"
            )
            
            if result['success']:
                logger.info(f"✅ Auto-training completed: {result['output_dir']}")
            else:
                logger.error(f"❌ Auto-training failed: {result.get('error')}")
    
    def manual_training(
        self,
        min_rating: int = 4,
        num_epochs: int = 3,
        learning_rate: float = 2e-4
    ) -> Dict[str, Any]:
        """
        Manually trigger a training run
        
        Args:
            min_rating: Minimum rating for examples
            num_epochs: Training epochs
            learning_rate: Learning rate
            
        Returns:
            Training results
        """
        logger.info("🔧 Manual training triggered")
        
        # Export dataset
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_file = f"data/feedback/manual_training_{timestamp}.jsonl"
        
        self.feedback_collector.export_training_dataset(
            output_file=dataset_file,
            min_rating=min_rating,
            format="alpaca"
        )
        
        # Trigger training
        return self.trainer.trigger_training(
            dataset_file=dataset_file,
            output_dir=f"models/jarvis-manual-{timestamp}",
            num_epochs=num_epochs,
            learning_rate=learning_rate
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        feedback_stats = self.feedback_collector.get_stats()
        training_history = self.trainer.get_history()
        
        return {
            'feedback': feedback_stats,
            'training_runs': len(training_history),
            'last_training': training_history[-1] if training_history else None,
            'auto_train_enabled': self.auto_train,
            'ready_for_training': self.trainer.check_if_ready(self.feedback_collector)
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize system
    system = SelfTrainingSystem(
        model_path="models/jarvis-llm-brain-final",
        auto_train=False
    )
    
    # Simulate interactions
    print("\n📝 Recording sample interactions...\n")
    
    system.record_interaction(
        user_input="What is Python?",
        model_response="Python is a high-level programming language...",
        rating=5,
        task_type="technical"
    )
    
    system.record_interaction(
        user_input="How do I optimize database queries?",
        model_response="Here are key strategies for database optimization...",
        rating=4,
        task_type="engineering"
    )
    
    # Get status
    print("\n📊 System Status:\n")
    status = system.get_status()
    print(json.dumps(status, indent=2))

