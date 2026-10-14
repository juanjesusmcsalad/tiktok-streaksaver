import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple


class Tracker:
    """
    Tracks message sending history and protects against spamming or duplicate sends.
    """

    def __init__(self, file_path: str = "history.json"):
        self.file_path = Path(file_path)
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.file_path.exists():
            return {"users": {}, "runs": []}
        try:
            with open(self.file_path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception:
            return {"users": {}, "runs": []}

    def _save(self) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Tracker] Error saving history: {e}")

    def can_send(self, username: str, cooldown_hours: float = 18.0) -> Tuple[bool, str]:
        """
        Determines whether a streak message can be sent to this user now.
        Prevents multiple messages within cooldown_hours (default 18h).
        """
        user_info = self.data.get("users", {}).get(username.lower())
        if not user_info:
            return True, "No prior send recorded"

        last_success = user_info.get("last_success_timestamp")
        if not last_success:
            return True, "Previous attempt failed; eligible for retry"

        try:
            last_dt = datetime.fromisoformat(last_success)
            now = datetime.now(timezone.utc)
            elapsed_hours = (now - last_dt).total_seconds() / 3600.0

            if elapsed_hours < cooldown_hours:
                remaining = cooldown_hours - elapsed_hours
                return False, f"Cooldown active: sent {elapsed_hours:.1f}h ago (wait {remaining:.1f}h)"
            return True, f"Eligible: last sent {elapsed_hours:.1f}h ago"
        except Exception as e:
            return True, f"Eligible (timestamp parse fallback: {e})"

    def record_attempt(
        self, username: str, success: bool, message: str, error: str = "", streak_info: Dict[str, Any] = None
    ) -> None:
        """
        Records the outcome of a message attempt.
        """
        uname = username.lower()
        now_str = datetime.now(timezone.utc).isoformat()

        if "users" not in self.data:
            self.data["users"] = {}

        if uname not in self.data["users"]:
            self.data["users"][uname] = {
                "display_name": username,
                "total_sent": 0,
                "streak_days": 0,
                "streak_status": "none",
                "streak_display": "",
                "last_success_timestamp": None,
                "last_attempt_timestamp": None,
                "last_message": None,
                "last_error": None,
            }

        user_data = self.data["users"][uname]
        user_data["last_attempt_timestamp"] = now_str
        user_data["display_name"] = username

        if streak_info:
            user_data["streak_days"] = streak_info.get("count", user_data.get("streak_days", 0))
            user_data["streak_status"] = streak_info.get("status", user_data.get("streak_status", "none"))
            user_data["streak_display"] = streak_info.get("display", user_data.get("streak_display", ""))

        if success:
            user_data["total_sent"] = user_data.get("total_sent", 0) + 1
            user_data["last_success_timestamp"] = now_str
            user_data["last_message"] = message
            user_data["last_error"] = None
        else:
            user_data["last_error"] = error

        self._save()

    def get_user_stats(self, username: str) -> Dict[str, Any]:
        return self.data.get("users", {}).get(username.lower(), {})

    def get_all_stats(self) -> Dict[str, Any]:
        return self.data.get("users", {})

    def reset(self, username: str = None) -> None:
        """
        Resets cooldown timestamps for testing.
        If username is provided, resets only that user.
        If None, clears all cooldowns.
        """
        if username:
            uname = username.lower()
            if uname in self.data.get("users", {}):
                self.data["users"][uname]["last_success_timestamp"] = None
        else:
            for u in self.data.get("users", {}).values():
                u["last_success_timestamp"] = None
        self._save()
