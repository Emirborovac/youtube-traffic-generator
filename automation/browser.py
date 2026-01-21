import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import Config
import time
import threading
import uuid
import os
import tempfile

# Global lock to prevent simultaneous browser initialization
_browser_init_lock = threading.Lock()
_instance_counter = 0


class SeleniumElement:
    """Wrapper to provide Playwright-like interface for Selenium elements"""
    
    def __init__(self, element):
        self._element = element
    
    def get_attribute(self, name):
        """Get element attribute"""
        return self._element.get_attribute(name)
    
    def click(self):
        """Click element"""
        self._element.click()
    
    def text_content(self):
        """Get element text content"""
        return self._element.text


class SeleniumPage:
    """Wrapper to provide Playwright-like interface for Selenium driver"""
    
    def __init__(self, driver):
        self._driver = driver
    
    def goto(self, url, timeout=30000):
        """Navigate to URL"""
        self._driver.set_page_load_timeout(timeout / 1000)
        self._driver.get(url)
    
    def wait_for_selector(self, selector, timeout=5000):
        """Wait for element to be present"""
        try:
            WebDriverWait(self._driver, timeout / 1000).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            raise Exception(f"Timeout waiting for selector: {selector}")
    
    def wait_for_load_state(self, state='networkidle', timeout=30000):
        """Wait for page to load - simplified for Selenium"""
        # Selenium doesn't have networkidle, so we wait for document ready
        WebDriverWait(self._driver, timeout / 1000).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        # Additional wait for dynamic content
        time.sleep(2)
    
    def query_selector(self, selector):
        """Find element by CSS selector"""
        try:
            element = self._driver.find_element(By.CSS_SELECTOR, selector)
            return SeleniumElement(element)
        except NoSuchElementException:
            return None
    
    def evaluate(self, script, *args):
        """Execute JavaScript"""
        # Handle Playwright-style scripts with arrow functions
        if '=>' in script:
            # Convert Playwright style to Selenium style
            # (offset) => { ... } becomes just the body with arguments[0]
            script = script.split('=>', 1)[1].strip()
            if script.startswith('{') and script.endswith('}'):
                script = script[1:-1]
            script = script.replace('offset', 'arguments[0]')
        
        return self._driver.execute_script(script, *args)
    
    def close(self):
        """Close page (no-op for Selenium, handled by driver.quit)"""
        pass


def parse_cookies_for_selenium(cookie_file):
    """Parse Netscape format cookies for Selenium"""
    cookies = []
    
    with open(cookie_file, 'r') as f:
        for line in f:
            line = line.strip()
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
                        'secure': secure == 'TRUE',
                    }
                    # Only add expiry if it's valid
                    if expiry != '0':
                        cookie['expiry'] = int(expiry)
                    
                    cookies.append(cookie)
            except Exception as e:
                continue
    
    return cookies


class BrowserSession:
    """Manages browser session with undetected-chromedriver"""
    
    def __init__(self, cookie_file=None):
        self.cookie_file = cookie_file
        self.driver = None
        self.page = None
        self.logs = []
        self.user_data_dir = None
    
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
        """Start browser session with undetected-chromedriver"""
        global _instance_counter
        
        try:
            self.log("Initializing undetected Chrome browser", 1)
            
            # Use lock to prevent simultaneous initialization (causes file conflicts)
            with _browser_init_lock:
                _instance_counter += 1
                instance_id = _instance_counter
                
                self.log(f"Acquiring browser lock (instance #{instance_id})", 1)
                
                # Create unique user data directory for this instance
                self.user_data_dir = os.path.join(
                    tempfile.gettempdir(), 
                    f'uc_profile_{instance_id}_{uuid.uuid4().hex[:8]}'
                )
                os.makedirs(self.user_data_dir, exist_ok=True)
                
                # Chrome options
                options = uc.ChromeOptions()
                options.add_argument(f'--user-data-dir={self.user_data_dir}')
                # Add any needed options here
                # options.add_argument('--headless')  # Uncomment for headless mode
                
                # Launch undetected Chrome (version_main matches user's Chrome)
                # use_subprocess=True helps with multiple instances
                self.driver = uc.Chrome(
                    options=options, 
                    version_main=143,
                    use_subprocess=True
                )
                
                # Small delay to let chromedriver fully initialize before releasing lock
                time.sleep(1)
            
            self.log("Browser launched", 2)
            
            # Create page wrapper
            self.page = SeleniumPage(self.driver)
            self.log("Page wrapper created", 3)
            
            # Load cookies - need to navigate to domain first
            if self.cookie_file:
                self.log("Navigating to YouTube to set cookies...", 4)
                self.driver.get("https://www.youtube.com")
                time.sleep(2)
                
                cookies = parse_cookies_for_selenium(self.cookie_file)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        pass  # Some cookies may fail, that's okay
                
                self.log(f"Loaded {len(cookies)} cookies", 5)
            
            self.log("Browser session ready", 6)
            return True
            
        except Exception as e:
            self.log(f"Error starting browser: {str(e)}")
            return False
    
    def navigate(self, url):
        """Navigate to URL"""
        try:
            self.driver.get(url)
            # Wait for page to load
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(2)  # Additional wait for dynamic content
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
            if self.driver:
                self.driver.quit()
            
            # Clean up temporary user data directory
            if self.user_data_dir and os.path.exists(self.user_data_dir):
                try:
                    import shutil
                    shutil.rmtree(self.user_data_dir, ignore_errors=True)
                except:
                    pass  # Ignore cleanup errors
            
            self.log("Browser session closed")
            return True
            
        except Exception as e:
            self.log(f"Error closing browser: {str(e)}")
            return False
    
    def get_logs(self):
        """Get all logs"""
        return self.logs
