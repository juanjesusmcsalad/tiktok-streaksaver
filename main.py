#!/usr/bin/env python3
"""
TikTok Streak Saver CLI
Modern, automated, anti-detection streak keeper for TikTok.
"""

import sys

# Ensure UTF-8 output on Windows consoles to prevent UnicodeEncodeError with emojis
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os
import json
import argparse
import subprocess
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

from streak_saver.tracker import Tracker
from streak_saver.notifier import Notifier
from streak_saver.session import SessionManager
from streak_saver.messenger import StreakMessenger
from streak_saver.scheduler import Scheduler

CONFIG_PATH = BASE_DIR / "config.json"
SESSION_PATH = BASE_DIR / "session.json"
HISTORY_PATH = BASE_DIR / "history.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        default_config = {
            "friends": [],
            "default_messages": ["🔥", "Streak! 🔥", "gm streak 🔥", "Daily streak 🔥"],
            "cooldown_hours": 18,
            "delay_between_chats_min": 6,
            "delay_between_chats_max": 14,
            "headless": True,
            "schedule_time": "09:00",
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error parsing config.json: {e}")
        sys.exit(1)


def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def cmd_login(args):
    """Run interactive login flow."""
    sm = SessionManager(session_path=str(SESSION_PATH))
    success = sm.interactive_login()
    if success:
        print("\n🎉 Setup complete! You can now run the streak saver.")
    else:
        print("\n⚠️ Login was not completed. Please try again.")


def cmd_run(args):
    """Execute streak saving routine and auto-close when done."""
    cfg = load_config()
    friends = cfg.get("friends", [])
    if not friends:
        print("\n" + "=" * 55)
        print("⚠️ No friends configured in your streak list!")
        print("🚀 Opening TikTok Streak Config so you can add friends...")
        print("=" * 55 + "\n")

        # Open TikTokStreakConfig
        config_exe = BASE_DIR / "TikTokStreakConfig.exe"
        if config_exe.exists():
            subprocess.Popen([str(config_exe)], cwd=str(BASE_DIR))
        else:
            gui_py = BASE_DIR / "gui_config.py"
            if gui_py.exists():
                subprocess.Popen([sys.executable, str(gui_py)], cwd=str(BASE_DIR))

        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                "No friends found in your streak list!\n\nPlease add at least one friend in TikTok Streak Config to start sending streaks.",
                "TikTok Streak Saver — Add Friends",
                0x00000030 | 0x00010000  # MB_ICONWARNING | MB_SETFOREGROUND
            )
        except Exception:
            pass
        return

    if args and getattr(args, "headful", False):
        cfg["headless"] = False

    force = bool(args and getattr(args, "force", False))
    tracker = Tracker(file_path=str(HISTORY_PATH))
    notifier = Notifier()

    messenger = StreakMessenger(cfg, tracker, session_path=str(SESSION_PATH))
    successful, skipped, failed = messenger.run_streak_saver(force=force)

    print("\n" + "=" * 50)
    print("📊 RUN SUMMARY")
    print(f"• Successfully sent: {len(successful)}")
    print(f"• Skipped (cooldown): {len(skipped)}")
    print(f"• Failed: {len(failed)}")
    print("=" * 50)

    # Dispatch webhooks if configured
    notifier.send_summary(successful, skipped, failed)
    print("👋 Finished streak check. Closing automatically.")


