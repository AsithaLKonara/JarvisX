/**
 * WhatsApp Executor for JarvisX Orchestrator
 * Handles WhatsApp message sending and order processing
 */

import axios from 'axios';

export class WhatsAppExecutor {
  private apiUrl: string;
  private token: string;

  constructor() {
    this.apiUrl = process.env.WHATSAPP_API_URL || 'https://graph.facebook.com/v18.0';
    this.token = process.env.WHATSAPP_TOKEN || '';
  }

  /**
   * Execute a WhatsApp step
   */
  public async execute(step: any, dryRun: boolean = false): Promise<any> {
    const { action, params } = step;

    try {
      console.log(`📱 WhatsApp executor: ${action} (dry_run: ${dryRun})`);

      if (dryRun) {
        return this.getDryRunResult(action, params);
      }

      switch (action) {
        case 'send_message':
          return await this.sendMessage(params.phone, params.message);
        
        case 'send_order_confirmation':
          return await this.sendOrderConfirmation(params.order, params.phone);
        
        case 'parse_incoming_message':
          return await this.parseIncomingMessage(params.message);
        
        case 'create_order_from_message':
          return await this.createOrderFromMessage(params.message);
        
        default:
          throw new Error(`Unknown WhatsApp action: ${action}`);
      }

    } catch (error: any) {
      console.error(`❌ WhatsApp executor failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get dry run result for WhatsApp actions
   */
  private getDryRunResult(action: string, params: any): any {
    return {
      action,
      params,
      dry_run: true,
      description: this.getActionDescription(action, params)
    };
  }

  /**
   * Get human-readable description of action
   */
  private getActionDescription(action: string, params: any): string {
    switch (action) {
      case 'send_message':
        return `Send message to ${params.phone}: "${params.message.substring(0, 50)}..."`;
      case 'send_order_confirmation':
        return `Send order confirmation for ${params.order.id} to ${params.phone}`;
      case 'parse_incoming_message':
        return `Parse incoming message: "${params.message.substring(0, 50)}..."`;
      case 'create_order_from_message':
        return `Create order from message: "${params.message.substring(0, 50)}..."`;
      default:
        return `Execute ${action}`;
    }
  }

  /**
   * Send a WhatsApp message
   */
  private async sendMessage(phone: string, message: string): Promise<any> {
    if (!this.token) {
      throw new Error('WhatsApp token not configured');
    }

    console.log(`📤 Sending WhatsApp message to ${phone}`);

    const payload = {
      messaging_product: 'whatsapp',
      to: phone,
      type: 'text',
      text: {
        body: message
      }
    };

    try {
      const response = await axios.post(
        `${this.apiUrl}/messages`,
        payload,
        {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return {
        success: true,
        action: 'send_message',
        phone,
        message_id: response.data.messages[0].id,
        status: 'sent'
      };

    } catch (error: any) {
      throw new Error(`Failed to send WhatsApp message: ${error.response?.data?.error?.message || error.message}`);
    }
  }

  /**
   * Send order confirmation message
   */
  private async sendOrderConfirmation(order: any, phone: string): Promise<any> {
    const message = this.formatOrderConfirmationMessage(order);
    return await this.sendMessage(phone, message);
  }

  /**
   * Format order confirmation message
   */
  private formatOrderConfirmationMessage(order: any): string {
    const items = order.items.map((item: any) => 
      `• ${item.title} x${item.qty}`
    ).join('\n');

    const total = order.total_amount ? `\n\nTotal: Rs. ${order.total_amount}` : '';

    return `✅ Order Confirmed!\n\nCustomer: ${order.customer.name}\nItems:\n${items}${total}\n\nThank you for your order!`;
  }

  /**
   * Parse incoming WhatsApp message
   */
  private async parseIncomingMessage(message: string): Promise<any> {
    console.log(`📥 Parsing incoming message`);

    // This would typically use an LLM service to parse the message
    // For now, we'll do basic parsing
    
    const parsedData = {
      message_type: this.detectMessageType(message),
      contains_order: this.detectOrderIntent(message),
      language: this.detectLanguage(message),
      entities: this.extractEntities(message)
    };

    return {
      success: true,
      action: 'parse_incoming_message',
      parsed_data: parsedData,
      original_message: message
    };
  }

  /**
   * Create order from WhatsApp message
   */
  private async createOrderFromMessage(message: string): Promise<any> {
    console.log(`🛒 Creating order from message`);

    // This would typically use an LLM service to extract order data
    // For now, we'll do basic extraction
    
    const orderData = {
      customer: {
        name: this.extractCustomerName(message),
        phone: this.extractPhoneNumber(message)
      },
      items: this.extractItems(message),
      source: 'whatsapp',
      timestamp: new Date().toISOString()
    };

    return {
      success: true,
      action: 'create_order_from_message',
      order_data: orderData
    };
  }

  /**
   * Detect message type
   */
  private detectMessageType(message: string): string {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('order') || lowerMessage.includes('ගන්න') || lowerMessage.includes('කැමති')) {
      return 'order';
    } else if (lowerMessage.includes('price') || lowerMessage.includes('මිල') || lowerMessage.includes('කීයද')) {
      return 'inquiry';
    } else if (lowerMessage.includes('delivery') || lowerMessage.includes('ඩෙලිවරි')) {
      return 'delivery';
    } else {
      return 'general';
    }
  }

  /**
   * Detect order intent
   */
  private detectOrderIntent(message: string): boolean {
    const orderKeywords = [
      'order', 'ගන්න', 'කැමති', 'buy', 'purchase',
      'මට ඕඩර්', 'මට ගන්න', 'මට කැමති'
    ];
    
    const lowerMessage = message.toLowerCase();
    return orderKeywords.some(keyword => lowerMessage.includes(keyword));
  }

  /**
   * Detect language
   */
  private detectLanguage(message: string): string {
    // Simple language detection based on Sinhala characters
    const sinhalaRegex = /[\u0D80-\u0DFF]/;
    return sinhalaRegex.test(message) ? 'si' : 'en';
  }

  /**
   * Extract entities from message
   */
  private extractEntities(message: string): any {
    const entities: any = {
      quantities: this.extractQuantities(message),
      products: this.extractProducts(message),
      phone_numbers: this.extractPhoneNumbers(message),
      addresses: this.extractAddresses(message)
    };

    return entities;
  }

  /**
   * Extract quantities from message
   */
  private extractQuantities(message: string): string[] {
    const quantityRegex = /(\d+)\s*(ක්|ක|pieces?|pcs?|units?)/gi;
    const matches = message.match(quantityRegex) || [];
    return matches.map(match => match.trim());
  }

  /**
   * Extract product names from message
   */
  private extractProducts(message: string): string[] {
    const commonProducts = [
      'laptop', 'computer', 'phone', 'mobile', 'tablet',
      'shirt', 'dress', 'pants', 'shoes',
      'book', 'pen', 'bag',
      'ලැප්ටොප්', 'කොම්පියුටර්', 'ජංගම දුරකථනය', 'ටැබ්ලට්',
      'ටොප්', 'ඇඳුම', 'කලිසම්', 'ඇඳුම්'
    ];

    const foundProducts: string[] = [];
    const lowerMessage = message.toLowerCase();

    commonProducts.forEach(product => {
      if (lowerMessage.includes(product)) {
        foundProducts.push(product);
      }
    });

    return foundProducts;
  }

  /**
   * Extract phone numbers from message
   */
  private extractPhoneNumbers(message: string): string[] {
    const phoneRegex = /(\+?94|0)?[0-9]{9}/g;
    return message.match(phoneRegex) || [];
  }

  /**
   * Extract addresses from message
   */
  private extractAddresses(message: string): string[] {
    // Simple address detection
    const addressKeywords = ['street', 'road', 'lane', 'avenue', 'ගම', 'කොටුව'];
    const addresses: string[] = [];
    
    const lines = message.split('\n');
    lines.forEach(line => {
      if (addressKeywords.some(keyword => line.toLowerCase().includes(keyword))) {
        addresses.push(line.trim());
      }
    });

    return addresses;
  }

  /**
   * Extract customer name from message
   */
  private extractCustomerName(message: string): string {
    // This is a simplified extraction
    // In a real implementation, you'd use more sophisticated NLP
    
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
  private extractPhoneNumber(message: string): string {
    const phoneNumbers = this.extractPhoneNumbers(message);
    return phoneNumbers.length > 0 ? phoneNumbers[0] : '';
  }

  /**
   * Extract items from message
   */
  private extractItems(message: string): any[] {
    const items: any[] = [];
    const products = this.extractProducts(message);
    const quantities = this.extractQuantities(message);

    products.forEach((product, index) => {
      const quantity = quantities[index] || '1';
      const qty = parseInt(quantity.replace(/\D/g, '')) || 1;

      items.push({
        sku: `${product.toUpperCase()}-001`,
        title: product,
        qty: qty
      });
    });

    return items;
  }

  /**
   * Check if WhatsApp service is configured
   */
  public isConfigured(): boolean {
    return !!(this.token && this.apiUrl);
  }
}
