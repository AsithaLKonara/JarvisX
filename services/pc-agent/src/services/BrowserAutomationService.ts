/**
 * Browser Automation Service for JarvisX PC Agent
 * Playwright integration for advanced browser control
 */

import { chromium, Browser, BrowserContext, Page } from 'playwright';
import axios from 'axios';

export interface BrowserAction {
  type: 'navigate' | 'click' | 'type' | 'fill' | 'select' | 'screenshot' | 'wait' | 'scroll';
  selector?: string;
  text?: string;
  url?: string;
  value?: string;
  options?: string;
  x?: number;
  y?: number;
  timeout?: number;
}

export interface BrowserSession {
  id: string;
  browser: Browser;
  context: BrowserContext;
  page: Page;
  startTime: Date;
  status: 'active' | 'inactive' | 'error';
}

export class BrowserAutomationService {
  private sessions: Map<string, BrowserSession> = new Map();
  private isInitialized: boolean = false;

  constructor() {
    this.initialize();
  }

  private async initialize(): Promise<void> {
    try {
      // Install Playwright browsers if needed
      console.log('🌐 Initializing Browser Automation Service...');
      this.isInitialized = true;
      console.log('✅ Browser Automation Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Browser Automation Service:', error);
      this.isInitialized = false;
    }
  }

  public async createSession(sessionId: string): Promise<BrowserSession> {
    try {
      console.log(`🌐 Creating browser session: ${sessionId}`);

      const browser = await chromium.launch({
        headless: false, // Set to true for headless mode
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--no-first-run',
          '--no-zygote',
          '--disable-gpu'
        ]
      });

      const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      });

      const page = await context.newPage();

      const session: BrowserSession = {
        id: sessionId,
        browser,
        context,
        page,
        startTime: new Date(),
        status: 'active'
      };

      this.sessions.set(sessionId, session);
      console.log(`✅ Browser session created: ${sessionId}`);

      return session;

    } catch (error) {
      console.error(`❌ Failed to create browser session ${sessionId}:`, error);
      throw error;
    }
  }

  public async executeAction(sessionId: string, action: BrowserAction): Promise<any> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    try {
      console.log(`🌐 Executing action: ${action.type} on session ${sessionId}`);

      switch (action.type) {
        case 'navigate':
          if (!action.url) throw new Error('URL required for navigate action');
          await session.page.goto(action.url, { waitUntil: 'networkidle' });
          return { success: true, message: `Navigated to ${action.url}` };

        case 'click':
          if (!action.selector) throw new Error('Selector required for click action');
          await session.page.click(action.selector, { timeout: action.timeout || 30000 });
          return { success: true, message: `Clicked element: ${action.selector}` };

        case 'type':
          if (!action.selector || !action.text) throw new Error('Selector and text required for type action');
          await session.page.fill(action.selector, action.text);
          return { success: true, message: `Typed "${action.text}" into ${action.selector}` };

        case 'fill':
          if (!action.selector || !action.value) throw new Error('Selector and value required for fill action');
          await session.page.fill(action.selector, action.value);
          return { success: true, message: `Filled ${action.selector} with "${action.value}"` };

        case 'select':
          if (!action.selector || !action.value) throw new Error('Selector and value required for select action');
          await session.page.selectOption(action.selector, action.value);
          return { success: true, message: `Selected "${action.value}" in ${action.selector}` };

        case 'screenshot':
          const screenshot = await session.page.screenshot({ fullPage: true });
          const base64Screenshot = screenshot.toString('base64');
          return { success: true, screenshot: base64Screenshot };

        case 'wait':
          if (action.selector) {
            await session.page.waitForSelector(action.selector, { timeout: action.timeout || 30000 });
          } else {
            await session.page.waitForTimeout(action.timeout || 1000);
          }
          return { success: true, message: 'Wait completed' };

        case 'scroll':
          if (action.x !== undefined && action.y !== undefined) {
            await session.page.mouse.wheel(action.x, action.y);
          } else {
            await session.page.evaluate(() => window.scrollBy(0, 100));
          }
          return { success: true, message: 'Scrolled' };

        default:
          throw new Error(`Unknown action type: ${action.type}`);
      }

    } catch (error) {
      console.error(`❌ Action execution failed for session ${sessionId}:`, error);
      throw error;
    }
  }

  public async getPageContent(sessionId: string): Promise<any> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    try {
      const title = await session.page.title();
      const url = session.page.url();
      const content = await session.page.content();

      return {
        success: true,
        data: {
          title,
          url,
          content: content.substring(0, 10000) // Limit content size
        }
      };

    } catch (error) {
      console.error(`❌ Failed to get page content for session ${sessionId}:`, error);
      throw error;
    }
  }

  public async getElements(sessionId: string, selector?: string): Promise<any> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    try {
      let elements;
      
      if (selector) {
        elements = await session.page.$$eval(selector, els => 
          els.map(el => ({
            tagName: el.tagName,
            textContent: el.textContent?.trim(),
            id: el.id,
            className: el.className,
            href: el.getAttribute('href'),
            src: el.getAttribute('src'),
            value: el.getAttribute('value'),
            type: el.getAttribute('type')
          }))
        );
      } else {
        // Get all interactive elements
        elements = await session.page.$$eval('button, input, select, textarea, a[href], [onclick]', els => 
          els.map(el => ({
            tagName: el.tagName,
            textContent: el.textContent?.trim(),
            id: el.id,
            className: el.className,
            href: el.getAttribute('href'),
            type: el.getAttribute('type'),
            placeholder: el.getAttribute('placeholder'),
            value: el.getAttribute('value')
          }))
        );
      }

      return {
        success: true,
        data: {
          elements,
          count: elements.length
        }
      };

    } catch (error) {
      console.error(`❌ Failed to get elements for session ${sessionId}:`, error);
      throw error;
    }
  }

  public async closeSession(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      console.warn(`Session ${sessionId} not found for closing`);
      return;
    }

    try {
      await session.browser.close();
      this.sessions.delete(sessionId);
      console.log(`✅ Browser session closed: ${sessionId}`);
    } catch (error) {
      console.error(`❌ Failed to close session ${sessionId}:`, error);
      throw error;
    }
  }

  public async closeAllSessions(): Promise<void> {
    console.log('🌐 Closing all browser sessions...');
    
    for (const [sessionId, session] of this.sessions) {
      try {
        await session.browser.close();
        console.log(`✅ Closed session: ${sessionId}`);
      } catch (error) {
        console.error(`❌ Failed to close session ${sessionId}:`, error);
      }
    }
    
    this.sessions.clear();
  }

  public getActiveSessions(): BrowserSession[] {
    return Array.from(this.sessions.values());
  }

  public getSessionStats(): any {
    const sessions = this.getActiveSessions();
    return {
      total: sessions.length,
      active: sessions.filter(s => s.status === 'active').length,
      inactive: sessions.filter(s => s.status === 'inactive').length,
      error: sessions.filter(s => s.status === 'error').length
    };
  }

  public isReady(): boolean {
    return this.isInitialized;
  }
}
