"""
Simple runner matching the user's workflow:
Initializes browser, checks/performs one-time session login,
and auto-sends streak messages with anti-ban protections.
"""

from utils import init_browser, login_tiktok, auto_send_message

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

if __name__ == "__main__":
    browser = init_browser(headless=True)
    login_tiktok()
    auto_send_message()
