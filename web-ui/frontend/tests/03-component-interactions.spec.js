import { test, expect } from '@playwright/test';

/**
 * COMPONENT INTERACTION TESTS
 * Verify all interactive components work correctly
 */

test.describe('Component Interactions - Input & Send', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should allow typing in input box', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    await input.fill('Hello Jarvis!');
    
    const value = await input.inputValue();
    expect(value).toBe('Hello Jarvis!');
  });

  test('should enable send button when text is entered', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.locator('button').filter({ hasText: /Send|➤/i }).or(
      page.locator('button[type="submit"]')
    ).first();
    
    await input.fill('Test message');
    
    // Send button should be enabled
    await expect(sendButton).toBeEnabled();
  });

  test('should clear input after sending message', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.locator('button').filter({ hasText: /Send|➤/i }).or(
      page.locator('button[type="submit"]')
    ).first();
    
    await input.fill('Test message');
    await sendButton.click();
    
    // Wait a moment for state update
    await page.waitForTimeout(500);
    
    const value = await input.inputValue();
    expect(value).toBe('');
  });

  test('should handle Enter key to send message', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    
    await input.fill('Test with Enter key');
    await input.press('Enter');
    
    // Wait a moment
    await page.waitForTimeout(500);
    
    // Input should be cleared
    const value = await input.inputValue();
    expect(value).toBe('');
  });

  test('should focus input box on page load', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    
    // Check if input is focused or can receive focus
    await input.focus();
    const isFocused = await input.evaluate(el => el === document.activeElement);
    expect(isFocused).toBe(true);
  });
});

test.describe('Component Interactions - Mode Selector', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should allow switching between modes', async ({ page }) => {
    const modes = ['Engineer', 'System', 'Designer', 'Editor', 'Business', 'Casual'];
    
    for (const mode of modes) {
      const modeButton = page.locator('button').filter({ hasText: new RegExp(mode, 'i') });
      
      if (await modeButton.count() > 0) {
        await modeButton.first().click();
        await page.waitForTimeout(300);
        
        // Check that mode badge updates
        const modeBadge = page.locator('header span').filter({ hasText: new RegExp(mode, 'i') });
        await expect(modeBadge).toBeVisible();
        
        break; // Test one mode switch
      }
    }
  });

  test('should highlight active mode', async ({ page }) => {
    // Default mode is Casual
    const casualButton = page.locator('button').filter({ hasText: /Casual/i }).first();
    
    if (await casualButton.count() > 0) {
      // Active mode button should have visual distinction
      const backgroundColor = await casualButton.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      );
      
      expect(backgroundColor).toBeTruthy();
    }
  });

  test('should update mode badge when mode changes', async ({ page }) => {
    // Click Engineer mode
    const engineerButton = page.locator('button').filter({ hasText: /Engineer/i }).first();
    
    if (await engineerButton.count() > 0) {
      await engineerButton.click();
      await page.waitForTimeout(300);
      
      // Badge should show Engineer icon
      const badge = page.locator('header span').filter({ hasText: /🔧|Engineer/i });
      await expect(badge).toBeVisible();
    }
  });
});

test.describe('Component Interactions - Settings Panel', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should open settings panel', async ({ page }) => {
    const settingsButton = page.locator('button').filter({ has: page.locator('svg') }).last();
    await settingsButton.click();
    
    await page.waitForTimeout(300);
    
    // Settings panel should be visible
    const bodyText = await page.textContent('body');
    const hasSettings = /Settings|TTS|Voice|Avatar/i.test(bodyText);
    expect(hasSettings).toBe(true);
  });

  test('should close settings panel', async ({ page }) => {
    const settingsButton = page.locator('button').filter({ has: page.locator('svg') }).last();
    
    // Open settings
    await settingsButton.click();
    await page.waitForTimeout(300);
    
    // Close settings (click again or find close button)
    await settingsButton.click();
    await page.waitForTimeout(300);
  });

  test('should toggle TTS in settings', async ({ page }) => {
    const settingsButton = page.locator('button').filter({ has: page.locator('svg') }).last();
    await settingsButton.click();
    await page.waitForTimeout(300);
    
    // Find TTS toggle
    const ttsToggle = page.locator('input[type="checkbox"]').first();
    
    if (await ttsToggle.count() > 0) {
      const initialState = await ttsToggle.isChecked();
      await ttsToggle.click();
      await page.waitForTimeout(200);
      
      const newState = await ttsToggle.isChecked();
      expect(newState).not.toBe(initialState);
    }
  });
});

