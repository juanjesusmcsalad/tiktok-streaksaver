# 🔥 TikTok Auto Streak Saver

<p align="center">
  <img src="app.ico" width="96" height="96" alt="TikTok Streak Saver Logo" />
</p>

<p align="center">
  <strong>A modern, automated, anti-detection TikTok Streak Keeper with a sleek Volt Dark GUI.</strong><br>
  Keep your daily streaks alive without running 24/7 background bloatware or risking account bans.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Playwright-Automated_Browser-45ba4b?style=flat&logo=playwright&logoColor=white" alt="Playwright" />
  <img src="https://img.shields.io/badge/Platform-Windows_10%20%7C%2011-0078D6?style=flat&logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/Anti--Detection-Stealth_Evasions-8B5CF6?style=flat" alt="Anti-Detection" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="MIT License" />
</p>

---

## ⚡ Highlights & Key Features

- **🎨 Volt Dark GUI (`TikTokStreakConfig.exe`)**:
  - Minimalist dark aesthetic (`#111111` / `#131313` / `#171717`) with native Windows 11 immersive titlebar dark mode.
  - **🔐 In-App QR Code Login**: 1-click button launches a secure browser. Scan the QR code with your TikTok mobile app, and the program extracts and saves your session tokens permanently.
  - **👥 Friend & Message Manager**: Add/edit friends, assign custom messages, or use randomized message pools (`🔥`, `Streak! 🔥`, `Daily streak 🔥`).
  - **🧪 Next-to-Name Test Button**: Hit `🧪 Test` right beside any friend's name to instantly save and launch a live test run.
  - **🚀 1-Click "Start"**: Validates configuration, launches the streak saver, and closes the UI automatically.
- **🛡️ Auto-Closing Autopilot (`TikTokStreakSaver.exe`)**:
  - **Zero Idle Memory**: Unlike traditional bots that hog RAM in the background all day, this program wakes up, sends streaks, and **closes immediately** (0 MB RAM between runs).
  - **PC Startup Option**: Automatically runs once when your PC turns on (`shell:startup`) and closes.
  - **Zero-Latency Task Scheduler**: Configure recurring runs (e.g. every 18 hours). Inspects native Windows XML directly with **0.48 ms** execution time.
- **🥷 Advanced Anti-Ban & Stealth**:
  - **No Plaintext Passwords**: No typing credentials into forms; no slide puzzle captchas.
  - **Human Keystroke Simulation**: Character-by-character typing with natural jitter (45ms–120ms delays) and human inter-chat pauses (6s–14s).
  - **ByteDance Frontier IM Integration**: Built specifically for TikTok Web's internal messaging protocol with multi-tier locator fallbacks.
  - **Smart 18-Hour Cooldown Tracker**: Prevents duplicate sends if you already messaged a friend today.
- **🔔 Discord & Telegram Webhooks**: Receive real-time alerts summarizing successfully sent, skipped, and failed streaks.

---

## 🆚 Why This Beats Legacy Scripts

| Feature | Legacy Scripts (e.g. `huuthang201`) | **TikTok Auto Streak Saver** |
|---|---|---|
| **Authentication** | Types username & password into Selenium (triggers captchas & lockouts) | **Interactive QR Code / Session Token** (`session.json`) — 100% captcha-free |
| **Bot Detection** | Flags `navigator.webdriver` immediately | **Playwright Stealth**: Mocks Chrome runtime, plugins, languages, and canvas |
| **Typing Behavior** | Pastes text instantly at 0ms (flags bot rate-limits) | **Human Keystroke Jitter** (45ms–120ms) with realistic random pauses |
| **Idle Footprint** | Stays running in memory 24/7 consuming CPU & RAM | **0 MB Background Footprint**: Runs and immediately terminates |
| **User Interface** | Terminal only / brittle manual edits | **Sleek Volt Dark Desktop GUI** + CLI flexibility |
| **Cooldown Safety** | Re-sends repeatedly, looking like a spam bot | **Persistent History Tracker** (`history.json`) with customizable cooldown |

---

## 🚀 Quick Start (No Python Required)

