"""
TikTok Streak Saver - Modern, automated streak keeper for TikTok.
"""

import sys

# Ensure UTF-8 output on Windows consoles to prevent UnicodeEncodeError with emojis
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .tracker import Tracker
from .notifier import Notifier
from .browser import BrowserManager
from .session import SessionManager
from .messenger import StreakMessenger

__all__ = [
    "Tracker",
    "Notifier",
    "BrowserManager",
    "SessionManager",
    "StreakMessenger",
]
