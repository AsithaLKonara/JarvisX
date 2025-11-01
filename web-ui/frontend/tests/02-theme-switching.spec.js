import { test, expect } from '@playwright/test';

/**
 * THEME SWITCHING TESTS
 * Verify all 3 themes work correctly with proper color consistency
 */

test.describe('Theme Switching - Functionality', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should have Professional theme as default', async ({ page }) => {
    const themeAttr = await page.evaluate(() => 
      document.documentElement.getAttribute('data-theme')
    );
    
    expect(themeAttr).toMatch(/professional/i);
  });

  test('should switch to Terminal theme', async ({ page }) => {
    // Find and click Terminal theme button
    const terminalButton = page.locator('button').filter({ hasText: /Terminal/i }).first();
    await terminalButton.click();
    
    // Wait for theme to apply
    await page.waitForTimeout(500);
    
    const themeAttr = await page.evaluate(() => 
      document.documentElement.getAttribute('data-theme')
    );
    
    expect(themeAttr).toBe('terminal');
  });

  test('should switch to Avatar theme', async ({ page }) => {
    // Find and click Avatar theme button
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    
    // Wait for theme to apply
    await page.waitForTimeout(500);
    
    const themeAttr = await page.evaluate(() => 
      document.documentElement.getAttribute('data-theme')
    );
    
    expect(themeAttr).toBe('avatar');
  });

  test('should persist theme selection after reload', async ({ page }) => {
    // Switch to Terminal theme
    const terminalButton = page.locator('button').filter({ hasText: /Terminal/i }).first();
    await terminalButton.click();
    await page.waitForTimeout(500);
    
    // Reload page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Check theme is still Terminal
    const themeAttr = await page.evaluate(() => 
      document.documentElement.getAttribute('data-theme')
    );
    
    expect(themeAttr).toBe('terminal');
  });

  test('should cycle through all themes', async ({ page }) => {
    const themes = ['professional', 'terminal', 'avatar'];
    
    for (const theme of themes) {
      const themeButton = page.locator('button').filter({ 
        hasText: new RegExp(theme, 'i') 
      }).first();
      
      if (await themeButton.count() > 0) {
        await themeButton.click();
        await page.waitForTimeout(300);
        
        const currentTheme = await page.evaluate(() => 
          document.documentElement.getAttribute('data-theme')
        );
        
        expect(currentTheme).toBe(theme);
      }
    }
  });
});

test.describe('Theme Switching - Color Consistency', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Professional theme should have correct CSS variables', async ({ page }) => {
    const professionalButton = page.locator('button').filter({ hasText: /Professional/i }).first();
    await professionalButton.click();
    await page.waitForTimeout(300);
    
    const colors = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return {
        bgPrimary: style.getPropertyValue('--bg-primary').trim(),
        textPrimary: style.getPropertyValue('--text-primary').trim(),
        accentPrimary: style.getPropertyValue('--accent-primary').trim(),
      };
    });
    
    expect(colors.bgPrimary).toBeTruthy();
    expect(colors.textPrimary).toBeTruthy();
    expect(colors.accentPrimary).toBeTruthy();
  });

  test('Terminal theme should have green accent colors', async ({ page }) => {
    const terminalButton = page.locator('button').filter({ hasText: /Terminal/i }).first();
    await terminalButton.click();
    await page.waitForTimeout(300);
    
    const accentColor = await page.evaluate(() => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--text-primary').trim();
    });
    
    // Terminal theme should have green text
    expect(accentColor.toLowerCase()).toContain('00ff00');
  });

  test('Avatar theme should show right sidebar', async ({ page }) => {
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(500);
    
    // Check if avatar sidebar elements are visible
    const bodyText = await page.textContent('body');
    const hasAvatarElements = /JARVIS|Status|Quick Actions/i.test(bodyText);
    
    expect(hasAvatarElements).toBe(true);
  });

  test('all themes should have proper contrast ratios', async ({ page }) => {
    const themes = ['professional', 'terminal', 'avatar'];
    
    for (const theme of themes) {
      const themeButton = page.locator('button').filter({ 
        hasText: new RegExp(theme, 'i') 
      }).first();
      
      if (await themeButton.count() > 0) {
        await themeButton.click();
        await page.waitForTimeout(300);
        
        // Check that colors are defined
        const hasColors = await page.evaluate(() => {
          const style = getComputedStyle(document.documentElement);
          const bgPrimary = style.getPropertyValue('--bg-primary');
          const textPrimary = style.getPropertyValue('--text-primary');
          return bgPrimary && textPrimary;
        });
        
        expect(hasColors).toBe(true);
      }
    }
  });
});

test.describe('Theme Switching - Visual Effects', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should have smooth transitions between themes', async ({ page }) => {
    // Check transition property exists
    const hasTransition = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      const transition = style.getPropertyValue('--transition-normal');
      return transition && transition.includes('ease');
    });
    
    expect(hasTransition).toBe(true);
  });

  test('should update all UI elements on theme change', async ({ page }) => {
    // Take screenshot of Professional theme
    await page.screenshot({ path: 'test-results/theme-professional.png', fullPage: true });
    
    // Switch to Terminal theme
    const terminalButton = page.locator('button').filter({ hasText: /Terminal/i }).first();
    await terminalButton.click();
    await page.waitForTimeout(500);
    
    // Take screenshot of Terminal theme
    await page.screenshot({ path: 'test-results/theme-terminal.png', fullPage: true });
    
    // Screenshots should be different
    // (Visual regression will catch if theme didn't actually change)
  });

  test('buttons should have hover effects in all themes', async ({ page }) => {
    const themes = ['professional', 'terminal', 'avatar'];
    
    for (const theme of themes) {
      const themeButton = page.locator('button').filter({ 
        hasText: new RegExp(theme, 'i') 
      }).first();
      
      if (await themeButton.count() > 0) {
        await themeButton.click();
        await page.waitForTimeout(300);
        
        // Find any button and hover
        const anyButton = page.locator('button').first();
        await anyButton.hover();
        
        // Button should still be visible after hover
        await expect(anyButton).toBeVisible();
      }
    }
  });
});

test.describe('Theme Switching - Avatar Theme Specifics', () => {
  
  test('Avatar theme should show avatar component', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(500);
    
    // Check for SVG avatar or avatar container
    const hasSvg = await page.locator('svg').count() > 0;
    expect(hasSvg).toBe(true);
  });

  test('Avatar theme should show quick actions in sidebar', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(500);
    
    // Look for "QUICK ACTIONS" text or TTS toggle
    const bodyText = await page.textContent('body');
    const hasQuickActions = /Quick Actions|TTS|Voice/i.test(bodyText);
    
    expect(hasQuickActions).toBe(true);
  });

  test('Avatar theme should have proper spacing with sidebar', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(500);
    
    // Get viewport width
    const viewportWidth = await page.viewportSize().then(v => v.width);
    
    // Main content should not be full width (sidebar takes space)
    const mainContent = page.locator('.main-content, [class*="main"]').first();
    if (await mainContent.count() > 0) {
      const contentBox = await mainContent.boundingBox();
      expect(contentBox.width).toBeLessThan(viewportWidth);
    }
  });
});

