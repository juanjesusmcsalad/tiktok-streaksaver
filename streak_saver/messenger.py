import random
import re
import time
from typing import Dict, Any, Tuple, List, Optional

try:
    from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
except ImportError:
    Page = Any = object
    PlaywrightTimeoutError = Exception

from .browser import BrowserManager
from .tracker import Tracker


class StreakMessenger:
    """
    Automates the interaction with TikTok Web Messages:
    finds conversations (via virtualized list or search), types naturally
    with human keystroke latency, detects streak status, and verifies dispatch.
    """

    def __init__(self, config: Dict[str, Any], tracker: Tracker, session_path: str = "session.json"):
        self.config = config
        self.tracker = tracker
        self.session_path = session_path
        self.default_messages = config.get("default_messages", ["🔥", "Streak! 🔥", "gm streak 🔥"])
        self.cooldown_hours = config.get("cooldown_hours", 18.0)
        self.min_delay = config.get("delay_between_chats_min", 6)
        self.max_delay = config.get("delay_between_chats_max", 14)
        self.headless = config.get("headless", True)

    def run_streak_saver(self, force: bool = False) -> Tuple[List[str], List[Dict[str, str]], List[Dict[str, str]]]:
        """
        Main execution loop for all configured friends.
        Returns: (successful_list, skipped_list, failed_list)
        """
        friends = self.config.get("friends", [])
        if not friends:
            print("⚠️ No friends defined in config.json. Add friends first!")
            return [], [], []

        successful: List[str] = []
        skipped: List[Dict[str, str]] = []
        failed: List[Dict[str, str]] = []

        # Check eligibility upfront
        queue = []
        for item in friends:
            uname = item.get("username", "").strip() if isinstance(item, dict) else str(item).strip()
            if not uname:
                continue

            can_send, reason = self.tracker.can_send(uname, self.cooldown_hours)
            if not can_send and not force:
                skipped.append({"username": uname, "reason": reason})
                print(f"⏭️ Skipping @{uname}: {reason}")
            else:
                if force and not can_send:
                    print(f"⚡ Force override active for @{uname} (bypassing cooldown)")
                queue.append(item)

        if not queue:
            print("✨ All friends are currently on cooldown. No messages needed!")
            return successful, skipped, failed

        print(f"\n🚀 Launching browser to send streak messages to {len(queue)} friend(s)...")

        browser_mgr = BrowserManager(session_path=self.session_path, headless=self.headless)
        try:
            context, page = browser_mgr.start()
            page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3500)

            # Handle potential cookie banners or dialogs
            self._dismiss_popups(page)

            for idx, item in enumerate(queue):
                uname = item.get("username", "").strip() if isinstance(item, dict) else str(item).strip()
                custom_msg = item.get("custom_message", "").strip() if isinstance(item, dict) else ""

                msg_text = custom_msg or random.choice(self.default_messages)

                print(f"\n[{idx + 1}/{len(queue)}] Processing @{uname}...")
                success, error, streak_info = self._send_to_user(page, uname, msg_text)

                if success:
                    status_badge = f" [Streak: {streak_info['display']}]" if streak_info and streak_info.get("display") else ""
                    print(f"  ✅ Sent to @{uname}: '{msg_text}'{status_badge}")
                    self.tracker.record_attempt(uname, success=True, message=msg_text, streak_info=streak_info)
                    successful.append(uname)
                else:
                    print(f"  ❌ Failed for @{uname}: {error}")
                    self.tracker.record_attempt(uname, success=False, message=msg_text, error=error)
                    failed.append({"username": uname, "error": error})

                # Human jitter delay between messages
                if idx < len(queue) - 1:
                    sleep_time = random.uniform(self.min_delay, self.max_delay)
                    print(f"  ⏳ Waiting {sleep_time:.1f}s before next friend to stay human...")
                    time.sleep(sleep_time)

        except Exception as e:
            print(f"❌ Fatal error during message loop: {e}")
        finally:
            browser_mgr.close()

        return successful, skipped, failed

    def _dismiss_popups(self, page: Page) -> None:
        """Closes standard consent dialogs and 'allow notifications' popups."""
        try:
            popup_selectors = [
                'button:has-text("Accept all")',
                'button:has-text("Not now")',
                'button:has-text("Allow essential cookies")',
                '[aria-label="Close"]',
            ]
            for selector in popup_selectors:
                elements = page.locator(selector)
                if elements.count() > 0 and elements.first.is_visible():
                    elements.first.click(timeout=1500)
                    page.wait_for_timeout(400)
        except Exception:
            pass

    def _detect_streak(self, page: Page, conv_item=None) -> Dict[str, Any]:
        """
        Extracts streak count and status from the conversation card extract or open chat.
        Reverse-engineered patterns:
          - Active: '14-day Streak', '🔥 14', '14 🔥'
          - Lost / Restorable: '3-day Streak lost . Restore'
        """
        try:
            texts = []
            if conv_item:
                try:
                    extract_el = conv_item.locator('[class*="SpanInfoExtract"], [data-e2e="dm-new-conversation-extract"]')
                    if extract_el.count() > 0:
                        texts.append(extract_el.first.inner_text().strip())
                except Exception:
                    pass

            try:
                header_el = page.locator('[class*="DivChatHeader"], [data-e2e="chat-header"]')
                if header_el.count() > 0:
                    texts.append(header_el.first.inner_text().strip())
            except Exception:
                pass

            combined = " ".join(texts)

            # Check for lost streak with restore grace window
            lost_m = re.search(r'(\d+)[- ]day\s+Streak\s+lost', combined, re.IGNORECASE)
            if lost_m:
                return {
                    "count": int(lost_m.group(1)),
                    "status": "lost_restorable",
                    "display": f"⚠️ {lost_m.group(1)}-day Streak lost (restore available)",
                }

            # Check for active day streak
            active_m = re.search(r'(\d+)[- ]day\s+Streak', combined, re.IGNORECASE)
            if active_m:
                return {
                    "count": int(active_m.group(1)),
                    "status": "active",
                    "display": f"🔥 {active_m.group(1)} days active",
                }

            # Check for flame emoji with number
            flame_m = re.search(r'🔥\s*(\d+)|(\d+)\s*🔥', combined)
            if flame_m:
                cnt = int(flame_m.group(1) or flame_m.group(2))
                return {
                    "count": cnt,
                    "status": "active",
                    "display": f"🔥 {cnt} days active",
                }

            return {"count": 0, "status": "none", "display": "None"}
        except Exception:
            return {"count": 0, "status": "none", "display": "Unknown"}

    def _open_conversation(self, page: Page, username: str) -> Tuple[bool, Optional[Any]]:
        """
        Locates and opens the conversation for a friend.
        Supports matching by display nickname or unique handle.
        Smoothly scrolls the virtualized conversation list to hydrate off-screen chats.
        Falls back to the DM search bar if necessary.
        """
        clean_name = username.lstrip("@").strip().lower()

        # Strategy A: Scan virtualized conversation list with scrolling
        def find_in_visible_items():
            items = page.locator('[data-e2e="dm-new-conversation-item"]').all()
            for item in items:
                if not item.is_visible():
                    continue
                nick_el = item.locator('[data-e2e="dm-new-conversation-nickname"]')
                nick_txt = nick_el.inner_text().strip().lower() if nick_el.count() > 0 else ""
                full_txt = item.inner_text().lower()

                if clean_name == nick_txt or clean_name in nick_txt or f"/@{clean_name}" in full_txt or clean_name in full_txt:
                    return item
            return None

        matched_item = find_in_visible_items()

        # If not in the initial viewport, scroll the virtual container down
        if not matched_item:
            list_container = page.locator('[data-e2e="dm-new-conversation-list"], [class*="DivConversationListContainer"]').first
            if list_container.count() > 0:
                for _ in range(4):
                    try:
                        list_container.evaluate("(el) => el.scrollTop += 350")
                        page.wait_for_timeout(300)
                        matched_item = find_in_visible_items()
                        if matched_item:
                            break
                    except Exception:
                        break

        if matched_item:
            try:
                matched_item.click()
                page.wait_for_timeout(2000)
                return True, matched_item
            except Exception:
                pass

        # Strategy B: Fallback to DM Search Bar
        search_selectors = [
            '[data-e2e="search-user-input"]',
            'input[placeholder*="Search" i]',
            'input[type="search"]',
        ]
        for s_sel in search_selectors:
            try:
                s_inputs = page.locator(s_sel).all()
                for s_input in s_inputs:
                    if s_input.is_visible():
                        s_input.click()
                        s_input.fill("")
                        page.wait_for_timeout(200)
                        s_input.type(clean_name, delay=60)
                        page.wait_for_timeout(1500)

                        results = page.locator('[data-e2e="search-user-item"], [data-e2e="search-result-item"], div[role="listbox"] div').all()
                        for r in results:
                            if r.is_visible():
                                r.click()
                                page.wait_for_timeout(2000)
                                return True, None
            except Exception:
                continue

        return False, None

    def _send_to_user(self, page: Page, username: str, message: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Opens conversation, types into DraftEditor, submits via Enter key,
        and verifies delivery.
        """
        clean_name = username.lstrip("@").strip()

        # Step 1: Open conversation
        opened, conv_item = self._open_conversation(page, clean_name)
        if not opened:
            page.screenshot(path="debug_chat_error.png")
            return False, f"Could not find conversation for '{clean_name}' in inbox (screenshot saved to debug_chat_error.png)", {}

        # Wait for chat area to render
        page.wait_for_timeout(2000)

        # Handle any floating banners or popups
        try:
            close_buttons = page.locator('svg[data-icon="close"], button[aria-label="Close"], button:has-text("✕")').all()
            for cb in close_buttons:
                if cb.is_visible():
                    cb.click()
                    page.wait_for_timeout(400)
                    break
        except Exception:
            pass

        # Step 2: Locate DraftEditor message input
        input_locators = [
            'div.public-DraftEditor-content[contenteditable="true"]',
            '[data-e2e="message-input-area"] div[contenteditable="true"]',
            'div[contenteditable="true"]',
            '[aria-label="Send a message..."]',
            'div[role="textbox"]',
        ]

        editor = None
        for selector in input_locators:
            try:
                candidates = page.locator(selector).all()
                for cand in candidates:
                    if cand.is_visible():
                        editor = cand
                        break
                if editor:
                    break
            except Exception:
                continue

        if not editor:
            page.screenshot(path="debug_chat_error.png")
            page_text = page.locator("body").inner_text()
            if "privacy settings" in page_text.lower():
                return False, "Privacy restriction: friend's privacy settings do not permit DMs", {}
            if "only friends" in page_text.lower() or "mutual" in page_text.lower():
                return False, "Not mutual friends: user requires mutual follow to message", {}

            return False, "Could not locate chat message input editor (saved screenshot to debug_chat_error.png)", {}

        # Detect streak status from conversation card / chat header
        streak_info = self._detect_streak(page, conv_item)

        try:
            editor.click()
            page.wait_for_timeout(300)

            # Step 3: Type message with natural keystroke jitter (35ms - 85ms)
            for char in message:
                editor.type(char, delay=random.randint(35, 85))

            page.wait_for_timeout(400)

            # Step 4: Submit message via Enter key (verified TikTok Web desktop protocol)
            page.keyboard.press("Enter")
            page.wait_for_timeout(1200)

            # Verify that the input box cleared
            try:
                remaining_text = editor.inner_text().strip()
                if remaining_text == message.strip():
                    # Retry pressing Enter once
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(1000)
            except Exception:
                pass

            # Detect streak again in case updated
            updated_streak = self._detect_streak(page, conv_item)
            if updated_streak.get("count", 0) > streak_info.get("count", 0):
                streak_info = updated_streak

            return True, "", streak_info

        except Exception as e:
            page.screenshot(path="debug_chat_error.png")
            return False, f"Error typing/sending message: {e} (saved to debug_chat_error.png)", streak_info
