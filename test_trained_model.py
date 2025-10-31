#!/usr/bin/env python3
"""
Comprehensive Test Suite for Trained Jarvis LLM Model
Tests all 7 operational modes + cross-platform + job capabilities
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Test cases covering all training domains
TEST_CASES = {
    "Engineer Mode": [
        "How do I optimize Python code for performance?",
        "Explain the difference between stack and heap memory",
        "What are the SOLID principles in software engineering?",
        "How do I implement binary search in Python?",
        "What is the time complexity of quicksort?",
    ],
    
    "System Monitor": [
        "Show me current CPU usage",
        "How much RAM is being used?",
        "List the top 5 processes by memory usage",
        "What is the disk space available?",
        "Check system temperature",
    ],
    
    "Designer Mode": [
        "How do I create a color palette for a website?",
        "What are the principles of good UI design?",
        "Explain the difference between RGB and CMYK",
        "How do I use Photoshop layers effectively?",
        "What is the golden ratio in design?",
    ],
    
    "Editor Mode": [
        "How do I add captions to a video?",
        "What is the best export format for YouTube videos?",
        "Explain color grading in video editing",
        "How do I create smooth transitions?",
        "What is B-roll footage?",
    ],
    
    "Business Mode": [
        "How do I create an invoice?",
        "Explain the difference between profit and revenue",
        "What is a cash flow statement?",
        "How do I calculate ROI?",
        "What are KPIs in business?",
    ],
    
    "Casual/Sinhala": [
        "Hello, how are you?",
        "Tell me a joke",
        "සුභ උදෑසනක්",  # Good morning in Sinhala
        "What's the weather like today?",
        "Recommend a good movie",
    ],
    
    "Cross-Platform": [
        "How do I automate Android tasks?",
        "Explain iOS Shortcuts automation",
        "What is remote desktop access?",
        "How do I control my smart home devices?",
        "Explain mobile app testing",
    ],
    
    "Job-Specific (IT)": [
        "What does a Software Engineer do?",
        "Explain the role of a DevOps Engineer",
        "What skills does a Data Scientist need?",
        "How do I become a Cybersecurity Analyst?",
        "What is the career path for a Web Developer?",
    ],
    
    "Job-Specific (Finance)": [
        "What does an Accountant do?",
        "Explain the role of a Financial Analyst",
        "What skills does an Auditor need?",
        "How do I become a Tax Consultant?",
        "What is the difference between CPA and CFA?",
    ],
    
    "Job-Specific (Creative)": [
        "What does a Graphic Designer do?",
        "Explain the role of a Video Editor",
        "What skills does a Content Creator need?",
        "How do I become a UI/UX Designer?",
        "What is motion graphics design?",
    ]
}


def test_jarvis_brain():
    """Test Jarvis brain with comprehensive test suite"""
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                          ║")
    print("║         🧪 Jarvis X V2 - Trained Model Comprehensive Test               ║")
    print("║                                                                          ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Import brain
    try:
        from jarvis_llm_brain import JarvisLLMBrain
        print("✅ Imported JarvisLLMBrain")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    print()
    print("📦 Initializing Jarvis brain...")
    print()
    
    # Initialize
    try:
        brain = JarvisLLMBrain()
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Check availability
    if not brain.is_available():
        print()
        print("❌ Brain not available!")
        print()
        print("🔧 Possible solutions:")
        print("   1. Deploy to Hugging Face Space and set CLOUD_LLM_URL")
        print("   2. Install GGUF model in models/gguf/")
        print("   3. Set up Ollama with jarvis-brain model")
        print()
        return False
    
    # Show brain stats
    stats = brain.get_stats()
    print()
    print("📊 Brain Status:")
    print(f"   Loaded: {stats['loaded']}")
    print(f"   GGUF (local): {stats['gguf_available']}")
    print(f"   Ollama: {stats['ollama_available']}")
    print(f"   Cloud: {stats['cloud_available']}")
    print(f"   Wrapper: {stats['wrapper_available']}")
    print(f"   Model Path: {stats['model_path']}")
    print()
    
    # Determine active backend
    if stats['gguf_available']:
        backend = "GGUF (Local - Fast)"
    elif stats['ollama_available']:
        backend = "Ollama (Local - Fast)"
    elif stats['cloud_available']:
        backend = "Cloud LLM (Hugging Face Space)"
    elif stats['wrapper_available']:
        backend = "Python Wrapper (Slower)"
    else:
        backend = "Unknown"
    
    print(f"🚀 Active Backend: {backend}")
    print()
    
    # Run tests
    print("=" * 74)
    print()
    print("🧪 RUNNING COMPREHENSIVE TESTS")
    print()
    print("=" * 74)
    print()
    
    results = {}
    total_tests = sum(len(tests) for tests in TEST_CASES.values())
    current_test = 0
    passed = 0
    failed = 0
    
    for category, test_queries in TEST_CASES.items():
        print(f"\n📋 {category}")
        print("-" * 74)
        
        category_results = []
        
        for query in test_queries:
            current_test += 1
            print(f"\n[{current_test}/{total_tests}] Testing: {query[:60]}...")
            
            try:
                response = brain.generate_response(query, max_length=200, temperature=0.7)
                
                # Basic quality checks
                if len(response) < 10:
                    status = "❌ FAIL"
                    reason = "Response too short"
                    failed += 1
                elif "error" in response.lower() and "failed" in response.lower():
                    status = "❌ FAIL"
                    reason = "Error in response"
                    failed += 1
                else:
                    status = "✅ PASS"
                    reason = f"Generated {len(response)} chars"
                    passed += 1
                
                print(f"   {status} - {reason}")
                print(f"   Response: {response[:100]}...")
                
                category_results.append({
                    "query": query,
                    "response": response,
                    "status": "pass" if status == "✅ PASS" else "fail",
                    "reason": reason
                })
                
            except Exception as e:
                status = "❌ ERROR"
                reason = str(e)
                failed += 1
                print(f"   {status} - {reason}")
                
                category_results.append({
                    "query": query,
                    "response": None,
                    "status": "error",
                    "reason": reason
                })
        
        results[category] = category_results
    
    # Summary
    print()
    print("=" * 74)
    print()
    print("📊 TEST SUMMARY")
    print()
    print("=" * 74)
    print()
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
    print(f"   ❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
    print()
    print(f"   Backend: {backend}")
    print()
    
    # Grade
    success_rate = passed / total_tests * 100
    if success_rate >= 95:
        grade = "A+ (Excellent!)"
    elif success_rate >= 90:
        grade = "A (Great!)"
    elif success_rate >= 85:
        grade = "B+ (Good)"
    elif success_rate >= 80:
        grade = "B (Acceptable)"
    elif success_rate >= 75:
        grade = "C+ (Needs Improvement)"
    else:
        grade = "C (Poor)"
    
    print(f"   Grade: {grade}")
    print()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    full_results = {
        "timestamp": datetime.now().isoformat(),
        "backend": backend,
        "stats": stats,
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "grade": grade,
        "results_by_category": results
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {results_file}")
    print()
    
    # Final message
    if success_rate >= 90:
        print("╔══════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                          ║")
        print("║              🎉 EXCELLENT! YOUR MODEL IS READY! 🎉                      ║")
        print("║                                                                          ║")
        print("╚══════════════════════════════════════════════════════════════════════════╝")
        print()
        print("✅ Your trained model is performing excellently!")
        print("✅ Ready for production use!")
        print()
    elif success_rate >= 75:
        print("╔══════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                          ║")
        print("║              ✅ GOOD! MODEL WORKING WELL                                ║")
        print("║                                                                          ║")
        print("╚══════════════════════════════════════════════════════════════════════════╝")
        print()
        print("✅ Your trained model is working well!")
        print("💡 Some fine-tuning might improve results")
        print()
    else:
        print("╔══════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                          ║")
        print("║              ⚠️  NEEDS IMPROVEMENT                                      ║")
        print("║                                                                          ║")
        print("╚══════════════════════════════════════════════════════════════════════════╝")
        print()
        print("⚠️  Model needs improvement")
        print("🔧 Check training logs and consider retraining")
        print()
    
    return success_rate >= 75


if __name__ == "__main__":
    success = test_jarvis_brain()
    sys.exit(0 if success else 1)

