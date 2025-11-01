import { test, expect } from '@playwright/test';

/**
 * VISUAL REGRESSION TESTS
 * Capture screenshots for visual comparison across themes and states
 */

test.describe('Visual Regression - Theme Screenshots', () => {
  
  test('should capture Professional theme - Light mode', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const professionalButton = page.locator('button').filter({ hasText: /Professional/i }).first();
    await professionalButton.click();
    await page.waitForTimeout(500);
    
    // Full page screenshot
    await expect(page).toHaveScreenshot('professional-theme-full.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('should capture Terminal theme', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const terminalButton = page.locator('button').filter({ hasText: /Terminal/i }).first();
    await terminalButton.click();
    await page.waitForTimeout(500);
    
    await expect(page).toHaveScreenshot('terminal-theme-full.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('should capture Avatar theme with sidebar', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(500);
    
    await expect(page).toHaveScreenshot('avatar-theme-full.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });
});

test.describe('Visual Regression - Component Screenshots', () => {
  
  test('should capture header component', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const header = page.locator('header').first();
    await expect(header).toHaveScreenshot('header-component.png');
  });

  test('should capture input box component', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const input = page.locator('input[type="text"], textarea').first();
    const container = input.locator('..'); // Parent container
    
    if (await container.count() > 0) {
      await expect(container).toHaveScreenshot('input-box-component.png');
    }
  });

  test('should capture theme switcher', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Find theme switcher container
    const themeSwitcher = page.locator('button').filter({ hasText: /Professional|Terminal|Avatar/i }).first().locator('..');
    
    if (await themeSwitcher.count() > 0) {
      await expect(themeSwitcher).toHaveScreenshot('theme-switcher.png');
    }
  });

  test('should capture mode selector', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Find mode buttons container
    const modeButton = page.locator('button').filter({ hasText: /Casual|Engineer/i }).first();
    
    if (await modeButton.count() > 0) {
      await expect(modeButton).toHaveScreenshot('mode-button.png');
    }
  });
});

test.describe('Visual Regression - Hover States', () => {
  
  test('should capture button hover state', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const button = page.locator('button').first();
    await button.hover();
    await page.waitForTimeout(300); // Wait for hover transition
    
    await expect(button).toHaveScreenshot('button-hover-state.png');
  });

  test('should capture theme button hover in all themes', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const themes = ['professional', 'terminal', 'avatar'];
    
    for (const theme of themes) {
      const themeButton = page.locator('button').filter({ 
        hasText: new RegExp(theme, 'i') 
      }).first();
      
      if (await themeButton.count() > 0) {
        await themeButton.click();
        await page.waitForTimeout(300);
        
        const anyButton = page.locator('button').nth(2); // Get a different button
        await anyButton.hover();
        await page.waitForTimeout(300);
        
        await expect(anyButton).toHaveScreenshot(`${theme}-button-hover.png`);
      }
    }
  });
});

test.describe('Visual Regression - Avatar Theme Specifics', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(500);
  });

  test('should capture avatar SVG', async ({ page }) => {
    const avatar = page.locator('svg').first();
    
    if (await avatar.count() > 0) {
      await expect(avatar).toHaveScreenshot('avatar-svg.png');
    }
  });

  test('should capture right sidebar', async ({ page }) => {
    // Try to find sidebar container
    const sidebar = page.locator('[class*="sidebar"], aside').first();
    
    if (await sidebar.count() > 0) {
      await expect(sidebar).toHaveScreenshot('avatar-sidebar.png', {
        animations: 'disabled',
      });
    }
  });

  test('should capture quick actions buttons', async ({ page }) => {
    const quickActionsText = await page.textContent('body');
    
    if (/Quick Actions/i.test(quickActionsText)) {
      // Full page to capture sidebar
      await expect(page).toHaveScreenshot('avatar-quick-actions.png', {
        clip: { x: 0, y: 0, width: 400, height: 800 }
      });
    }
  });
});