1. Download the latest **`TikTokStreakSaver-v1.0.0.zip`** from [**Releases**](https://github.com).
2. Extract the folder anywhere on your PC (e.g., in your Downloads or Documents folder).
3. Double-click **`TikTokStreakConfig.exe`**:
   - Because you aren't logged in yet, it will open to the **🔐 Account & Login** tab.
   - Click **`🔑 Log In to TikTok (Browser / QR Code)`**.
   - Open TikTok on your phone, go to **Profile → Menu (top right) → QR Code / Scan**, and scan the QR code on your screen.
   - Your session will be saved automatically, and you will be routed straight to the **Friends** tab!
4. Add your friends' handles, customize their messages, and click **`🚀 START`** or **`🧪 Test`**!

---

## 🛠️ Developer / Source Setup

If you want to run from source or contribute:

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/tiktok-streak-saver.git
cd tiktok-streak-saver
```

### 2. Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 3. Launch the Configuration GUI
```bash
python gui_config.py
```

### 4. Or Run Headless via CLI
```bash
# Log in once interactively
python main.py login

# Run streak saver (headless & auto-closing)
python main.py run

# Check status and streak history
python main.py status
```

---

## 💻 CLI Commands Reference

`main.py` (and `TikTokStreakSaver.exe`) provides a full command-line interface:

| Command | Description |
|---|---|
| `python main.py run` | Sends streaks to all eligible friends and closes |
| `python main.py run --force` | Bypasses cooldown timers and forces an immediate send |
| `python main.py run --headful` | Runs with a visible browser window for debugging |
| `python main.py login` | Opens interactive browser to scan TikTok login QR code |
| `python main.py status` | Displays session health and friend streak days |
| `python main.py reset [username]` | Resets the cooldown timer (for testing) |
| `python main.py startup` | Registers silent auto-run on Windows PC boot |
| `python main.py startup --remove`| Removes from Windows startup |
| `python main.py schedule -H 18` | Registers Windows Task Scheduler job repeating every 18 hours |
| `python main.py schedule --remove`| Removes the Windows scheduled task |

---

## ⚙️ Configuration (`config.json`)

The configuration file is automatically managed by `TikTokStreakConfig.exe`, but can also be edited manually:

```json
{
  "friends": [
    {
      "username": "friend_handle",
      "custom_message": "Good morning! Streak 🔥"
    }
  ],
  "default_messages": [
    "🔥",
    "Streak! 🔥",
    "gm! Streak 🔥",
    "Daily streak 🔥",
    "🔥 keep it going!",
    "Streak time 🔥"
  ],
  "cooldown_hours": 18,
  "delay_between_chats_min": 6,
  "delay_between_chats_max": 14,
  "headless": true
}
```

---

## 🔔 Discord & Telegram Webhook Notifications

To receive summary notifications whenever your streaks are sent:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in your webhook or bot credentials:
   ```env
   DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
   TELEGRAM_BOT_TOKEN="123456789:ABCDEF..."
   TELEGRAM_CHAT_ID="987654321"
   ```

---

## 🏗️ Building Executables (.exe)

To compile both standalone executables from source:
```powershell
python build.py
```
This produces:
- `dist/TikTokStreakSaver/TikTokStreakConfig.exe` (Single-file GUI with embedded icon)
- `dist/TikTokStreakSaver/TikTokStreakSaver.exe` (Standalone runner with bundled Playwright runtime)

---

## 🔒 Security & Privacy

- **No Passwords Stored**: Your TikTok password is never requested, typed, or stored.
- **Local Storage Only**: All session tokens and cookies are saved locally on your own machine in `session.json`.
- **Zero Telemetry**: No analytics or external tracking scripts are included.
- **Git Safety**: `session.json`, `history.json`, and `.env` are included in `.gitignore` by default so private tokens are never accidentally committed.

---

## ⚠️ Disclaimer

This project is for educational and personal automation purposes only. TikTok is a registered trademark of ByteDance Ltd. This repository is not affiliated with, authorized, maintained, sponsored, or endorsed by TikTok or ByteDance. Use responsibly and adhere to TikTok's Terms of Service.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