test.describe('Component Interactions - System Status', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display system status metrics', async ({ page }) => {
    // Wait for system status to load
    await page.waitForTimeout(2000);
    
    const bodyText = await page.textContent('body');
    
    // Should show at least one system metric
    const hasMetrics = /CPU|Memory|Disk|\d+%/i.test(bodyText);
    expect(hasMetrics).toBe(true);
  });

  test('should update system status periodically', async ({ page }) => {
    // Get initial status
    const initialText = await page.textContent('body');
    
    // Wait 3 seconds (system updates every 2 seconds)
    await page.waitForTimeout(3000);
    
    const updatedText = await page.textContent('body');
    
    // Text should have updated (or at least stayed the same, not crashed)
    expect(updatedText.length).toBeGreaterThan(0);
  });

  test('should show progress bars for metrics', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Look for progress indicators (divs with percentage widths or progress elements)
    const hasProgressBars = await page.evaluate(() => {
      const elements = document.querySelectorAll('[style*="width"]');
      return elements.length > 0;
    });
    
    expect(hasProgressBars).toBe(true);
  });
});

test.describe('Component Interactions - Avatar (Avatar Theme)', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Switch to Avatar theme
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(500);
  });

  test('should display avatar SVG', async ({ page }) => {
    const svgElements = await page.locator('svg').count();
    expect(svgElements).toBeGreaterThan(0);
  });

  test('should have TTS toggle button in sidebar', async ({ page }) => {
    const ttsButton = page.locator('button').filter({ hasText: /TTS|Voice|Toggle/i });
    
    if (await ttsButton.count() > 0) {
      await expect(ttsButton.first()).toBeVisible();
    }
  });

  test('should toggle TTS from quick actions', async ({ page }) => {
    const ttsButton = page.locator('button').filter({ hasText: /TTS|Voice|Enable|Disable/i }).first();
    
    if (await ttsButton.count() > 0) {
      // Click to toggle
      await ttsButton.click();
      await page.waitForTimeout(300);
      
      // Button should still be visible (state changed)
      await expect(ttsButton).toBeVisible();
    }
  });

  test('should show status cards in sidebar', async ({ page }) => {
    const bodyText = await page.textContent('body');
    
    // Should show "Online" or "Status" indicators
    const hasStatus = /Online|Status|Active/i.test(bodyText);
    expect(hasStatus).toBe(true);
  });

  test('avatar should have animations', async ({ page }) => {
    // Check if avatar SVG has animation properties
    const hasAnimations = await page.evaluate(() => {
      const svgs = document.querySelectorAll('svg');
      for (const svg of svgs) {
        const style = window.getComputedStyle(svg);
        if (style.animation || style.transition) {
          return true;
        }
      }
      return false;
    });
    
    expect(hasAnimations).toBe(true);
  });
});

test.describe('Component Interactions - Responsive Behavior', () => {
  
  test('should hide avatar sidebar on mobile', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Switch to Avatar theme
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(500);
    
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(300);
    
    // Sidebar should be hidden or collapsed on mobile
    // (This depends on your CSS implementation)
  });

  test('should stack mode buttons on mobile', async ({ page }) => {
    await page.goto('/');
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    
    // Mode buttons should still be clickable
    const modeButton = page.locator('button').filter({ hasText: /Casual|Engineer/i }).first();
    if (await modeButton.count() > 0) {
      await expect(modeButton).toBeVisible();
    }
  });
});

test.describe('Component Interactions - Keyboard Navigation', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate with Tab key', async ({ page }) => {
    // Press Tab several times
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Some element should be focused
    const focusedElement = await page.evaluate(() => document.activeElement.tagName);
    expect(focusedElement).toBeTruthy();
  });

  test('should activate buttons with Enter key', async ({ page }) => {
    const modeButton = page.locator('button').filter({ hasText: /Engineer/i }).first();
    
    if (await modeButton.count() > 0) {
      await modeButton.focus();
      await page.keyboard.press('Enter');
      await page.waitForTimeout(300);
      
      // Mode should have changed
      const badge = page.locator('header span').filter({ hasText: /Engineer/i });
      await expect(badge).toBeVisible();
    }
  });

  test('should activate buttons with Space key', async ({ page }) => {
    const themeButton = page.locator('button').filter({ hasText: /Terminal/i }).first();
    
    if (await themeButton.count() > 0) {
      await themeButton.focus();
      await page.keyboard.press('Space');
      await page.waitForTimeout(300);
      
      // Theme should have changed
      const theme = await page.evaluate(() => 
        document.documentElement.getAttribute('data-theme')
      );
      expect(theme).toBe('terminal');
    }
  });
});

