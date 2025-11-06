#!/usr/bin/env python3
"""
Quick Test - Optimized LLM System
Tests quantization, inference speed, and self-training
"""

import sys
import os
import logging
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.optimized_brain_integration import create_optimized_brain

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
    """Run comprehensive test"""
    
    print_header("🚀 Optimized LLM System - Quick Test")
    
    print("This test will:")
    print("  1. Load model with 4-bit quantization")
    print("  2. Perform warmup (2 iterations)")
    print("  3. Test inference speed (3 queries)")
    print("  4. Test self-training feedback collection")
    print("  5. Show performance statistics")
    print()
    
    input("Press Enter to start test... ")
    
    # Step 1: Initialize
    print_section("📦 Step 1: Initializing Optimized Brain")
    
    start_time = time.time()
    
    try:
        brain = create_optimized_brain(
            quantization="4bit",
            enable_self_training=True,
            auto_train=False
        )
    except Exception as e:
        print(f"\n❌ Failed to initialize brain: {e}")
        print("\nPossible issues:")
        print("  1. Model not found (check path)")
        print("  2. Dependencies missing (run: pip install -r requirements.txt)")
        print("  3. Insufficient memory (close other apps)")
        return 1
    
    init_time = time.time() - start_time
    
    if not brain.is_available():
        print("\n❌ Brain not available")
        return 1
    
    print(f"\n✅ Initialization complete in {init_time:.1f}s")
    
    # Step 2: Show stats
    print_section("📊 Step 2: System Statistics")
    
    stats = brain.get_stats()
    
    print(f"\nModel Configuration:")
    print(f"  • Quantization: {stats['quantization']}")
    print(f"  • Device: {stats['llm']['device']}")
    print(f"  • Memory: ~{stats['llm']['estimated_memory_gb']} GB")
    print(f"  • torch.compile: {'✅ Enabled' if stats['llm']['torch_compile_enabled'] else '❌ Disabled'}")
    print(f"  • Flash Attention: {'✅ Enabled' if stats['llm']['flash_attention_enabled'] else '❌ Disabled'}")
    
    print(f"\nSelf-Training:")
    print(f"  • Enabled: {'✅ Yes' if stats['self_training_enabled'] else '❌ No'}")
    print(f"  • Auto-train: {'✅ Yes' if stats['auto_train_enabled'] else '❌ No'}")
    
    # Step 3: Test inference
    print_section("🧪 Step 3: Testing Inference Speed")
    
    test_queries = [
        ("What is Python?", "technical"),
        ("Explain machine learning in simple terms", "technical"),
        ("How to optimize SQL queries?", "engineering")
    ]
    
    inference_times = []
    
    for i, (query, task_type) in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{len(test_queries)}: {query}")
        
        try:
            start = time.time()
            response = brain.get_response(
                user_input=query,
                max_length=150,
                temperature=0.7,
                task_type=task_type
            )
            elapsed = time.time() - start
            
            inference_times.append(elapsed)
            
            print(f"⚡ Response in {elapsed:.2f}s ({len(response)} chars)")
            print(f"📄 Preview: {response[:150]}...")
            
            # Simulate user feedback
            rating = 5 if i == 1 else 4
            brain.record_feedback(
                user_input=query,
                model_response=response,
                rating=rating,
                feedback_text="Test feedback",
                task_type=task_type
            )
            print(f"📊 Feedback recorded (rating: {rating})")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            continue
    
    # Step 4: Performance analysis
    print_section("📈 Step 4: Performance Analysis")
    
    if inference_times:
        avg_time = sum(inference_times) / len(inference_times)
        min_time = min(inference_times)
        max_time = max(inference_times)
        
        print(f"\nInference Times:")
        print(f"  • Average: {avg_time:.2f}s")
        print(f"  • Fastest: {min_time:.2f}s")
        print(f"  • Slowest: {max_time:.2f}s")
        print(f"  • Total queries: {len(inference_times)}")
        
        # Performance rating
        if avg_time < 3:
            rating = "🌟 Excellent"
        elif avg_time < 5:
            rating = "✅ Good"
        elif avg_time < 8:
            rating = "⚠️  Acceptable"
        else:
            rating = "❌ Slow"
        
        print(f"\nPerformance Rating: {rating}")
        
        if avg_time > 5:
            print("\n💡 Tips to improve speed:")
            print("  • First response is slower (torch.compile warmup)")
            print("  • Close other applications to free memory")
            print("  • Reduce max_length to 128 or less")
            print("  • Use GPU if available")
    
    # Step 5: Self-training status
    if brain.self_training_system:
        print_section("🤖 Step 5: Self-Training Status")
        
        st_stats = brain.self_training_system.get_status()
        
        print(f"\nFeedback Collection:")
        print(f"  • Total feedback: {st_stats['feedback']['total_feedback']}")
        print(f"  • Positive (4-5 stars): {st_stats['feedback']['positive']}")
        print(f"  • Negative (1-2 stars): {st_stats['feedback']['negative']}")
        print(f"  • Neutral (3 stars): {st_stats['feedback']['neutral']}")
        print(f"  • Positive rate: {st_stats['feedback']['positive_rate']:.1f}%")
        
        print(f"\nTraining Status:")
        print(f"  • Ready for training: {'✅ Yes' if st_stats['ready_for_training'] else '❌ No (need 100+ examples)'}")
        print(f"  • Training runs: {st_stats['training_runs']}")
        
        if st_stats['last_training']:
            print(f"  • Last training: {st_stats['last_training']['timestamp']}")
    
    # Final summary
    print_header("✅ Test Complete!")
    
    print("Summary:")
    print(f"  • Initialization: {init_time:.1f}s")
    if inference_times:
        print(f"  • Average inference: {avg_time:.2f}s")
    print(f"  • Memory usage: ~{stats['llm']['estimated_memory_gb']} GB")
    print(f"  • Queries tested: {len(test_queries)}")
    print()
    
    print("Next Steps:")
    print("  1. Integrate with hybrid brain (update core/hybrid_brain.py)")
    print("  2. Deploy to production")
    print("  3. Collect user feedback")
    print("  4. Retrain weekly/monthly for continuous improvement")
    print()
    
    print("📚 See OPTIMIZED_LLM_GUIDE.md for full documentation")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

