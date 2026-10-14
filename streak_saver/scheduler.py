import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable


class Scheduler:
    """
    Manages background scheduling:
    1. Native Windows Task Scheduler integration (schtasks)
    2. Python daemon loop for long-running processes / VPS
    """

    TASK_NAME = "TikTokStreakSaver"

    @classmethod
    def setup_windows_task(cls, interval_hours: int = 18, start_time: str = None) -> bool:
        """
        Registers a Windows Scheduled Task (schtasks) that runs TikTokStreakSaver
        every interval_hours (e.g. 18h). Runs headless, sends streaks, and auto-exits.
        """
        if getattr(sys, "frozen", False):
            exe_path = Path(sys.executable).resolve()
            if "TikTokStreakConfig" in exe_path.name:
                exe_path = exe_path.parent / "TikTokStreakSaver.exe"
            cmd = f'"{exe_path}" run'
        else:
            python_exe = sys.executable
            script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            main_script = os.path.join(script_dir, "main.py")
            cmd = f'"{python_exe}" "{main_script}" run'

        interval_hours = max(1, int(interval_hours))
        if interval_hours < 24:
            sc_type = "HOURLY"
            mo_val = interval_hours
            desc_text = f"every {interval_hours} hour(s)"
        else:
            sc_type = "DAILY"
            mo_val = max(1, interval_hours // 24)
            desc_text = f"every {mo_val} day(s) ({interval_hours}h)"

        schtask_cmd = [
            "schtasks",
            "/create",
            "/tn",
            cls.TASK_NAME,
            "/tr",
            cmd,
            "/sc",
            sc_type,
            "/mo",
            str(mo_val),
            "/f",
        ]
        if start_time:
            schtask_cmd.extend(["/st", start_time])

        try:
            res = subprocess.run(schtask_cmd, capture_output=True, text=True, check=True)
            print(f"✅ Windows Task '{cls.TASK_NAME}' registered successfully: {desc_text}.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Windows Scheduled Task: {e.stderr or e.stdout}")
            return False

    @classmethod
    def remove_windows_task(cls) -> bool:
        """Removes the Windows Scheduled Task."""
        schtask_cmd = ["schtasks", "/delete", "/tn", cls.TASK_NAME, "/f"]
        try:
            subprocess.run(schtask_cmd, capture_output=True, text=True, check=True)
            print(f"✅ Windows Task '{cls.TASK_NAME}' removed.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to remove task: {e.stderr or e.stdout}")
            return False

    @classmethod
    def get_task_status(cls) -> dict:
        """
        Queries Windows Task Scheduler for the task status.
        Uses instant direct disk inspection (<1ms) to eliminate all subprocess/AMSI delay.
        """
        task_file = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "Tasks" / cls.TASK_NAME
        if not task_file.exists():
            return {"exists": False}

        try:
            try:
                xml_str = task_file.read_text(encoding="utf-16", errors="ignore")
            except Exception:
                xml_str = task_file.read_text(encoding="utf-8", errors="ignore")

            repeat_info = "Daily"
            if "<Interval>PT" in xml_str:
                val = xml_str.split("<Interval>PT", 1)[1].split("</Interval>", 1)[0]
                repeat_info = f"Every {val.lower()}"

            return {
                "exists": True,
                "status": "Ready",
                "next_run": "Active on schedule",
                "repeat": repeat_info,
            }
        except Exception:
            return {"exists": True, "status": "Ready", "next_run": "Active", "repeat": "Scheduled"}

    @classmethod
    def run_daemon_loop(cls, target_time_str: str, job_func: Callable[[], None]) -> None:
        """
        Runs an infinite Python daemon loop that fires job_func daily at target_time_str (HH:MM).
        """
        print(f"🕒 Daemon active. Waiting to execute daily at {target_time_str}...")
        while True:
            now = datetime.now()
            target_hour, target_minute = map(int, target_time_str.split(":"))
            scheduled_today = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

            if scheduled_today <= now:
                scheduled_today += timedelta(days=1)

            seconds_to_wait = (scheduled_today - now).total_seconds()
            hours_wait = seconds_to_wait / 3600.0
            print(f"💤 Sleeping for {hours_wait:.2f} hours until next trigger at {scheduled_today.strftime('%Y-%m-%d %H:%M')}...")

            time.sleep(seconds_to_wait)

            print(f"\n⏰ Triggering scheduled streak job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}!")
            try:
                job_func()
            except Exception as e:
                print(f"❌ Error during daemon job execution: {e}")

            time.sleep(60)  # Avoid double triggers in same minute
