#!/bin/bash

# Demo script for Orchestrator service
# Tests task planning, approval, and execution flow

echo "🎯 JarvisX Orchestrator Demo"
echo "============================"

# Check if orchestrator is running
echo "Checking orchestrator health..."
curl -s http://localhost:3000/health | jq '.' || {
    echo "❌ Orchestrator is not running. Please start it with: docker-compose up orchestrator"
    exit 1
}

echo "✅ Orchestrator is running"

# Test 1: Create a simple task
echo -e "\n📝 Test 1: Creating a simple task"
TASK_RESPONSE=$(curl -s -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Open Cursor IDE",
    "user_id": "demo_user",
    "context": {"preferences": {"auto_approve_simple": true}}
  }')

echo "$TASK_RESPONSE" | jq '.'

TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.task_id')

if [ "$TASK_ID" = "null" ] || [ -z "$TASK_ID" ]; then
    echo "❌ Failed to create task"
    exit 1
fi

echo "✅ Task created with ID: $TASK_ID"

# Test 2: Get task details
echo -e "\n📋 Test 2: Getting task details"
curl -s http://localhost:3000/tasks/$TASK_ID | jq '.'

# Test 3: Dry run approval
echo -e "\n🔍 Test 3: Dry run approval"
curl -s -X PATCH http://localhost:3000/tasks/$TASK_ID/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "demo_user", "dry_run": true}' | jq '.'

# Test 4: Real approval (if not auto-approved)
echo -e "\n✅ Test 4: Real approval"
curl -s -X PATCH http://localhost:3000/tasks/$TASK_ID/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "demo_user", "dry_run": false}' | jq '.'

# Test 5: Create a more complex task
echo -e "\n🛒 Test 5: Creating e-commerce order task"
COMPLEX_TASK_RESPONSE=$(curl -s -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create order for John Smith, 2 laptops, deliver tomorrow",
    "user_id": "demo_user"
  }')

echo "$COMPLEX_TASK_RESPONSE" | jq '.'

COMPLEX_TASK_ID=$(echo "$COMPLEX_TASK_RESPONSE" | jq -r '.task_id')

if [ "$COMPLEX_TASK_ID" != "null" ] && [ -n "$COMPLEX_TASK_ID" ]; then
    echo "✅ Complex task created with ID: $COMPLEX_TASK_ID"
    
    # Test dry run for complex task
    echo -e "\n🔍 Testing dry run for complex task"
    curl -s -X PATCH http://localhost:3000/tasks/$COMPLEX_TASK_ID/approve \
      -H "Content-Type: application/json" \
      -d '{"approved_by": "demo_user", "dry_run": true}' | jq '.'
fi

# Test 6: Get user tasks
echo -e "\n📊 Test 6: Getting user tasks"
curl -s http://localhost:3000/tasks?user_id=demo_user | jq '.'

# Test 7: Get pending tasks
echo -e "\n⏳ Test 7: Getting pending tasks"
curl -s http://localhost:3000/tasks/pending/list | jq '.'

# Test 8: Admin stats
echo -e "\n📈 Test 8: Getting admin statistics"
curl -s http://localhost:3000/admin/stats | jq '.'

echo -e "\n✅ Orchestrator demo completed!"
echo "💡 Check the audit logs at http://localhost:3000/admin/audit-logs to see all actions."