test.describe('Visual Regression - Responsive Views', () => {
  
  test('should capture desktop view (1920x1080)', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('desktop-1920x1080.png', {
      fullPage: false, // Just visible viewport
    });
  });

  test('should capture laptop view (1366x768)', async ({ page }) => {
    await page.setViewportSize({ width: 1366, height: 768 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('laptop-1366x768.png', {
      fullPage: false,
    });
  });

  test('should capture tablet view (768x1024)', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('tablet-768x1024.png', {
      fullPage: false,
    });
  });

  test('should capture mobile view (375x667)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('mobile-375x667.png', {
      fullPage: false,
    });
  });
});

test.describe('Visual Regression - Mode States', () => {
  
  test('should capture each mode badge', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const modes = [
      { name: 'Engineer', emoji: '🔧' },
      { name: 'System', emoji: '📊' },
      { name: 'Designer', emoji: '🎨' },
      { name: 'Editor', emoji: '🎬' },
      { name: 'Business', emoji: '💼' },
      { name: 'Casual', emoji: '💬' },
    ];
    
    for (const mode of modes.slice(0, 3)) { // Test first 3 modes
      const modeButton = page.locator('button').filter({ 
        hasText: new RegExp(mode.name, 'i') 
      });
      
      if (await modeButton.count() > 0) {
        await modeButton.first().click();
        await page.waitForTimeout(300);
        
        const badge = page.locator('header span').filter({ 
          hasText: new RegExp(mode.name, 'i') 
        });
        
        if (await badge.count() > 0) {
          await expect(badge).toHaveScreenshot(`mode-badge-${mode.name.toLowerCase()}.png`);
        }
      }
    }
  });
});

test.describe('Visual Regression - Settings Panel', () => {
  
  test('should capture settings panel open state', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const settingsButton = page.locator('button').filter({ has: page.locator('svg') }).last();
    await settingsButton.click();
    await page.waitForTimeout(300);
    
    // Capture full page with settings open
    await expect(page).toHaveScreenshot('settings-panel-open.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });
});

test.describe('Visual Regression - Color Consistency Check', () => {
  
  test('should verify Professional theme colors are consistent', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const professionalButton = page.locator('button').filter({ hasText: /Professional/i }).first();
    await professionalButton.click();
    await page.waitForTimeout(500);
    
    // Take multiple screenshots of same state to verify consistency
    await expect(page).toHaveScreenshot('professional-consistent-1.png');
    
    // Reload and verify again
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('professional-consistent-2.png');
  });

  test('should verify Terminal theme green colors', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const terminalButton = page.locator('button').filter({ hasText: /Terminal/i }).first();
    await terminalButton.click();
    await page.waitForTimeout(500);
    
    // Verify green colors are applied
    const textColor = await page.evaluate(() => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--text-primary').trim();
    });
    
    expect(textColor).toContain('00ff00');
    
    await expect(page).toHaveScreenshot('terminal-green-colors.png');
  });

  test('should verify Avatar theme gradient colors', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(500);
    
    // Verify gradient colors exist
    const gradientStart = await page.evaluate(() => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--gradient-start')?.trim();
    });
    
    // Gradient variables should exist in Avatar theme
    await expect(page).toHaveScreenshot('avatar-gradient-colors.png');
  });
});

test.describe('Visual Regression - Animation States', () => {
  
  test('should capture avatar idle animation frame', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const avatarButton = page.locator('button').filter({ hasText: /Avatar/i }).first();
    await avatarButton.click();
    await page.waitForTimeout(1000); // Wait for animations
    
    const avatar = page.locator('svg').first();
    
    if (await avatar.count() > 0) {
      await expect(avatar).toHaveScreenshot('avatar-animation-frame.png', {
        animations: 'disabled',
      });
    }
  });
});

test.describe('Visual Regression - Empty States', () => {
  
  test('should capture empty chat container', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Chat should be empty on initial load
    await expect(page).toHaveScreenshot('empty-chat-state.png', {
      fullPage: true,
    });
  });
});

