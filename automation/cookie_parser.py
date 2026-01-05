import os
from pathlib import Path

def parse_netscape_cookies(cookie_file):
    """
    Parse Netscape format cookies file
    Returns list of cookie dictionaries compatible with Playwright
    """
    cookies = []
    
    if not os.path.exists(cookie_file):
        raise FileNotFoundError(f"Cookie file not found: {cookie_file}")
    
    with open(cookie_file, 'r', encoding='utf-8') as f:
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
                print(f"⚠ Warning: Error parsing cookie line: {str(e)}")
                continue
    
    return cookies

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


