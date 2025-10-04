/**
 * Web Executor Service
 * Standalone service for web automation tasks
 */

const express = require('express');
const cors = require('cors');
const { chromium } = require('playwright');

const app = express();
const PORT = process.env.PORT || 8004;

// Middleware
app.use(cors());
app.use(express.json());

/**
 * Create order in e-commerce admin panel
 */
async function createOrder(config, order) {
  console.log(`🛒 Creating order for ${order.customer.name}`);
  
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Navigate to admin login
    await page.goto(config.admin_url);
    
    // Login
    await page.fill('#email', config.admin_email);
    await page.fill('#password', config.admin_password);
    await page.click('button[type="submit"]');
    await page.waitForNavigation();
    
    // Navigate to create order page
    await page.goto(`${config.admin_url}/orders/new`);
    
    // Fill customer information
    await page.fill('#customer-name', order.customer.name);
    if (order.customer.phone) {
      await page.fill('#customer-phone', order.customer.phone);
    }
    if (order.customer.address) {
      await page.fill('#customer-address', order.customer.address);
    }
    
    // Add items
    for (let i = 0; i < order.items.length; i++) {
      const item = order.items[i];
      
      if (i > 0) {
        await page.click('#add-item-button');
      }
      
      await page.fill(`#item-sku-${i}`, item.sku);
      await page.fill(`#item-title-${i}`, item.title);
      await page.fill(`#item-quantity-${i}`, item.qty.toString());
      
      if (item.price) {
        await page.fill(`#item-price-${i}`, item.price.toString());
      }
    }
    
    // Submit order
    await page.click('#submit-order');
    await page.waitForSelector('.success-message');
    
    // Get order ID from success message
    const orderIdElement = await page.$('.order-id');
    const orderId = orderIdElement ? await orderIdElement.textContent() : 'unknown';
    
    return {
      success: true,
      order_id: orderId,
      customer: order.customer.name,
      items_count: order.items.length
    };
    
  } finally {
    await browser.close();
  }
}

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'web-executor',
    timestamp: new Date().toISOString()
  });
});

// Create order endpoint
app.post('/create-order', async (req, res) => {
  try {
    const { config, order, dry_run } = req.body;
    
    if (dry_run) {
      return res.json({
        success: true,
        dry_run: true,
        action: 'create_order',
        customer: order.customer.name,
        items_count: order.items.length,
        estimated_steps: [
          'Navigate to admin login',
          'Login with credentials',
          'Navigate to create order page',
          'Fill customer information',
          'Add order items',
          'Submit order'
        ]
      });
    }
    
    const result = await createOrder(config, order);
    res.json(result);
    
  } catch (error) {
    console.error('❌ Order creation failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Generic web automation endpoint
app.post('/execute', async (req, res) => {
  try {
    const { action, params, dry_run } = req.body;
    
    if (dry_run) {
      return res.json({
        success: true,
        dry_run: true,
        action,
        params,
        description: `Would execute: ${action} with provided parameters`
      });
    }
    
    const browser = await chromium.launch({ 
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
      const page = await browser.newPage();
      let result;
      
      switch (action) {
        case 'navigate':
          await page.goto(params.url);
          result = { success: true, url: params.url, title: await page.title() };
          break;
          
        case 'click':
          await page.click(params.selector);
          result = { success: true, selector: params.selector };
          break;
          
        case 'fill':
          await page.fill(params.selector, params.value);
          result = { success: true, selector: params.selector, value: params.value };
          break;
          
        case 'screenshot':
          await page.screenshot({ path: params.path });
          result = { success: true, screenshot_path: params.path };
          break;
          
        default:
          throw new Error(`Unknown action: ${action}`);
      }
      
      res.json(result);
      
    } finally {
      await browser.close();
    }
    
  } catch (error) {
    console.error('❌ Web automation failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🌐 Web Executor service running on port ${PORT}`);
});

module.exports = app;
