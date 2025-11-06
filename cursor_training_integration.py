#!/usr/bin/env python3
"""
Cursor AI Training Integration
Automate training data collection using Cursor AI to:
- Generate diverse training queries
- Evaluate model responses
- Rate responses automatically
- Build high-quality datasets
"""

import sys
import os
import logging
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cursor_training.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CursorTrainingBot:
    """
    Automated training bot using Cursor AI
    """
    
    def __init__(self, training_gui_url: str = "http://localhost:5001"):
        """
        Initialize Cursor training bot
        
        Args:
            training_gui_url: URL of the training GUI
        """
        self.training_gui_url = training_gui_url
        self.training_log = []
        
        # Create directories
        Path('logs').mkdir(exist_ok=True)
        Path('cursor_training_data').mkdir(exist_ok=True)
        
        logger.info("🤖 Cursor Training Bot initialized")
        logger.info(f"   Training GUI: {training_gui_url}")
    
    def generate_training_queries(self, 
                                 domain: str = "technical",
                                 count: int = 10,
                                 difficulty: str = "mixed") -> List[str]:
        """
        Generate diverse training queries
        
        Args:
            domain: Domain type (technical, engineering, design, business)
            count: Number of queries to generate
            difficulty: Difficulty level (easy, medium, hard, mixed)
            
        Returns:
            List of generated queries
        """
        logger.info(f"📝 Generating {count} {domain} queries ({difficulty} difficulty)...")
        
        # Query templates by domain
        templates = {
            'technical': [
                "What is {topic} and how does it work?",
                "Explain {topic} in simple terms",
                "What are the key concepts in {topic}?",
                "How do I implement {topic}?",
                "What are best practices for {topic}?",
                "Compare {topic1} vs {topic2}",
                "What are common mistakes with {topic}?",
                "How to optimize {topic}?",
                "Pros and cons of {topic}",
                "Real-world applications of {topic}"
            ],
            'engineering': [
                "How to debug {problem}?",
                "Best way to implement {feature}?",
                "Architecture for {system}?",
                "How to scale {application}?",
                "Performance optimization for {component}?",
                "Security considerations for {feature}?",
                "Testing strategy for {module}?",
                "Refactoring {code_pattern}?",
                "Design patterns for {problem}?",
                "Code review checklist for {project}?"
            ],
            'design': [
                "UI/UX principles for {element}?",
                "Color scheme for {brand_type}?",
                "Layout design for {page_type}?",
                "Typography choices for {content}?",
                "Accessibility in {component}?",
                "Responsive design for {device}?",
                "Animation guidelines for {interaction}?",
                "Design system for {application}?",
                "User research methods for {product}?",
                "Prototyping tools for {design_type}?"
            ],
            'business': [
                "Marketing strategy for {product}?",
                "Revenue model for {business}?",
                "Customer acquisition for {service}?",
                "Pricing strategy for {offering}?",
                "Business metrics for {company_type}?",
                "Growth tactics for {startup}?",
                "Competitive analysis for {market}?",
                "Financial planning for {business_stage}?",
                "Team structure for {organization}?",
                "Risk management in {industry}?"
            ]
        }
        
        # Topics by domain
        topics = {
            'technical': [
                'machine learning', 'deep learning', 'neural networks', 'algorithms',
                'data structures', 'REST APIs', 'GraphQL', 'microservices',
                'Docker', 'Kubernetes', 'CI/CD', 'cloud computing',
                'blockchain', 'cryptocurrency', 'quantum computing', 'IoT'
            ],
            'engineering': [
                'memory leaks', 'null pointer exceptions', 'async/await',
                'user authentication', 'payment processing', 'real-time chat',
                'video streaming', 'image uploads', 'caching', 'load balancing',
                'database indexing', 'API versioning', 'error handling',
                'logging systems', 'monitoring dashboards', 'A/B testing'
            ],
            'design': [
                'navigation menu', 'B2B SaaS', 'landing page', 'dashboard',
                'serif vs sans-serif', 'mobile app', 'desktop website',
                'button interactions', 'enterprise application', 'e-commerce',
                'form design', 'data visualization', 'icon design',
                'brand identity', 'mobile first', 'dark mode'
            ],
            'business': [
                'SaaS product', 'subscription service', 'B2B customers',
                'enterprise clients', 'freemium model', 'early-stage startup',
                'tech industry', 'Series A', 'product-market fit',
                'remote team', 'healthcare', 'financial services'
            ]
        }
        
        queries = []
        domain_templates = templates.get(domain, templates['technical'])
        domain_topics = topics.get(domain, topics['technical'])
        
        import random
        
        for i in range(count):
            template = random.choice(domain_templates)
            
            # Fill in template with random topics
            if '{topic}' in template:
                topic = random.choice(domain_topics)
                query = template.replace('{topic}', topic)
            elif '{topic1}' in template and '{topic2}' in template:
                topic1, topic2 = random.sample(domain_topics, 2)
                query = template.replace('{topic1}', topic1).replace('{topic2}', topic2)
            else:
                # Fill other placeholders with random topics
                for placeholder in ['{problem}', '{feature}', '{system}', 
                                  '{application}', '{component}', '{element}',
                                  '{brand_type}', '{page_type}', '{content}',
                                  '{product}', '{business}', '{service}']:
                    if placeholder in template:
                        topic = random.choice(domain_topics)
                        query = template.replace(placeholder, topic)
                        break
                else:
                    query = template
            
            queries.append(query)
        
        logger.info(f"✅ Generated {len(queries)} queries")
        return queries
    
    def send_query(self, query: str, task_type: str = "technical") -> Dict:
        """
        Send query to training GUI
        
        Args:
            query: Query to send
            task_type: Task type
            
        Returns:
            Response data
        """
        try:
            response = requests.post(
                f"{self.training_gui_url}/api/chat",
                json={"message": query, "task_type": task_type},
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                logger.info(f"✅ Response received in {data['inference_time']:.2f}s")
                return data
            else:
                logger.error(f"❌ Request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Send query error: {e}")
            return None
    
    def evaluate_response(self, query: str, response: str, 
                         criteria: List[str] = None) -> Dict:
        """
        Evaluate response quality using heuristics
        
        Args:
            query: Original query
            response: Model response
            criteria: Evaluation criteria
            
        Returns:
            Evaluation results with rating
        """
        if criteria is None:
            criteria = [
                'accuracy',
                'completeness',
                'clarity',
                'relevance',
                'actionability'
            ]
        
        # Simple heuristic evaluation
        score = 0
        max_score = len(criteria) * 20  # 20 points per criterion
        feedback = []
        
        # Length check (reasonable length)
        if 50 <= len(response) <= 1000:
            score += 15
            feedback.append("✅ Good length")
        elif len(response) < 50:
            feedback.append("⚠️  Response too short")
        else:
            score += 10
            feedback.append("⚠️  Response very long")
        
        # Structure check (paragraphs/points)
        if '\n' in response or '.' in response:
            score += 15
            feedback.append("✅ Well-structured")
        
        # Technical terms (if technical domain)
        technical_keywords = ['api', 'database', 'server', 'code', 'function',
                            'algorithm', 'data', 'system', 'process', 'method']
        if any(keyword in response.lower() for keyword in technical_keywords):
            score += 15
            feedback.append("✅ Contains technical terms")
        
        # Actionability (contains how-to or steps)
        action_words = ['first', 'second', 'step', 'follow', 'use', 'implement',
                       'configure', 'setup', 'install', 'create']
        if any(word in response.lower() for word in action_words):
            score += 15
            feedback.append("✅ Actionable advice")
        
        # Examples (code or scenarios)
        if '`' in response or 'example' in response.lower():
            score += 15
            feedback.append("✅ Includes examples")
        
        # Quality markers
        quality_markers = ['best practice', 'important', 'key', 'essential',
                          'consider', 'recommend', 'advantage', 'benefit']
        if any(marker in response.lower() for marker in quality_markers):
            score += 15
            feedback.append("✅ Quality markers present")
        
        # Convert to 1-5 star rating
        rating = min(5, max(1, int((score / max_score) * 5) + 1))
        
        return {
            'rating': rating,
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'feedback': feedback
        }
    
    def rate_response(self, conversation_id: int, rating: int, 
                     feedback: str = "") -> bool:
        """
        Rate a response in training GUI
        
        Args:
            conversation_id: Conversation ID
            rating: Rating (1-5)
            feedback: Optional feedback text
            
        Returns:
            Success status
        """
        try:
            response = requests.post(
                f"{self.training_gui_url}/api/rate",
                json={
                    "conversation_id": conversation_id,
                    "rating": rating,
                    "feedback": feedback
                },
                timeout=10
            )
            
            if response.ok:
                logger.info(f"✅ Rated conversation {conversation_id}: {rating} stars")
                return True
            else:
                logger.error(f"❌ Rating failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Rate error: {e}")
            return False
    
    def automated_training_session(self,
                                   domain: str = "technical",
                                   num_queries: int = 20,
                                   min_rating_threshold: int = 4,
                                   delay_between_queries: float = 2.0):
        """
        Run automated training session
        
        Args:
            domain: Domain for queries
            num_queries: Number of queries to run
            min_rating_threshold: Minimum rating to save
            delay_between_queries: Delay in seconds
        """
        logger.info("\n" + "="*70)
        logger.info("🤖 AUTOMATED TRAINING SESSION")
        logger.info("="*70)
        logger.info(f"   Domain: {domain}")
        logger.info(f"   Queries: {num_queries}")
        logger.info(f"   Min Rating: {min_rating_threshold} stars")
        logger.info("")
        
        # Generate queries
        queries = self.generate_training_queries(domain, num_queries)
        
        session_stats = {
            'total': 0,
            'successful': 0,
            'high_quality': 0,  # 4-5 stars
            'ratings': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
        
        # Process each query
        for i, query in enumerate(queries, 1):
            logger.info(f"\n{'─'*70}")
            logger.info(f"Query {i}/{num_queries}")
            logger.info(f"{'─'*70}")
            logger.info(f"📝 Query: {query}")
            
            # Send query
            result = self.send_query(query, domain)
            
            if not result:
                logger.warning("⚠️  Skipping due to error")
                continue
            
            response = result['response']
            conversation_id = result['conversation_id']
            
            logger.info(f"💬 Response: {response[:150]}...")
            
            # Evaluate response
            evaluation = self.evaluate_response(query, response)
            rating = evaluation['rating']
            
            logger.info(f"\n📊 Evaluation:")
            logger.info(f"   Rating: {'⭐' * rating} ({rating}/5)")
            logger.info(f"   Score: {evaluation['score']}/{evaluation['max_score']} ({evaluation['percentage']:.1f}%)")
            for fb in evaluation['feedback']:
                logger.info(f"   {fb}")
            
            # Rate in GUI
            feedback_text = " | ".join(evaluation['feedback'])
            self.rate_response(conversation_id, rating, feedback_text)
            
            # Update stats
            session_stats['total'] += 1
            session_stats['successful'] += 1
            session_stats['ratings'][rating] += 1
            if rating >= min_rating_threshold:
                session_stats['high_quality'] += 1
            
            # Log entry
            self.training_log.append({
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'response': response,
                'rating': rating,
                'evaluation': evaluation,
                'domain': domain
            })
            
            # Delay before next query
            if i < num_queries:
                time.sleep(delay_between_queries)
        
        # Session summary
        logger.info("\n" + "="*70)
        logger.info("📊 SESSION SUMMARY")
        logger.info("="*70)
        logger.info(f"Total queries: {session_stats['total']}")
        logger.info(f"Successful: {session_stats['successful']}")
        logger.info(f"High quality (4-5 stars): {session_stats['high_quality']}")
        logger.info(f"\nRating distribution:")
        for rating in [5, 4, 3, 2, 1]:
            count = session_stats['ratings'][rating]
            if count > 0:
                bar = '█' * count
                logger.info(f"  {'⭐' * rating}: {bar} ({count})")
        logger.info("="*70)
        
        # Save session log
        self._save_session_log(domain, session_stats)
        
        return session_stats
    
    def _save_session_log(self, domain: str, stats: Dict):
        """Save session log to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"cursor_training_data/session_{domain}_{timestamp}.json"
        
        session_data = {
            'domain': domain,
            'timestamp': timestamp,
            'stats': stats,
            'log': self.training_log
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logger.info(f"\n💾 Session log saved: {filename}")
    
    def export_training_dataset(self, min_rating: int = 4) -> str:
        """
        Export training dataset from session
        
        Args:
            min_rating: Minimum rating to include
            
        Returns:
            Filename of exported dataset
        """
        # Filter high-quality examples
        dataset = []
        for entry in self.training_log:
            if entry['rating'] >= min_rating:
                dataset.append({
                    'instruction': entry['query'],
                    'input': '',
                    'output': entry['response'],
                    'metadata': {
                        'rating': entry['rating'],
                        'domain': entry['domain'],
                        'evaluation': entry['evaluation'],
                        'timestamp': entry['timestamp']
                    }
                })
        
        # Save dataset
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"cursor_training_data/dataset_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        logger.info(f"\n📦 Exported {len(dataset)} training examples: {filename}")
        return filename


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cursor AI Training Integration')
    parser.add_argument('--domain', default='technical',
                       choices=['technical', 'engineering', 'design', 'business'],
                       help='Training domain')
    parser.add_argument('--queries', type=int, default=20,
                       help='Number of queries to generate')
    parser.add_argument('--min-rating', type=int, default=4,
                       help='Minimum rating for export (1-5)')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between queries (seconds)')
    parser.add_argument('--gui-url', default='http://localhost:5001',
                       help='Training GUI URL')
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = CursorTrainingBot(args.gui_url)
    
    # Run training session
    stats = bot.automated_training_session(
        domain=args.domain,
        num_queries=args.queries,
        min_rating_threshold=args.min_rating,
        delay_between_queries=args.delay
    )
    
    # Export dataset
    if stats['high_quality'] > 0:
        bot.export_training_dataset(min_rating=args.min_rating)
    else:
        logger.warning("⚠️  No high-quality examples to export")
    
    logger.info("\n✅ Training session complete!")


if __name__ == '__main__':
    main()

