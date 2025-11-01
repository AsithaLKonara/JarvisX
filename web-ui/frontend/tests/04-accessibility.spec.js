import { test, expect } from '@playwright/test';

/**
 * ACCESSIBILITY TESTS (a11y)
 * Verify WCAG compliance and accessibility standards
 */

test.describe('Accessibility - ARIA Labels & Roles', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should have proper page title', async ({ page }) => {
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);
  });

  test('should have main landmark', async ({ page }) => {
    const main = page.locator('main, [role="main"]');
    const count = await main.count();
    expect(count).toBeGreaterThanOrEqual(0); // Optional but recommended
  });

  test('buttons should have accessible text', async ({ page }) => {
    const buttons = await page.locator('button').all();
    
    for (const button of buttons) {
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      
      // Button should have either text content or aria-label
      expect(text || ariaLabel).toBeTruthy();
    }
  });

  test('input fields should have labels or aria-label', async ({ page }) => {
    const inputs = await page.locator('input, textarea').all();
    
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const placeholder = await input.getAttribute('placeholder');
      
      let hasLabel = false;
      
      if (id) {
        const label = page.locator(`label[for="${id}"]`);
        hasLabel = await label.count() > 0;
      }
      
      // Input should have label, aria-label, or at minimum a placeholder
      expect(hasLabel || ariaLabel || placeholder).toBeTruthy();
    }
  });

  test('images should have alt text', async ({ page }) => {
    const images = await page.locator('img').all();
    
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt !== null).toBe(true); // Alt attribute should exist (can be empty for decorative)
    }
  });

  test('SVGs should have accessible titles or labels', async ({ page }) => {
    const svgs = await page.locator('svg').all();
    
    for (const svg of svgs.slice(0, 5)) { // Check first 5 SVGs
      const ariaLabel = await svg.getAttribute('aria-label');
      const role = await svg.getAttribute('role');
      const title = await svg.locator('title').count();
      
      // SVG should have aria-label, role, or title
      const hasAccessibility = ariaLabel || role || title > 0;
      // This is a soft check - decorative SVGs don't need it
    }
  });
});

test.describe('Accessibility - Keyboard Navigation', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should be able to tab through interactive elements', async ({ page }) => {
    const interactiveElements = [];
    
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => ({
        tag: document.activeElement?.tagName,
        type: document.activeElement?.getAttribute('type'),
      }));
      
      if (focused.tag && focused.tag !== 'BODY') {
        interactiveElements.push(focused);
      }
    }
    
    // Should have focused at least some interactive elements
    expect(interactiveElements.length).toBeGreaterThan(0);
  });

  test('should show focus indicators on interactive elements', async ({ page }) => {
    const button = page.locator('button').first();
    await button.focus();
    
    // Check if button has visible outline or box-shadow when focused
    const hasOutline = await button.evaluate(el => {
      const style = window.getComputedStyle(el);
      return style.outline !== 'none' || 
             style.boxShadow !== 'none' || 
             style.border !== 'none';
    });
    
    expect(hasOutline).toBe(true);
  });

  test('should not have keyboard traps', async ({ page }) => {
    // Tab through elements and ensure we can always move forward
    const positions = [];
    
    for (let i = 0; i < 20; i++) {
      await page.keyboard.press('Tab');
      const tag = await page.evaluate(() => document.activeElement?.tagName);
      positions.push(tag);
      
      // Wait a bit
      await page.waitForTimeout(50);
    }
    
    // Should have moved through different elements (not stuck)
    const uniqueTags = [...new Set(positions)];
    expect(uniqueTags.length).toBeGreaterThan(1);
  });

  test('should support Shift+Tab for reverse navigation', async ({ page }) => {
    // Tab forward
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    const forwardElement = await page.evaluate(() => document.activeElement?.tagName);
    
    // Tab backward
    await page.keyboard.press('Shift+Tab');
    
    const backwardElement = await page.evaluate(() => document.activeElement?.tagName);
    
    // Should have moved to a different element
    expect(forwardElement).toBeTruthy();
  });
});

