from playwright.sync_api import sync_playwright
import os

def parse_netscape_cookies(cookie_file):
    """Parse Netscape format cookies file"""
    cookies = []
    
    with open(cookie_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            try:
                parts = line.split('\t')
                if len(parts) >= 7:
                    domain, flag, path, secure, expiry, name, value = parts[:7]
                    
                    cookie = {
                        'name': name,
                        'value': value,
                        'domain': domain,
                        'path': path,
                        'expires': int(expiry) if expiry != '0' else -1,
                        'httpOnly': False,
                        'secure': secure == 'TRUE',
                        'sameSite': 'None' if secure == 'TRUE' else 'Lax'
                    }
                    cookies.append(cookie)
            except Exception as e:
                print(f"Error parsing line: {line[:50]}... - {e}")
                continue
    
    return cookies

def main():
    # Proxy configuration
    proxy = {
        "server": "http://dc.decodo.com:10000",
        "username": "sp3vk5ed5y",
        "password": "a7ExhnYi~Mu8Cfd36t"
    }
    
    # Parse cookies
    cookies = parse_netscape_cookies('cookies.txt')
    print(f"Loaded {len(cookies)} cookies")
    
    with sync_playwright() as p:
        # Launch browser with proxy
        browser = p.chromium.launch(
            headless=False,
            proxy=proxy
        )
        
        # Create context
        context = browser.new_context()
        
        # Add cookies to context
        context.add_cookies(cookies)
        
        # Create page
        page = context.new_page()
        
        # Navigate to YouTube
        page.goto("https://www.youtube.com")
        
        print("Browser is open with proxy and cookies loaded. Close it manually when done.")
        
        # Wait indefinitely until browser is closed
        try:
            page.wait_for_event("close", timeout=0)
        except:
            pass
        
        print("Browser closed.")
        
        browser.close()

if __name__ == "__main__":
    main()