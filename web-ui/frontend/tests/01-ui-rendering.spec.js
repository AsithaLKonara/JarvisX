import { test, expect } from '@playwright/test';

/**
 * UI RENDERING TESTS
 * Verify all core UI components render correctly
 */

test.describe('UI Rendering - Core Components', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for app to fully load
    await page.waitForLoadState('networkidle');
  });

  test('should load the main application', async ({ page }) => {
    await expect(page).toHaveTitle(/Jarvis/i);
  });

  test('should display header with logo and title', async ({ page }) => {
    const header = page.locator('header');
    await expect(header).toBeVisible();
    
    const title = header.locator('h1');
    await expect(title).toContainText('JARVIS X');
    await expect(title).toContainText('V2');
  });

  test('should display current mode badge', async ({ page }) => {
    const modeBadge = page.locator('header span').filter({ hasText: /Casual|Engineer|System/i });
    await expect(modeBadge).toBeVisible();
  });

  test('should display theme switcher buttons', async ({ page }) => {
    const themeSwitcher = page.locator('button').filter({ hasText: /Professional|Terminal|Avatar/i }).first();
    await expect(themeSwitcher).toBeVisible();
  });

  test('should display settings button', async ({ page }) => {
    const settingsButton = page.locator('button').filter({ has: page.locator('svg') }).last();
    await expect(settingsButton).toBeVisible();
  });

  test('should display chat container', async ({ page }) => {
    // Chat container should be present (even if empty)
    const chatContainer = page.locator('.chat-container, [class*="chat"]').first();
    await expect(chatContainer).toBeVisible();
  });

  test('should display input box', async ({ page }) => {
    const inputBox = page.locator('input[type="text"], textarea').first();
    await expect(inputBox).toBeVisible();
    await expect(inputBox).toBeEnabled();
  });

  test('should display send button', async ({ page }) => {
    const sendButton = page.locator('button').filter({ hasText: /Send|➤/i }).or(
      page.locator('button[type="submit"]')
    ).first();
    await expect(sendButton).toBeVisible();
  });

  test('should display mode selector', async ({ page }) => {
    // Check for mode buttons
    const modes = ['Engineer', 'System', 'Designer', 'Editor', 'Business', 'Casual', 'Career'];
    let foundMode = false;
    
    for (const mode of modes) {
      const modeButton = page.locator('button').filter({ hasText: new RegExp(mode, 'i') });
      if (await modeButton.count() > 0) {
        foundMode = true;
        break;
      }
    }
    
    expect(foundMode).toBe(true);
  });

  test('should display system status component', async ({ page }) => {
    // System status should show CPU, Memory, or Disk info
    const statusText = await page.textContent('body');
    const hasSystemInfo = /CPU|Memory|Disk|Status/i.test(statusText);
    expect(hasSystemInfo).toBe(true);
  });

  test('should not have console errors on load', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Filter out known/acceptable errors
    const criticalErrors = errors.filter(err => 
      !err.includes('favicon') && 
      !err.includes('404')
    );
    
    expect(criticalErrors.length).toBe(0);
  });

  test('should have proper viewport responsiveness', async ({ page }) => {
    // Test different viewport sizes
    const viewports = [
      { width: 1920, height: 1080, name: 'Desktop' },
      { width: 1366, height: 768, name: 'Laptop' },
      { width: 768, height: 1024, name: 'Tablet' },
      { width: 375, height: 667, name: 'Mobile' },
    ];

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.waitForTimeout(500); // Allow layout to adjust
      
      // Check that main container is still visible
      const appContainer = page.locator('.app-container, [class*="app"]').first();
      await expect(appContainer).toBeVisible();
    }
  });

  test('should load all CSS styles', async ({ page }) => {
    // Check that CSS variables are applied
    const bgColor = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--bg-primary');
    });
    
    expect(bgColor).toBeTruthy();
  });
});

test.describe('UI Rendering - No White Screen Issues', () => {
  
  test('should not show blank white screen', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // Check that some text is visible on the page
    const bodyText = await page.textContent('body');
    expect(bodyText.length).toBeGreaterThan(0);
    
    // Check for JARVIS title
    await expect(page.locator('text=/JARVIS/i')).toBeVisible();
  });

  test('should render within 3 seconds', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForSelector('h1', { timeout: 3000 });
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000);
  });
});

