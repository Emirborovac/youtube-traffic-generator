from playwright.sync_api import sync_playwright
from automation.cookie_parser import parse_netscape_cookies
from config import Config
import time

class BrowserSession:
    """Manages browser session with proxy and cookies"""
    
    def __init__(self, cookie_file=None):
        self.cookie_file = cookie_file
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.logs = []
    
    def log(self, message, step=None):
        """Add log message"""
        if step:
            log_msg = f"Step {step}: {message}"
        else:
            log_msg = message
        
        self.logs.append({
            'timestamp': time.time(),
            'message': log_msg
        })
        print(f"✓ {log_msg}")
    
    def start(self):
        """Start browser session - 100% identical to test.py"""
        try:
            self.log("Initializing browser", 1)
            
            # Start Playwright
            self.playwright = sync_playwright().start()
            
            # Launch browser (NO proxy - exactly like test.py)
            self.browser = self.playwright.chromium.launch(headless=False)
            self.log("Browser launched", 2)
            
            # Create context (NO proxy - exactly like test.py)
            self.context = self.browser.new_context()
            self.log("Context created", 3)
            
            # Add cookies to context (exactly like test.py)
            if self.cookie_file:
                cookies = parse_netscape_cookies(self.cookie_file)
                self.context.add_cookies(cookies)
                self.log(f"Loaded {len(cookies)} cookies", 4)
            
            # Create page (exactly like test.py)
            self.page = self.context.new_page()
            self.log("Browser session ready", 5)
            
            return True
            
        except Exception as e:
            self.log(f"Error starting browser: {str(e)}")
            return False
    
    def navigate(self, url):
        """Navigate to URL"""
        try:
            self.page.goto(url, timeout=30000)
            self.page.wait_for_load_state('networkidle', timeout=30000)
            return True
        except Exception as e:
            self.log(f"Error navigating to {url}: {str(e)}")
            return False
    
    def wait(self, seconds):
        """Wait for specified seconds"""
        time.sleep(seconds)
    
    def close(self):
        """Close browser session"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            self.log("Browser session closed")
            return True
            
        except Exception as e:
            self.log(f"Error closing browser: {str(e)}")
            return False
    
    def get_logs(self):
        """Get all logs"""
        return self.logs


