#!/usr/bin/env python3
"""
Complete AI Integration Test
Tests the full pipeline: Request → AI Processing → Action Extraction → Execution → Response
"""

import time
import sys
import json
from typing import Dict, Any

print("🧪 Complete AI Integration Test\n")
print("=" * 70)

# Test results
results = {
    'total_tests': 0,
    'passed': 0,
    'failed': 0,
    'response_times': [],
    'test_details': []
}

def test_unified_orchestrator():
    """Test unified orchestrator with various request types"""
    print("\n📋 Testing Unified Orchestrator\n")
    print("-" * 70)
    
    try:
        from core.unified_orchestrator import UnifiedOrchestrator
        
        orch = UnifiedOrchestrator()
        
        # Check availability
        status = orch.get_status()
        print(f"✅ Unified Orchestrator initialized")
        print(f"   AI Available: {status.get('ai_available', False)}")
        print(f"   STT Available: {status.get('stt_available', False)}")
        print(f"   TTS Available: {status.get('tts_available', False)}")
        print()
        
        # Test cases
        test_cases = [
            {
                'name': 'Simple Question',
                'request': 'What is Python programming?',
                'expected_actions': 0,
                'description': 'Should return conversational response'
            },
            {
                'name': 'System Monitoring',
                'request': 'Check CPU usage',
                'expected_actions': 1,
                'description': 'Should extract system monitoring action'
            },
            {
                'name': 'Business Operation',
                'request': 'Generate an invoice for client ABC with amount 1000',
                'expected_actions': 1,
                'description': 'Should extract business action'
            },
            {
                'name': 'Multi-step Request',
                'request': 'Check system status and then create a report',
                'expected_actions': 2,
                'description': 'Should extract multiple actions'
            },
            {
                'name': 'Code Analysis',
                'request': 'Analyze the code in the current directory',
                'expected_actions': 0,
                'description': 'Should return code analysis response'
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"Test {i}/{len(test_cases)}: {test['name']}")
            print(f"Request: \"{test['request']}\"")
            print(f"Expected: {test['description']}")
            
            start_time = time.time()
            try:
                result = orch.process_text_command(test['request'], enable_tts=False)
                elapsed = time.time() - start_time
                
                results['total_tests'] += 1
                results['response_times'].append(elapsed)
                
                success = result.get('success', False)
                response = result.get('response', '')
                actions = result.get('actions', [])
                
                print(f"⏱️  Response time: {elapsed:.2f}s")
                print(f"✅ Success: {success}")
                print(f"📝 Response length: {len(response)} chars")
                print(f"🔧 Actions extracted: {len(actions)}")
                
                if actions:
                    print("   Actions:")
                    for action in actions:
                        # Handle both dict and string formats
                        if isinstance(action, dict):
                            action_type = action.get('action_type', 'unknown')
                            description = action.get('description', '')
                        elif isinstance(action, str):
                            action_type = action
                            description = ''
                        else:
                            action_type = str(type(action).__name__)
                            description = str(action)
                        print(f"     - {action_type}: {description[:50]}")
                
                # Validate
                if success:
                    if len(actions) >= test['expected_actions']:
                        results['passed'] += 1
                        print("✅ PASSED")
                    else:
                        results['failed'] += 1
                        print(f"⚠️  PARTIAL: Expected {test['expected_actions']} actions, got {len(actions)}")
                else:
                    results['failed'] += 1
                    print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                
                results['test_details'].append({
                    'test': test['name'],
                    'success': success,
                    'response_time': elapsed,
                    'actions_count': len(actions),
                    'response_preview': response[:100] + '...' if len(response) > 100 else response
                })
                
            except Exception as e:
                results['total_tests'] += 1
                results['failed'] += 1
                print(f"❌ ERROR: {e}")
                import traceback
                traceback.print_exc()
            
            print()
        
        return True
        
    except ImportError as e:
        print(f"❌ Unified Orchestrator not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hybrid_brain():
    """Test hybrid brain system"""
    print("\n📋 Testing Hybrid Brain System\n")
    print("-" * 70)
    
    try:
        from core.hybrid_brain import HybridBrain
        
        brain = HybridBrain()
        
        test_cases = [
            'What is machine learning?',
            'Check CPU usage',
            'Hello, how are you?',
            'Generate an invoice for client XYZ'
        ]
        
        for i, request in enumerate(test_cases, 1):
            print(f"Test {i}/{len(test_cases)}: \"{request}\"")
            
            start_time = time.time()
            try:
                response = brain.get_response(request)
                elapsed = time.time() - start_time
                
                results['total_tests'] += 1
                results['response_times'].append(elapsed)
                
                print(f"⏱️  Response time: {elapsed:.2f}s")
                print(f"📝 Response: {response[:150]}...")
                print(f"✅ SUCCESS")
                print()
                
                results['passed'] += 1
                results['test_details'].append({
                    'test': f'Hybrid Brain: {request[:30]}',
                    'success': True,
                    'response_time': elapsed,
                    'response_preview': response[:100]
                })
                
            except Exception as e:
                results['total_tests'] += 1
                results['failed'] += 1
                print(f"❌ ERROR: {e}")
                print()
        
        # Get statistics
        stats = brain.get_statistics()
        print("📊 Hybrid Brain Statistics:")
        print(f"   Total Calls: {stats.get('total_calls', 0)}")
        print(f"   LLM Calls: {stats.get('llm_calls', 0)}")
        print(f"   HelaGPT Calls: {stats.get('helagpt_calls', 0)}")
        print(f"   LLM Available: {stats.get('llm_available', False)}")
        print(f"   HelaGPT Available: {stats.get('helagpt_available', False)}")
        print()
        
        return True
        
    except ImportError as e:
        print(f"⚠️  Hybrid Brain not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_action_execution():
    """Test action extraction and execution"""
    print("\n📋 Testing Action Execution\n")
    print("-" * 70)
    
    try:
        from core.unified_orchestrator import UnifiedOrchestrator
        
        orch = UnifiedOrchestrator()
        
        action_tests = [
            {
                'request': 'Check CPU and memory usage',
                'expected_actions': ['monitor_cpu', 'monitor_memory']
            },
            {
                'request': 'List files in the current directory',
                'expected_actions': ['list_directory']
            },
            {
                'request': 'Generate invoice for client Test with amount 500',
                'expected_actions': ['generate_invoice']
            }
        ]
        
        for i, test in enumerate(action_tests, 1):
            print(f"Test {i}/{len(action_tests)}: \"{test['request']}\"")
            
            start_time = time.time()
            try:
                result = orch.process_text_command(test['request'], enable_tts=False)
                elapsed = time.time() - start_time
                
                actions = result.get('actions', [])
                execution_results = result.get('execution_results', [])
                
                print(f"⏱️  Response time: {elapsed:.2f}s")
                print(f"🔧 Actions extracted: {len(actions)}")
                print(f"✅ Actions executed: {len(execution_results)}")
                
                if execution_results:
                    for j, exec_result in enumerate(execution_results, 1):
                        success = exec_result.get('success', False)
                        action_type = exec_result.get('action_type', 'unknown')
                        print(f"   Action {j}: {action_type} - {'✅ Success' if success else '❌ Failed'}")
                
                results['total_tests'] += 1
                if result.get('success') and len(actions) > 0:
                    results['passed'] += 1
                    print("✅ PASSED")
                else:
                    results['failed'] += 1
                    print("⚠️  PARTIAL or FAILED")
                
                print()
                
            except Exception as e:
                results['total_tests'] += 1
                results['failed'] += 1
                print(f"❌ ERROR: {e}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing actions: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_quality():
    """Test response quality and format"""
    print("\n📋 Testing Response Quality\n")
    print("-" * 70)
    
    try:
        from core.unified_orchestrator import UnifiedOrchestrator
        
        orch = UnifiedOrchestrator()
        
        quality_tests = [
            {
                'request': 'Explain quantum computing',
                'min_length': 50,
                'should_have': ['quantum', 'computing']
            },
            {
                'request': 'What is the weather today?',
                'min_length': 20,
                'should_have': []
            }
        ]
        
        for i, test in enumerate(quality_tests, 1):
            print(f"Test {i}/{len(quality_tests)}: \"{test['request']}\"")
            
            start_time = time.time()
            try:
                result = orch.process_text_command(test['request'], enable_tts=False)
                elapsed = time.time() - start_time
                
                response = result.get('response', '')
                response_lower = response.lower()
                
                print(f"⏱️  Response time: {elapsed:.2f}s")
                print(f"📝 Response length: {len(response)} chars")
                print(f"📄 Preview: {response[:200]}...")
                
                # Quality checks
                checks = []
                if len(response) >= test['min_length']:
                    checks.append("✅ Length sufficient")
                else:
                    checks.append(f"❌ Length too short (min: {test['min_length']})")
                
                for keyword in test['should_have']:
                    if keyword.lower() in response_lower:
                        checks.append(f"✅ Contains '{keyword}'")
                    else:
                        checks.append(f"⚠️  Missing '{keyword}'")
                
                for check in checks:
                    print(f"   {check}")
                
                results['total_tests'] += 1
                if result.get('success') and len(response) >= test['min_length']:
                    results['passed'] += 1
                    print("✅ PASSED")
                else:
                    results['failed'] += 1
                    print("⚠️  QUALITY ISSUES")
                
                print()
                
            except Exception as e:
                results['total_tests'] += 1
                results['failed'] += 1
                print(f"❌ ERROR: {e}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing quality: {e}")
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print()
    
    print(f"Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed']} ({results['passed']/results['total_tests']*100:.1f}%)" if results['total_tests'] > 0 else "✅ Passed: 0")
    print(f"❌ Failed: {results['failed']} ({results['failed']/results['total_tests']*100:.1f}%)" if results['total_tests'] > 0 else "❌ Failed: 0")
    print()
    
    if results['response_times']:
        avg_time = sum(results['response_times']) / len(results['response_times'])
        min_time = min(results['response_times'])
        max_time = max(results['response_times'])
        
        print("⏱️  Response Times:")
        print(f"   Average: {avg_time:.2f}s")
        print(f"   Min: {min_time:.2f}s")
        print(f"   Max: {max_time:.2f}s")
        print()
        
        if avg_time < 2:
            print("✅ EXCELLENT: Average response time < 2s")
        elif avg_time < 5:
            print("✅ GOOD: Average response time < 5s")
        elif avg_time < 10:
            print("⚠️  MODERATE: Average response time 5-10s")
        else:
            print("❌ SLOW: Average response time > 10s")
        print()
    
    # Save results
    with open('ai_integration_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("💾 Results saved to: ai_integration_test_results.json")
    print()
    print("=" * 70)

# Run all tests
if __name__ == "__main__":
    print("Starting complete AI integration tests...\n")
    
    # Test 1: Unified Orchestrator
    test_unified_orchestrator()
    
    # Test 2: Hybrid Brain
    test_hybrid_brain()
    
    # Test 3: Action Execution
    test_action_execution()
    
    # Test 4: Response Quality
    test_response_quality()
    
    # Print summary
    print_summary()
    
    # Exit code
    sys.exit(0 if results['failed'] == 0 else 1)

