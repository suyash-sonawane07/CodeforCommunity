import { test, expect } from '@playwright/test';

test.describe('Auth Flow', () => {
  test('Clear cookies, visit /supervisor -> redirected to /login once (no loop)', async ({ page }) => {
    let navCount = 0;
    page.on('framenavigated', () => navCount++);

    await page.goto('http://localhost:3000/supervisor');
    
    // Wait for network idle or URL to settle
    await page.waitForURL('**/login*');
    
    expect(page.url()).toContain('/login');
    // Ensure it doesn't loop
    await page.waitForTimeout(1000);
    expect(navCount).toBeLessThan(5); // 1 for goto, maybe 1 for redirect
  });

  test('Log in as user@demo.com -> land on /user, visit /supervisor -> bounced to /user', async ({ page }) => {
    let navCount = 0;
    
    await page.goto('http://localhost:3000/login');
    
    // Login
    await page.fill('input[type="email"]', 'user@demo.com');
    await page.fill('input[type="password"]', 'demo123');
    
    page.on('framenavigated', () => navCount++);
    await page.click('button[type="submit"]');
    
    await page.waitForURL('**/user');
    expect(page.url()).toContain('/user');
    
    // Reset count
    navCount = 0;
    await page.goto('http://localhost:3000/supervisor');
    await page.waitForURL('**/user');
    
    expect(page.url()).toContain('/user');
    await page.waitForTimeout(1000);
    expect(navCount).toBeLessThan(5);
  });
});
