from automation.browser import BrowserSession
from config import Config

class ShortsHandler:
    """Handles shorts automation (like, watch)"""
    
    def __init__(self, url, cookie_file):
        self.url = url
        self.cookie_file = cookie_file
        self.browser = BrowserSession(cookie_file)
        self.success = False
    
    def execute(self):
        """Execute shorts automation workflow"""
        try:
            # Step 1-5: Start browser
            if not self.browser.start():
                return False, self.browser.get_logs()
            
            # Step 6: Navigate to YouTube first to activate cookies
            self.browser.log("Navigating to YouTube to activate session", 6)
            if not self.browser.navigate("https://www.youtube.com"):
                self.browser.close()
                return False, self.browser.get_logs()
            
            self.browser.wait(2)
            
            # Step 7: Navigate to shorts
            self.browser.log("Navigating to shorts URL", 7)
            if not self.browser.navigate(self.url):
                self.browser.close()
                return False, self.browser.get_logs()
            
            self.browser.log("Shorts page loaded successfully", 8)
            
            # Step 9: Check and click like button
            self.browser.log("Checking like button", 9)
            self._handle_like_button()
            
            # Step 10: Watch shorts
            self.browser.log(f"Watching shorts for {Config.WATCH_DURATION} seconds", 10)
            self.browser.wait(Config.WATCH_DURATION)
            
            # Step 11: Close browser
            self.browser.log("Shorts automation completed successfully", 11)
            self.browser.close()
            
            self.success = True
            return True, self.browser.get_logs()
            
        except Exception as e:
            self.browser.log(f"Error in shorts automation: {str(e)}")
            self.browser.close()
            return False, self.browser.get_logs()
    
    def _handle_like_button(self):
        """Check and click like button if not already liked"""
        try:
            # Wait for like button to be visible
            self.browser.page.wait_for_selector('button[aria-label*="like"]', timeout=5000)
            
            # Find like button (shorts have different structure)
            like_button = self.browser.page.query_selector('like-button-view-model button[aria-label*="like"]')
            
            if not like_button:
                # Try alternative selector
                like_button = self.browser.page.query_selector('button[aria-label*="like this video"]')
            
            if like_button:
                # Check if already liked (aria-pressed="true")
                aria_pressed = like_button.get_attribute('aria-pressed')
                
                if aria_pressed == 'true':
                    self.browser.log("Shorts already liked - skipping")
                else:
                    # Click like button
                    like_button.click()
                    self.browser.wait(1)
                    self.browser.log("Like button clicked successfully")
            else:
                self.browser.log("Like button not found - continuing")
                
        except Exception as e:
            self.browser.log(f"Could not handle like button: {str(e)}")