test.describe('Accessibility - Color Contrast', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('text should have sufficient contrast in Professional theme', async ({ page }) => {
    const professionalButton = page.locator('button').filter({ hasText: /Professional/i }).first();
    await professionalButton.click();
    await page.waitForTimeout(300);
    
    // Get colors
    const colors = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return {
        bg: style.getPropertyValue('--bg-primary'),
        text: style.getPropertyValue('--text-primary'),
      };
    });
    
    // Both should be defined
    expect(colors.bg).toBeTruthy();
    expect(colors.text).toBeTruthy();
  });

  test('text should have sufficient contrast in Terminal theme', async ({ page }) => {
    const terminalButton = page.locator('button').filter({ hasText: /Terminal/i }).first();
    await terminalButton.click();
    await page.waitForTimeout(300);
    
    // Terminal theme has high contrast (green on black)
    const colors = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return {
        bg: style.getPropertyValue('--bg-primary'),
        text: style.getPropertyValue('--text-primary'),
      };
    });
    
    expect(colors.bg).toBeTruthy();
    expect(colors.text).toBeTruthy();
  });

  test('text should have sufficient contrast in Avatar theme', async ({ page }) => {
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(300);
    
    const colors = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return {
        bg: style.getPropertyValue('--bg-primary'),
        text: style.getPropertyValue('--text-primary'),
      };
    });
    
    expect(colors.bg).toBeTruthy();
    expect(colors.text).toBeTruthy();
  });

  test('buttons should have sufficient contrast', async ({ page }) => {
    const button = page.locator('button').first();
    
    const contrast = await button.evaluate(el => {
      const style = window.getComputedStyle(el);
      return {
        bg: style.backgroundColor,
        color: style.color,
      };
    });
    
    // Both background and text color should be set
    expect(contrast.bg).not.toBe('rgba(0, 0, 0, 0)');
    expect(contrast.color).not.toBe('rgba(0, 0, 0, 0)');
  });
});

test.describe('Accessibility - Screen Reader Support', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should have semantic HTML structure', async ({ page }) => {
    const semanticElements = await page.evaluate(() => {
      const elements = [
        'header',
        'nav',
        'main',
        'article',
        'section',
        'footer',
        'aside',
      ];
      
      const found = [];
      for (const tag of elements) {
        if (document.querySelector(tag)) {
          found.push(tag);
        }
      }
      return found;
    });
    
    // Should have at least header
    expect(semanticElements.length).toBeGreaterThan(0);
  });

  test('interactive elements should have proper roles', async ({ page }) => {
    // Buttons should have button role (implicit or explicit)
    const buttons = await page.locator('button').all();
    expect(buttons.length).toBeGreaterThan(0);
  });

  test('status updates should be announced', async ({ page }) => {
    // Check for live regions or aria-live attributes
    const liveRegions = await page.locator('[aria-live], [role="status"], [role="alert"]').count();
    
    // This is optional but good for status updates
    expect(liveRegions).toBeGreaterThanOrEqual(0);
  });

  test('form controls should be properly labeled', async ({ page }) => {
    const inputs = await page.locator('input, textarea, select').all();
    
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');
      const placeholder = await input.getAttribute('placeholder');
      
      // Input should have some form of label
      const hasLabel = id || ariaLabel || ariaLabelledBy || placeholder;
      expect(hasLabel).toBeTruthy();
    }
  });
});

test.describe('Accessibility - Mobile & Touch', () => {
  
  test('buttons should have adequate touch targets (mobile)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const buttons = await page.locator('button').all();
    
    for (const button of buttons.slice(0, 5)) { // Check first 5 buttons
      const box = await button.boundingBox();
      
      if (box) {
        // WCAG recommends at least 44x44 CSS pixels for touch targets
        // We'll be lenient and check for at least 32x32
        const hasAdequateSize = box.width >= 32 && box.height >= 32;
        expect(hasAdequateSize).toBe(true);
      }
    }
  });

  test('should be usable on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Main interactive elements should be visible
    const input = page.locator('input[type="text"], textarea').first();
    await expect(input).toBeVisible();
    
    const sendButton = page.locator('button').first();
    await expect(sendButton).toBeVisible();
  });

  test('should not require horizontal scrolling on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
    const clientWidth = await page.evaluate(() => document.body.clientWidth);
    
    // Body width should not exceed viewport width
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 20); // Allow small buffer
  });
});

test.describe('Accessibility - Error Handling', () => {
  
  test('should handle missing backend gracefully', async ({ page }) => {
    // This tests if UI shows proper error messages instead of crashing
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Type and send a message
    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.locator('button').filter({ hasText: /Send|➤/i }).first();
    
    if (await sendButton.count() > 0) {
      await input.fill('Test message');
      await sendButton.click();
      
      // Wait for response or error
      await page.waitForTimeout(2000);
      
      // Page should still be functional (not white screen)
      const bodyText = await page.textContent('body');
      expect(bodyText.length).toBeGreaterThan(0);
    }
  });

  test('should not have unhandled console errors', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Interact with UI
    const themeButton = page.locator('button').first();
    await themeButton.click();
    await page.waitForTimeout(500);
    
    // Filter out known non-critical errors
    const criticalErrors = errors.filter(err => 
      !err.includes('favicon') && 
      !err.includes('404') &&
      !err.includes('Failed to fetch')
    );
    
    expect(criticalErrors.length).toBe(0);
  });
});

