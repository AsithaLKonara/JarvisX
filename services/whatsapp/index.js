/**
 * WhatsApp Service
 * Handles WhatsApp Business API integration for order processing
 */

const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 8003;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configuration
const WHATSAPP_TOKEN = process.env.WHATSAPP_TOKEN;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:3000';
const API_URL = 'https://graph.facebook.com/v18.0';

/**
 * Send WhatsApp message
 */
async function sendWhatsAppMessage(phone, message) {
  if (!WHATSAPP_TOKEN) {
    throw new Error('WhatsApp token not configured');
  }

  const payload = {
    messaging_product: 'whatsapp',
    to: phone,
    type: 'text',
    text: {
      body: message
    }
  };

  const response = await axios.post(
    `${API_URL}/messages`,
    payload,
    {
      headers: {
        'Authorization': `Bearer ${WHATSAPP_TOKEN}`,
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data;
}

/**
 * Parse incoming WhatsApp message for orders
 */
function parseOrderMessage(message) {
  // Basic parsing - in production, this would use an LLM service
  const orderData = {
    customer: {
      name: extractCustomerName(message),
      phone: extractPhoneNumber(message)
    },
    items: extractItems(message),
    source: 'whatsapp',
    timestamp: new Date().toISOString()
  };

  return orderData;
}

/**
 * Extract customer name from message
 */
function extractCustomerName(message) {
  const namePatterns = [
    /මගේ නම ([\w\s]+)/i,
    /මම ([\w\s]+)/i,
    /name is ([\w\s]+)/i,
    /i am ([\w\s]+)/i
  ];

  for (const pattern of namePatterns) {
    const match = message.match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }

  return 'Customer';
}

/**
 * Extract phone number from message
 */
function extractPhoneNumber(message) {
  const phoneRegex = /(\+?94|0)?[0-9]{9}/g;
  const matches = message.match(phoneRegex);
  return matches ? matches[0] : '';
}

/**
 * Extract items from message
 */
function extractItems(message) {
  const items = [];
  const commonProducts = [
    'laptop', 'computer', 'phone', 'mobile', 'tablet',
    'shirt', 'dress', 'pants', 'shoes',
    'ලැප්ටොප්', 'කොම්පියුටර්', 'ජංගම දුරකථනය'
  ];

  const lowerMessage = message.toLowerCase();
  
  commonProducts.forEach(product => {
    if (lowerMessage.includes(product)) {
      // Extract quantity
      const quantityRegex = new RegExp(`(\\d+)\\s*${product}`, 'i');
      const match = message.match(quantityRegex);
      const qty = match ? parseInt(match[1]) : 1;

      items.push({
        sku: `${product.toUpperCase()}-001`,
        title: product,
        qty: qty
      });
    }
  });

  return items;
}

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'whatsapp',
    configured: !!WHATSAPP_TOKEN,
    timestamp: new Date().toISOString()
  });
});

// Webhook endpoint for incoming messages
app.post('/webhook', (req, res) => {
  try {
    const body = req.body;

    // Verify webhook (in production, verify the signature)
    if (WEBHOOK_SECRET && req.headers['x-hub-signature-256'] !== WEBHOOK_SECRET) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    // Handle different webhook events
    if (body.object === 'whatsapp_business_account') {
      body.entry.forEach(entry => {
        entry.changes.forEach(change => {
          if (change.field === 'messages') {
            change.value.messages?.forEach(async (message) => {
              try {
                const phone = message.from;
                const messageText = message.text.body;
                
                console.log(`📱 Received WhatsApp message from ${phone}: ${messageText}`);

                // Parse order from message
                const orderData = parseOrderMessage(messageText);
                
                // Send to orchestrator
                await axios.post(`${ORCHESTRATOR_URL}/tasks`, {
                  text: messageText,
                  user_id: 'whatsapp_user',
                  context: {
                    source: 'whatsapp',
                    phone: phone,
                    order_data: orderData
                  }
                });

                // Send acknowledgment
                await sendWhatsAppMessage(phone, 'මට ඔබේ පණිවිඩය ලැබුණා. ඉක්මනින් පිළිතුරු දෙන්නම්.');

              } catch (error) {
                console.error('❌ Error processing WhatsApp message:', error);
              }
            });
          }
        });
      });
    }

    res.status(200).send('OK');
  } catch (error) {
    console.error('❌ Webhook error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Webhook verification
app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === WEBHOOK_SECRET) {
    console.log('✅ Webhook verified');
    res.status(200).send(challenge);
  } else {
    console.log('❌ Webhook verification failed');
    res.status(403).send('Forbidden');
  }
});

// Send message endpoint
app.post('/send-message', async (req, res) => {
  try {
    const { phone, message } = req.body;

    if (!phone || !message) {
      return res.status(400).json({
        error: 'Phone number and message are required'
      });
    }

    const result = await sendWhatsAppMessage(phone, message);
    
    res.json({
      success: true,
      message_id: result.messages[0].id,
      status: 'sent'
    });

  } catch (error) {
    console.error('❌ Send message failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Parse order endpoint
app.post('/parse-order', (req, res) => {
  try {
    const { message } = req.body;

    if (!message) {
      return res.status(400).json({
        error: 'Message is required'
      });
    }

    const orderData = parseOrderMessage(message);
    
    res.json({
      success: true,
      order_data: orderData
    });

  } catch (error) {
    console.error('❌ Parse order failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`📱 WhatsApp service running on port ${PORT}`);
  console.log(`🔗 Webhook URL: http://localhost:${PORT}/webhook`);
  console.log(`🤖 WhatsApp configured: ${!!WHATSAPP_TOKEN}`);
});

module.exports = app;
