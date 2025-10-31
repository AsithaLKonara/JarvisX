"""
JARVIS AI - Dataset Collector
Collects and prepares training data from user interactions and conversation logs.
"""

import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import re
from dataclasses import dataclass

@dataclass
class TrainingExample:
    """Individual training example."""
    input_text: str
    output_text: str
    context: Dict[str, Any]
    timestamp: datetime
    quality_score: float
    category: str

class DatasetCollector:
    """
    Collects training data from various sources for AI model fine-tuning.
    Sources: conversation logs, user patterns, command history, content creation.
    """
    
    def __init__(self, memory_db_path: str = "jarvis_memory.db"):
        """Initialize dataset collector."""
        self.logger = logging.getLogger(__name__)
        self.memory_db_path = memory_db_path
        self.training_examples = []
        
        self.logger.info("Dataset Collector initialized")
    
    def collect_conversation_data(self, days_back: int = 30) -> List[TrainingExample]:
        """Collect conversation data for training."""
        try:
            self.logger.info(f"Collecting conversation data from last {days_back} days")
            
            # Connect to memory database
            conn = sqlite3.connect(self.memory_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get conversation history
            cutoff_date = datetime.now() - timedelta(days=days_back)
            cursor.execute("""
                SELECT * FROM commands 
                WHERE timestamp > ? AND ai_response IS NOT NULL
                ORDER BY timestamp
            """, (cutoff_date.isoformat(),))
            
            rows = cursor.fetchall()
            examples = []
            
            for row in rows:
                if row['ai_response'] and row['ai_response'].strip():
                    # Clean and prepare text
                    input_text = self._clean_text(row['command'])
                    output_text = self._clean_text(row['ai_response'])
                    
                    # Skip if too short or low quality
                    if len(input_text) < 5 or len(output_text) < 5:
                        continue
                    
                    # Calculate quality score
                    quality_score = self._calculate_quality_score(input_text, output_text)
                    
                    if quality_score > 0.3:  # Only include higher quality examples
                        example = TrainingExample(
                            input_text=input_text,
                            output_text=output_text,
                            context={
                                'timestamp': row['timestamp'],
                                'intent': row.get('intent', 'unknown'),
                                'confidence': row.get('confidence', 0.5)
                            },
                            timestamp=datetime.fromisoformat(row['timestamp']),
                            quality_score=quality_score,
                            category='conversation'
                        )
                        examples.append(example)
            
            conn.close()
            
            self.logger.info(f"Collected {len(examples)} conversation examples")
            return examples
        
        except Exception as e:
            self.logger.error(f"Error collecting conversation data: {e}")
            return []
    
    def collect_command_patterns(self) -> List[TrainingExample]:
        """Collect command patterns and their successful executions."""
        try:
            self.logger.info("Collecting command patterns")
            
            conn = sqlite3.connect(self.memory_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get successful commands
            cursor.execute("""
                SELECT command, ai_response, intent, confidence
                FROM commands 
                WHERE confidence > 0.7 AND ai_response IS NOT NULL
                ORDER BY confidence DESC
            """)
            
            rows = cursor.fetchall()
            examples = []
            
            # Group by intent for pattern learning
            intent_patterns = {}
            for row in rows:
                intent = row['intent'] or 'general'
                if intent not in intent_patterns:
                    intent_patterns[intent] = []
                
                intent_patterns[intent].append({
                    'command': row['command'],
                    'response': row['ai_response'],
                    'confidence': row['confidence']
                })
            
            # Create training examples from patterns
            for intent, patterns in intent_patterns.items():
                if len(patterns) >= 3:  # Only use intents with multiple examples
                    # Create pattern-based examples
                    for i, pattern in enumerate(patterns[:10]):  # Limit to 10 per intent
                        input_text = self._create_pattern_input(pattern['command'], intent)
                        output_text = self._clean_text(pattern['response'])
                        
                        example = TrainingExample(
                            input_text=input_text,
                            output_text=output_text,
                            context={
                                'intent': intent,
                                'pattern_index': i,
                                'confidence': pattern['confidence']
                            },
                            timestamp=datetime.now(),
                            quality_score=pattern['confidence'],
                            category='command_pattern'
                        )
                        examples.append(example)
            
            conn.close()
            
            self.logger.info(f"Collected {len(examples)} command pattern examples")
            return examples
        
        except Exception as e:
            self.logger.error(f"Error collecting command patterns: {e}")
            return []
    
    def collect_goal_achievements(self) -> List[TrainingExample]:
        """Collect completed goals and their outcomes for training."""
        try:
            self.logger.info("Collecting goal achievement data")
            
            # This would connect to goal database
            # For now, create synthetic examples based on common goal patterns
            goal_examples = [
                {
                    'input': 'I want to learn Python programming',
                    'output': 'Great goal! I can help you learn Python. Let me create a structured learning plan with daily exercises, project suggestions, and progress tracking. We can start with basics and gradually move to advanced topics.',
                    'category': 'learning_goal'
                },
                {
                    'input': 'Help me organize my files better',
                    'output': 'I\'ll help you organize your files! Let me analyze your current file structure and create an automated organization system. I can sort by type, date, project, and create smart folders.',
                    'category': 'organization_goal'
                },
                {
                    'input': 'Create a content creation workflow',
                    'output': 'I\'ll set up a comprehensive content creation workflow for you! This will include idea generation, script writing, video recording with OBS, editing automation, and publishing to YouTube.',
                    'category': 'content_goal'
                }
            ]
            
            examples = []
            for goal in goal_examples:
                example = TrainingExample(
                    input_text=goal['input'],
                    output_text=goal['output'],
                    context={'category': goal['category']},
                    timestamp=datetime.now(),
                    quality_score=0.9,
                    category='goal_achievement'
                )
                examples.append(example)
            
            self.logger.info(f"Collected {len(examples)} goal achievement examples")
            return examples
        
        except Exception as e:
            self.logger.error(f"Error collecting goal achievements: {e}")
            return []
    
    def collect_content_creation_patterns(self) -> List[TrainingExample]:
        """Collect content creation patterns and successful workflows."""
        try:
            self.logger.info("Collecting content creation patterns")
            
            # Content creation examples based on successful patterns
            content_examples = [
                {
                    'input': 'Create a tutorial video about Python basics',
                    'output': 'I\'ll help you create a comprehensive Python tutorial video! Let me plan the content structure, generate a script, set up OBS recording, and prepare the editing workflow. We\'ll cover variables, functions, and basic concepts.',
                    'category': 'tutorial_creation'
                },
                {
                    'input': 'Generate ideas for my YouTube channel',
                    'output': 'I\'ll generate creative ideas for your YouTube channel! Based on your interests and trending topics, here are some engaging video concepts: tech reviews, coding tutorials, productivity tips, and AI discussions.',
                    'category': 'idea_generation'
                },
                {
                    'input': 'Help me write a blog post about AI',
                    'output': 'I\'ll help you write an engaging blog post about AI! Let me research current trends, create an outline, write compelling content, and optimize it for SEO. We\'ll cover practical applications and future implications.',
                    'category': 'blog_writing'
                }
            ]
            
            examples = []
            for content in content_examples:
                example = TrainingExample(
                    input_text=content['input'],
                    output_text=content['output'],
                    context={'category': content['category']},
                    timestamp=datetime.now(),
                    quality_score=0.85,
                    category='content_creation'
                )
                examples.append(example)
            
            self.logger.info(f"Collected {len(examples)} content creation examples")
            return examples
        
        except Exception as e:
            self.logger.error(f"Error collecting content creation patterns: {e}")
            return []
    
    def create_training_dataset(self, output_file: str = "training_dataset.json") -> Dict[str, Any]:
        """Create comprehensive training dataset from all sources."""
        try:
            self.logger.info("Creating comprehensive training dataset")
            
            # Collect from all sources
            all_examples = []
            
            # Conversation data
            conversation_examples = self.collect_conversation_data()
            all_examples.extend(conversation_examples)
            
            # Command patterns
            command_examples = self.collect_command_patterns()
            all_examples.extend(command_examples)
            
            # Goal achievements
            goal_examples = self.collect_goal_achievements()
            all_examples.extend(goal_examples)
            
            # Content creation
            content_examples = self.collect_content_creation_patterns()
            all_examples.extend(content_examples)
            
            # Filter and sort by quality
            filtered_examples = [ex for ex in all_examples if ex.quality_score > 0.5]
            filtered_examples.sort(key=lambda x: x.quality_score, reverse=True)
            
            # Create dataset structure
            dataset = {
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'total_examples': len(filtered_examples),
                    'sources': ['conversation', 'command_patterns', 'goal_achievements', 'content_creation'],
                    'quality_threshold': 0.5,
                    'version': '1.0'
                },
                'examples': [
                    {
                        'input': ex.input_text,
                        'output': ex.output_text,
                        'context': ex.context,
                        'quality_score': ex.quality_score,
                        'category': ex.category,
                        'timestamp': ex.timestamp.isoformat()
                    }
                    for ex in filtered_examples
                ],
                'statistics': self._calculate_dataset_statistics(filtered_examples)
            }
            
            # Save dataset
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Training dataset created: {output_file} ({len(filtered_examples)} examples)")
            return dataset
        
        except Exception as e:
            self.logger.error(f"Error creating training dataset: {e}")
            return {}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for training."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might interfere with training
        text = re.sub(r'[^\w\s.,!?;:\-()]', '', text)
        
        return text
    
    def _calculate_quality_score(self, input_text: str, output_text: str) -> float:
        """Calculate quality score for training example."""
        try:
            score = 0.0
            
            # Length factor (optimal range)
            input_len = len(input_text.split())
            output_len = len(output_text.split())
            
            if 5 <= input_len <= 50:
                score += 0.3
            if 10 <= output_len <= 100:
                score += 0.3
            
            # Content quality indicators
            if any(word in output_text.lower() for word in ['help', 'assist', 'create', 'generate', 'plan']):
                score += 0.2
            
            if '?' in input_text:  # Questions are good training examples
                score += 0.1
            
            if len(output_text) > len(input_text) * 1.5:  # Substantial response
                score += 0.1
            
            # Avoid very short or repetitive responses
            if output_text.lower() in ['ok', 'yes', 'no', 'thanks']:
                score -= 0.3
            
            return max(0.0, min(1.0, score))
        
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {e}")
            return 0.0
    
    def _create_pattern_input(self, command: str, intent: str) -> str:
        """Create pattern-based input for training."""
        # Add context to make the input more generalizable
        context_prefixes = {
            'file_management': 'Help me with file management: ',
            'web_search': 'I need to search for: ',
            'content_creation': 'I want to create content about: ',
            'learning': 'I want to learn about: ',
            'automation': 'Help me automate: '
        }
        
        prefix = context_prefixes.get(intent, '')
        return f"{prefix}{command}"
    
    def _calculate_dataset_statistics(self, examples: List[TrainingExample]) -> Dict[str, Any]:
        """Calculate dataset statistics."""
        try:
            categories = {}
            quality_scores = []
            input_lengths = []
            output_lengths = []
            
            for ex in examples:
                # Category distribution
                categories[ex.category] = categories.get(ex.category, 0) + 1
                
                # Quality scores
                quality_scores.append(ex.quality_score)
                
                # Length statistics
                input_lengths.append(len(ex.input_text.split()))
                output_lengths.append(len(ex.output_text.split()))
            
            return {
                'category_distribution': categories,
                'quality_stats': {
                    'min': min(quality_scores) if quality_scores else 0,
                    'max': max(quality_scores) if quality_scores else 0,
                    'avg': sum(quality_scores) / len(quality_scores) if quality_scores else 0
                },
                'length_stats': {
                    'input_avg': sum(input_lengths) / len(input_lengths) if input_lengths else 0,
                    'output_avg': sum(output_lengths) / len(output_lengths) if output_lengths else 0,
                    'input_min': min(input_lengths) if input_lengths else 0,
                    'input_max': max(input_lengths) if input_lengths else 0,
                    'output_min': min(output_lengths) if output_lengths else 0,
                    'output_max': max(output_lengths) if output_lengths else 0
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error calculating dataset statistics: {e}")
            return {}
    
    def export_for_huggingface(self, output_dir: str = "huggingface_dataset") -> bool:
        """Export dataset in Hugging Face format for fine-tuning."""
        try:
            self.logger.info("Exporting dataset for Hugging Face fine-tuning")
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Create training dataset
            dataset = self.create_training_dataset()
            
            # Convert to Hugging Face format
            hf_data = {
                'train': []
            }
            
            for example in dataset['examples']:
                hf_data['train'].append({
                    'text': f"Human: {example['input']}\nAssistant: {example['output']}"
                })
            
            # Save in Hugging Face format
            train_file = output_path / "train.json"
            with open(train_file, 'w', encoding='utf-8') as f:
                json.dump(hf_data, f, indent=2, ensure_ascii=False)
            
            # Save metadata
            metadata_file = output_path / "dataset_info.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(dataset['metadata'], f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Dataset exported to Hugging Face format: {output_dir}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting for Hugging Face: {e}")
            return False
