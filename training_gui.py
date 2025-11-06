#!/usr/bin/env python3
"""
Jarvis Training GUI - Simple Web Interface for Model Training
Allows users to interact with the model, rate responses, and build training datasets
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Import optimization components
try:
    from core.optimized_brain_integration import create_optimized_brain
    OPTIMIZED_AVAILABLE = True
except:
    OPTIMIZED_AVAILABLE = False
    print("⚠️  Optimized brain not available, using fallback")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training_gui.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, 
            static_folder='training_gui_static',
            template_folder='training_gui_templates')
CORS(app)

# Global brain instance
brain = None
conversation_history = []

def initialize_brain():
    """Initialize the optimized brain"""
    global brain
    
    if not OPTIMIZED_AVAILABLE:
        logger.warning("Optimized brain not available")
        return False
    
    try:
        logger.info("Initializing optimized brain...")
        brain = create_optimized_brain(
            quantization="4bit",
            enable_self_training=True,
            auto_train=False
        )
        
        if brain.is_available():
            logger.info("✅ Brain initialized successfully")
            return True
        else:
            logger.error("❌ Brain failed to initialize")
            return False
            
    except Exception as e:
        logger.error(f"❌ Brain initialization failed: {e}")
        return False


@app.route('/')
def index():
    """Serve the main training interface"""
    return render_template('training.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    global brain, conversation_history
    
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        task_type = data.get('task_type', 'general')
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400
        
        if not brain or not brain.is_available():
            return jsonify({'error': 'Model not loaded'}), 503
        
        # Generate response
        logger.info(f"Query: {user_input[:100]}...")
        
        start_time = datetime.now()
        response = brain.get_response(
            user_input=user_input,
            max_length=256,
            temperature=0.7,
            task_type=task_type
        )
        end_time = datetime.now()
        
        inference_time = (end_time - start_time).total_seconds()
        
        # Add to conversation history
        conversation_entry = {
            'id': len(conversation_history),
            'timestamp': start_time.isoformat(),
            'user_input': user_input,
            'model_response': response,
            'task_type': task_type,
            'inference_time': inference_time,
            'rating': None,
            'feedback': None
        }
        
        conversation_history.append(conversation_entry)
        
        logger.info(f"Response generated in {inference_time:.2f}s")
        
        return jsonify({
            'response': response,
            'conversation_id': conversation_entry['id'],
            'inference_time': inference_time,
            'timestamp': start_time.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rate', methods=['POST'])
def rate_response():
    """Rate a model response"""
    global brain, conversation_history
    
    try:
        data = request.json
        conversation_id = data.get('conversation_id')
        rating = data.get('rating')
        feedback_text = data.get('feedback', '')
        
        if conversation_id is None or rating is None:
            return jsonify({'error': 'Missing conversation_id or rating'}), 400
        
        if conversation_id >= len(conversation_history):
            return jsonify({'error': 'Invalid conversation_id'}), 400
        
        # Update conversation history
        conversation_history[conversation_id]['rating'] = rating
        conversation_history[conversation_id]['feedback'] = feedback_text
        
        # Record feedback in brain
        if brain and brain.self_training_system:
            entry = conversation_history[conversation_id]
            brain.record_feedback(
                user_input=entry['user_input'],
                model_response=entry['model_response'],
                rating=rating,
                feedback_text=feedback_text,
                task_type=entry['task_type']
            )
        
        logger.info(f"Rated conversation {conversation_id}: {rating} stars")
        
        return jsonify({
            'success': True,
            'message': 'Feedback recorded'
        })
        
    except Exception as e:
        logger.error(f"Rating error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    try:
        return jsonify({
            'history': conversation_history,
            'total': len(conversation_history)
        })
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get training statistics"""
    global brain
    
    try:
        stats = {
            'total_conversations': len(conversation_history),
            'rated_conversations': sum(1 for c in conversation_history if c['rating'] is not None),
            'avg_rating': 0,
            'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
        
        # Calculate rating stats
        rated = [c for c in conversation_history if c['rating'] is not None]
        if rated:
            stats['avg_rating'] = sum(c['rating'] for c in rated) / len(rated)
            for c in rated:
                stats['rating_distribution'][c['rating']] += 1
        
        # Get brain stats
        if brain and brain.is_available():
            brain_stats = brain.get_stats()
            stats['brain'] = brain_stats
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['GET'])
def export_dataset():
    """Export training dataset"""
    try:
        # Filter rated conversations
        rated = [c for c in conversation_history if c['rating'] is not None and c['rating'] >= 4]
        
        # Convert to training format
        dataset = []
        for entry in rated:
            dataset.append({
                'instruction': entry['user_input'],
                'input': '',
                'output': entry['model_response'],
                'metadata': {
                    'rating': entry['rating'],
                    'task_type': entry['task_type'],
                    'timestamp': entry['timestamp']
                }
            })
        
        return jsonify({
            'dataset': dataset,
            'total_examples': len(dataset),
            'export_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history
    
    try:
        conversation_history = []
        logger.info("Conversation history cleared")
        
        return jsonify({
            'success': True,
            'message': 'History cleared'
        })
        
    except Exception as e:
        logger.error(f"Clear error: {e}")
        return jsonify({'error': str(e)}), 500


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("  🎓 Jarvis Training GUI")
    print("="*70 + "\n")
    
    # Create directories
    Path('logs').mkdir(exist_ok=True)
    Path('training_gui_static').mkdir(exist_ok=True)
    Path('training_gui_templates').mkdir(exist_ok=True)
    
    # Initialize brain
    print("📦 Initializing optimized brain...")
    if initialize_brain():
        print("✅ Brain ready!\n")
    else:
        print("⚠️  Brain initialization failed (will use fallback)\n")
    
    # Start server
    print("🚀 Starting training GUI...")
    print(f"   URL: http://localhost:5001")
    print(f"   Logs: logs/training_gui.log")
    print("\nPress Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)


if __name__ == '__main__':
    main()

