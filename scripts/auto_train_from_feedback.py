#!/usr/bin/env python3
"""
Automated Training from Feedback
Exports feedback dataset and triggers training run
"""

import sys
import os
import logging
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning.self_training_system import FeedbackCollector, ContinualTrainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_section(text):
    """Print formatted section"""
    print("\n" + "-"*70)
    print(f"  {text}")
    print("-"*70)


def main():
    """Main training automation"""
    
    print_header("🤖 Automated Training from Feedback")
    
    # Initialize components
    print_section("📊 Step 1: Checking Feedback Data")
    
    feedback_collector = FeedbackCollector("data/feedback")
    stats = feedback_collector.get_stats()
    
    print(f"\nFeedback Statistics:")
    print(f"  • Total feedback: {stats['total_feedback']}")
    print(f"  • Positive (4-5 stars): {stats['positive']}")
    print(f"  • Negative (1-2 stars): {stats['negative']}")
    print(f"  • Neutral (3 stars): {stats['neutral']}")
    print(f"  • Positive rate: {stats['positive_rate']:.1f}%")
    
    # Check if ready
    if not stats['ready_for_training']:
        print(f"\n⚠️  Not ready for training yet")
        print(f"   Need at least 100 positive examples")
        print(f"   Current: {stats['positive']}/100")
        print()
        print("Collect more feedback and try again!")
        return 1
    
    print(f"\n✅ Ready for training! ({stats['positive']} positive examples)")
    
    # Ask for confirmation
    print()
    proceed = input("Proceed with training? (yes/no): ").strip().lower()
    
    if proceed not in ['yes', 'y']:
        print("\n❌ Training cancelled")
        return 0
    
    # Export dataset
    print_section("📦 Step 2: Exporting Training Dataset")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dataset_file = f"data/feedback/training_dataset_{timestamp}.jsonl"
    
    try:
        feedback_collector.export_training_dataset(
            output_file=dataset_file,
            min_rating=4,
            format="alpaca"
        )
        
        print(f"\n✅ Dataset exported to: {dataset_file}")
        
        # Show sample
        with open(dataset_file, 'r') as f:
            first_line = f.readline()
            sample = json.loads(first_line)
            print(f"\n📄 Sample Entry:")
            print(f"   Instruction: {sample['instruction'][:80]}...")
            print(f"   Output: {sample['output'][:80]}...")
        
    except Exception as e:
        print(f"\n❌ Failed to export dataset: {e}")
        return 1
    
    # Prepare training
    print_section("🚀 Step 3: Preparing Training")
    
    model_path = "jarvis-llm-brain-final fine tune 7B model"
    if not os.path.exists(model_path):
        model_path = "models/jarvis-llm-brain-final"
    
    output_dir = f"models/jarvis-trained-{timestamp}"
    
    print(f"\nTraining Configuration:")
    print(f"  • Base model: {model_path}")
    print(f"  • Dataset: {dataset_file}")
    print(f"  • Output: {output_dir}")
    print(f"  • Examples: {stats['positive']}")
    
    # Training parameters
    print(f"\nTraining Parameters:")
    print(f"  • Epochs: 3")
    print(f"  • Learning rate: 2e-4")
    print(f"  • Batch size: 4")
    print(f"  • Min rating: 4 stars")
    
    print()
    confirm = input("Start training? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\n❌ Training cancelled")
        return 0
    
    # Trigger training
    print_section("🔥 Step 4: Training Model")
    
    print("\n⚠️  TRAINING SIMULATION")
    print("=" * 70)
    print()
    print("In production, this would:")
    print("  1. Load base model")
    print("  2. Prepare LoRA adapters")
    print("  3. Train on feedback dataset")
    print("  4. Save updated model")
    print("  5. Evaluate on validation set")
    print()
    print("Estimated time: 2-4 hours on GPU, 12-24 hours on CPU")
    print()
    print("For actual training, use one of these methods:")
    print()
    print("Option 1: Google Colab Pro (Recommended)")
    print("  • Upload dataset to Colab")
    print("  • Use JarvisX_V2_LLM_Training.ipynb")
    print("  • Train with A100 GPU (faster)")
    print("  • Download trained model")
    print()
    print("Option 2: Local Training")
    print("  • Use training script: scripts/train_lora.py")
    print("  • Requires GPU for reasonable speed")
    print("  • Monitor with tensorboard")
    print()
    print("Option 3: Hugging Face AutoTrain")
    print("  • Upload dataset to HF")
    print("  • Use AutoTrain UI")
    print("  • Download trained model")
    print()
    
    trainer = ContinualTrainer(model_path)
    
    result = trainer.trigger_training(
        dataset_file=dataset_file,
        output_dir=output_dir,
        num_epochs=3,
        learning_rate=2e-4
    )
    
    if result['success']:
        print_section("✅ Step 5: Training Complete")
        
        print(f"\nTraining ID: {result['training_id']}")
        print(f"Output directory: {result['output_dir']}")
        print()
        print("Next Steps:")
        print(f"  1. Backup current model:")
        print(f"     mv '{model_path}' '{model_path}.backup.{timestamp}'")
        print()
        print(f"  2. Deploy new model:")
        print(f"     mv '{output_dir}' '{model_path}'")
        print()
        print(f"  3. Test new model:")
        print(f"     python3 scripts/quick_test_optimized.py")
        print()
        print(f"  4. If issues, restore backup:")
        print(f"     mv '{model_path}.backup.{timestamp}' '{model_path}'")
        print()
        
    else:
        print_section("❌ Training Failed")
        print(f"\nError: {result.get('error')}")
        print()
        print("Check logs for details")
    
    # Show training history
    print_section("📊 Training History")
    
    history = trainer.get_history()
    
    print(f"\nTotal training runs: {len(history)}")
    print()
    
    if history:
        print("Recent training runs:")
        for run in history[-5:]:  # Last 5 runs
            print(f"\n  • ID: {run['id']}")
            print(f"    Date: {run['timestamp']}")
            print(f"    Status: {run['status']}")
            if 'completed_at' in run:
                print(f"    Completed: {run['completed_at']}")
    
    print_header("🎉 Automation Complete!")
    
    print("Summary:")
    print(f"  • Feedback collected: {stats['total_feedback']}")
    print(f"  • Training examples: {stats['positive']}")
    print(f"  • Dataset: {dataset_file}")
    print(f"  • Status: Training {'completed' if result['success'] else 'failed'}")
    print()
    
    return 0 if result['success'] else 1


if __name__ == "__main__":
    sys.exit(main())

