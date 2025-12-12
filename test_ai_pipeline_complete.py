#!/usr/bin/env python3
"""
Complete AI Pipeline Test
Tests: Request → AI Processing → Action Extraction → Execution → Response
"""

import time
import sys
import json
from datetime import datetime

print("🚀 COMPLETE AI PIPELINE TEST\n")
print("=" * 70)

results = {
    'timestamp': datetime.now().isoformat(),
    'tests': [],
    'summary': {}
}

def test_request(request: str, request_type: str = "General"):
    """Test a single request through the complete pipeline"""
    print(f"\n📤 Request ({request_type}): \"{request}\"")
    print("-" * 70)
    
    test_result = {
        'request': request,
        'type': request_type,
        'success': False,
        'response_time': 0,
        'response': '',
        'actions_count': 0,
        'actions_executed': 0,
        'errors': []
    }
    
    start_time = time.time()
    
    try:
        from core.unified_orchestrator import UnifiedOrchestrator
        
        orch = UnifiedOrchestrator()
        result = orch.process_text_command(request, enable_tts=False)
        
        elapsed = time.time() - start_time
        test_result['response_time'] = elapsed
        
        success = result.get('success', False)
        response = result.get('response', '')
        actions = result.get('actions', [])
        execution_results = result.get('execution_results', [])
        
        test_result['success'] = success
        test_result['response'] = response
        test_result['actions_count'] = len(actions)
        test_result['actions_executed'] = len(execution_results)
        
        print(f"⏱️  Response Time: {elapsed:.2f}s")
        print(f"✅ Success: {success}")
        print(f"📝 Response ({len(response)} chars):")
        print(f"   {response[:200]}{'...' if len(response) > 200 else ''}")
        print(f"🔧 Actions Extracted: {len(actions)}")
        print(f"⚡ Actions Executed: {len(execution_results)}")
        
        if actions:
            print("   Extracted Actions:")
            for i, action in enumerate(actions, 1):
                if isinstance(action, dict):
                    action_type = action.get('action_type', 'unknown')
                    tool = action.get('tool', 'unknown')
                    print(f"     {i}. {action_type}/{tool}")
                elif isinstance(action, str):
                    print(f"     {i}. {action}")
                else:
                    print(f"     {i}. {str(action)[:50]}")
        
        if execution_results:
            print("   Execution Results:")
            for i, exec_result in enumerate(execution_results, 1):
                if isinstance(exec_result, dict):
                    exec_success = exec_result.get('success', False)
                    action_type = exec_result.get('action_type', 'unknown')
                    error = exec_result.get('error', '')
                    print(f"     {i}. {action_type}: {'✅ Success' if exec_success else '❌ Failed'}")
                    if error:
                        print(f"        Error: {error[:100]}")
                else:
                    print(f"     {i}. {str(exec_result)[:100]}")
        
        if not success:
            error = result.get('error', 'Unknown error')
            test_result['errors'].append(error)
            print(f"❌ Error: {error}")
        
    except Exception as e:
        elapsed = time.time() - start_time
        test_result['response_time'] = elapsed
        test_result['errors'].append(str(e))
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    results['tests'].append(test_result)
    return test_result

# Test Suite
print("\n🧪 TESTING COMPLETE AI PIPELINE\n")

# Test 1: Simple Conversational
test_request("What is machine learning?", "Conversational")

# Test 2: System Monitoring
test_request("Check CPU and memory usage", "System Monitoring")

# Test 3: File Operations
test_request("List files in the current directory", "File Operations")

# Test 4: Business Operations
test_request("Generate an invoice for client TestCorp with amount 1500 dollars", "Business")

# Test 5: Multi-step Task
test_request("Check system health and create a summary report", "Multi-step")

# Test 6: Code/Technical
test_request("Explain how Python decorators work", "Technical")

# Test 7: Real Action Execution
test_request("Monitor CPU usage right now", "Action Execution")

# Summary
print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)

total_tests = len(results['tests'])
passed = sum(1 for t in results['tests'] if t['success'])
failed = total_tests - passed
total_actions = sum(t['actions_count'] for t in results['tests'])
executed_actions = sum(t['actions_executed'] for t in results['tests'])
response_times = [t['response_time'] for t in results['tests']]

print(f"\nTotal Tests: {total_tests}")
print(f"✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
print(f"❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
print(f"\nActions Extracted: {total_actions}")
print(f"Actions Executed: {executed_actions}")

if response_times:
    avg_time = sum(response_times) / len(response_times)
    min_time = min(response_times)
    max_time = max(response_times)
    
    print(f"\n⏱️  Response Times:")
    print(f"   Average: {avg_time:.2f}s")
    print(f"   Min: {min_time:.2f}s")
    print(f"   Max: {max_time:.2f}s")
    
    if avg_time < 2:
        print("   ✅ EXCELLENT: Average < 2s")
    elif avg_time < 5:
        print("   ✅ GOOD: Average < 5s")
    else:
        print("   ⚠️  MODERATE: Average >= 5s")

results['summary'] = {
    'total_tests': total_tests,
    'passed': passed,
    'failed': failed,
    'total_actions': total_actions,
    'executed_actions': executed_actions,
    'avg_response_time': sum(response_times) / len(response_times) if response_times else 0
}

# Save results
with open('ai_pipeline_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n💾 Results saved to: ai_pipeline_test_results.json")
print("\n" + "=" * 70)
print("✅ TEST COMPLETE!")
print("=" * 70)

sys.exit(0 if failed == 0 else 1)

