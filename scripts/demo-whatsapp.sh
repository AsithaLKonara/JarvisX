#!/bin/bash

# Demo script for WhatsApp service
# Tests WhatsApp message parsing and order creation

echo "📱 JarvisX WhatsApp Service Demo"
echo "==============================="

# Check if WhatsApp service is running
echo "Checking WhatsApp service health..."
curl -s http://localhost:8003/health | jq '.' || {
    echo "❌ WhatsApp service is not running. Please start it with: docker-compose up whatsapp"
    exit 1
}

echo "✅ WhatsApp service is running"

# Test 1: Parse Sinhala order message
echo -e "\n🇱🇰 Test 1: Parsing Sinhala order message"
curl -s -X POST http://localhost:8003/parse-order \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ආයුබෝවන්, මට ලැප්ටොප් 2ක් ගන්න ඕන. මගේ නම කමල්. අද්දර්ස් 123 කොල්ලොම්බෝ. මිල කීයද?"
  }' | jq '.'

# Test 2: Parse English order message
echo -e "\n🇺🇸 Test 2: Parsing English order message"
curl -s -X POST http://localhost:8003/parse-order \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi, I want to order 2 laptops and 1 mouse. My name is John Smith, phone 0771234567. Deliver to 123 Main St tomorrow."
  }' | jq '.'

# Test 3: Parse mixed language message
echo -e "\n🌐 Test 3: Parsing mixed language message"
curl -s -X POST http://localhost:8003/parse-order \
  -H "Content-Type: application/json" \
  -d '{
    "message": "මට laptop 1ක් කැමති. මගේ නම John. Phone 0771234567. Delivery tomorrow please."
  }' | jq '.'

# Test 4: Parse inquiry message
echo -e "\n❓ Test 4: Parsing inquiry message"
curl -s -X POST http://localhost:8003/parse-order \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ආයුබෝවන්, laptop මිල කීයද? මට ගන්න ඕන."
  }' | jq '.'

# Test 5: Test webhook simulation (without actual WhatsApp)
echo -e "\n🔗 Test 5: Simulating webhook call"
curl -s -X POST http://localhost:8003/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "changes": [{
        "field": "messages",
        "value": {
          "messages": [{
            "from": "94771234567",
            "text": {
              "body": "මට ටොප් 3ක් ගන්න ඕන. මගේ නම සරත්."
            }
          }]
        }
      }]
    }]
  }' | jq '.'

# Test 6: Send test message (if WhatsApp token is configured)
if [ -n "$WHATSAPP_TOKEN" ]; then
    echo -e "\n📤 Test 6: Sending test message"
    curl -s -X POST http://localhost:8003/send-message \
      -H "Content-Type: application/json" \
      -d '{
        "phone": "94771234567",
        "message": "මට ඔබේ පණිවිඩය ලැබුණා. ඉක්මනින් පිළිතුරු දෙන්නම්. 🚀"
      }' | jq '.'
else
    echo -e "\n⚠️ Test 6: Skipped (WHATSAPP_TOKEN not configured)"
fi

# Test 7: Test webhook verification
echo -e "\n🔐 Test 7: Testing webhook verification"
curl -s "http://localhost:8003/webhook?hub.mode=subscribe&hub.verify_token=$WEBHOOK_SECRET&hub.challenge=test_challenge" | jq '.'

echo -e "\n✅ WhatsApp demo completed!"
echo "💡 Configure WHATSAPP_TOKEN in your .env file to test actual message sending."
echo "📋 Webhook URL: http://your-domain.com:8003/webhook"
