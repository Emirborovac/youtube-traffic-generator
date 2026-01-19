import os
from pathlib import Path
import http.cookiejar

def parse_netscape_cookies(cookie_file):
    """
    Parse Netscape format cookies file using http.cookiejar
    Returns list of cookie dictionaries compatible with Playwright
    """
    if not os.path.exists(cookie_file):
        raise FileNotFoundError(f"Cookie file not found: {cookie_file}")
    
    # Use MozillaCookieJar for proper Netscape format parsing
    cookie_jar = http.cookiejar.MozillaCookieJar(cookie_file)
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
    
    return playwright_cookies

def get_available_cookies(cookies_dir='cookies_store'):
    """
    Get list of available cookie files
    Returns list of cookie file paths
    """
    cookies_path = Path(cookies_dir)
    
    if not cookies_path.exists():
        os.makedirs(cookies_path, exist_ok=True)
        return []
    
    # Find all .txt files in cookies_store
    cookie_files = list(cookies_path.glob('*.txt'))
    
    return [str(f) for f in cookie_files]

def validate_cookie_file(cookie_file):
    """
    Validate if cookie file is valid
    Returns (is_valid, error_message)
    """
    try:
        cookies = parse_netscape_cookies(cookie_file)
        
        if len(cookies) == 0:
            return False, "No valid cookies found in file"
        
        # Check for essential YouTube cookies
        cookie_names = [c['name'] for c in cookies]
        
        if not any('youtube' in name.lower() or 'google' in name.lower() for name in cookie_names):
            return False, "No YouTube/Google cookies found"
        
        return True, f"Valid cookie file with {len(cookies)} cookies"
        
    except Exception as e:
        return False, str(e)


