import asyncio
from playwright.async_api import async_playwright
import http.cookiejar
import time

async def login_youtube_with_cookies():
    # Parse Netscape format cookies
    cookie_jar = http.cookiejar.MozillaCookieJar('cookies.txt')
    cookie_jar.load(ignore_discard=True, ignore_expires=True)
    
    # Convert to Playwright format
    playwright_cookies = []
    for cookie in cookie_jar:
        playwright_cookie = {
            'name': cookie.name,
            'value': cookie.value,
            'domain': cookie.domain,
            'path': cookie.path,
            'expires': cookie.expires if cookie.expires else -1,
            'httpOnly': bool(cookie.has_nonstandard_attr('HttpOnly')),
            'secure': cookie.secure,
            # Secure cookies MUST use 'None' to be sent cross-site (required for YouTube auth)
            'sameSite': 'None' if cookie.secure else 'Lax'
        }
        playwright_cookies.append(playwright_cookie)
    
    async with async_playwright() as p:
        # Launch browser (headless=False to see it in action)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Add cookies to the browser context
        await context.add_cookies(playwright_cookies)
        
        # Create new page and navigate to YouTube
        page = await context.new_page()
        await page.goto('https://www.youtube.com')
        
        print("Navigated to YouTube with cookies loaded")
        print("Waiting 50 seconds...")
        
        # Wait 50 seconds
        await asyncio.sleep(50)
        
        print("Closing browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_youtube_with_cookies())