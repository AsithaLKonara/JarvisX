#!/usr/bin/env python3
"""
Demo: Automated Training System
Shows what the Cursor AI integration does without needing the full model
"""

import random
import time
from datetime import datetime

def generate_queries(domain='technical', count=10):
    """Generate sample training queries"""
    
    templates = {
        'technical': [
            "What is {topic} and how does it work?",
            "Explain {topic} in simple terms",
            "Compare {topic1} vs {topic2}",
            "How to optimize {topic}?",
            "Best practices for {topic}?"
        ]
    }
    
    topics = [
        'machine learning', 'Docker', 'Kubernetes', 'REST APIs',
        'GraphQL', 'microservices', 'CI/CD', 'cloud computing'
    ]
    
    queries = []
    for _ in range(count):
        template = random.choice(templates[domain])
        if '{topic1}' in template:
            t1, t2 = random.sample(topics, 2)
            query = template.replace('{topic1}', t1).replace('{topic2}', t2)
        else:
            topic = random.choice(topics)
            query = template.replace('{topic}', topic)
        queries.append(query)
    
    return queries


def simulate_response(query):
    """Simulate a model response"""
    responses = [
        f"{query.split()[1] if len(query.split()) > 1 else 'This'} is a fundamental concept in modern software development. It involves several key principles:\n\n1. First, understand the core architecture\n2. Implement best practices\n3. Consider scalability and performance\n4. Test thoroughly\n\nExample: When implementing this, start with a simple prototype and iterate based on feedback.",
        
        f"Great question! {query.split()[1] if len(query.split()) > 1 else 'This topic'} has revolutionized how we build applications. Key points:\n\n• Core concept: Distributed systems\n• Benefits: Scalability, flexibility\n• Trade-offs: Complexity vs simplicity\n• Best use cases: Enterprise applications\n\nIn practice, you'll want to start small and gradually adopt these patterns.",
        
        f"To answer this effectively, let's break it down:\n\n**What it is:** A modern approach to software architecture\n**How it works:** By separating concerns and enabling independent scaling\n**Why it matters:** Improves maintainability and team velocity\n\nCode example:\n```python\n# Simple implementation\nclass Service:\n    def process(self, data):\n        return data\n```"
    ]
    
    return random.choice(responses)


def evaluate_response(query, response):
    """Evaluate response quality"""
    score = 0
    feedback = []
    
    # Length check
    if 50 <= len(response) <= 1000:
        score += 15
        feedback.append("✅ Good length")
    
    # Structure
    if '\n' in response:
        score += 15
        feedback.append("✅ Well-structured")
    
    # Technical terms
    technical_terms = ['api', 'system', 'architecture', 'code', 'implement']
    if any(term in response.lower() for term in technical_terms):
        score += 15
        feedback.append("✅ Technical depth")
    
    # Actionable
    if any(word in response.lower() for word in ['first', 'step', 'example']):
        score += 15
        feedback.append("✅ Actionable advice")
    
    # Examples
    if '```' in response or 'example' in response.lower():
        score += 20
        feedback.append("✅ Includes examples")
    
    # Quality markers
    if any(marker in response.lower() for marker in ['best practice', 'key', 'important']):
        score += 20
        feedback.append("✅ Quality markers")
    
    rating = min(5, max(1, int((score / 100) * 5) + 1))
    
    return {
        'rating': rating,
        'score': score,
        'percentage': score,
        'feedback': feedback
    }


def run_demo():
    """Run the demonstration"""
    print("\n" + "="*70)
    print("  🤖 AUTOMATED TRAINING SYSTEM - DEMONSTRATION")
    print("="*70)
    print()
    print("This shows what the Cursor AI integration does:")
    print("  1. Auto-generate diverse queries")
    print("  2. Send to model for responses")
    print("  3. Auto-evaluate quality")
    print("  4. Auto-rate 1-5 stars")
    print("  5. Export training dataset")
    print()
    print("="*70)
    print()
    
    # Generate queries
    print("📝 STEP 1: Generating Training Queries")
    print("-"*70)
    queries = generate_queries('technical', 10)
    print(f"✅ Generated {len(queries)} technical queries:\n")
    for i, q in enumerate(queries, 1):
        print(f"   {i}. {q}")
    print()
    
    input("Press Enter to continue...")
    print()
    
    # Process queries
    print("🤖 STEP 2: Processing Queries & Evaluating Responses")
    print("-"*70)
    print()
    
    results = []
    stats = {'total': 0, 'ratings': {1:0, 2:0, 3:0, 4:0, 5:0}}
    
    for i, query in enumerate(queries[:5], 1):  # Demo 5 queries
        print(f"{'─'*70}")
        print(f"Query {i}/5")
        print(f"{'─'*70}")
        print(f"📝 Query: {query}")
        print()
        
        # Simulate response time
        print("⏳ Generating response...", end='', flush=True)
        time.sleep(0.5)
        response = simulate_response(query)
        print(" ✅ Done (0.5s)")
        print()
        
        print(f"💬 Response:")
        print(f"   {response[:150]}...")
        print()
        
        # Evaluate
        print("📊 Evaluating...")
        evaluation = evaluate_response(query, response)
        rating = evaluation['rating']
        
        print(f"   Rating: {'⭐' * rating} ({rating}/5)")
        print(f"   Score: {evaluation['score']}/100 ({evaluation['percentage']}%)")
        for fb in evaluation['feedback']:
            print(f"   {fb}")
        print()
        
        stats['total'] += 1
        stats['ratings'][rating] += 1
        
        results.append({
            'query': query,
            'response': response,
            'rating': rating,
            'evaluation': evaluation
        })
        
        if i < 5:
            time.sleep(0.3)
    
    # Summary
    print("="*70)
    print("📊 SESSION SUMMARY")
    print("="*70)
    print(f"Total queries processed: {stats['total']}")
    high_quality = stats['ratings'][4] + stats['ratings'][5]
    print(f"High quality (4-5 stars): {high_quality}")
    print()
    print("Rating distribution:")
    for rating in [5, 4, 3, 2, 1]:
        count = stats['ratings'][rating]
        if count > 0:
            bar = '█' * count
            print(f"  {'⭐' * rating}: {bar} ({count})")
    print("="*70)
    print()
    
    # Show what gets exported
    print("📦 STEP 3: Export Training Dataset")
    print("-"*70)
    print()
    print(f"Exporting {high_quality} high-quality examples (4-5 stars)...")
    print()
    
    dataset = []
    for r in results:
        if r['rating'] >= 4:
            dataset.append({
                'instruction': r['query'],
                'input': '',
                'output': r['response'],
                'metadata': {
                    'rating': r['rating'],
                    'domain': 'technical',
                    'timestamp': datetime.now().isoformat()
                }
            })
    
    print("Sample training example:")
    print("-"*70)
    if dataset:
        import json
        print(json.dumps(dataset[0], indent=2))
    print()
    
    print("="*70)
    print("✅ DEMONSTRATION COMPLETE!")
    print("="*70)
    print()
    print("This is what happens automatically when you run:")
    print("  python3 cursor_training_integration.py --queries 100")
    print()
    print("With the real system:")
    print("  • Uses your actual optimized model")
    print("  • Processes 100s of queries automatically")
    print("  • Saves to cursor_training_data/")
    print("  • Ready for model retraining")
    print()
    print("🎯 Result: High-quality training dataset in minutes!")
    print()


if __name__ == '__main__':
    run_demo()