def cmd_status(args):
    """Check session health and tracked friend streaks."""
    print("🔍 Checking session status...")
    sm = SessionManager(session_path=str(SESSION_PATH))
    valid, msg = sm.validate_session()

    if valid:
        print(f"✅ Session Status: VALID ({msg})")
    else:
        print(f"❌ Session Status: INVALID ({msg})")

    cfg = load_config()
    tracker = Tracker(file_path=str(HISTORY_PATH))
    stats = tracker.get_all_stats()
    cooldown_hours = cfg.get("cooldown_hours", 18.0)

    print("\n📋 Configured Friends:")
    friends = cfg.get("friends", [])
    if not friends:
        print("  (No friends configured yet. Run 'python main.py add <username>')")
    else:
        header = f"{'Friend':<14} | {'Streak Status':<28} | {'Cooldown / Status':<35} | {'Sent':<5}"
        print(header)
        print("-" * len(header))
        for f in friends:
            uname = f.get("username") if isinstance(f, dict) else str(f)
            user_stat = stats.get(uname.lower(), {})
            total_sent = user_stat.get("total_sent", 0)

            # Streak display
            streak_disp = user_stat.get("streak_display")
            if not streak_disp:
                days = user_stat.get("streak_days", 0)
                streak_disp = f"🔥 {days} days" if days > 0 else "None"

            # Cooldown check
            can_send, reason = tracker.can_send(uname, cooldown_hours)
            tag = "🟢 Ready" if can_send else "⏳ Cooldown"
            cooldown_desc = f"{tag}: {reason}"

            print(f"@{uname:<13} | {streak_disp:<28} | {cooldown_desc:<35} | {total_sent:<5}")


def cmd_add(args):
    """Add a friend to the streak list."""
    cfg = load_config()
    uname = args.username.strip().lstrip("@")
    custom_msg = args.message or ""

    existing = [f.get("username").lower() for f in cfg.get("friends", []) if isinstance(f, dict)]
    if uname.lower() in existing:
        print(f"⚠️ Friend @{uname} is already in the list.")
        return

    cfg.setdefault("friends", []).append({"username": uname, "custom_message": custom_msg})
    save_config(cfg)
    print(f"✅ Added @{uname} to streak list! (Custom message: '{custom_msg or 'Random pool'}')")


def cmd_remove(args):
    """Remove a friend from the streak list."""
    cfg = load_config()
    uname = args.username.strip().lstrip("@").lower()

    friends = cfg.get("friends", [])
    new_friends = [f for f in friends if (f.get("username", "").lower() if isinstance(f, dict) else str(f).lower()) != uname]

    if len(new_friends) == len(friends):
        print(f"⚠️ Friend @{uname} not found in config.")
    else:
        cfg["friends"] = new_friends
        save_config(cfg)
        print(f"✅ Removed @{uname} from streak list.")


def cmd_startup(args):
    """Configure running automatically when PC turns on (Windows Startup folder)."""
    startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    if not startup_dir.exists():
        print(f"❌ Could not locate Windows Startup directory: {startup_dir}")
        return

    shortcut_path = startup_dir / "TikTokStreakSaver.lnk"

    if args and getattr(args, "remove", False):
        if shortcut_path.exists():
            shortcut_path.unlink()
            print("✅ Removed TikTok Streak Saver from Windows Startup.")
        else:
            print("ℹ️ TikTok Streak Saver was not in Windows Startup.")
        return

    # Determine executable or script target
    if getattr(sys, "frozen", False):
        target = str(Path(sys.executable).resolve())
        cwd = str(Path(sys.executable).resolve().parent)
        args_str = "run"
    else:
        target = sys.executable
        cwd = str(BASE_DIR)
        args_str = f'"{BASE_DIR / "main.py"}" run'

    ps_cmd = (
        f"$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{shortcut_path}'); "
        f"$s.TargetPath = '{target}'; "
        f"$s.Arguments = '{args_str}'; "
        f"$s.WorkingDirectory = '{cwd}'; "
        f"$s.Description = 'TikTok Auto Streak Saver'; "
        f"$s.Save()"
    )

    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, capture_output=True)
        print("🎉 Successfully added TikTok Streak Saver to Windows Startup!")
        print(f"📁 Shortcut: {shortcut_path}")
        print("💡 Whenever you turn on your PC, it will automatically send streaks and close.")
    except Exception as e:
        print(f"❌ Failed to create Windows Startup shortcut: {e}")


