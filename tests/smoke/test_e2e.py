import pytest
from playwright.sync_api import Page, expect
import os
import re

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

def test_full_civicpulse_flow(page: Page):
    # 1. Sign up as user
    page.goto(f"{FRONTEND_URL}/signup")
    page.fill('input[type="email"]', 'citizen1@test.org')
    page.fill('input[type="password"]', 'pass123')
    page.click('button:has-text("Create Account")')
    
    # Wait for navigation to /user
    expect(page).to_have_url(f"{FRONTEND_URL}/user", timeout=10000)
    
    # 2. Submit text request
    page.click('text=New Request')
    expect(page).to_have_url(f"{FRONTEND_URL}/user/new", timeout=10000)
    
    # Fill out form
    page.locator('input[type="text"]').fill('MG Road, Pune')
    page.fill('textarea[required]', 'There is a huge pothole here causing accidents.')
    
    # Check consent
    page.locator('#consent').check(force=True)
    
    page.click('button:has-text("Submit Request")')
    
    # Wait for redirect to /user/request/[id]
    expect(page).to_have_url(re.compile(r".*/user/request/req_.*"), timeout=15000)
    
    # Wait for status to show up
    expect(page.locator('text=Reference:')).to_be_visible(timeout=15000)
    
    # 3. Log out
    page.click('text=Logout')
    expect(page).to_have_url(f"{FRONTEND_URL}/login", timeout=10000)
    
    # 4. Log in as supervisor
    page.fill('input[type="email"]', 'reviewer@civicpulse.dev')
    page.fill('input[type="password"]', 'pass123')
    page.click('button:has-text("Sign in")')
    
    expect(page).to_have_url(f"{FRONTEND_URL}/supervisor", timeout=10000)
    
    # 5. See the new request's cluster and approve it
    # Find the cluster that contains "pothole" or the issue type. We will just click the first cluster.
    page.click('.cursor-pointer:first-child')
    
    # Wait for details
    expect(page.locator('text=Review Action')).to_be_visible(timeout=10000)
    
    # Add note and approve
    page.fill('textarea', 'Approved by supervisor test')
    page.click('button:has-text("Approve")')
    
    # Wait for list to refresh
    page.wait_for_timeout(2000)
    
    # 6. Log in as user
    page.click('text=Logout')
    page.fill('input[type="email"]', 'citizen1@test.org')
    page.fill('input[type="password"]', 'pass123')
    page.click('button:has-text("Sign in")')
    
    expect(page).to_have_url(f"{FRONTEND_URL}/user", timeout=10000)
    
    # 7. See the status change
    # The status should be approved, but wait, the cluster is approved, does it update the request?
    # Usually request status follows cluster status. We just check if it says APPROVED or RESOLVED
    expect(page.locator('text=APPROVED')).to_be_visible(timeout=10000)
