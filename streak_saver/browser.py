import os
import sys
from pathlib import Path
try:
    from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
except ImportError:
    sync_playwright = None
    Browser = BrowserContext = Page = Playwright = Any = object


STEALTH_INIT_SCRIPT = """
// Strip navigator.webdriver flag
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Mock Chrome runtime
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};

// Mock languages & plugins
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});
"""

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)


class BrowserManager:
    """
    Manages Playwright browser lifecycle with anti-fingerprinting evasion,
    custom headers, and session persistence.
    """

    def __init__(self, session_path: str = "session.json", headless: bool = True):
        self.session_path = Path(session_path)
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    def start(self, interactive: bool = False) -> Tuple[BrowserContext, Page]:
        """
        Launches browser with stealth flags and loads session if available.
        """
        if getattr(sys, "frozen", False):
            bundle_dir = getattr(sys, "_MEIPASS", str(Path(sys.executable).parent))
            bundled_browsers = os.path.join(bundle_dir, "ms-playwright")
            local_browsers = os.path.join(str(Path(sys.executable).parent), "ms-playwright")
            if os.path.exists(bundled_browsers):
                os.environ["PLAYWRIGHT_BROWSERS_PATH"] = bundled_browsers
            elif os.path.exists(local_browsers):
                os.environ["PLAYWRIGHT_BROWSERS_PATH"] = local_browsers

        try:
            self.playwright = sync_playwright().start()
        except Exception as e:
            if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
                print("\n[!] Playwright browser binary missing. Please run:\n    playwright install chromium\n")
            raise e

        # Anti-detection launch args
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--disable-infobars",
        ]

        is_headless = False if interactive else self.headless

        # Try standard chromium launch, with fallback to system Edge/Chrome
        launch_kwargs = {
            "headless": is_headless,
            "args": launch_args,
        }

        try:
            self.browser = self.playwright.chromium.launch(**launch_kwargs)
        except Exception as e:
            err_str = str(e)
            if "Executable doesn't exist" in err_str or "playwright install" in err_str:
                # Automatic fallback to system Microsoft Edge or Google Chrome!
                try:
                    self.browser = self.playwright.chromium.launch(channel="msedge", **launch_kwargs)
                except Exception:
                    try:
                        self.browser = self.playwright.chromium.launch(channel="chrome", **launch_kwargs)
                    except Exception:
                        print("\n[!] No compatible browser found. Please run: playwright install chromium\n")
                        raise e
            else:
                raise e

        context_kwargs = {
            "user_agent": DEFAULT_USER_AGENT,
            "viewport": {"width": 1280, "height": 800},
            "device_scale_factor": 1,
            "locale": "en-US",
            "timezone_id": "America/New_York",
        }

        # Load session state if exists and not logging in freshly
        if not interactive and self.session_path.exists():
            context_kwargs["storage_state"] = str(self.session_path)

        self.context = self.browser.new_context(**context_kwargs)
        self.context.add_init_script(STEALTH_INIT_SCRIPT)

        page = self.context.new_page()
        return self.context, page

    def save_session(self) -> None:
        """
        Saves current cookies and storage state to session.json.
        """
        if self.context:
            self.context.storage_state(path=str(self.session_path))

    def close(self) -> None:
        """
        Safely shuts down browser and playwright instances.
        """
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass

        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass

        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
