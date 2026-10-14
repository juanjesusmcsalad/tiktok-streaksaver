#!/usr/bin/env python3
"""
TikTok Streak Saver - Configuration GUI (Volt Dark Theme)
Sleek, minimalist dark configuration tool matching the Volt palette:
#111111 / #131313 / #171717 with #929292 / #cccccc accents.
"""

import sys
import os
import json
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# --- Volt Theme Palette ---
BG_CANVAS = "#111111"       # Base deep black canvas
BG_SURFACE = "#131313"      # Editor/table background & active tabs
BG_PANEL = "#171717"        # Cards, sidebars, inactive tabs
BG_RAISED = "#202020"       # Button background & raised cards
BG_HOVER = "#282828"        # Hover state
BG_ACTIVE = "#303030"       # Active / pressed state

BORDER_SUBTLE = "#1e1e1e"   # Subtle micro-borders
BORDER_COLOR = "#262626"    # Standard 1px structural borders
BORDER_STRONG = "#363636"   # Emphasized borders
BORDER_ACCENT = "#4a4a4a"   # Focus / highlight borders

TEXT_PRIMARY = "#cccccc"     # Crisp primary text
TEXT_SECONDARY = "#929292"   # Secondary muted text
TEXT_MUTED = "#666666"       # Tertiary / placeholder text
TEXT_WHITE = "#ffffff"       # High-contrast headers / active items

COLOR_SUCCESS = "#10b981"    # Volt green status dot
COLOR_WARNING = "#eab308"    # Amber warning
COLOR_ERROR = "#ef4444"      # Red error

FONT_FAMILY = "Segoe UI"
FONT_MAIN = (FONT_FAMILY, 9)
FONT_BOLD = (FONT_FAMILY, 9, "bold")
FONT_TITLE = (FONT_FAMILY, 10, "bold")
FONT_MONO = ("Consolas", 8)

import ctypes

# Resolve target config and icon paths
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent

DIST_CONFIG = APP_DIR / "dist" / "TikTokStreakSaver" / "config.json"
LOCAL_CONFIG = APP_DIR / "config.json"
DIST_SESSION = APP_DIR / "dist" / "TikTokStreakSaver" / "session.json"
LOCAL_SESSION = APP_DIR / "session.json"

if getattr(sys, "frozen", False):
    CONFIG_PATH = APP_DIR / "config.json"
    SESSION_PATH = APP_DIR / "session.json"
    EXE_PATH = APP_DIR / "TikTokStreakSaver.exe"
else:
    CONFIG_PATH = DIST_CONFIG if DIST_CONFIG.exists() else LOCAL_CONFIG
    SESSION_PATH = DIST_SESSION if DIST_SESSION.exists() else LOCAL_SESSION
    EXE_PATH = APP_DIR / "dist" / "TikTokStreakSaver" / "TikTokStreakSaver.exe"

def get_icon_path() -> Path:
    candidates = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "app.ico")
        candidates.append(Path(sys.executable).resolve().parent / "app.ico")
    candidates.append(APP_DIR / "app.ico")
    candidates.append(APP_DIR / "dist" / "TikTokStreakSaver" / "app.ico")
    for p in candidates:
        if p.exists():
            return p
    return APP_DIR / "app.ico"

ICON_PATH = get_icon_path()


def apply_dark_titlebar(window, bg_color=0x00171717, text_color=0x00cccccc, border_color=0x00262626):
    """
    Enables Windows 10/11 immersive dark mode and custom title bar caption color.
    Eliminates the default white/cream Windows titlebar completely.
    """
    try:
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if not hwnd:
            hwnd = window.winfo_id()

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19
        DWMWA_BORDER_COLOR = 34
        DWMWA_CAPTION_COLOR = 35
        DWMWA_TEXT_COLOR = 36

        # 1. Enable immersive dark mode (Windows 10 19041+ & Windows 11)
        val = ctypes.c_int(2)
        res = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(val), ctypes.sizeof(val)
        )
        if res != 0:
            val = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, ctypes.byref(val), ctypes.sizeof(val)
            )

        # 2. Windows 11 custom caption color (COLORREF: 0x00BBGGRR -> #171717 is 0x00171717)
        cap = ctypes.c_int(bg_color)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(cap), ctypes.sizeof(cap)
        )

        # 3. Windows 11 custom text color (#cccccc is 0x00cccccc)
        txt = ctypes.c_int(text_color)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_TEXT_COLOR, ctypes.byref(txt), ctypes.sizeof(txt)
        )

        # 4. Windows 11 custom border color (#262626 is 0x00262626)
        brd = ctypes.c_int(border_color)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_BORDER_COLOR, ctypes.byref(brd), ctypes.sizeof(brd)
        )

        # 5. Redraw frame immediately to eliminate white titlebar flash
        SWP_FLAGS = 0x0001 | 0x0002 | 0x0004 | 0x0020
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_FLAGS)
    except Exception:
        pass


class DarkButton(tk.Button):
    """Custom sleek button following Volt dark theme."""
    def __init__(self, parent, text="", command=None, width=None, is_primary=False, **kwargs):
        bg = BG_RAISED if not is_primary else "#242424"
        fg = TEXT_WHITE if is_primary else TEXT_PRIMARY
        border_col = BORDER_STRONG if is_primary else BORDER_COLOR
        
        super().__init__(
            parent,
            text=text,
            command=command,
            font=FONT_MAIN,
            bg=bg,
            fg=fg,
            activebackground=BG_ACTIVE,
            activeforeground=TEXT_WHITE,
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=border_col,
            highlightcolor=BORDER_ACCENT,
            cursor="hand2",
            padx=10,
            pady=4,
            **kwargs
        )
        if width:
            self.configure(width=width)
        
        self.default_bg = bg
        self.default_fg = fg
        self.default_border = border_col
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        self.configure(bg=BG_HOVER, fg=TEXT_WHITE, highlightbackground=BORDER_ACCENT)

    def _on_leave(self, e):
        self.configure(bg=self.default_bg, fg=self.default_fg, highlightbackground=self.default_border)


class DarkEntry(tk.Entry):
    """Sleek text input with dark surface and subtle border."""
    def __init__(self, parent, textvariable=None, width=None, **kwargs):
        super().__init__(
            parent,
            textvariable=textvariable,
            font=FONT_MAIN,
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_WHITE,
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=BORDER_ACCENT,
            selectbackground=BG_HOVER,
            selectforeground=TEXT_WHITE,
            **kwargs
        )
        if width:
            self.configure(width=width)


class ConfigGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TikTok Streak Saver — Config")
        # Increased size for more comfortable layout: 820x640
        self.geometry("820x640")
        self.minsize(740, 560)
        self.configure(bg=BG_CANVAS)

        # Set custom Volt icon
        icon_path = get_icon_path()
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        # Apply immersive dark titlebar (Volt #171717 caption, #cccccc text, #262626 border)
        apply_dark_titlebar(self, bg_color=0x00171717, text_color=0x00cccccc, border_color=0x00262626)
        self.after(50, lambda: apply_dark_titlebar(self, bg_color=0x00171717, text_color=0x00cccccc, border_color=0x00262626))
        self.after(200, lambda: apply_dark_titlebar(self, bg_color=0x00171717, text_color=0x00cccccc, border_color=0x00262626))

        # Load configuration
        self.config_data = self._load_config()

        # Build Volt dark ttk styles
        self._setup_ttk_styles()

        # Build UI Structure
        self._build_topbar()
        self._build_tabbar()
        self._build_container()
        self._build_statusbar()

        # Show initial tab: if logged in -> friends, if not logged in -> account
        initial_tab = "friends" if self._has_active_session() else "account"
        self._switch_tab(initial_tab)
        self._populate_all_data()
        self._refresh_account_status()

    def _setup_ttk_styles(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # 1. Treeview (Friends table) - Strip outer Treeview.field to eliminate white box outline
        self.style.layout("Volt.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        self.style.configure(
            "Volt.Treeview",
            background=BG_SURFACE,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_SURFACE,
            borderwidth=0,
            bordercolor=BG_SURFACE,
            lightcolor=BG_SURFACE,
            darkcolor=BG_SURFACE,
            font=FONT_MAIN,
            rowheight=26
        )
        self.style.map(
            "Volt.Treeview",
            background=[("selected", BG_RAISED)],
            foreground=[("selected", TEXT_WHITE)],
            bordercolor=[("selected", BG_SURFACE)],
            lightcolor=[("selected", BG_SURFACE)],
            darkcolor=[("selected", BG_SURFACE)]
        )

        # 2. Treeview Headings - Strip Treeheading.border to eliminate white header outlines
        self.style.layout("Volt.Treeview.Heading", [
            ("Treeheading.cell", {"sticky": "nswe"}),
            ("Treeheading.padding", {"sticky": "nswe", "children": [
                ("Treeheading.image", {"side": "right", "sticky": ""}),
                ("Treeheading.text", {"sticky": "we"})
            ]})
        ])
        self.style.configure(
            "Volt.Treeview.Heading",
            background=BG_PANEL,
            foreground=TEXT_SECONDARY,
            relief="flat",
            font=FONT_BOLD,
            borderwidth=0,
            bordercolor=BG_SURFACE,
            lightcolor=BG_SURFACE,
            darkcolor=BG_SURFACE,
            padding=6
        )
        self.style.map(
            "Volt.Treeview.Heading",
            background=[("active", BG_HOVER)],
            foreground=[("active", TEXT_WHITE)],
            bordercolor=[("active", BG_SURFACE)],
            lightcolor=[("active", BG_SURFACE)],
            darkcolor=[("active", BG_SURFACE)]
        )

        # 3. Scrollbars - Match Volt dark surface and remove all light outlines
        self.style.configure(
            "Volt.Vertical.TScrollbar",
            background=BG_RAISED,
            troughcolor=BG_SURFACE,
            bordercolor=BG_SURFACE,
            lightcolor=BG_SURFACE,
            darkcolor=BG_SURFACE,
            arrowcolor=TEXT_MUTED,
            arrowsize=11,
            relief="flat",
            borderwidth=0
        )
        self.style.map(
            "Volt.Vertical.TScrollbar",
            background=[("active", BG_HOVER), ("pressed", BG_ACTIVE)],
            bordercolor=[("active", BG_SURFACE), ("pressed", BG_SURFACE)],
            lightcolor=[("active", BG_SURFACE), ("pressed", BG_SURFACE)],
            darkcolor=[("active", BG_SURFACE), ("pressed", BG_SURFACE)]
        )

    def _load_config(self) -> dict:
        default_cfg = {
            "friends": [
                {"username": "lou", "custom_message": "test"}
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
            "headless": True
        }
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showwarning("Config Warning", f"Could not parse {CONFIG_PATH.name}: {e}\nUsing defaults.")
        return default_cfg

    def _save_config(self, show_prompt=True):
        # 1. Friends from treeview
        friends = []
        for child in self.friends_tree.get_children():
            values = self.friends_tree.item(child, "values")
            uname = values[0].strip().lstrip("@")
            msg = values[1].strip()
            if uname:
                item = {"username": uname}
                if msg:
                    item["custom_message"] = msg
                friends.append(item)

        # 2. Messages from listbox
        messages = list(self.messages_listbox.get(0, tk.END))
        if not messages:
            messages = ["🔥", "Streak! 🔥"]

        # 3. Settings
        try:
            cooldown = float(self.cooldown_var.get())
        except ValueError:
            cooldown = 18.0

        try:
            min_delay = int(self.min_delay_var.get())
            max_delay = int(self.max_delay_var.get())
        except ValueError:
            min_delay, max_delay = 6, 14

        self.config_data["friends"] = friends
        self.config_data["default_messages"] = messages
        self.config_data["cooldown_hours"] = cooldown
        self.config_data["delay_between_chats_min"] = min_delay
        self.config_data["delay_between_chats_max"] = max_delay
        self.config_data["headless"] = self.headless_var.get()

        saved_paths = []
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            saved_paths.append(str(CONFIG_PATH))

            # Sync with repo root config.json if different and exists
            if LOCAL_CONFIG.exists() and LOCAL_CONFIG.resolve() != CONFIG_PATH.resolve():
                with open(LOCAL_CONFIG, "w", encoding="utf-8") as f:
                    json.dump(self.config_data, f, indent=2, ensure_ascii=False)
                saved_paths.append(str(LOCAL_CONFIG))

            # Sync with dist config.json if different and exists
            if DIST_CONFIG.exists() and DIST_CONFIG.resolve() != CONFIG_PATH.resolve():
                with open(DIST_CONFIG, "w", encoding="utf-8") as f:
                    json.dump(self.config_data, f, indent=2, ensure_ascii=False)
                saved_paths.append(str(DIST_CONFIG))

            self.status_msg_var.set(f"Saved to {CONFIG_PATH.name}")
            self._update_stats_badge()
            if show_prompt:
                messagebox.showinfo("Volt Config Saved", f"Configuration updated successfully!\n\nTarget:\n" + "\n".join(saved_paths))
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save config: {e}")

    # --- UI Construction ---

    def _build_topbar(self):
        """Top titlebar / brand bar with clean Volt aesthetic."""
        topbar = tk.Frame(self, bg=BG_PANEL, height=36)
        topbar.pack(fill=tk.X, side=tk.TOP)
        topbar.pack_propagate(False)

        # Left brand indicator
        left_box = tk.Frame(topbar, bg=BG_PANEL)
        left_box.pack(side=tk.LEFT, padx=12, fill=tk.Y)

        dot = tk.Label(left_box, text="●", font=("Segoe UI", 9), fg=COLOR_SUCCESS, bg=BG_PANEL)
        dot.pack(side=tk.LEFT, padx=(0, 6))

        title = tk.Label(left_box, text="TIKTOK STREAK SAVER", font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL)
        title.pack(side=tk.LEFT)

        tag = tk.Label(left_box, text="CONFIG", font=FONT_MONO, fg=TEXT_SECONDARY, bg=BG_SURFACE, padx=6, pady=1)
        tag.pack(side=tk.LEFT, padx=(8, 0))

        # Right: Account badge & path breadcrumb
        path_lbl = tk.Label(
            topbar,
            text=f"{CONFIG_PATH.name}",
            font=FONT_MONO,
            fg=TEXT_MUTED,
            bg=BG_PANEL
        )
        path_lbl.pack(side=tk.RIGHT, padx=12)

        self.top_account_badge = tk.Label(
            topbar,
            text="🟢 LOGGED IN",
            font=FONT_MONO,
            fg=COLOR_SUCCESS,
            bg=BG_SURFACE,
            padx=8,
            pady=1,
            cursor="hand2"
        )
        self.top_account_badge.pack(side=tk.RIGHT, padx=(0, 6))
        self.top_account_badge.bind("<Button-1>", lambda e: self._switch_tab("account"))

        # 1px border under titlebar
        sep = tk.Frame(self, bg=BORDER_COLOR, height=1)
        sep.pack(fill=tk.X, side=tk.TOP)

    def _build_tabbar(self):
        """Sleek tab strip matching Volt tabs."""
        self.tabbar = tk.Frame(self, bg=BG_PANEL, height=34)
        self.tabbar.pack(fill=tk.X, side=tk.TOP)
        self.tabbar.pack_propagate(False)

        self.tab_buttons = {}
        tabs = [
            ("friends", "👥  Friends"),
            ("messages", "💬  Default Messages"),
            ("settings", "⚙️  Settings & Startup"),
            ("account", "🔐  Account & Login"),
        ]

        for tab_id, text in tabs:
            btn = tk.Label(
                self.tabbar,
                text=text,
                font=FONT_MAIN,
                bg=BG_PANEL,
                fg=TEXT_SECONDARY,
                cursor="hand2",
                padx=16,
                pady=7
            )
            btn.pack(side=tk.LEFT, fill=tk.Y)
            btn.bind("<Button-1>", lambda e, tid=tab_id: self._switch_tab(tid))
            btn.bind("<Enter>", lambda e, b=btn, tid=tab_id: self._on_tab_hover(b, tid))
            btn.bind("<Leave>", lambda e, b=btn, tid=tab_id: self._on_tab_leave(b, tid))
            self.tab_buttons[tab_id] = btn

        # 1px separator line under tab bar
        sep = tk.Frame(self, bg=BORDER_COLOR, height=1)
        sep.pack(fill=tk.X, side=tk.TOP)

    def _on_tab_hover(self, btn, tab_id):
        if getattr(self, "current_tab", "") != tab_id:
            btn.configure(bg=BG_HOVER, fg=TEXT_WHITE)

    def _on_tab_leave(self, btn, tab_id):
        if getattr(self, "current_tab", "") != tab_id:
            btn.configure(bg=BG_PANEL, fg=TEXT_SECONDARY)

    def _switch_tab(self, tab_id):
        self.current_tab = tab_id
        # Update tab button styling
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(bg=BG_SURFACE, fg=TEXT_WHITE, font=FONT_BOLD)
            else:
                btn.configure(bg=BG_PANEL, fg=TEXT_SECONDARY, font=FONT_MAIN)

        # Show selected content frame
        for tid, frame in self.tab_frames.items():
            if tid == tab_id:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()

        if tab_id == "settings":
            if hasattr(self, "_check_startup_status"):
                self._check_startup_status()
            if hasattr(self, "_check_schedule_status"):
                self._check_schedule_status()
        elif tab_id == "account":
            if hasattr(self, "_refresh_account_status"):
                self._refresh_account_status()

    def _build_container(self):
        """Central content area for active tab."""
        self.container = tk.Frame(self, bg=BG_SURFACE)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.tab_frames = {
            "friends": self._create_friends_tab(self.container),
            "messages": self._create_messages_tab(self.container),
            "settings": self._create_settings_tab(self.container),
            "account": self._create_account_tab(self.container),
        }

    # --- Tab 1: Friends ---
    def _create_friends_tab(self, parent) -> tk.Frame:
        frame = tk.Frame(parent, bg=BG_SURFACE, padx=14, pady=12)

        # Header note
        desc = tk.Label(
            frame,
            text="Configured friends to receive automated streak messages on PC boot.",
            font=FONT_MAIN,
            fg=TEXT_SECONDARY,
            bg=BG_SURFACE
        )
        desc.pack(anchor=tk.W, pady=(0, 8))

        # Table container matching background
        table_border = tk.Frame(frame, bg=BG_SURFACE, bd=0, highlightthickness=0)
        table_border.pack(fill=tk.BOTH, expand=True)

        table_inner = tk.Frame(table_border, bg=BG_SURFACE, bd=0, highlightthickness=0)
        table_inner.pack(fill=tk.BOTH, expand=True)

        columns = ("username", "custom_message")
        self.friends_tree = ttk.Treeview(
            table_inner,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Volt.Treeview"
        )
        self.friends_tree.heading("username", text="Friend Username / Handle")
        self.friends_tree.heading("custom_message", text="Custom Message (Blank = Random Default)")

        self.friends_tree.column("username", width=260, anchor=tk.W)
        self.friends_tree.column("custom_message", width=480, anchor=tk.W)

        scroll = ttk.Scrollbar(table_inner, orient=tk.VERTICAL, command=self.friends_tree.yview, style="Volt.Vertical.TScrollbar")
        self.friends_tree.configure(yscrollcommand=scroll.set)

        self.friends_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.friends_tree.bind("<<TreeviewSelect>>", self._on_friend_selected)

        # Bottom Add / Edit Card
        card = tk.Frame(frame, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=12, pady=10)
        card.pack(fill=tk.X, pady=(10, 0))

        # Card Title
        c_title = tk.Label(card, text="ADD OR UPDATE FRIEND", font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL)
        c_title.pack(anchor=tk.W, pady=(0, 6))

        # Input fields grid
        f_grid = tk.Frame(card, bg=BG_PANEL)
        f_grid.pack(fill=tk.X)

        tk.Label(f_grid, text="Username / Handle:", font=FONT_MAIN, fg=TEXT_SECONDARY, bg=BG_PANEL).grid(row=0, column=0, sticky=tk.W, padx=4, pady=3)
        self.friend_uname_var = tk.StringVar()
        self.friend_uname_entry = DarkEntry(f_grid, textvariable=self.friend_uname_var, width=18)
        self.friend_uname_entry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=3)

        # Single button to "test" next to their name (saves and opens TikTokStreakSaver)
        self.test_friend_btn = DarkButton(f_grid, text="🧪 Test", command=self._test_friend)
        self.test_friend_btn.grid(row=0, column=2, sticky=tk.W, padx=(2, 10), pady=3)

        tk.Label(f_grid, text="Custom Message:", font=FONT_MAIN, fg=TEXT_SECONDARY, bg=BG_PANEL).grid(row=0, column=3, sticky=tk.W, padx=(4, 4), pady=3)
        self.friend_msg_var = tk.StringVar()
        self.friend_msg_entry = DarkEntry(f_grid, textvariable=self.friend_msg_var)
        self.friend_msg_entry.grid(row=0, column=4, sticky=tk.EW, padx=4, pady=3)
        f_grid.columnconfigure(4, weight=1)

        # Buttons row
        btn_bar = tk.Frame(card, bg=BG_PANEL)
        btn_bar.pack(fill=tk.X, pady=(8, 0))

        DarkButton(btn_bar, text="➕ Add Friend", command=self._add_friend).pack(side=tk.LEFT, padx=(0, 6))
        DarkButton(btn_bar, text="✏️ Update Selected", command=self._update_friend).pack(side=tk.LEFT, padx=(0, 6))
        DarkButton(btn_bar, text="🗑️ Remove Selected", command=self._remove_friend).pack(side=tk.LEFT, padx=(0, 6))
        DarkButton(btn_bar, text="Clear", command=self._clear_friend_inputs).pack(side=tk.LEFT, padx=(0, 8))

        # "Start" button: closes UI and starts TikTokStreakSaver
        DarkButton(btn_bar, text="🚀 Start Streak Saver (Close & Run)", is_primary=True, command=self._start_and_close).pack(side=tk.RIGHT)

        return frame

    # --- Tab 2: Messages Pool ---
    def _create_messages_tab(self, parent) -> tk.Frame:
        frame = tk.Frame(parent, bg=BG_SURFACE, padx=14, pady=12)

        desc = tk.Label(
            frame,
            text="Random default messages used when a friend does not have a custom message set.",
            font=FONT_MAIN,
            fg=TEXT_SECONDARY,
            bg=BG_SURFACE
        )
        desc.pack(anchor=tk.W, pady=(0, 8))

        # Listbox container matching background
        list_border = tk.Frame(frame, bg=BG_SURFACE, bd=0, highlightthickness=0)
        list_border.pack(fill=tk.BOTH, expand=True)

        list_inner = tk.Frame(list_border, bg=BG_SURFACE, bd=0, highlightthickness=0)
        list_inner.pack(fill=tk.BOTH, expand=True)

        self.messages_listbox = tk.Listbox(
            list_inner,
            font=FONT_MAIN,
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            selectbackground=BG_RAISED,
            selectforeground=TEXT_WHITE,
            activestyle="none",
            bd=0,
            highlightthickness=0
        )
        msg_scroll = ttk.Scrollbar(list_inner, orient=tk.VERTICAL, command=self.messages_listbox.yview, style="Volt.Vertical.TScrollbar")
        self.messages_listbox.configure(yscrollcommand=msg_scroll.set)

        self.messages_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Add / delete row
        add_bar = tk.Frame(frame, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=10, pady=8)
        add_bar.pack(fill=tk.X, pady=(10, 0))

        self.new_msg_var = tk.StringVar()
        self.new_msg_entry = DarkEntry(add_bar, textvariable=self.new_msg_var)
        self.new_msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        DarkButton(add_bar, text="➕ Add Message", command=self._add_message).pack(side=tk.LEFT, padx=(0, 6))
        DarkButton(add_bar, text="🗑️ Delete Selected", command=self._delete_message).pack(side=tk.LEFT)

        return frame

    # --- Tab 3: Settings & Startup ---
    def _create_settings_tab(self, parent) -> tk.Frame:
        frame = tk.Frame(parent, bg=BG_SURFACE, padx=14, pady=12)

        # Card 1: Windows PC Startup
        card1 = tk.Frame(frame, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=12, pady=10)
        card1.pack(fill=tk.X, pady=(0, 10))

        c1_title = tk.Label(card1, text="WINDOWS STARTUP (RUN ON PC BOOT)", font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL)
        c1_title.pack(anchor=tk.W, pady=(0, 4))

        self.startup_status_lbl = tk.Label(card1, text="Checking startup status...", font=FONT_BOLD, fg=COLOR_SUCCESS, bg=BG_PANEL)
        self.startup_status_lbl.pack(anchor=tk.W, pady=(0, 4))

        c1_sub = tk.Label(
            card1,
            text="Launches automatically once when Windows boots up, sends streaks, and immediately closes with zero memory footprint.",
            font=FONT_MAIN,
            fg=TEXT_SECONDARY,
            bg=BG_PANEL,
            wraplength=740,
            justify=tk.LEFT
        )
        c1_sub.pack(anchor=tk.W, pady=(0, 8))

        c1_btns = tk.Frame(card1, bg=BG_PANEL)
        c1_btns.pack(fill=tk.X)
        DarkButton(c1_btns, text="🚀 Enable PC Startup", is_primary=True, command=self._enable_startup).pack(side=tk.LEFT, padx=(0, 8))
        DarkButton(c1_btns, text="Disable Startup", command=self._disable_startup).pack(side=tk.LEFT)

        self._check_startup_status()

        # Card 2: Windows Task Scheduler (Recurring Every X Hours)
        card_sched = tk.Frame(frame, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=12, pady=10)
        card_sched.pack(fill=tk.X, pady=(0, 10))

        cs_title = tk.Label(card_sched, text="AUTOMATED TASK SCHEDULER (REPEATING EVERY X HOURS)", font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL)
        cs_title.pack(anchor=tk.W, pady=(0, 4))

        self.schedule_status_lbl = tk.Label(card_sched, text="Checking scheduler status...", font=FONT_BOLD, fg=COLOR_SUCCESS, bg=BG_PANEL)
        self.schedule_status_lbl.pack(anchor=tk.W, pady=(0, 4))

        cs_sub = tk.Label(
            card_sched,
            text="Wakes up automatically based on your Cooldown Hours (e.g. every 18h) even if your PC is never shut down. 0 MB RAM when idle.",
            font=FONT_MAIN,
            fg=TEXT_SECONDARY,
            bg=BG_PANEL,
            wraplength=740,
            justify=tk.LEFT
        )
        cs_sub.pack(anchor=tk.W, pady=(0, 8))

        cs_btns = tk.Frame(card_sched, bg=BG_PANEL)
        cs_btns.pack(fill=tk.X)
        self.sched_btn = DarkButton(cs_btns, text="🕒 Enable Schedule (Every 18h)", is_primary=True, command=self._enable_schedule)
        self.sched_btn.pack(side=tk.LEFT, padx=(0, 8))
        DarkButton(cs_btns, text="Disable Schedule", command=self._disable_schedule).pack(side=tk.LEFT)

        self._check_schedule_status()

        # Card 3: Timing & Cooldowns
        card2 = tk.Frame(frame, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=12, pady=10)
        card2.pack(fill=tk.X, pady=(0, 10))

        c2_title = tk.Label(card2, text="TIMING & SAFETY LIMITS", font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL)
        c2_title.pack(anchor=tk.W, pady=(0, 8))

        grid2 = tk.Frame(card2, bg=BG_PANEL)
        grid2.pack(fill=tk.X)

        tk.Label(grid2, text="Cooldown / Schedule (Hours):", font=FONT_MAIN, fg=TEXT_SECONDARY, bg=BG_PANEL).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.cooldown_var = tk.StringVar(value="18")
        self.cooldown_var.trace_add("write", self._on_cooldown_var_changed)
        DarkEntry(grid2, textvariable=self.cooldown_var, width=8).grid(row=0, column=1, sticky=tk.W, padx=6, pady=3)
        tk.Label(grid2, text="(Hours between streak runs — automatically adjusts Task Scheduler interval)", font=FONT_MAIN, fg=TEXT_MUTED, bg=BG_PANEL).grid(row=0, column=2, sticky=tk.W)

        tk.Label(grid2, text="Delay Between Chats:", font=FONT_MAIN, fg=TEXT_SECONDARY, bg=BG_PANEL).grid(row=1, column=0, sticky=tk.W, pady=3)
        d_frame = tk.Frame(grid2, bg=BG_PANEL)
        d_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W)

        self.min_delay_var = tk.StringVar(value="6")
        self.max_delay_var = tk.StringVar(value="14")
        DarkEntry(d_frame, textvariable=self.min_delay_var, width=4).pack(side=tk.LEFT)
        tk.Label(d_frame, text="s to", font=FONT_MAIN, fg=TEXT_SECONDARY, bg=BG_PANEL).pack(side=tk.LEFT, padx=4)
        DarkEntry(d_frame, textvariable=self.max_delay_var, width=4).pack(side=tk.LEFT)
        tk.Label(d_frame, text="s (Random human pause between friends)", font=FONT_MAIN, fg=TEXT_MUTED, bg=BG_PANEL).pack(side=tk.LEFT, padx=6)

        self.headless_var = tk.BooleanVar(value=True)
        cb = tk.Checkbutton(
            card2,
            text=" Run browser silently in background (headless)",
            variable=self.headless_var,
            font=FONT_MAIN,
            fg=TEXT_PRIMARY,
            bg=BG_PANEL,
            activebackground=BG_PANEL,
            activeforeground=TEXT_WHITE,
            selectcolor=BG_SURFACE,
            bd=0,
            highlightthickness=0
        )
        cb.pack(anchor=tk.W, pady=(8, 0))

        # Card 3: Quick Diagnostics
        card3 = tk.Frame(frame, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=12, pady=10)
        card3.pack(fill=tk.X)

        c3_title = tk.Label(card3, text="QUICK ACTIONS & DIAGNOSTICS", font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL)
        c3_title.pack(anchor=tk.W, pady=(0, 6))

        c3_btns = tk.Frame(card3, bg=BG_PANEL)
        c3_btns.pack(fill=tk.X)

        DarkButton(c3_btns, text="▶️ Run Streak Saver Now", is_primary=True, command=self._run_streak_saver).pack(side=tk.LEFT, padx=(0, 8))
        DarkButton(c3_btns, text="🔄 Reset Cooldowns (Test)", command=self._reset_cooldowns).pack(side=tk.LEFT, padx=(0, 8))
        DarkButton(c3_btns, text="🔍 Check Status & Streaks", command=self._check_status).pack(side=tk.LEFT)

        return frame

    # --- Tab 4: Account & Login ---
    def _create_account_tab(self, parent) -> tk.Frame:
        frame = tk.Frame(parent, bg=BG_SURFACE, padx=14, pady=12)

        # Header note
        desc = tk.Label(
            frame,
            text="Manage your TikTok account session. Log in once via browser QR code to keep streaks running permanently.",
            font=FONT_MAIN,
            fg=TEXT_SECONDARY,
            bg=BG_SURFACE
        )
        desc.pack(anchor=tk.W, pady=(0, 10))

        # Card 1: Account Status Checker
        card1 = tk.Frame(frame, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=14, pady=12)
        card1.pack(fill=tk.X, pady=(0, 10))

        c1_title = tk.Label(card1, text="TIKTOK ACCOUNT & SESSION STATUS", font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL)
        c1_title.pack(anchor=tk.W, pady=(0, 6))

        self.account_status_lbl = tk.Label(card1, text="Checking session...", font=FONT_BOLD, fg=COLOR_SUCCESS, bg=BG_PANEL)
        self.account_status_lbl.pack(anchor=tk.W, pady=(0, 8))

        # Details Grid
        details_grid = tk.Frame(card1, bg=BG_PANEL)
        details_grid.pack(fill=tk.X, pady=(0, 10))

        tk.Label(details_grid, text="Authentication Method:", font=FONT_MAIN, fg=TEXT_SECONDARY, bg=BG_PANEL).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.acc_method_lbl = tk.Label(details_grid, text="Checking...", font=FONT_MONO, fg=TEXT_PRIMARY, bg=BG_PANEL)
        self.acc_method_lbl.grid(row=0, column=1, sticky=tk.W, padx=8, pady=2)

        tk.Label(details_grid, text="Session Expiration:", font=FONT_MAIN, fg=TEXT_SECONDARY, bg=BG_PANEL).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.acc_expires_lbl = tk.Label(details_grid, text="Checking...", font=FONT_MONO, fg=TEXT_PRIMARY, bg=BG_PANEL)
        self.acc_expires_lbl.grid(row=1, column=1, sticky=tk.W, padx=8, pady=2)

        tk.Label(details_grid, text="Active Auth Tokens:", font=FONT_MAIN, fg=TEXT_SECONDARY, bg=BG_PANEL).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.acc_tokens_lbl = tk.Label(details_grid, text="Checking...", font=FONT_MONO, fg=TEXT_PRIMARY, bg=BG_PANEL)
        self.acc_tokens_lbl.grid(row=2, column=1, sticky=tk.W, padx=8, pady=2)

        # Buttons in Card 1
        c1_btns = tk.Frame(card1, bg=BG_PANEL)
        c1_btns.pack(fill=tk.X, pady=(4, 0))
        DarkButton(c1_btns, text="🔄 Refresh Details", command=self._refresh_account_status).pack(side=tk.LEFT)

        # Card 2: Interactive Login / Re-authentication
        card2 = tk.Frame(frame, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=14, pady=12)
        card2.pack(fill=tk.X, pady=(0, 10))

        c2_title = tk.Label(card2, text="LOGIN / RE-AUTHENTICATE", font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL)
        c2_title.pack(anchor=tk.W, pady=(0, 4))

        c2_sub = tk.Label(
            card2,
            text="Click below to open TikTok's official login screen in a secure browser. Open TikTok on your phone, go to Profile → Menu → QR Code / Scan, and scan the on-screen code. Your session tokens will be extracted and saved locally forever.",
            font=FONT_MAIN,
            fg=TEXT_SECONDARY,
            bg=BG_PANEL,
            wraplength=740,
            justify=tk.LEFT
        )
        c2_sub.pack(anchor=tk.W, pady=(0, 10))

        c2_btns = tk.Frame(card2, bg=BG_PANEL)
        c2_btns.pack(fill=tk.X)
        self.login_btn = DarkButton(c2_btns, text="🔑 Log In to TikTok (Browser / QR Code)", is_primary=True, command=self._start_login_process)
        self.login_btn.pack(side=tk.LEFT, padx=(0, 8))
        DarkButton(c2_btns, text="🚪 Log Out", command=self._logout_session).pack(side=tk.LEFT)

        # Card 3: Security & Session Info
        card3 = tk.Frame(frame, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=14, pady=12)
        card3.pack(fill=tk.X)

        c3_title = tk.Label(card3, text="SECURITY & PRIVACY", font=FONT_TITLE, fg=TEXT_WHITE, bg=BG_PANEL)
        c3_title.pack(anchor=tk.W, pady=(0, 4))

        sec_text = (
            "• All session tokens are saved locally in session.json on your computer only.\n"
            "• Your password is never stored or typed anywhere by the application.\n"
            "• The app uses anti-detection scripts (masking navigator.webdriver) to mimic a genuine user."
        )
        tk.Label(card3, text=sec_text, font=FONT_MAIN, fg=TEXT_MUTED, bg=BG_PANEL, justify=tk.LEFT).pack(anchor=tk.W)

        return frame

    def _build_statusbar(self):
        """Volt status bar with monospace stats and primary Save button."""
        sep = tk.Frame(self, bg=BORDER_COLOR, height=1)
        sep.pack(fill=tk.X, side=tk.BOTTOM)

        statusbar = tk.Frame(self, bg=BG_PANEL, height=36, padx=12)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        statusbar.pack_propagate(False)

        # Left status indicator
        self.status_msg_var = tk.StringVar(value="Ready")
        s_left = tk.Frame(statusbar, bg=BG_PANEL)
        s_left.pack(side=tk.LEFT, fill=tk.Y)

        s_dot = tk.Label(s_left, text="●", font=("Segoe UI", 8), fg=COLOR_SUCCESS, bg=BG_PANEL)
        s_dot.pack(side=tk.LEFT, padx=(0, 5))

        s_text = tk.Label(s_left, textvariable=self.status_msg_var, font=FONT_MONO, fg=TEXT_SECONDARY, bg=BG_PANEL)
        s_text.pack(side=tk.LEFT)

        # Start button on the right (saves, closes UI, and starts streak saver)
        start_btn = DarkButton(
            statusbar,
            text="🚀  START",
            is_primary=True,
            command=self._start_and_close
        )
        start_btn.pack(side=tk.RIGHT, padx=(8, 0), pady=4)

        # Save button on the right
        save_btn = DarkButton(
            statusbar,
            text="💾  SAVE CONFIG",
            command=self._save_config
        )
        save_btn.pack(side=tk.RIGHT, pady=4)

        # Middle stats badge
        self.stats_var = tk.StringVar(value="")
        stats_lbl = tk.Label(statusbar, textvariable=self.stats_var, font=FONT_MONO, fg=TEXT_MUTED, bg=BG_PANEL)
        stats_lbl.pack(side=tk.RIGHT, padx=14)

    # --- Data Population & Handlers ---

    def _populate_all_data(self):
        # Friends
        for item in self.friends_tree.get_children():
            self.friends_tree.delete(item)

        friends = self.config_data.get("friends", [])
        for f in friends:
            if isinstance(f, dict):
                uname = f.get("username", "")
                msg = f.get("custom_message", "")
            else:
                uname = str(f)
                msg = ""
            self.friends_tree.insert("", tk.END, values=(uname, msg))

        # Messages
        self.messages_listbox.delete(0, tk.END)
        for msg in self.config_data.get("default_messages", []):
            self.messages_listbox.insert(tk.END, msg)

        # Settings
        self.cooldown_var.set(str(self.config_data.get("cooldown_hours", 18)))
        self.min_delay_var.set(str(self.config_data.get("delay_between_chats_min", 6)))
        self.max_delay_var.set(str(self.config_data.get("delay_between_chats_max", 14)))
        self.headless_var.set(bool(self.config_data.get("headless", True)))

        self._update_stats_badge()

    def _update_stats_badge(self):
        count_f = len(self.friends_tree.get_children()) if hasattr(self, "friends_tree") else 0
        count_m = self.messages_listbox.size() if hasattr(self, "messages_listbox") else 0
        self.stats_var.set(f"{count_f} FRIENDS  |  {count_m} TEMPLATES  |  AUTO-CLOSE: ON")

    def _on_friend_selected(self, event):
        selected = self.friends_tree.selection()
        if not selected:
            return
        values = self.friends_tree.item(selected[0], "values")
        if values:
            self.friend_uname_var.set(values[0])
            self.friend_msg_var.set(values[1] if len(values) > 1 else "")

    def _add_friend(self):
        uname = self.friend_uname_var.get().strip().lstrip("@")
        msg = self.friend_msg_var.get().strip()
        if not uname:
            messagebox.showwarning("Missing Username", "Please enter a TikTok username or handle.")
            return

        for child in self.friends_tree.get_children():
            v = self.friends_tree.item(child, "values")
            if v[0].lower() == uname.lower():
                messagebox.showinfo("Already Exists", f"@{uname} is already in the list. Use 'Update Selected' to edit.")
                return

        self.friends_tree.insert("", tk.END, values=(uname, msg))
        self._clear_friend_inputs()
        self.status_msg_var.set(f"Added @{uname} (Unsaved changes)")
        self._update_stats_badge()

    def _update_friend(self):
        selected = self.friends_tree.selection()
        if not selected:
            messagebox.showinfo("Select Friend", "Select a friend from the list above to update.")
            return
        uname = self.friend_uname_var.get().strip().lstrip("@")
        msg = self.friend_msg_var.get().strip()
        if not uname:
            messagebox.showwarning("Missing Username", "Please enter a TikTok username.")
            return
        self.friends_tree.item(selected[0], values=(uname, msg))
        self.status_msg_var.set(f"Updated @{uname} (Unsaved changes)")

    def _remove_friend(self):
        selected = self.friends_tree.selection()
        if not selected:
            messagebox.showinfo("Select Friend", "Select a friend from the list to remove.")
            return
        values = self.friends_tree.item(selected[0], "values")
        uname = values[0] if values else "friend"
        if messagebox.askyesno("Confirm Remove", f"Remove @{uname} from your streak list?"):
            self.friends_tree.delete(selected[0])
            self._clear_friend_inputs()
            self.status_msg_var.set(f"Removed @{uname} (Unsaved changes)")
            self._update_stats_badge()

    def _clear_friend_inputs(self):
        self.friend_uname_var.set("")
        self.friend_msg_var.set("")
        self.friends_tree.selection_remove(self.friends_tree.selection())

    def _add_message(self):
        txt = self.new_msg_var.get().strip()
        if not txt:
            return
        self.messages_listbox.insert(tk.END, txt)
        self.new_msg_var.set("")
        self.status_msg_var.set("Added new message template")
        self._update_stats_badge()

    def _delete_message(self):
        selected = self.messages_listbox.curselection()
        if not selected:
            return
        self.messages_listbox.delete(selected[0])
        self.status_msg_var.set("Removed message template")
        self._update_stats_badge()

    def _get_startup_shortcut(self) -> Path:
        return Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "TikTokStreakSaver.lnk"

    def _check_startup_status(self):
        lnk = self._get_startup_shortcut()
        if lnk.exists():
            self.startup_status_lbl.configure(
                text="🟢  STARTUP ENABLED (Runs silently on PC boot and auto-closes)",
                fg=COLOR_SUCCESS
            )
        else:
            self.startup_status_lbl.configure(
                text="⚪  STARTUP DISABLED (Will not launch automatically on boot)",
                fg=TEXT_SECONDARY
            )

    def _enable_startup(self):
        lnk = self._get_startup_shortcut()
        if EXE_PATH.exists():
            target = str(EXE_PATH.resolve())
            cwd = str(EXE_PATH.resolve().parent)
            args_str = "run"
        else:
            target = sys.executable
            cwd = str(APP_DIR)
            args_str = f'"{APP_DIR / "main.py"}" run'

        ps_cmd = (
            f"$ws = New-Object -ComObject WScript.Shell; "
            f"$s = $ws.CreateShortcut('{lnk}'); "
            f"$s.TargetPath = '{target}'; "
            f"$s.Arguments = '{args_str}'; "
            f"$s.WorkingDirectory = '{cwd}'; "
            f"$s.Description = 'TikTok Auto Streak Saver'; "
            f"$s.Save()"
        )
        try:
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, capture_output=True, creationflags=flags)
            self._check_startup_status()
            messagebox.showinfo("Startup Enabled", f"TikTok Streak Saver registered in Windows Startup!\n\nPath:\n{lnk}")
        except Exception as e:
            messagebox.showerror("Startup Error", f"Failed to enable startup: {e}")

    def _disable_startup(self):
        lnk = self._get_startup_shortcut()
        if lnk.exists():
            try:
                lnk.unlink()
                self._check_startup_status()
                messagebox.showinfo("Startup Disabled", "Removed from Windows Startup.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove startup shortcut: {e}")
        else:
            messagebox.showinfo("Not Enabled", "Startup was not enabled.")

    def _on_cooldown_var_changed(self, *args):
        try:
            val = int(float(self.cooldown_var.get().strip()))
            if hasattr(self, "sched_btn"):
                self.sched_btn.configure(text=f"🕒 Enable Schedule (Every {val}h)")
        except Exception:
            if hasattr(self, "sched_btn"):
                self.sched_btn.configure(text="🕒 Enable Schedule")

    def _get_schedule_cmd(self) -> str:
        if EXE_PATH.exists():
            return f'"{EXE_PATH.resolve()}" run'
        else:
            return f'"{sys.executable}" "{APP_DIR / "main.py"}" run'

    def _check_schedule_status(self):
        # Instant direct disk inspection (< 1 ms, zero subprocesses, no GUI freeze)
        task_file = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "Tasks" / "TikTokStreakSaver"
        if not task_file.exists():
            self.schedule_status_lbl.configure(
                text="⚪  SCHEDULE DISABLED (Not registered in Windows Task Scheduler)",
                fg=TEXT_SECONDARY
            )
            return

        try:
            try:
                xml_str = task_file.read_text(encoding="utf-16", errors="ignore")
            except Exception:
                xml_str = task_file.read_text(encoding="utf-8", errors="ignore")

            interval = "18h"
            if "<Interval>PT" in xml_str:
                val = xml_str.split("<Interval>PT", 1)[1].split("</Interval>", 1)[0]
                interval = val.lower()
            elif "<ScheduleByDay>" in xml_str:
                interval = "daily"

            self.schedule_status_lbl.configure(
                text=f"🟢  SCHEDULE ACTIVE (Repeats every {interval} — 0 MB RAM when idle)",
                fg=COLOR_SUCCESS
            )
        except Exception:
            self.schedule_status_lbl.configure(
                text="🟢  SCHEDULE ACTIVE (Task registered)",
                fg=COLOR_SUCCESS
            )

    def _enable_schedule(self):
        # Save any pending config first
        self._save_config(show_prompt=False)
        try:
            hours = int(float(self.cooldown_var.get().strip()))
            hours = max(1, hours)
        except ValueError:
            hours = 18

        cmd = self._get_schedule_cmd()
        if hours < 24:
            sc_type = "HOURLY"
            mo_val = str(hours)
            desc = f"every {hours} hour(s)"
        else:
            days = max(1, hours // 24)
            sc_type = "DAILY"
            mo_val = str(days)
            desc = f"every {days} day(s) ({hours}h)"

        schtask_cmd = [
            "schtasks",
            "/create",
            "/tn",
            "TikTokStreakSaver",
            "/tr",
            cmd,
            "/sc",
            sc_type,
            "/mo",
            mo_val,
            "/f"
        ]

        self.schedule_status_lbl.configure(text="⏳  Registering schedule with Windows...", fg=TEXT_MUTED)

        def _worker():
            try:
                subprocess.run(
                    schtask_cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
                self.after(0, lambda: self._on_schedule_enabled_success(desc, cmd))
            except subprocess.CalledProcessError as e:
                err = e.stderr or e.stdout
                self.after(0, lambda: messagebox.showerror("Scheduler Error", f"Failed to register task: {err}"))
            finally:
                self.after(0, self._check_schedule_status)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_schedule_enabled_success(self, desc, cmd):
        self._check_schedule_status()
        messagebox.showinfo(
            "Task Scheduler Enabled",
            f"Windows Task Scheduler registered successfully!\n\n"
            f"• Recurrence: {desc}\n"
            f"• Task Name:  TikTokStreakSaver\n"
            f"• Action:     Runs headless & auto-closes\n\n"
            f"Dormant with 0 MB background RAM between runs."
        )

    def _disable_schedule(self):
        self.schedule_status_lbl.configure(text="⏳  Removing schedule...", fg=TEXT_MUTED)

        def _worker():
            try:
                subprocess.run(
                    ["schtasks", "/delete", "/tn", "TikTokStreakSaver", "/f"],
                    capture_output=True,
                    text=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
                self.after(0, lambda: messagebox.showinfo("Schedule Disabled", "Windows Task 'TikTokStreakSaver' was removed."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to remove task: {e}"))
            finally:
                self.after(0, self._check_schedule_status)

        threading.Thread(target=_worker, daemon=True).start()

    def _run_streak_saver(self):
        self._save_config(show_prompt=False)
        cmd = [str(EXE_PATH)] if EXE_PATH.exists() else [sys.executable, str(APP_DIR / "main.py"), "run"]
        try:
            subprocess.Popen(cmd, cwd=str(EXE_PATH.parent if EXE_PATH.exists() else APP_DIR), creationflags=subprocess.CREATE_NEW_CONSOLE)
            messagebox.showinfo("Launched", "Launched TikTok Streak Saver in a new console window!")
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch: {e}")

    def _reset_cooldowns(self):
        cmd = [str(EXE_PATH), "reset"] if EXE_PATH.exists() else [sys.executable, str(APP_DIR / "main.py"), "reset"]
        try:
            res = subprocess.run(cmd, cwd=str(EXE_PATH.parent if EXE_PATH.exists() else APP_DIR), capture_output=True, text=True)
            messagebox.showinfo("Reset Complete", res.stdout or "Cooldowns reset successfully!")
        except Exception as e:
            messagebox.showerror("Reset Error", f"Could not reset: {e}")

    def _check_status(self):
        cmd = [str(EXE_PATH), "status"] if EXE_PATH.exists() else [sys.executable, str(APP_DIR / "main.py"), "status"]
        try:
            res = subprocess.run(cmd, cwd=str(EXE_PATH.parent if EXE_PATH.exists() else APP_DIR), capture_output=True, text=True)
            messagebox.showinfo("Current Status & Streaks", res.stdout or "No status returned.")
        except Exception as e:
            messagebox.showerror("Status Error", f"Could not check status: {e}")

    # --- Account & Session Management Methods ---
    def _has_active_session(self) -> bool:
        """Instant disk check if a valid session.json exists with auth cookies."""
        paths = [SESSION_PATH]
        if not getattr(sys, "frozen", False):
            paths.extend([DIST_SESSION, LOCAL_SESSION])
        
        for p in paths:
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8-sig"))
                    cookies = data.get("cookies", [])
                    for c in cookies:
                        if c.get("name") in {"sessionid", "sessionid_ss", "sid_tt"} and len(c.get("value", "")) > 10:
                            return True
                except Exception:
                    pass
        return False

    def _get_active_session_path(self) -> Path:
        if SESSION_PATH.exists():
            return SESSION_PATH
        if not getattr(sys, "frozen", False):
            if DIST_SESSION.exists():
                return DIST_SESSION
            if LOCAL_SESSION.exists():
                return LOCAL_SESSION
        return SESSION_PATH

    def _get_session_details(self) -> dict:
        sess_path = self._get_active_session_path()
        if not sess_path.exists():
            return {
                "logged_in": False,
                "method": "Not Authenticated",
                "expires": "N/A",
                "tokens": "None",
                "path": str(sess_path.name)
            }
        try:
            data = json.loads(sess_path.read_text(encoding="utf-8-sig"))
            cookies = data.get("cookies", [])
            has_auth = False
            method = "Browser / QR"
            max_exp = 0
            token_names = []
            for c in cookies:
                name = c.get("name", "")
                if name in {"sessionid", "sessionid_ss", "sid_tt", "ttwid"}:
                    token_names.append(name)
                    has_auth = True
                if name == "last_login_method":
                    method = str(c.get("value", method))
                exp = c.get("expires", 0)
                if isinstance(exp, (int, float)) and exp > max_exp:
                    max_exp = exp

            expires_str = "Permanent / Long-lived"
            if max_exp > 0:
                import datetime
                dt = datetime.datetime.fromtimestamp(max_exp)
                expires_str = dt.strftime("%B %d, %Y")

            return {
                "logged_in": has_auth,
                "method": method,
                "expires": expires_str,
                "tokens": ", ".join(sorted(set(token_names))) if token_names else "None",
                "path": str(sess_path.name)
            }
        except Exception as e:
            return {
                "logged_in": False,
                "method": "Error reading session",
                "expires": str(e),
                "tokens": "None",
                "path": str(sess_path.name)
            }

    def _refresh_account_status(self):
        details = self._get_session_details()
        is_logged_in = details["logged_in"]

        if hasattr(self, "account_status_lbl"):
            if is_logged_in:
                self.account_status_lbl.configure(
                    text="🟢  LOGGED IN (Session Active & Authenticated)",
                    fg=COLOR_SUCCESS
                )
            else:
                self.account_status_lbl.configure(
                    text="🔴  NOT LOGGED IN (No active session — please click Log In below)",
                    fg=COLOR_ERROR
                )

        if hasattr(self, "acc_method_lbl"):
            self.acc_method_lbl.configure(text=details["method"])
        if hasattr(self, "acc_expires_lbl"):
            self.acc_expires_lbl.configure(text=details["expires"])
        if hasattr(self, "acc_tokens_lbl"):
            self.acc_tokens_lbl.configure(text=details["tokens"])

        if hasattr(self, "top_account_badge"):
            if is_logged_in:
                self.top_account_badge.configure(text="🟢 LOGGED IN", fg=COLOR_SUCCESS)
            else:
                self.top_account_badge.configure(text="🔴 NOT LOGGED IN", fg=COLOR_ERROR)

    def _test_friend(self):
        """Saves current friend config and opens TikTokStreakSaver in a visible console to test."""
        uname = self.friend_uname_var.get().strip().lstrip("@")
        msg = self.friend_msg_var.get().strip()
        if uname:
            found = False
            for child in self.friends_tree.get_children():
                v = self.friends_tree.item(child, "values")
                if v[0].lower() == uname.lower():
                    self.friends_tree.item(child, values=(uname, msg))
                    found = True
                    break
            if not found:
                self.friends_tree.insert("", tk.END, values=(uname, msg))
            self._update_stats_badge()

        if not self.friends_tree.get_children():
            messagebox.showwarning("No Friends", "Please enter a TikTok friend username first.")
            return

        # Save config silently
        self._save_config(show_prompt=False)

        # Open TikTokStreakSaver
        cmd = [str(EXE_PATH)] if EXE_PATH.exists() else [sys.executable, str(APP_DIR / "main.py")]
        try:
            flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
            subprocess.Popen(cmd, cwd=str(EXE_PATH.parent if EXE_PATH.exists() else APP_DIR), creationflags=flags)
            self.status_msg_var.set("Saved & launched TikTok Streak Saver for testing")
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch TikTokStreakSaver: {e}")

    def _start_and_close(self):
        """Saves config, starts TikTokStreakSaver, and closes the configuration UI."""
        uname = self.friend_uname_var.get().strip().lstrip("@")
        msg = self.friend_msg_var.get().strip()
        if uname:
            found = False
            for child in self.friends_tree.get_children():
                v = self.friends_tree.item(child, "values")
                if v[0].lower() == uname.lower():
                    self.friends_tree.item(child, values=(uname, msg))
                    found = True
                    break
            if not found:
                self.friends_tree.insert("", tk.END, values=(uname, msg))
            self._update_stats_badge()

        if not self.friends_tree.get_children():
            messagebox.showwarning(
                "No Friends Added",
                "Please add at least one friend to your streak list before starting."
            )
            return

        # Save config
        self._save_config(show_prompt=False)

        # Launch TikTokStreakSaver
        cmd = [str(EXE_PATH)] if EXE_PATH.exists() else [sys.executable, str(APP_DIR / "main.py")]
        try:
            flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
            subprocess.Popen(cmd, cwd=str(EXE_PATH.parent if EXE_PATH.exists() else APP_DIR), creationflags=flags)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start TikTokStreakSaver: {e}")
            return

        # Close the configuration UI
        self.destroy()

    def _start_login_process(self):
        """Launches interactive browser login so user can scan QR code."""
        cmd = [str(EXE_PATH), "login"] if EXE_PATH.exists() else [sys.executable, str(APP_DIR / "main.py"), "login"]
        self.account_status_lbl.configure(text="⏳  Browser opening... please scan QR code on screen", fg=COLOR_WARNING)
        
        def _worker():
            try:
                flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(EXE_PATH.parent if EXE_PATH.exists() else APP_DIR),
                    creationflags=flags
                )
                proc.wait()
                self.after(0, self._on_login_finished)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Login Error", f"Could not launch login: {e}"))
                self.after(0, self._refresh_account_status)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_login_finished(self):
        self._refresh_account_status()
        if self._has_active_session():
            messagebox.showinfo(
                "Login Successful",
                "🎉 Login successful!\n\n"
                "Your authentication tokens have been securely saved to session.json.\n"
                "You are ready to configure friends and start sending daily streaks."
            )
            self._switch_tab("friends")
        else:
            messagebox.showwarning(
                "Login Incomplete",
                "No authenticated session was detected.\n\n"
                "If the browser closed before you scanned the QR code, click 'Log In to TikTok' to try again."
            )

    def _logout_session(self):
        """Clears local session.json after confirmation."""
        sess_path = self._get_active_session_path()
        if not sess_path.exists():
            messagebox.showinfo("Not Logged In", "You are not currently logged in.")
            return

        if messagebox.askyesno(
            "Confirm Log Out",
            "Are you sure you want to log out of TikTok?\n\n"
            "This will delete session.json and pause automated streaks until you log back in."
        ):
            try:
                if sess_path.exists():
                    sess_path.unlink()
                if not getattr(sys, "frozen", False):
                    if DIST_SESSION.exists():
                        DIST_SESSION.unlink()
                    if LOCAL_SESSION.exists():
                        LOCAL_SESSION.unlink()
                self._refresh_account_status()
                messagebox.showinfo("Logged Out", "Successfully logged out. Your local session tokens were removed.")
            except Exception as e:
                messagebox.showerror("Log Out Error", f"Failed to delete session file: {e}")


def main():
    app = ConfigGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