def cmd_schedule(args):
    """Configure Windows Task Scheduler execution based on interval hours."""
    if args and getattr(args, "status", False):
        info = Scheduler.get_task_status()
        if info.get("exists"):
            print("🟢 Windows Task 'TikTokStreakSaver' is ACTIVE!")
            print(f"• Status:   {info.get('status')}")
            print(f"• Next Run: {info.get('next_run')}")
            if info.get("repeat") != "N/A":
                print(f"• Repeats:  {info.get('repeat')}")
        else:
            print("⚪ No Windows Task 'TikTokStreakSaver' currently registered.")
        return

    if args and getattr(args, "remove", False):
        Scheduler.remove_windows_task()
        return

    cfg = load_config()
    hours = args.hours if (args and args.hours is not None) else cfg.get("cooldown_hours", 18)
    time_str = getattr(args, "time", None)
    Scheduler.setup_windows_task(interval_hours=hours, start_time=time_str)


def cmd_daemon(args):
    """Run in continuous daemon mode."""
    cfg = load_config()
    time_str = args.time or cfg.get("schedule_time", "09:00")
    Scheduler.run_daemon_loop(time_str, lambda: cmd_run(None))


def cmd_reset(args):
    """Reset cooldown timestamps."""
    tracker = Tracker(file_path=str(HISTORY_PATH))
    uname = args.username.strip().lstrip("@") if args.username else None
    tracker.reset(uname)
    if uname:
        print(f"✅ Cooldown timer reset for @{uname}! You can now run 'python main.py run'.")
    else:
        print("✅ Cooldown timers reset for ALL friends! You can now run 'python main.py run'.")


def main():
    # If launched with NO arguments (e.g. double-clicked or launched at startup),
    # automatically default to running the streak saver and then exit cleanly!
    if len(sys.argv) == 1:
        print("🚀 Auto-running TikTok Streak Saver...")
        cmd_run(None)
        sys.exit(0)

    parser = argparse.ArgumentParser(description="TikTok Streak Saver - Modern automated streak manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # run
    p_run = subparsers.add_parser("run", help="Send streak messages to eligible friends now and auto-close")
    p_run.add_argument("-v", "--headful", action="store_true", help="Run with visible browser window for debugging")
    p_run.add_argument("-f", "--force", action="store_true", help="Bypass cooldown checks and force send messages now")

    # startup
    p_startup = subparsers.add_parser("startup", help="Configure auto-run on Windows startup (runs once on PC boot and closes)")
    p_startup.add_argument("--remove", action="store_true", help="Remove from Windows startup")

    # reset
    p_reset = subparsers.add_parser("reset", help="Reset cooldown timer for testing")
    p_reset.add_argument("username", nargs="?", default=None, help="Optional username to reset (omit to reset all)")

    # login
    subparsers.add_parser("login", help="Open interactive browser to authenticate with TikTok")

    # status
    subparsers.add_parser("status", help="Check session validity and friend streak history")

    # add
    p_add = subparsers.add_parser("add", help="Add friend to streak list")
    p_add.add_argument("username", help="TikTok username/nickname")
    p_add.add_argument("-m", "--message", help="Optional custom message for this friend", default="")

    # remove
    p_rem = subparsers.add_parser("remove", help="Remove friend from streak list")
    p_rem.add_argument("username", help="TikTok username to remove")

    # schedule
    p_sched = subparsers.add_parser("schedule", help="Register/unregister recurring Windows Task Scheduler job")
    p_sched.add_argument("-H", "--hours", type=int, default=None, help="Execution interval in hours (e.g. 18)")
    p_sched.add_argument("-t", "--time", help="Initial start time (HH:MM, e.g. 09:00)", default=None)
    p_sched.add_argument("--status", action="store_true", help="Check status of scheduled task")
    p_sched.add_argument("--remove", action="store_true", help="Remove existing Windows scheduled task")

    # daemon
    p_daemon = subparsers.add_parser("daemon", help="Run background daemon loop")
    p_daemon.add_argument("-t", "--time", help="Daily execution time (e.g. 09:00)", default=None)

    args = parser.parse_args()

    command_map = {
        "run": cmd_run,
        "startup": cmd_startup,
        "reset": cmd_reset,
        "login": cmd_login,
        "status": cmd_status,
        "add": cmd_add,
        "remove": cmd_remove,
        "schedule": cmd_schedule,
        "daemon": cmd_daemon,
    }

    cmd_fn = command_map.get(args.command)
    if cmd_fn:
        cmd_fn(args)


if __name__ == "__main__":
    main()
