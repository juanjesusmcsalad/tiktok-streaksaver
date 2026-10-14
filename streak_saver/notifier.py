import os
try:
    import requests
except ImportError:
    requests = None
from typing import List, Dict, Any, Optional


class Notifier:
    """
    Sends notifications to Discord and Telegram when streak actions complete or fail.
    """

    def __init__(self, discord_webhook: Optional[str] = None, telegram_token: Optional[str] = None, telegram_chat_id: Optional[str] = None):
        self.discord_webhook = discord_webhook or os.getenv("DISCORD_WEBHOOK_URL", "").strip()
        self.telegram_token = telegram_token or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.telegram_chat_id = telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID", "").strip()

    def send_summary(self, successful: List[str], skipped: List[Dict[str, str]], failed: List[Dict[str, str]]) -> None:
        """
        Dispatches summary to all configured channels.
        """
        total = len(successful) + len(skipped) + len(failed)
        if total == 0:
            return

        title = "🔥 TikTok Streak Saver Report"
        description_lines = [
            f"**Execution Summary:**",
            f"• ✅ **Sent:** {len(successful)} ({', '.join(successful) if successful else 'None'})",
            f"• ⏭️ **Skipped (Cooldown):** {len(skipped)}",
            f"• ❌ **Failed:** {len(failed)}",
        ]

        if failed:
            description_lines.append("\n**Failures:**")
            for item in failed:
                description_lines.append(f"- `@{item.get('username')}`: {item.get('error')}")

        message_body = "\n".join(description_lines)

        self._send_discord(title, message_body, is_error=bool(failed and not successful))
        self._send_telegram(f"{title}\n\n{message_body}")

    def _send_discord(self, title: str, description: str, is_error: bool = False) -> None:
        if not self.discord_webhook or not requests:
            return

        payload = {
            "embeds": [
                {
                    "title": title,
                    "description": description,
                    "color": 0xFF0050 if not is_error else 0xFF3333,  # TikTok pinkish red or warning red
                    "footer": {"text": "TikTok Streak Saver • Automated Engine"},
                }
            ]
        }
        try:
            requests.post(self.discord_webhook, json=payload, timeout=8)
        except Exception as e:
            print(f"[Notifier] Failed to send Discord webhook: {e}")

    def _send_telegram(self, text: str) -> None:
        if not self.telegram_token or not self.telegram_chat_id or not requests:
            return

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        try:
            requests.post(url, json=payload, timeout=8)
        except Exception as e:
            print(f"[Notifier] Failed to send Telegram alert: {e}")
