"""
Automated Build Script for TikTokStreakSaver.exe and TikTokStreakConfig.exe
Compiles the application, GUI configurator, and bundles runtime dependencies.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist" / "TikTokStreakSaver"


def build_all():
    print("🚀 [1/2] Building TikTokStreakSaver.exe with PyInstaller...")

    # 1. Main background / CLI runner
    cmd_main = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--console",
        "--name",
        "TikTokStreakSaver",
        f"--icon={BASE_DIR / 'app.ico'}",
        "--collect-all",
        "playwright",
        str(BASE_DIR / "main.py"),
    ]

    try:
        subprocess.run(cmd_main, check=True, cwd=str(BASE_DIR))
        print("✅ TikTokStreakSaver.exe compiled successfully!\n")

        # 2. Configuration GUI executable
        print("🎨 [2/2] Building TikTokStreakConfig.exe (GUI) with PyInstaller...")
        cmd_gui = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            f"--icon={BASE_DIR / 'app.ico'}",
            "--add-data",
            f"{BASE_DIR / 'app.ico'};.",
            "--name",
            "TikTokStreakConfig",
            "--distpath",
            str(DIST_DIR),
            str(BASE_DIR / "gui_config.py"),
        ]
        subprocess.run(cmd_gui, check=True, cwd=str(BASE_DIR))
        print("✅ TikTokStreakConfig.exe compiled successfully!\n")

        # Copy runtime configs and icon to the dist directory
        for item in ["config.json", "session.json", ".env.example", "README.md", "app.ico"]:
            src = BASE_DIR / item
            if src.exists():
                shutil.copy2(src, DIST_DIR / item)
                print(f"📦 Synced {item} -> {DIST_DIR / item}")

        print("\n🎉 Both executables are ready inside:")
        print(f"👉 Core Runner: {DIST_DIR / 'TikTokStreakSaver.exe'}")
        print(f"👉 Config GUI:  {DIST_DIR / 'TikTokStreakConfig.exe'}\n")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with exit code {e.returncode}")


if __name__ == "__main__":
    build_all()
