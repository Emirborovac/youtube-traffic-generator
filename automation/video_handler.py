from automation.browser import BrowserSession
from config import Config
import random
import time

class VideoHandler:
    """Handles video automation (like, subscribe, watch, seek)"""
    
    def __init__(self, url, cookie_file):
        self.url = url
        self.cookie_file = cookie_file
        self.browser = BrowserSession(cookie_file)
        self.success = False
    
    def execute(self):
        """Execute video automation workflow"""
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
            
            # Step 7: Navigate to video
            self.browser.log("Navigating to video URL", 7)
            if not self.browser.navigate(self.url):
                self.browser.close()
                return False, self.browser.get_logs()
            
            self.browser.log("Video page loaded successfully", 8)
            
            # Step 9: Check and click like button
            self.browser.log("Checking like button", 9)
            self._handle_like_button()
            
            # Step 10: Check and click subscribe button
            self.browser.log("Checking subscribe button", 10)
            self._handle_subscribe_button()
            
            # Step 11: Start watching with random seeking
            self.browser.log(f"Watching video for {Config.WATCH_DURATION} seconds with random seeking", 11)
            self._watch_with_seeking(Config.WATCH_DURATION)
            
            # Step 12: Close browser
            self.browser.log("Video automation completed successfully", 12)
            self.browser.close()
            
            self.success = True
            return True, self.browser.get_logs()
            
        except Exception as e:
            self.browser.log(f"Error in video automation: {str(e)}")
            self.browser.close()
            return False, self.browser.get_logs()
    
    def _handle_like_button(self):
        """Check and click like button if not already liked"""
        try:
            # Wait for like button to be visible
            self.browser.page.wait_for_selector('button[aria-label*="like"]', timeout=5000)
            
            # Find like button
            like_button = self.browser.page.query_selector('button[aria-label*="like"]')
            
            if like_button:
                # Check if already liked (aria-pressed="true")
                aria_pressed = like_button.get_attribute('aria-pressed')
                
                if aria_pressed == 'true':
                    self.browser.log("Video already liked - skipping")
                else:
                    # Click like button
                    like_button.click()
                    self.browser.wait(1)
                    self.browser.log("Like button clicked successfully")
            else:
                self.browser.log("Like button not found - continuing")
                
        except Exception as e:
            self.browser.log(f"Could not handle like button: {str(e)}")
    
    def _handle_subscribe_button(self):
        """Check and click subscribe button if not already subscribed"""
        try:
            # Wait for subscribe button area
            self.browser.page.wait_for_selector('#subscribe-button', timeout=5000)
            
            # Look for "Subscribe" button (not "Subscribed")
            subscribe_button = self.browser.page.query_selector('button[aria-label*="Subscribe to"]')
            
            if subscribe_button:
                # Check button text
                button_text = subscribe_button.text_content()
                
                if 'Subscribe' in button_text and 'Subscribed' not in button_text:
                    subscribe_button.click()
                    self.browser.wait(1)
                    self.browser.log("Subscribe button clicked successfully")
                else:
                    self.browser.log("Already subscribed - skipping")
            else:
                self.browser.log("Subscribe button not found or already subscribed")
                
        except Exception as e:
            self.browser.log(f"Could not handle subscribe button: {str(e)}")
    
    def _watch_with_seeking(self, duration):
        """Watch video with random seeking (3 times)"""
        try:
            # Find video player
            video = self.browser.page.query_selector('video')
            
            if not video:
                self.browser.log("Video player not found - just waiting")
                self.browser.wait(duration)
                return
            
            # Random seek 3 times during watch duration
            seek_count = 3
            intervals = sorted([random.randint(5, duration - 5) for _ in range(seek_count)])
            
            last_time = 0
            for i, seek_time in enumerate(intervals):
                # Wait until seek time
                wait_duration = seek_time - last_time
                self.browser.wait(wait_duration)
                
                # Random seek forward/backward (5-15 seconds)
                seek_offset = random.choice([-15, -10, -5, 5, 10, 15])
                
                self.browser.page.evaluate(f"""
                    (offset) => {{
                        const video = document.querySelector('video');
                        if (video) {{
                            video.currentTime = Math.max(0, video.currentTime + offset);
                        }}
                    }}
                """, seek_offset)
                
                self.browser.log(f"Random seek #{i+1}: {seek_offset}s")
                
                last_time = seek_time
            
            # Wait remaining time
            remaining = duration - last_time
            if remaining > 0:
                self.browser.wait(remaining)
                
        except Exception as e:
            self.browser.log(f"Error during seeking: {str(e)} - continuing normal watch")
            self.browser.wait(duration)


