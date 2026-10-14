"""
Drop-in replacement for the legacy utils.py in huuthang201/tiktok-streak.
Upgraded to use Playwright with anti-detection and persistent session management.
"""

import os
from streak_saver.browser import BrowserManager
from streak_saver.session import SessionManager
from streak_saver.tracker import Tracker
from streak_saver.messenger import StreakMessenger
from streak_saver.notifier import Notifier


def init_browser(headless=True):
    """Initializes stealth browser manager."""
    mgr = BrowserManager(headless=headless)
    return mgr


def login_tiktok(browser=None, wait=None, username=None, password=None):
    """
    Performs safe session authentication.
    Instead of brittle plaintext password typing (which triggers instant captchas),
    this opens an interactive session to log in via QR code or credentials once,
    saving the state to session.json.
    """
    sm = SessionManager()
    if not os.path.exists("session.json"):
        print("⚡ No existing session found. Opening interactive login window...")
        sm.interactive_login()
    else:
        print("✅ Found existing session.json!")


def auto_send_message(browser=None, wait=None, config=None):
    """
    Dispatches streak messages using anti-ban delays, jitter,
    and automatic conversation resolution.
    """
    import json
    cfg = config
    if not cfg:
        with open("config.json", "r", encoding="utf-8-sig") as f:
            cfg = json.load(f)

    tracker = Tracker()
    messenger = StreakMessenger(cfg, tracker)
    successful, skipped, failed = messenger.run_streak_saver()

    notifier = Notifier()
    notifier.send_summary(successful, skipped, failed)
    return successful, skipped, failed
