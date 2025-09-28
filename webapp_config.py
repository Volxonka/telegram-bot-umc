# Configuration for Web App Integration

# Web App URLs
# For production, replace with your actual domain
# WEBAPP_BASE_URL = "https://your-domain.com"

# For development with ngrok:
# WEBAPP_BASE_URL = "https://your-ngrok-url.ngrok.io"

# For production on Render:
WEBAPP_BASE_URL = "https://telegram-webapp-umc.onrender.com"

# For local testing (temporary):
# WEBAPP_BASE_URL = "http://localhost:8081"

# Web App pages
WEBAPP_PAGES = {
    "main": "/enhanced.html",
    "mobile_test": "/mobile-test.html",
    "simple": "/test.html"
}

# Default web app page
DEFAULT_WEBAPP_PAGE = "main"

def get_webapp_url(page="main"):
    """Get full URL for web app page"""
    return f"{WEBAPP_BASE_URL}{WEBAPP_PAGES.get(page, WEBAPP_PAGES[DEFAULT_WEBAPP_PAGE])}"

def get_webapp_info():
    """Get WebAppInfo object for Telegram"""
    from telegram import WebAppInfo
    return WebAppInfo(url=get_webapp_url())
