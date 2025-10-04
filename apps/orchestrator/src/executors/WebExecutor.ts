/**
 * Web Executor for JarvisX Orchestrator
 * Handles web automation using Playwright
 */

import { chromium, Browser, Page } from 'playwright';

export class WebExecutor {
  private browser: Browser | null = null;

  /**
   * Execute a web automation step
   */
  public async execute(step: any, dryRun: boolean = false): Promise<any> {
    const { action, params } = step;

    try {
      console.log(`🌐 Web executor: ${action} (dry_run: ${dryRun})`);

      if (dryRun) {
        return this.getDryRunResult(action, params);
      }

      switch (action) {
        case 'navigate':
          return await this.navigate(params.url, params.wait_for);
        
        case 'click':
          return await this.click(params.selector, params.wait_for);
        
        case 'fill':
          return await this.fill(params.selector, params.value);
        
        case 'select':
          return await this.select(params.selector, params.value);
        
        case 'screenshot':
          return await this.screenshot(params.path);
        
        case 'create_order':
          return await this.createOrder(params.order_data, params.config);
        
        case 'login':
          return await this.login(params.credentials, params.config);
        
        case 'extract_data':
          return await this.extractData(params.selectors);
        
        default:
          throw new Error(`Unknown web action: ${action}`);
      }

    } catch (error: any) {
      console.error(`❌ Web executor failed: ${error.message}`);
      throw error;
    } finally {
      // Clean up browser if it was created
      if (this.browser && action === 'create_order') {
        await this.browser.close();
        this.browser = null;
      }
    }
  }

  /**
   * Get dry run result for web actions
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
      case 'navigate':
        return `Navigate to ${params.url}`;
      case 'click':
        return `Click element: ${params.selector}`;
      case 'fill':
        return `Fill ${params.selector} with "${params.value}"`;
      case 'select':
        return `Select "${params.value}" from ${params.selector}`;
      case 'screenshot':
        return `Take screenshot and save to ${params.path}`;
      case 'create_order':
        return `Create order for ${params.order_data.customer.name}`;
      case 'login':
        return `Login to ${params.config.login_url}`;
      case 'extract_data':
        return `Extract data using ${Object.keys(params.selectors).length} selectors`;
      default:
        return `Execute ${action}`;
    }
  }

  /**
   * Navigate to a URL
   */
  private async navigate(url: string, waitFor?: string): Promise<any> {
    const page = await this.getPage();
    
    console.log(`🌐 Navigating to: ${url}`);
    await page.goto(url);
    
    if (waitFor) {
      await page.waitForSelector(waitFor);
    }

    return {
      success: true,
      action: 'navigate',
      url,
      title: await page.title()
    };
  }

  /**
   * Click an element
   */
  private async click(selector: string, waitFor?: string): Promise<any> {
    const page = await this.getPage();
    
    console.log(`🖱️ Clicking: ${selector}`);
    await page.click(selector);
    
    if (waitFor) {
      await page.waitForSelector(waitFor);
    }

    return {
      success: true,
      action: 'click',
      selector
    };
  }

  /**
   * Fill an input field
   */
  private async fill(selector: string, value: string): Promise<any> {
    const page = await this.getPage();
    
    console.log(`✏️ Filling ${selector} with: ${value}`);
    await page.fill(selector, value);

    return {
      success: true,
      action: 'fill',
      selector,
      value
    };
  }

  /**
   * Select an option from dropdown
   */
  private async select(selector: string, value: string): Promise<any> {
    const page = await this.getPage();
    
    console.log(`📋 Selecting ${value} from ${selector}`);
    await page.selectOption(selector, value);

    return {
      success: true,
      action: 'select',
      selector,
      value
    };
  }

  /**
   * Take a screenshot
   */
  private async screenshot(path: string): Promise<any> {
    const page = await this.getPage();
    
    console.log(`📸 Taking screenshot: ${path}`);
    await page.screenshot({ path });

    return {
      success: true,
      action: 'screenshot',
      path
    };
  }

  /**
   * Create an order in e-commerce admin panel
   */
  private async createOrder(orderData: any, config: any): Promise<any> {
    console.log(`🛒 Creating order for ${orderData.customer.name}`);
    
    const page = await this.getPage();
    
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
    await page.fill('#customer-name', orderData.customer.name);
    if (orderData.customer.phone) {
      await page.fill('#customer-phone', orderData.customer.phone);
    }
    if (orderData.customer.address) {
      await page.fill('#customer-address', orderData.customer.address);
    }
    
    // Add items
    for (let i = 0; i < orderData.items.length; i++) {
      const item = orderData.items[i];
      
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
      action: 'create_order',
      order_id: orderId,
      customer: orderData.customer.name,
      items_count: orderData.items.length
    };
  }

  /**
   * Login to a website
   */
  private async login(credentials: any, config: any): Promise<any> {
    console.log(`🔐 Logging in to ${config.login_url}`);
    
    const page = await this.getPage();
    
    await page.goto(config.login_url);
    
    await page.fill(config.username_selector, credentials.username);
    await page.fill(config.password_selector, credentials.password);
    await page.click(config.submit_selector);
    
    await page.waitForNavigation();
    
    return {
      success: true,
      action: 'login',
      url: config.login_url
    };
  }

  /**
   * Extract data from page
   */
  private async extractData(selectors: any): Promise<any> {
    console.log(`📊 Extracting data using ${Object.keys(selectors).length} selectors`);
    
    const page = await this.getPage();
    const extractedData: any = {};
    
    for (const [key, selector] of Object.entries(selectors)) {
      try {
        const element = await page.$(selector as string);
        if (element) {
          const text = await element.textContent();
          extractedData[key] = text?.trim();
        } else {
          extractedData[key] = null;
        }
      } catch (error) {
        extractedData[key] = null;
      }
    }

    return {
      success: true,
      action: 'extract_data',
      data: extractedData
    };
  }

  /**
   * Get or create browser page
   */
  private async getPage(): Promise<Page> {
    if (!this.browser) {
      this.browser = await chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });
    }
    
    const pages = this.browser.pages();
    if (pages.length > 0) {
      return pages[0];
    }
    
    return await this.browser.newPage();
  }

  /**
   * Close browser
   */
  public async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }
}
