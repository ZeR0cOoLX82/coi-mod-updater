#!/usr/bin/env python3
"""
COI-Extended Mod Updater - Full Edition
Stability Fixes Applied (Dry-Run Report):
  #1  Zombie-Threads _minimize()
  #2  Zombie-Threads _open_settings_standalone()
  #3  Stilles Versagen open_updater_manual()
  #4  TclError in Tooltip._show()
  #5  Datenverlust in rollback_mod()
  #6  Datei-Leichen in extract_zip()
  #7  ZeroDivisionError in download_asset()
  #8  JSONDecodeError in load_cache()
"""

import os, sys, json, shutil, zipfile, threading, requests, time, hashlib, locale, math
import tkinter as tk
import winreg
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Tuple
from PIL import Image, ImageDraw
import pystray

try:
    from plyer import notification as plyer_notify
    PLYER_OK = True
except ImportError:
    PLYER_OK = False

# ============================================================
# CONSTANTS
# ============================================================

FONT_UI = "Segoe UI"

DEFAULT_SETTINGS: Dict = {
    "github_token":        "",
    "check_interval":      3,
    "check_on_start":      True,
    "mods_folder":         "",
    "allowed_mods": [
        "COIExtended.Automation", "COIExtended.Cheats", "COIExtended.Core",
        "COIExtended.Difficulty", "COIExtended.ItemSink", "COIExtended.RecipeMaker",
        "COIExtended.StoragePlus", "COIExtended.Tweaks",
    ],
    "notifications":       True,
    "run_on_startup":      False,
    "theme":               "dark",
    "language":            None,
    "max_backups":         3,
    "verify_sha256":       True,
    "download_retries":    3,
    "maintenance_enabled": False,
    "maintenance_start":   "02:00",
    "maintenance_end":     "05:00",
    "font_size":           9,
}

GITHUB_USER    = "Keranik"
GITHUB_REPO    = "COI-Extended"
EXCLUDED_FILES = {"COIExtended.Sanitizer.zip"}

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))

_APP_DATA = os.path.join(
    os.environ.get("APPDATA") or os.path.expanduser("~"),
    "COIModUpdater"
)
os.makedirs(_APP_DATA, exist_ok=True)

SETTINGS_FILE = os.path.join(_APP_DATA, "settings.json")
CACHE_FILE    = os.path.join(_APP_DATA, "coi_mod_versions.json")
LOG_FILE      = os.path.join(_APP_DATA, "coi_updater.log")
BACKUPS_DIR   = os.path.join(_APP_DATA, "backups")
ICON_FILE     = os.path.join(BASE_DIR,  "coi_updater.ico")

REQUEST_TIMEOUT  = 15
DOWNLOAD_TIMEOUT = 120
CHUNK_SIZE       = 8192

# ============================================================
# THEMES
# ============================================================

THEMES = {
    "dark": {
        "bg": "#1e1e1e", "bg2": "#141414", "fg": "#ffffff", "fg2": "#cccccc",
        "accent": "#00c87a", "info": "#4da6ff", "warn": "#ffaa00",
        "error": "#ff4444", "update": "#ff88ff", "skip": "#666666",
        "logbg": "#0d0d0d", "entry_bg": "#2a2a2a", "btn_bg": "#333333",
        "tooltip_bg": "#2a2a2a", "tooltip_fg": "#cccccc",
    },
    "light": {
        "bg": "#f0f0f0", "bg2": "#e0e0e0", "fg": "#000000", "fg2": "#333333",
        "accent": "#007a4a", "info": "#0055cc", "warn": "#cc7700",
        "error": "#cc0000", "update": "#880088", "skip": "#999999",
        "logbg": "#ffffff", "entry_bg": "#ffffff", "btn_bg": "#dddddd",
        "tooltip_bg": "#ffffcc", "tooltip_fg": "#333333",
    }
}

# ============================================================
# LANGUAGES
# ============================================================

LANG_STRINGS = {
    "en": {
        "title": "COI-Extended Mod Updater", "by": "by ZeR0cOoLX82",
        "initializing": "Initializing...", "checking": "Checking for updates...",
        "up_to_date": "✓ All mods are up to date!",
        "updating": "Updating {n} mod(s)...",
        "updated_ok": "✓ {ok}/{total} updated! (Release: {tag})",
        "updated_warn": "⚠ {ok}/{total} updated – check log.",
        "overall_prog": "Overall Progress:", "file_prog": "File Progress:",
        "log_label": "Log:", "close_tray": "Close to Tray", "exit": "Exit",
        "open_updater": "Open Updater", "check_now": "Check for Updates Now",
        "auto_check": "Auto-check every {n}h", "open_log": "Open Log File",
        "settings": "Settings", "rollback": "Rollback Mod",
        "no_backups": "No Backups Available",
        "next_check": "Next check in {t}",
        "notif_title": "COI Mod Update",
        "notif_found": "{n} update(s) found!",
        "notif_done": "{ok} mod(s) updated successfully.",
        "startup_on": "Run on Startup ✓", "startup_off": "Run on Startup",
        "tab_general": "General", "tab_mods": "Mods",
        "tab_appearance": "Appearance", "tab_advanced": "Advanced",
        "tab_maintenance": "Maintenance",
        "save": "Save", "cancel": "Cancel", "browse": "Browse",
        "folder_lbl": "Mods Folder:", "interval_lbl": "Check Interval (h):",
        "token_lbl": "GitHub Token (optional):", "startup_lbl": "Run on Startup:",
        "notif_lbl": "Notifications:", "theme_lbl": "Theme:", "lang_lbl": "Language:",
        "font_size_lbl": "Font Size:",
        "backups_lbl": "Max Backups per Mod:", "verify_lbl": "Verify SHA256:",
        "retry_lbl": "Download Retries:",
        "maint_enabled_lbl": "Enable Maintenance Window:",
        "maint_start_lbl": "Allow updates from (HH:MM):",
        "maint_end_lbl": "Allow updates until (HH:MM):",
        "maint_blocked": "Outside maintenance window. Next window: {start}",
        "release_notes": "Release Notes", "view_log": "View Log",
        "dashboard": "Dashboard", "filter_lbl": "Filter:", "refresh": "↻ Refresh",
        "disk_error": "Not enough disk space! Need {need} MB, have {have} MB.",
        "sha_error": "SHA256 mismatch for {name}! File may be corrupted.",
        "pending": "⬆ Pending", "up2date": "✓ Up to date",
        "col_mod": "Mod", "col_github": "GitHub", "col_local": "Local",
        "col_status": "Status", "backing_up": "Backing up...",
        "no_log": "No log file found.", "rollback_title": "Rollback",
        "rollback_select": "Select backup to restore:",
        "rollback_ok": "Rollback successful!", "rollback_fail": "Rollback failed!",
        "release_notes_title": "Release Notes – {tag}",
        "no_release_notes": "No release notes available.",
        "lang_auto": "Auto (System)",
        "stats_total": "Total installs: {n}", "stats_last": "Last update: {t}",
        "rate_limit": "API calls left: {n} / reset: {t}",
        "dash_col_mod": "Mod", "dash_col_ver": "Release",
        "dash_col_installed": "Last Installed", "dash_col_size": "Size on Disk",
        "dash_col_backups": "Backups",
        "not_installed": "not installed",
        "no_updates_available": "No updates available right now.",
        "eta_label": "ETA: ~{s}s  |  {speed} KB/s",
        "eta_done": "",
        "data_path_lbl": "Data folder:",
        "tt_close_tray":    "Minimize to system tray",
        "tt_view_log":      "Open colored log viewer",
        "tt_dashboard":     "Show mod status & disk usage",
        "tt_release_notes": "Read the latest changelog",
        "tt_rollback":      "Restore a previous mod backup",
        "tt_settings":      "Open settings",
        "tt_exit":          "Quit the application completely",
        "no_connection":    "Could not reach GitHub API.\nPlease check your connection.",
    },
    "de": {
        "title": "COI-Extended Mod Updater", "by": "von ZeR0cOoLX82",
        "initializing": "Initialisiere...", "checking": "Suche nach Updates...",
        "up_to_date": "✓ Alle Mods sind aktuell!",
        "updating": "Aktualisiere {n} Mod(s)...",
        "updated_ok": "✓ {ok}/{total} aktualisiert! (Release: {tag})",
        "updated_warn": "⚠ {ok}/{total} aktualisiert – Log prüfen.",
        "overall_prog": "Gesamtfortschritt:", "file_prog": "Dateifortschritt:",
        "log_label": "Log:", "close_tray": "In Tray minimieren", "exit": "Beenden",
        "open_updater": "Updater öffnen", "check_now": "Jetzt auf Updates prüfen",
        "auto_check": "Automatisch alle {n}h", "open_log": "Log-Datei öffnen",
        "settings": "Einstellungen", "rollback": "Mod zurücksetzen",
        "no_backups": "Keine Backups vorhanden",
        "next_check": "Nächste Prüfung in {t}",
        "notif_title": "COI Mod Update",
        "notif_found": "{n} Update(s) gefunden!",
        "notif_done": "{ok} Mod(s) erfolgreich aktualisiert.",
        "startup_on": "Autostart aktiv ✓", "startup_off": "Mit Windows starten",
        "tab_general": "Allgemein", "tab_mods": "Mods",
        "tab_appearance": "Design", "tab_advanced": "Erweitert",
        "tab_maintenance": "Wartungsfenster",
        "save": "Speichern", "cancel": "Abbrechen", "browse": "Durchsuchen",
        "folder_lbl": "Mods-Ordner:", "interval_lbl": "Prüfintervall (h):",
        "token_lbl": "GitHub Token (optional):", "startup_lbl": "Autostart:",
        "notif_lbl": "Benachrichtigungen:", "theme_lbl": "Design:", "lang_lbl": "Sprache:",
        "font_size_lbl": "Schriftgröße:",
        "backups_lbl": "Max. Backups pro Mod:", "verify_lbl": "SHA256 prüfen:",
        "retry_lbl": "Download-Versuche:",
        "maint_enabled_lbl": "Wartungsfenster aktivieren:",
        "maint_start_lbl": "Updates erlaubt ab (HH:MM):",
        "maint_end_lbl": "Updates erlaubt bis (HH:MM):",
        "maint_blocked": "Außerhalb des Wartungsfensters. Nächstes Fenster: {start}",
        "release_notes": "Release Notes", "view_log": "Log anzeigen",
        "dashboard": "Dashboard", "filter_lbl": "Filter:", "refresh": "↻ Aktualisieren",
        "disk_error": "Nicht genug Speicher! Benötigt {need} MB, vorhanden {have} MB.",
        "sha_error": "SHA256-Fehler für {name}! Datei möglicherweise beschädigt.",
        "pending": "⬆ Ausstehend", "up2date": "✓ Aktuell",
        "col_mod": "Mod", "col_github": "GitHub", "col_local": "Lokal",
        "col_status": "Status", "backing_up": "Backup läuft...",
        "no_log": "Keine Log-Datei gefunden.", "rollback_title": "Rollback",
        "rollback_select": "Backup zum Wiederherstellen wählen:",
        "rollback_ok": "Rollback erfolgreich!", "rollback_fail": "Rollback fehlgeschlagen!",
        "release_notes_title": "Release Notes – {tag}",
        "no_release_notes": "Keine Release Notes verfügbar.",
        "lang_auto": "Auto (System)",
        "stats_total": "Installationen gesamt: {n}", "stats_last": "Letztes Update: {t}",
        "rate_limit": "API-Aufrufe übrig: {n} / Reset: {t}",
        "dash_col_mod": "Mod", "dash_col_ver": "Release",
        "dash_col_installed": "Letzte Installation", "dash_col_size": "Größe",
        "dash_col_backups": "Backups",
        "not_installed": "nicht installiert",
        "no_updates_available": "Gerade keine Updates verfügbar.",
        "eta_label": "ETA: ~{s}s  |  {speed} KB/s",
        "eta_done": "",
        "data_path_lbl": "Datenpfad:",
        "tt_close_tray":    "In den System-Tray minimieren",
        "tt_view_log":      "Farbigen Log-Viewer öffnen",
        "tt_dashboard":     "Mod-Status & Festplattennutzung anzeigen",
        "tt_release_notes": "Aktuelles Changelog lesen",
        "tt_rollback":      "Vorherige Mod-Version wiederherstellen",
        "tt_settings":      "Einstellungen öffnen",
        "tt_exit":          "Anwendung vollständig beenden",
        "no_connection":    "GitHub API nicht erreichbar.\nBitte Verbindung prüfen.",
    }
}

# ============================================================
# GLOBALS
# ============================================================

settings:            Dict                 = {}
tray_icon                                 = None
gui_window                                = None
gui_lock           = threading.Lock()
stop_event         = threading.Event()
next_check_time:   Optional[datetime]    = None
last_rate_info:    Dict                  = {}
_static_tray_img:  Optional[Image.Image] = None
_tray_anim_stop    = threading.Event()
_tray_animating    = False
_TRAY_FRAMES:      List[Image.Image]     = []

# ============================================================
# HELPERS
# ============================================================

def fs(delta: int = 0) -> int:
    return max(7, settings.get("font_size", 9) + delta)


def translate(key: str, **kwargs) -> str:
    lang = settings.get("language") or "en"
    s = LANG_STRINGS.get(lang, LANG_STRINGS["en"]).get(key, key)
    return s.format(**kwargs) if kwargs else s


def theme_config() -> Dict:
    return THEMES.get(settings.get("theme", "dark"), THEMES["dark"])

# ============================================================
# TOOLTIP  –  FIX #4: winfo_exists() check
# ============================================================

class Tooltip:
    _delay_ms = 500

    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text   = text
        self._tip   = None
        self._after = None
        widget.bind("<Enter>",  self._schedule)
        widget.bind("<Leave>",  self._cancel)
        widget.bind("<Button>", self._cancel)

    def _schedule(self, _=None):
        self._cancel()
        self._after = self.widget.after(self._delay_ms, self._show)

    def _cancel(self, _=None):
        if self._after:
            self.widget.after_cancel(self._after)
            self._after = None
        if self._tip:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None

    def _show(self, _=None):
        # FIX #4 – Widget könnte in den 500ms bereits zerstört worden sein
        if not self.widget.winfo_exists():
            return
        t = theme_config()
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        self._tip.attributes("-topmost", True)
        tk.Label(
            self._tip, text=self.text,
            bg=t["tooltip_bg"], fg=t["tooltip_fg"],
            font=(FONT_UI, fs(-1)), relief="solid", bd=1,
            padx=8, pady=4
        ).pack()

# ============================================================
# ANIMATED TRAY ICON
# ============================================================

def _generate_static_icon() -> Image.Image:
    if os.path.exists(ICON_FILE):
        return Image.open(ICON_FILE).resize((64, 64)).convert("RGBA")
    img  = Image.new("RGBA", (64, 64), (26, 26, 46, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill="#00c87a")
    return img


def generate_tray_frames(count: int = 10) -> List[Image.Image]:
    frames    = []
    cx = cy   = 32
    r_outer   = 22
    r_dot     = 4
    base_img  = Image.new("RGBA", (64, 64), (26, 26, 46, 255))
    base_draw = ImageDraw.Draw(base_img)
    base_draw.ellipse([14, 14, 50, 50], fill="#1a3a2a")
    for frame_i in range(count):
        img  = base_img.copy()
        draw = ImageDraw.Draw(img)
        for dot_i in range(count):
            angle = math.radians(-90 + (360 / count) * dot_i + (360 / count) * frame_i)
            x = cx + r_outer * math.cos(angle)
            y = cy + r_outer * math.sin(angle)
            brightness = int(40 + 215 * (dot_i / count))
            col = (0, brightness, int(brightness * 0.55), 255)
            draw.ellipse([x - r_dot, y - r_dot, x + r_dot, y + r_dot], fill=col)
        draw.ellipse([26, 26, 38, 38], fill="#00c87a")
        frames.append(img)
    return frames


def start_tray_animation():
    global _tray_animating
    if _tray_animating or not _TRAY_FRAMES or not tray_icon:
        return
    _tray_animating = True
    _tray_anim_stop.clear()

    def _loop():
        global _tray_animating
        i = 0
        while not _tray_anim_stop.is_set():
            try:
                tray_icon.icon = _TRAY_FRAMES[i % len(_TRAY_FRAMES)]
            except Exception:
                break
            i += 1
            time.sleep(0.1)
        try:
            if tray_icon and _static_tray_img:
                tray_icon.icon = _static_tray_img
        except Exception:
            pass
        _tray_animating = False

    threading.Thread(target=_loop, daemon=True).start()


def stop_tray_animation():
    _tray_anim_stop.set()

# ============================================================
# LANGUAGE / SETTINGS
# ============================================================

def detect_system_language() -> str:
    try:
        code = locale.getlocale()[0]
        if code and code.startswith("de"):
            return "de"
    except Exception:
        pass
    return "en"


def load_settings() -> Dict:
    global settings
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if "language" not in loaded or loaded["language"] is None:
            loaded["language"] = detect_system_language()
        settings = {**DEFAULT_SETTINGS, **loaded}
    else:
        settings = DEFAULT_SETTINGS.copy()
        settings["language"] = detect_system_language()
    return settings


def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get_headers() -> Dict:
    h = {"Accept": "application/vnd.github+json"}
    token = settings.get("github_token", "").strip()
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def get_mods_folder() -> str:
    override = settings.get("mods_folder", "").strip()
    if override and os.path.isdir(override):
        return override
    env = os.environ.get("COI_MODS_FOLDER")
    if env:
        return os.path.abspath(env)
    return os.path.join(
        os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"),
        "..", "LocalLow", "MaFi Games", "Captain of Industry", "Mods"
    )

# ============================================================
# MAINTENANCE WINDOW
# ============================================================

def parse_hhmm(s: str) -> Tuple[int, int]:
    try:
        h, m = s.strip().split(":")
        return int(h), int(m)
    except Exception:
        return 0, 0


def is_in_maintenance_window() -> bool:
    if not settings.get("maintenance_enabled", False):
        return True
    now    = datetime.now()
    sh, sm = parse_hhmm(settings.get("maintenance_start", "02:00"))
    eh, em = parse_hhmm(settings.get("maintenance_end",   "05:00"))
    start  = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end    = now.replace(hour=eh, minute=em, second=0, microsecond=0)
    if start <= end:
        return start <= now <= end
    return now >= start or now <= end


def next_maintenance_start() -> str:
    sh, sm = parse_hhmm(settings.get("maintenance_start", "02:00"))
    now    = datetime.now()
    start  = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    if start <= now:
        start += timedelta(days=1)
    return start.strftime("%d.%m. %H:%M")

# ============================================================
# WINDOWS STARTUP
# ============================================================

STARTUP_KEY  = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_NAME = "COIModUpdater"


def set_startup(enable: bool):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE)
        if enable:
            exe = sys.executable if getattr(sys, "frozen", False) \
                else f'pythonw "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, STARTUP_NAME, 0, winreg.REG_SZ, exe)
        else:
            try:
                winreg.DeleteValue(key, STARTUP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        settings["run_on_startup"] = enable
        save_settings()
    except Exception as e:
        write_log("ERROR", f"Startup registry failed: {e}")


def is_startup_enabled() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, STARTUP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False

# ============================================================
# NOTIFICATIONS / LOGGING
# ============================================================

def notify(title: str, msg: str):
    if not settings.get("notifications", True):
        return
    if PLYER_OK:
        try:
            plyer_notify.notify(title=title, message=msg,
                                app_name="COI Mod Updater", timeout=5)
        except Exception:
            pass


def write_log(tag: str, msg: str):
    line = f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] [{tag:<8}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def log(tag: str, msg: str, gui=None):
    write_log(tag, msg)
    if gui is not None:
        gui.schedule_log_message(
            tag, f"[{datetime.now().strftime('%H:%M:%S')}] [{tag}] {msg}")

# ============================================================
# CACHE  –  FIX #8: JSONDecodeError abfangen
# ============================================================

def load_cache() -> Dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # FIX #8 – Korrupte/unvollständige JSON-Datei → frisch starten
            write_log("ERROR", "Cache file corrupted or unreadable, starting fresh.")
    return {"assets": {}}


def save_cache(cache: Dict):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except OSError as e:
        write_log("ERROR", f"Could not save cache: {e}")


def get_stats(cache: Dict) -> Tuple[int, str]:
    assets     = cache.get("assets", {})
    total      = sum(1 for a in assets.values() if a.get("last_installed"))
    last_times = [a["last_installed"] for a in assets.values() if a.get("last_installed")]
    last_str   = format_time(max(last_times)) if last_times else "-"
    return total, last_str

# ============================================================
# UTILS
# ============================================================

def format_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%d.%m.%Y %H:%M")
    except Exception:
        return iso_str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_countdown(dt: Optional[datetime]) -> str:
    if dt is None:
        return ""
    total = max(0, int((dt - datetime.now()).total_seconds()))
    h, r  = divmod(total, 3600)
    m, s  = divmod(r, 60)
    return f"{h}h {m:02d}m" if h > 0 else f"{m}m {s:02d}s"


def free_space_mb(path: str) -> float:
    try:
        return shutil.disk_usage(path).free / (1024 * 1024)
    except Exception:
        return float("inf")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def folder_size_mb(path: str) -> float:
    total = 0
    try:
        for root, _, files in os.walk(path):
            for file in files:
                try:
                    total += os.path.getsize(os.path.join(root, file))
                except Exception:
                    pass
    except Exception:
        pass
    return round(total / (1024 * 1024), 2)

# ============================================================
# GITHUB
# ============================================================

def get_latest_release() -> Optional[Dict]:
    global last_rate_info
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
    for attempt in range(3):
        try:
            r = requests.get(url, headers=get_headers(), timeout=REQUEST_TIMEOUT)
            last_rate_info = {
                "remaining": r.headers.get("X-RateLimit-Remaining", "?"),
                "reset":     r.headers.get("X-RateLimit-Reset", ""),
            }
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            if attempt < 2:
                time.sleep(2 ** attempt)
    return None


def get_filtered_assets(release: Dict) -> List[Dict]:
    allowed = set(settings.get("allowed_mods", DEFAULT_SETTINGS["allowed_mods"]))
    result  = []
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if not name.lower().endswith(".zip") or name in EXCLUDED_FILES:
            continue
        mod_name = os.path.splitext(name)[0]
        if mod_name not in allowed:
            continue
        result.append({
            "name":       name,
            "mod_name":   mod_name,
            "url":        asset["browser_download_url"],
            "updated_at": asset.get("updated_at", ""),
            "size_kb":    round(asset.get("size", 0) / 1024, 1),
            "size_bytes": asset.get("size", 0),
            "digest":     asset.get("digest", ""),
        })
    return result

# ============================================================
# INSTALL LOGIC
# ============================================================

def mod_path(mod_name: str) -> str:
    return os.path.join(get_mods_folder(), mod_name)


def is_installed(mod_name: str) -> bool:
    p = mod_path(mod_name)
    return os.path.isdir(p) and any(os.scandir(p))


def needs_update(cache: Dict, mod_name: str, updated_at: str) -> bool:
    if not is_installed(mod_name):
        return True
    return cache.get("assets", {}).get(mod_name, {}).get("updated_at") != updated_at


def create_backup(mod_name: str, release_tag: str) -> bool:
    src = mod_path(mod_name)
    if not os.path.isdir(src):
        return False
    backup_dir = os.path.join(BACKUPS_DIR, mod_name)
    os.makedirs(backup_dir, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(backup_dir, f"{mod_name}_{release_tag}_{ts}.zip")
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(src):
                for file in files:
                    fp = os.path.join(root, file)
                    zf.write(fp, os.path.relpath(fp, os.path.dirname(src)))
        _prune_backups(mod_name)
        write_log("BACKUP", f"Created: {os.path.basename(zip_path)}")
        return True
    except Exception as e:
        write_log("ERROR", f"Backup failed for {mod_name}: {e}")
        return False


def _prune_backups(mod_name: str):
    d = os.path.join(BACKUPS_DIR, mod_name)
    if not os.path.isdir(d):
        return
    files = sorted([f for f in os.listdir(d) if f.endswith(".zip")], reverse=True)
    for old in files[settings.get("max_backups", 3):]:
        try:
            os.remove(os.path.join(d, old))
        except Exception:
            pass


def get_backups(mod_name: str) -> List[str]:
    d = os.path.join(BACKUPS_DIR, mod_name)
    if not os.path.isdir(d):
        return []
    return sorted([f for f in os.listdir(d) if f.endswith(".zip")], reverse=True)


# FIX #5 – Zuerst nach temp entpacken, DANN erst Original löschen
def rollback_mod(mod_name: str, backup_file: str) -> bool:
    zip_path = os.path.join(BACKUPS_DIR, mod_name, backup_file)
    if not os.path.exists(zip_path):
        return False
    target = mod_path(mod_name)
    temp   = target + "_rb_tmp"
    try:
        # SCHRITT 1 – Backup nach temp entpacken und Integrität prüfen
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(temp)

        # SCHRITT 2 – Erst bei erfolgreichem Entpacken Original löschen
        if os.path.exists(target):
            shutil.rmtree(target)

        # SCHRITT 3 – Entpackte Daten an Zielort verschieben
        items = os.listdir(temp)
        if len(items) == 1 and os.path.isdir(os.path.join(temp, items[0])):
            shutil.move(os.path.join(temp, items[0]), target)
        else:
            os.makedirs(target, exist_ok=True)
            for item in items:
                shutil.move(os.path.join(temp, item), os.path.join(target, item))

        write_log("ROLLBACK", f"{mod_name} → {backup_file}")
        return True
    except Exception as e:
        write_log("ERROR", f"Rollback failed for {mod_name}: {e}")
        return False
    finally:
        shutil.rmtree(temp, ignore_errors=True)

# ============================================================
# DOWNLOAD  –  FIX #7: ZeroDivisionError abfangen
# ============================================================

def download_asset(asset: Dict, gui=None) -> str:
    mods_dir = get_mods_folder()
    os.makedirs(mods_dir, exist_ok=True)
    temp_zip = os.path.join(mods_dir, f"_temp_{asset['name']}")
    retries  = settings.get("download_retries", 3)

    need_mb = asset["size_bytes"] / (1024 * 1024) * 1.5
    have_mb = free_space_mb(mods_dir)
    if have_mb < need_mb:
        raise IOError(translate("disk_error",
                                need=round(need_mb, 1), have=round(have_mb, 1)))

    log("DOWN", f"Downloading {asset['name']} ({asset['size_kb']} KB)", gui)
    if gui:
        gui.schedule_file_progress(0)
        gui.schedule_eta("")

    for attempt in range(1, retries + 1):
        try:
            with requests.get(asset["url"], headers=get_headers(),
                              stream=True, timeout=DOWNLOAD_TIMEOUT) as r:
                r.raise_for_status()
                total      = int(r.headers.get("content-length", 0))
                done       = 0
                start_time = time.time()
                with open(temp_zip, "wb") as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        if not chunk:
                            continue
                        f.write(chunk)
                        done += len(chunk)
                        if gui:
                            if total:
                                gui.schedule_file_progress((done / total) * 100)
                            elapsed = time.time() - start_time
                            # FIX #7 – speed_bps kann 0 sein bei Stagnation
                            if elapsed > 0.5 and total:
                                speed_bps = done / elapsed
                                if speed_bps > 0:
                                    remaining = (total - done) / speed_bps
                                    speed_kb  = round(speed_bps / 1024, 1)
                                    gui.schedule_eta(
                                        translate("eta_label",
                                                  s=int(remaining), speed=speed_kb))
            break
        except Exception as e:
            if attempt < retries:
                log("WARN", f"Attempt {attempt} failed: {e}. Retrying...", gui)
                time.sleep(2 ** attempt)
            else:
                raise

    if gui:
        gui.schedule_file_progress(100)
        gui.schedule_eta(translate("eta_done"))

    if settings.get("verify_sha256", True):
        digest = asset.get("digest", "")
        if digest.startswith("sha256:"):
            expected = digest[7:]
            actual   = sha256_of(temp_zip)
            if actual != expected:
                os.remove(temp_zip)
                raise ValueError(translate("sha_error", name=asset["name"]))
            log("OK", f"SHA256 verified: {asset['name']}", gui)

    return temp_zip


# FIX #6 – finally garantiert Bereinigung des temp-Ordners
def extract_zip(zip_path: str, mod_name: str, gui=None):
    target = mod_path(mod_name)
    temp   = zip_path + "_tmp"
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(temp)
        items = os.listdir(temp)
        if len(items) == 1 and os.path.isdir(os.path.join(temp, items[0])):
            shutil.move(os.path.join(temp, items[0]), target)
        else:
            os.makedirs(target, exist_ok=True)
            for item in items:
                shutil.move(os.path.join(temp, item), os.path.join(target, item))
        log("UNZIP", f"Extracted: {mod_name}", gui)
    finally:
        # FIX #6 – temp-Ordner wird IMMER gelöscht, auch bei Fehlern
        shutil.rmtree(temp, ignore_errors=True)


def install_mod(asset: Dict, cache: Dict, release_tag: str, gui=None) -> bool:
    mod_name = asset["mod_name"]
    gh_ts    = format_time(asset["updated_at"])
    local_ts = format_time(
        cache.get("assets", {}).get(mod_name, {}).get("updated_at", "")) or "never"
    t = theme_config()

    if gui:
        gui.schedule_mod_status(mod_name, gh_ts, local_ts, "Updating...", t["update"])

    temp_zip = None
    try:
        temp_zip = download_asset(asset, gui)
        if gui:
            gui.schedule_mod_status(mod_name, gh_ts, local_ts,
                                    translate("backing_up"), t["warn"])
        create_backup(mod_name, release_tag)
        p = mod_path(mod_name)
        if os.path.exists(p):
            log("DEL", f"Removing old: {mod_name}", gui)
            shutil.rmtree(p)
        extract_zip(temp_zip, mod_name, gui)
        if "assets" not in cache:
            cache["assets"] = {}
        cache["assets"][mod_name] = {
            "updated_at":     asset["updated_at"],
            "release_tag":    release_tag,
            "last_installed": utc_now_iso(),
        }
        save_cache(cache)
        if gui:
            gui.schedule_mod_status(mod_name, gh_ts,
                                    format_time(asset["updated_at"]),
                                    "✓ OK", t["accent"])
        log("OK", f"{mod_name} updated.", gui)
        return True
    except Exception as exc:
        log("ERROR", f"{mod_name}: {exc}", gui)
        if gui:
            gui.schedule_mod_status(mod_name, gh_ts, local_ts, "Error", t["error"])
        return False
    finally:
        if temp_zip and os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except Exception:
                pass

# ============================================================
# UPDATE RUNNER
# ============================================================

def run_update(assets: List[Dict], to_update: List[Dict],
               cache: Dict, release_tag: str, gui):
    t = theme_config()
    log("CHECK", f"Release: {release_tag}", gui)
    start_tray_animation()

    for a in assets:
        mod      = a["mod_name"]
        gh_ts    = format_time(a["updated_at"])
        local    = cache.get("assets", {}).get(mod, {}).get("updated_at", "")
        local_ts = format_time(local) if local else "never"
        is_new   = needs_update(cache, mod, a["updated_at"])
        gui.schedule_mod_status(
            mod, gh_ts, local_ts,
            translate("pending") if is_new else translate("up2date"),
            t["update"] if is_new else t["accent"])

    if not to_update:
        stop_tray_animation()
        gui.schedule_overall_status(translate("up_to_date"), t["accent"])
        gui.schedule_overall_progress(100)
        gui.schedule_enable_close()
        return

    gui.schedule_overall_status(translate("updating", n=len(to_update)), t["info"])
    gui.schedule_overall_progress(0, maximum=len(to_update))
    installed = 0

    for i, asset in enumerate(to_update):
        if install_mod(asset, cache, release_tag, gui):
            installed += 1
        gui.schedule_overall_progress(i + 1)

    stop_tray_animation()

    if installed == len(to_update):
        gui.schedule_overall_status(
            translate("updated_ok",
                      ok=installed, total=len(to_update), tag=release_tag),
            t["accent"])
        notify(translate("notif_title"), translate("notif_done", ok=installed))
    else:
        gui.schedule_overall_status(
            translate("updated_warn", ok=installed, total=len(to_update)), t["warn"])

    gui.schedule_file_progress(100)
    gui.schedule_eta(translate("eta_done"))
    gui.schedule_enable_close()

    if tray_icon:
        tray_icon.title = f"COI Updater – {datetime.now().strftime('%H:%M')}"

# ============================================================
# DASHBOARD
# ============================================================

class DashboardWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        t = theme_config()
        self.title(translate("dashboard"))
        self.geometry("720x380")
        self.configure(bg=t["bg"])
        self._build(t)

    def _build(self, t):
        cache         = load_cache()
        total, last_v = get_stats(cache)

        stats_frame = tk.Frame(self, bg=t["bg2"], pady=6)
        stats_frame.pack(fill="x")
        tk.Label(stats_frame, text=translate("stats_total", n=total),
                 bg=t["bg2"], fg=t["accent"],
                 font=(FONT_UI, fs(), "bold")).pack(side="left", padx=20)
        tk.Label(stats_frame, text=translate("stats_last", t=last_v),
                 bg=t["bg2"], fg=t["fg2"],
                 font=(FONT_UI, fs())).pack(side="left", padx=20)

        remaining = last_rate_info.get("remaining", "?")
        reset_ts  = last_rate_info.get("reset", "")
        try:
            reset_str = datetime.fromtimestamp(int(reset_ts)).strftime("%H:%M") \
                if reset_ts else "-"
        except Exception:
            reset_str = "-"
        tk.Label(stats_frame,
                 text=translate("rate_limit", n=remaining, t=reset_str),
                 bg=t["bg2"], fg=t["info"],
                 font=(FONT_UI, fs())).pack(side="right", padx=20)

        path_frame = tk.Frame(self, bg=t["bg"], pady=2)
        path_frame.pack(fill="x", padx=14)
        tk.Label(path_frame, text=translate("data_path_lbl"),
                 bg=t["bg"], fg=t["skip"],
                 font=(FONT_UI, fs(-2))).pack(side="left")
        tk.Label(path_frame, text=_APP_DATA,
                 bg=t["bg"], fg=t["skip"],
                 font=("Consolas", fs(-2))).pack(side="left", padx=4)

        cols   = [translate("dash_col_mod"), translate("dash_col_ver"),
                  translate("dash_col_installed"), translate("dash_col_size"),
                  translate("dash_col_backups")]
        widths = [28, 14, 18, 10, 8]

        header = tk.Frame(self, bg=t["bg2"])
        header.pack(fill="x", padx=14, pady=(8, 2))
        for col, w in zip(cols, widths):
            tk.Label(header, text=col, bg=t["bg2"], fg=t["accent"],
                     font=(FONT_UI, fs(), "bold"), width=w, anchor="w").pack(side="left")

        scroll_frame = tk.Frame(self, bg=t["bg"])
        scroll_frame.pack(fill="both", expand=True, padx=14)

        allowed = settings.get("allowed_mods", DEFAULT_SETTINGS["allowed_mods"])
        assets  = cache.get("assets", {})
        for mod in allowed:
            entry   = assets.get(mod, {})
            version = entry.get("release_tag", "-")
            inst    = format_time(entry["last_installed"]) \
                if entry.get("last_installed") else translate("not_installed")
            size_mb = f"{folder_size_mb(mod_path(mod))} MB" if is_installed(mod) else "-"
            backups = str(len(get_backups(mod)))
            color   = t["fg"] if is_installed(mod) else t["skip"]
            row = tk.Frame(scroll_frame, bg=t["bg"])
            row.pack(fill="x", pady=1)
            for val, w in zip([mod, version, inst, size_mb, backups], widths):
                tk.Label(row, text=val, bg=t["bg"], fg=color,
                         font=("Consolas", fs(-1)), width=w, anchor="w").pack(side="left")

        tk.Button(self, text=translate("refresh"),
                  command=lambda: [self.destroy(), DashboardWindow(self.master)],
                  bg=t["btn_bg"], fg=t["fg"],
                  relief="flat", padx=12, pady=4).pack(pady=8)

# ============================================================
# RELEASE NOTES
# ============================================================

class ReleaseNotesWindow(tk.Toplevel):
    def __init__(self, parent, release: Dict, cache: Dict = None):
        super().__init__(parent)
        t   = theme_config()
        tag = release.get("tag_name", "?")
        self.title(translate("release_notes_title", tag=tag))
        self.geometry("680x460")
        self.configure(bg=t["bg"])
        body = release.get("body", "").strip() or translate("no_release_notes")
        if cache:
            assets    = get_filtered_assets(release)
            to_update = [a["mod_name"] for a in assets
                         if needs_update(cache, a["mod_name"], a["updated_at"])]
            if to_update:
                body = "── Changes for: " + ", ".join(to_update) + " ──\n\n" + body
        box = scrolledtext.ScrolledText(
            self, bg=t["logbg"], fg=t["fg2"],
            font=("Consolas", fs()), wrap="word")
        box.pack(fill="both", expand=True, padx=12, pady=12)
        box.insert("end", body)
        box.configure(state="disabled")

# ============================================================
# ROLLBACK
# ============================================================

class RollbackWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        t = theme_config()
        self.title(translate("rollback_title"))
        self.configure(bg=t["bg"])
        self.resizable(False, False)
        self.grab_set()
        self._build(t)

    def _build(self, t):
        tk.Label(self, text=translate("rollback_select"),
                 bg=t["bg"], fg=t["fg"],
                 font=(FONT_UI, fs(), "bold")).pack(padx=20, pady=(14, 6))
        allowed = settings.get("allowed_mods", DEFAULT_SETTINGS["allowed_mods"])
        frame   = tk.Frame(self, bg=t["bg"])
        frame.pack(padx=20, pady=6)
        self._mod_var    = tk.StringVar(value=allowed[0] if allowed else "")
        self._backup_var = tk.StringVar()
        tk.Label(frame, text="Mod:", bg=t["bg"], fg=t["fg2"]).grid(row=0, column=0, sticky="w")
        mod_cb = ttk.Combobox(frame, textvariable=self._mod_var,
                              values=allowed, state="readonly", width=34)
        mod_cb.grid(row=0, column=1, padx=8, pady=4)
        mod_cb.bind("<<ComboboxSelected>>", self._refresh_backups)
        tk.Label(frame, text="Backup:", bg=t["bg"], fg=t["fg2"]).grid(row=1, column=0, sticky="w")
        self._backup_cb = ttk.Combobox(frame, textvariable=self._backup_var,
                                       state="readonly", width=34)
        self._backup_cb.grid(row=1, column=1, padx=8, pady=4)
        self._refresh_backups()
        bf = tk.Frame(self, bg=t["bg"])
        bf.pack(pady=12)
        tk.Button(bf, text="Rollback", command=self._do_rollback,
                  bg=t["accent"], fg="#000000",
                  font=(FONT_UI, fs(), "bold"),
                  relief="flat", padx=18, pady=4).pack(side="left", padx=6)
        tk.Button(bf, text=translate("cancel"), command=self.destroy,
                  bg=t["btn_bg"], fg=t["fg"],
                  relief="flat", padx=18, pady=4).pack(side="left", padx=6)

    def _refresh_backups(self, *_):
        backs = get_backups(self._mod_var.get())
        self._backup_cb["values"] = backs
        self._backup_var.set(backs[0] if backs else translate("no_backups"))

    def _do_rollback(self):
        mod    = self._mod_var.get()
        backup = self._backup_var.get()
        if backup == translate("no_backups") or not backup:
            return
        ok = rollback_mod(mod, backup)
        messagebox.showinfo(translate("rollback_title"),
                            translate("rollback_ok") if ok else translate("rollback_fail"),
                            parent=self)
        self.destroy()

# ============================================================
# LOG VIEWER
# ============================================================

class LogViewer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        t = theme_config()
        self.title(translate("view_log"))
        self.geometry("760x480")
        self.configure(bg=t["bg"])
        self._build(t)
        self._load()

    def _build(self, t):
        ctrl = tk.Frame(self, bg=t["bg"])
        ctrl.pack(fill="x", padx=10, pady=6)
        tk.Label(ctrl, text=translate("filter_lbl"),
                 bg=t["bg"], fg=t["fg2"],
                 font=(FONT_UI, fs())).pack(side="left")
        self._filter = ttk.Combobox(ctrl, state="readonly", width=12,
                                    values=["ALL", "OK", "UPDATE", "ERROR",
                                            "WARN", "DOWN", "CHECK", "BACKUP", "ROLLBACK"])
        self._filter.set("ALL")
        self._filter.pack(side="left", padx=6)
        self._filter.bind("<<ComboboxSelected>>", lambda e: self._load())
        tk.Button(ctrl, text=translate("refresh"), command=self._load,
                  bg=t["btn_bg"], fg=t["fg"],
                  font=(FONT_UI, fs()),
                  relief="flat", padx=8).pack(side="left")
        tk.Label(ctrl, text=LOG_FILE,
                 bg=t["bg"], fg=t["skip"],
                 font=("Consolas", fs(-2))).pack(side="right", padx=10)

        self.box = scrolledtext.ScrolledText(
            self, bg=t["logbg"], fg=t["fg2"],
            font=("Consolas", fs(-1)), state="disabled")
        self.box.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        for tag, color in [
            ("OK", t["accent"]), ("UPDATE", t["update"]),
            ("ERROR", t["error"]), ("WARN", t["warn"]),
            ("DOWN", t["info"]),  ("CHECK", t["info"]),
            ("BACKUP", t["info"]), ("ROLLBACK", t["warn"]),
            ("START", t["accent"]),
        ]:
            self.box.tag_config(tag, foreground=color)

        self._stats_var = tk.StringVar()
        tk.Label(self, textvariable=self._stats_var,
                 bg=t["bg2"], fg=t["skip"],
                 font=(FONT_UI, fs(-1))).pack(fill="x", padx=10, pady=(0, 6))

    def _load(self):
        self.box.configure(state="normal")
        self.box.delete("1.0", "end")
        sel = self._filter.get()
        if not os.path.exists(LOG_FILE):
            self.box.insert("end", translate("no_log"))
            self.box.configure(state="disabled")
            return
        lines_shown = 0
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                matched_tag = "OK"
                for tag in ["OK", "UPDATE", "ERROR", "WARN", "DOWN",
                            "CHECK", "BACKUP", "ROLLBACK", "START"]:
                    if f"[{tag}" in line:
                        matched_tag = tag
                        break
                if sel != "ALL" and f"[{sel}" not in line:
                    continue
                start = self.box.index("end-1c")
                self.box.insert("end", line)
                self.box.tag_add(matched_tag, start, self.box.index("end-1c"))
                lines_shown += 1
        cache        = load_cache()
        total, last  = get_stats(cache)
        self._stats_var.set(
            f"  {translate('stats_total', n=total)}"
            f"   {translate('stats_last', t=last)}"
            f"   |   {lines_shown} lines shown")
        self.box.see("end")
        self.box.configure(state="disabled")

# ============================================================
# SETTINGS
# ============================================================

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        t = theme_config()
        self.title(translate("settings"))
        self.configure(bg=t["bg"])
        self.resizable(False, False)
        self.grab_set()
        self._build(t)

    def _build(self, t):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self._folder_var      = tk.StringVar(value=settings.get("mods_folder", ""))
        self._interval_var    = tk.IntVar(value=settings.get("check_interval", 3))
        self._token_var       = tk.StringVar(value=settings.get("github_token", ""))
        self._startup_var     = tk.BooleanVar(value=is_startup_enabled())
        self._notif_var       = tk.BooleanVar(value=settings.get("notifications", True))
        self._theme_var       = tk.StringVar(value=settings.get("theme", "dark"))
        self._lang_var        = tk.StringVar(value=settings.get("language") or "auto")
        self._font_size_var   = tk.IntVar(value=settings.get("font_size", 9))
        self._backups_var     = tk.IntVar(value=settings.get("max_backups", 3))
        self._verify_var      = tk.BooleanVar(value=settings.get("verify_sha256", True))
        self._retry_var       = tk.IntVar(value=settings.get("download_retries", 3))
        self._maint_en_var    = tk.BooleanVar(value=settings.get("maintenance_enabled", False))
        self._maint_start_var = tk.StringVar(value=settings.get("maintenance_start", "02:00"))
        self._maint_end_var   = tk.StringVar(value=settings.get("maintenance_end",   "05:00"))

        # ── General ──
        gen = tk.Frame(nb, bg=t["bg"], padx=15, pady=10)
        nb.add(gen, text=translate("tab_general"))
        for r, (lbl, w) in enumerate([
            (translate("folder_lbl"),   self._make_folder_row(gen)),
            (translate("interval_lbl"), tk.Spinbox(gen, from_=1, to=24,
                                                   textvariable=self._interval_var,
                                                   width=6, bg=t["entry_bg"], fg=t["fg"])),
            (translate("token_lbl"),    tk.Entry(gen, textvariable=self._token_var,
                                                 width=32, show="*",
                                                 bg=t["entry_bg"], fg=t["fg"])),
            (translate("startup_lbl"),  tk.Checkbutton(gen, variable=self._startup_var,
                                                       bg=t["bg"], fg=t["fg"],
                                                       selectcolor=t["entry_bg"])),
            (translate("notif_lbl"),    tk.Checkbutton(gen, variable=self._notif_var,
                                                       bg=t["bg"], fg=t["fg"],
                                                       selectcolor=t["entry_bg"])),
        ]):
            tk.Label(gen, text=lbl, bg=t["bg"], fg=t["fg2"],
                     font=(FONT_UI, fs()), width=28, anchor="w"
                     ).grid(row=r, column=0, sticky="w", pady=5)
            w.grid(row=r, column=1, sticky="w", padx=6)

        tk.Label(gen,
                 text=f"  Data: {_APP_DATA}",
                 bg=t["bg"], fg=t["skip"],
                 font=("Consolas", fs(-2))
                 ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # ── Appearance ──
        app_tab = tk.Frame(nb, bg=t["bg"], padx=15, pady=10)
        nb.add(app_tab, text=translate("tab_appearance"))
        for r, (lbl, var, opts) in enumerate([
            (translate("theme_lbl"), self._theme_var, ["dark", "light"]),
            (translate("lang_lbl"),  self._lang_var,  ["auto", "en", "de"]),
        ]):
            tk.Label(app_tab, text=lbl, bg=t["bg"], fg=t["fg2"],
                     font=(FONT_UI, fs()), width=28, anchor="w"
                     ).grid(row=r, column=0, sticky="w", pady=5)
            ttk.Combobox(app_tab, textvariable=var, values=opts,
                         state="readonly", width=10
                         ).grid(row=r, column=1, sticky="w", padx=6)

        tk.Label(app_tab,
                 text=f"  ← \"{translate('lang_auto')}\" = Windows language",
                 bg=t["bg"], fg=t["skip"],
                 font=(FONT_UI, fs(-1))).grid(row=1, column=2, sticky="w")

        self._font_preview = tk.StringVar(value=f"{self._font_size_var.get()} pt")
        tk.Label(app_tab, text=translate("font_size_lbl"),
                 bg=t["bg"], fg=t["fg2"], font=(FONT_UI, fs()), width=28, anchor="w"
                 ).grid(row=2, column=0, sticky="w", pady=5)
        slider_frame = tk.Frame(app_tab, bg=t["bg"])
        slider_frame.grid(row=2, column=1, sticky="w", padx=6)
        tk.Scale(
            slider_frame, from_=7, to=14, orient="horizontal",
            variable=self._font_size_var,
            command=lambda v: self._font_preview.set(f"{int(float(v))} pt"),
            bg=t["bg"], fg=t["fg2"],
            troughcolor=t["entry_bg"], highlightthickness=0,
            length=120, showvalue=False
        ).pack(side="left")
        tk.Label(slider_frame, textvariable=self._font_preview,
                 bg=t["bg"], fg=t["accent"],
                 font=(FONT_UI, fs(), "bold"), width=5).pack(side="left", padx=4)

        # ── Mods ──
        mods_tab = tk.Frame(nb, bg=t["bg"], padx=15, pady=10)
        nb.add(mods_tab, text=translate("tab_mods"))
        active = set(settings.get("allowed_mods", DEFAULT_SETTINGS["allowed_mods"]))
        self._mod_vars: Dict = {}
        for i, mod in enumerate(DEFAULT_SETTINGS["allowed_mods"]):
            v = tk.BooleanVar(value=(mod in active))
            self._mod_vars[mod] = v
            tk.Checkbutton(mods_tab, text=mod, variable=v,
                           bg=t["bg"], fg=t["fg"], font=(FONT_UI, fs()),
                           selectcolor=t["entry_bg"]).grid(row=i, column=0, sticky="w", pady=2)

        # ── Advanced ──
        adv = tk.Frame(nb, bg=t["bg"], padx=15, pady=10)
        nb.add(adv, text=translate("tab_advanced"))
        for r, (lbl, w) in enumerate([
            (translate("backups_lbl"), tk.Spinbox(adv, from_=1, to=10,
                                                  textvariable=self._backups_var,
                                                  width=6, bg=t["entry_bg"], fg=t["fg"])),
            (translate("verify_lbl"),  tk.Checkbutton(adv, variable=self._verify_var,
                                                      bg=t["bg"], fg=t["fg"],
                                                      selectcolor=t["entry_bg"])),
            (translate("retry_lbl"),   tk.Spinbox(adv, from_=1, to=10,
                                                  textvariable=self._retry_var,
                                                  width=6, bg=t["entry_bg"], fg=t["fg"])),
        ]):
            tk.Label(adv, text=lbl, bg=t["bg"], fg=t["fg2"],
                     font=(FONT_UI, fs()), width=28, anchor="w"
                     ).grid(row=r, column=0, sticky="w", pady=5)
            w.grid(row=r, column=1, sticky="w", padx=6)

        # ── Maintenance ──
        maint = tk.Frame(nb, bg=t["bg"], padx=15, pady=10)
        nb.add(maint, text=translate("tab_maintenance"))
        for r, (lbl, w) in enumerate([
            (translate("maint_enabled_lbl"),
             tk.Checkbutton(maint, variable=self._maint_en_var,
                            bg=t["bg"], fg=t["fg"], selectcolor=t["entry_bg"])),
            (translate("maint_start_lbl"),
             tk.Entry(maint, textvariable=self._maint_start_var,
                      width=8, bg=t["entry_bg"], fg=t["fg"])),
            (translate("maint_end_lbl"),
             tk.Entry(maint, textvariable=self._maint_end_var,
                      width=8, bg=t["entry_bg"], fg=t["fg"])),
        ]):
            tk.Label(maint, text=lbl, bg=t["bg"], fg=t["fg2"],
                     font=(FONT_UI, fs()), width=32, anchor="w"
                     ).grid(row=r, column=0, sticky="w", pady=6)
            w.grid(row=r, column=1, sticky="w", padx=6)
        tk.Label(maint,
                 text="  Format: HH:MM (24h)  |  Overnight supported (e.g. 22:00–04:00)",
                 bg=t["bg"], fg=t["skip"],
                 font=(FONT_UI, fs(-1))
                 ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 0))

        bf = tk.Frame(self, bg=t["bg"])
        bf.pack(pady=10)
        tk.Button(bf, text=translate("save"), command=self._save,
                  bg=t["accent"], fg="#000000",
                  font=(FONT_UI, fs(), "bold"),
                  relief="flat", padx=18, pady=4).pack(side="left", padx=6)
        tk.Button(bf, text=translate("cancel"), command=self.destroy,
                  bg=t["btn_bg"], fg=t["fg"],
                  font=(FONT_UI, fs()),
                  relief="flat", padx=18, pady=4).pack(side="left", padx=6)

    def _make_folder_row(self, parent) -> tk.Frame:
        t = theme_config()
        f = tk.Frame(parent, bg=t["bg"])
        tk.Entry(f, textvariable=self._folder_var, width=26,
                 bg=t["entry_bg"], fg=t["fg"]).pack(side="left")
        tk.Button(f, text=translate("browse"),
                  command=lambda: self._folder_var.set(
                      filedialog.askdirectory() or self._folder_var.get()),
                  bg=t["btn_bg"], fg=t["fg"],
                  relief="flat", padx=6).pack(side="left", padx=4)
        return f

    def _save(self):
        settings["mods_folder"]         = self._folder_var.get().strip()
        settings["check_interval"]      = self._interval_var.get()
        settings["github_token"]        = self._token_var.get().strip()
        settings["notifications"]       = self._notif_var.get()
        settings["theme"]               = self._theme_var.get()
        settings["font_size"]           = self._font_size_var.get()
        settings["max_backups"]         = self._backups_var.get()
        settings["verify_sha256"]       = self._verify_var.get()
        settings["download_retries"]    = self._retry_var.get()
        settings["allowed_mods"]        = [m for m, v in self._mod_vars.items() if v.get()]
        settings["maintenance_enabled"] = self._maint_en_var.get()
        settings["maintenance_start"]   = self._maint_start_var.get().strip()
        settings["maintenance_end"]     = self._maint_end_var.get().strip()
        lang_val = self._lang_var.get()
        settings["language"] = None if lang_val == "auto" else lang_val
        set_startup(self._startup_var.get())
        save_settings()
        self.destroy()

# ============================================================
# MAIN GUI
# ============================================================

class COIUpdaterGUI(tk.Tk):
    def __init__(self, assets: List[Dict], to_update: List[Dict],
                 cache: Dict, release_tag: str, release: Dict):
        super().__init__()
        self.assets        = assets
        self.to_update     = to_update
        self.cache         = cache
        self.release_tag   = release_tag
        self.release       = release
        self.close_enabled = False

        self.title(translate("title"))
        self.configure(bg=theme_config()["bg"])
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._minimize)

        if os.path.exists(ICON_FILE):
            try:
                self.iconbitmap(ICON_FILE)
            except Exception:
                pass

        self._build_ui()
        threading.Thread(
            target=run_update,
            args=(assets, to_update, cache, release_tag, self),
            daemon=True
        ).start()
        self._tick_countdown()

    def _build_ui(self):
        t = theme_config()

        header = tk.Frame(self, bg=t["bg2"], pady=10)
        header.pack(fill="x")
        tk.Label(header, text=translate("title"),
                 font=(FONT_UI, fs(4), "bold"),
                 bg=t["bg2"], fg=t["accent"]).pack()
        tk.Label(header,
                 text=f"{translate('by')}  •  {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                 font=(FONT_UI, fs(-1)), bg=t["bg2"], fg=t["skip"]).pack()

        self.status_var = tk.StringVar(value=translate("initializing"))
        self.status_label = tk.Label(
            self, textvariable=self.status_var,
            font=(FONT_UI, fs(1), "bold"),
            bg=t["bg"], fg=t["accent"], pady=6)
        self.status_label.pack()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("green.Horizontal.TProgressbar",
                        troughcolor="#333333", background=t["accent"], thickness=14)

        tk.Label(self, text=translate("overall_prog"),
                 font=(FONT_UI, fs(-1)),
                 bg=t["bg"], fg=t["skip"]).pack(anchor="w", padx=20)
        self.overall_bar = ttk.Progressbar(
            self, length=580, mode="determinate",
            style="green.Horizontal.TProgressbar")
        self.overall_bar.pack(padx=20, pady=(0, 8))

        table_frame = tk.Frame(self, bg=t["bg"])
        table_frame.pack(padx=20, pady=(0, 6), fill="x")
        for col, h in enumerate([translate("col_mod"), translate("col_github"),
                                  translate("col_local"), translate("col_status")]):
            tk.Label(table_frame, text=h, bg=t["bg"], fg=t["accent"],
                     font=(FONT_UI, fs(), "bold"), width=22, anchor="w"
                     ).grid(row=0, column=col, sticky="w")

        self.status_labels: Dict = {}
        for idx, a in enumerate(self.assets):
            mod = a["mod_name"]
            tk.Label(table_frame, text=mod, bg=t["bg"], fg=t["fg"],
                     font=(FONT_UI, fs()), width=22, anchor="w"
                     ).grid(row=idx+1, column=0, sticky="w")
            labels = [
                tk.Label(table_frame, text="-", bg=t["bg"], fg=t["fg2"],
                         font=("Consolas", fs(-1)), width=18, anchor="w"),
                tk.Label(table_frame, text="-", bg=t["bg"], fg=t["fg2"],
                         font=("Consolas", fs(-1)), width=18, anchor="w"),
                tk.Label(table_frame, text="-", bg=t["bg"], fg=t["fg2"],
                         font=("Consolas", fs(-1)), width=14, anchor="w"),
            ]
            for col_idx, lbl in enumerate(labels):
                lbl.grid(row=idx+1, column=col_idx+1, sticky="w")
            self.status_labels[mod] = labels

        progress_frame = tk.Frame(self, bg=t["bg"])
        progress_frame.pack(fill="x", padx=20)
        tk.Label(progress_frame, text=translate("file_prog"),
                 font=(FONT_UI, fs(-1)),
                 bg=t["bg"], fg=t["skip"]).pack(side="left")
        self.eta_var = tk.StringVar(value="")
        tk.Label(progress_frame, textvariable=self.eta_var,
                 font=(FONT_UI, fs(-1), "bold"),
                 bg=t["bg"], fg=t["info"]).pack(side="right")

        self.file_bar = ttk.Progressbar(
            self, length=580, mode="determinate",
            style="green.Horizontal.TProgressbar")
        self.file_bar.pack(padx=20, pady=(2, 8))

        tk.Label(self, text=translate("log_label"),
                 font=(FONT_UI, fs(), "bold"),
                 bg=t["bg"], fg=t["accent"]).pack(anchor="w", padx=20)
        self.log_box = scrolledtext.ScrolledText(
            self, width=72, height=7,
            bg=t["logbg"], fg=t["fg2"],
            font=("Consolas", fs(-1)), state="disabled", relief="flat")
        self.log_box.pack(padx=20, pady=(0, 8))
        for tag, color in [
            ("OK", t["accent"]), ("UPDATE", t["update"]),
            ("ERROR", t["error"]), ("INFO", t["info"]),
            ("WARN", t["warn"]),  ("DOWN", t["info"]),
            ("UNZIP", t["info"]), ("DEL", t["warn"]),
            ("CHECK", t["info"]), ("SKIP", t["skip"]),
            ("BACKUP", t["info"]), ("START", t["accent"]),
        ]:
            self.log_box.tag_config(tag, foreground=color)

        self.countdown_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.countdown_var,
                 font=(FONT_UI, fs(-1)), bg=t["bg"], fg=t["skip"]).pack()

        btn_frame = tk.Frame(self, bg=t["bg"])
        btn_frame.pack(pady=(4, 2))

        self.close_btn = tk.Button(
            btn_frame, text=translate("close_tray"),
            font=(FONT_UI, fs(), "bold"), bg=t["btn_bg"], fg=t["fg"],
            relief="flat", padx=14, pady=5, cursor="hand2",
            command=self._minimize, state="disabled")
        self.close_btn.pack(side="left", padx=5)
        Tooltip(self.close_btn, translate("tt_close_tray"))

        log_btn = tk.Button(btn_frame, text=translate("view_log"),
                            font=(FONT_UI, fs()), bg=t["btn_bg"], fg=t["info"],
                            relief="flat", padx=10, pady=5, cursor="hand2",
                            command=lambda: LogViewer(self))
        log_btn.pack(side="left", padx=5)
        Tooltip(log_btn, translate("tt_view_log"))

        dash_btn = tk.Button(btn_frame, text=translate("dashboard"),
                             font=(FONT_UI, fs()), bg=t["btn_bg"], fg=t["accent"],
                             relief="flat", padx=10, pady=5, cursor="hand2",
                             command=lambda: DashboardWindow(self))
        dash_btn.pack(side="left", padx=5)
        Tooltip(dash_btn, translate("tt_dashboard"))

        rn_btn = tk.Button(btn_frame, text=translate("release_notes"),
                           font=(FONT_UI, fs()), bg=t["btn_bg"], fg=t["update"],
                           relief="flat", padx=10, pady=5, cursor="hand2",
                           command=lambda: ReleaseNotesWindow(self, self.release, self.cache))
        rn_btn.pack(side="left", padx=5)
        Tooltip(rn_btn, translate("tt_release_notes"))

        btn_frame2 = tk.Frame(self, bg=t["bg"])
        btn_frame2.pack(pady=(2, 10))

        rb_btn = tk.Button(btn_frame2, text=translate("rollback"),
                           font=(FONT_UI, fs()), bg=t["btn_bg"], fg=t["warn"],
                           relief="flat", padx=10, pady=5, cursor="hand2",
                           command=lambda: RollbackWindow(self))
        rb_btn.pack(side="left", padx=5)
        Tooltip(rb_btn, translate("tt_rollback"))

        set_btn = tk.Button(btn_frame2, text=translate("settings"),
                            font=(FONT_UI, fs()), bg=t["btn_bg"], fg=t["fg2"],
                            relief="flat", padx=10, pady=5, cursor="hand2",
                            command=lambda: SettingsWindow(self))
        set_btn.pack(side="left", padx=5)
        Tooltip(set_btn, translate("tt_settings"))

        self.exit_btn = tk.Button(
            btn_frame2, text=translate("exit"),
            font=(FONT_UI, fs()), bg="#2a0000", fg=t["error"],
            relief="flat", padx=14, pady=5, cursor="hand2",
            command=self._exit_app, state="disabled")
        self.exit_btn.pack(side="left", padx=5)
        Tooltip(self.exit_btn, translate("tt_exit"))

    def schedule_log_message(self, tag: str, entry: str):
        self.after(0, self._log_message, tag, entry)

    def schedule_mod_status(self, mod: str, gh_ts: str, local_ts: str,
                             status: str, color: str):
        self.after(0, self._set_mod_status, mod, gh_ts, local_ts, status, color)

    def schedule_overall_status(self, text: str, color: str):
        self.after(0, self._set_overall_status, text, color)

    def schedule_file_progress(self, value: float):
        self.after(0, lambda: self.file_bar.configure(value=value))

    def schedule_overall_progress(self, value: float, maximum: Optional[float] = None):
        def _update():
            if maximum is not None:
                self.overall_bar.configure(maximum=maximum)
            self.overall_bar.configure(value=value)
        self.after(0, _update)

    def schedule_eta(self, text: str):
        self.after(0, lambda: self.eta_var.set(text))

    def schedule_enable_close(self):
        self.after(0, self._enable_close)

    def _log_message(self, tag: str, entry: str):
        self.log_box.configure(state="normal")
        start = self.log_box.index("end-1c")
        self.log_box.insert("end", entry + "\n")
        end = self.log_box.index("end-1c")
        self.log_box.tag_add(tag, start, end)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_mod_status(self, mod: str, gh_ts: str, local_ts: str,
                         status: str, color: str):
        if mod in self.status_labels:
            self.status_labels[mod][0].config(text=gh_ts)
            self.status_labels[mod][1].config(text=local_ts)
            self.status_labels[mod][2].config(text=status, fg=color)

    def _set_overall_status(self, text: str, color: str):
        self.status_var.set(text)
        self.status_label.config(fg=color)

    def _enable_close(self):
        self.close_enabled = True
        self.close_btn.configure(state="normal")
        self.exit_btn.configure(state="normal")

    def _tick_countdown(self):
        if next_check_time:
            cd = format_countdown(next_check_time)
            self.countdown_var.set(translate("next_check", t=cd) if cd else "")
        self.after(1000, self._tick_countdown)

    # FIX #1 – quit() + destroy() statt withdraw() um Zombie-Mainloop zu verhindern
    def _minimize(self):
        if self.close_enabled:
            global gui_window
            gui_window = None
            self.quit()
            self.destroy()

    def _exit_app(self):
        stop_event.set()
        stop_tray_animation()
        if tray_icon:
            tray_icon.stop()
        self.destroy()
        sys.exit(0)

# ============================================================
# BACKGROUND CHECKER
# ============================================================

def check_for_updates(silent: bool = False):
    global gui_window, next_check_time
    write_log("CHECK", f"Checking for updates (silent={silent})")

    if not is_in_maintenance_window():
        nxt = next_maintenance_start()
        write_log("INFO", translate("maint_blocked", start=nxt))
        if tray_icon:
            tray_icon.title = f"COI Updater – {translate('maint_blocked', start=nxt)}"
        return

    if tray_icon:
        tray_icon.title = "COI Updater – Checking..."

    cache   = load_cache()
    release = get_latest_release()

    if not release:
        write_log("ERROR", "Could not reach GitHub API")
        if tray_icon:
            tray_icon.title = "COI Updater – Connection error"
        return

    release_tag = release["tag_name"]
    assets      = get_filtered_assets(release)
    to_update   = [a for a in assets
                   if needs_update(cache, a["mod_name"], a["updated_at"])]

    if not to_update:
        write_log("INFO", f"All mods up to date. Release: {release_tag}")
        if tray_icon:
            tray_icon.title = \
                f"COI Updater – Up to date ✓  ({datetime.now().strftime('%H:%M')})"
        return

    write_log("UPDATE", f"{len(to_update)} mod(s) need update.")
    notify(translate("notif_title"), translate("notif_found", n=len(to_update)))
    if tray_icon:
        tray_icon.title = f"COI Updater – {len(to_update)} update(s) found!"

    with gui_lock:
        if gui_window is not None:
            return
        gui_window = True

    def open_window():
        global gui_window
        win = COIUpdaterGUI(assets, to_update, cache, release_tag, release)
        win.mainloop()
        gui_window = None

    threading.Thread(target=open_window, daemon=False).start()


# FIX #3 – Fehlermeldung wenn GitHub nicht erreichbar
def open_updater_manual():
    global gui_window
    cache   = load_cache()
    release = get_latest_release()
    if not release:
        write_log("ERROR", "Could not reach GitHub for manual open.")
        def _show_error():
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(translate("title"), translate("no_connection"))
            root.destroy()
        threading.Thread(target=_show_error, daemon=True).start()
        return

    release_tag = release["tag_name"]
    assets      = get_filtered_assets(release)
    to_update   = [a for a in assets
                   if needs_update(cache, a["mod_name"], a["updated_at"])]

    with gui_lock:
        if gui_window is not None:
            return
        gui_window = True

    def open_window():
        global gui_window
        win = COIUpdaterGUI(assets, to_update, cache, release_tag, release)
        win.mainloop()
        gui_window = None

    threading.Thread(target=open_window, daemon=False).start()


def background_loop():
    global next_check_time
    interval = settings.get("check_interval", 3)
    if settings.get("check_on_start", True):
        time.sleep(3)
        check_for_updates(silent=True)
    while not stop_event.is_set():
        next_check_time = datetime.now() + timedelta(hours=interval)
        for _ in range(interval * 60):
            if stop_event.is_set():
                return
            time.sleep(60)
        check_for_updates(silent=True)

# ============================================================
# SYSTEM TRAY
# ============================================================

def build_tray_icon() -> pystray.Icon:
    global _static_tray_img
    _static_tray_img = _generate_static_icon()
    interval         = settings.get("check_interval", 3)

    def _toggle_startup(icon, item):
        set_startup(not is_startup_enabled())

    def _build_menu():
        return pystray.Menu(
            pystray.MenuItem(translate("title"), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(translate("open_updater"),
                lambda icon, item: threading.Thread(
                    target=open_updater_manual, daemon=True).start()),
            pystray.MenuItem(translate("check_now"),
                lambda icon, item: threading.Thread(
                    target=check_for_updates,
                    kwargs={"silent": False}, daemon=True).start()),
            pystray.MenuItem(translate("auto_check", n=interval), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                translate("startup_on") if is_startup_enabled()
                else translate("startup_off"), _toggle_startup),
            pystray.MenuItem(translate("settings"),
                lambda icon, item: threading.Thread(
                    target=_open_settings_standalone, daemon=True).start()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(translate("open_log"),
                lambda icon, item: os.startfile(LOG_FILE)
                    if os.path.exists(LOG_FILE) else None),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(translate("exit"),
                lambda icon, item: (stop_event.set(), icon.stop(), sys.exit(0))),
        )

    return pystray.Icon("COI Updater", _static_tray_img,
                        f"COI Updater – Every {interval}h", _build_menu())


# FIX #2 – Mainloop an SettingsWindow-Lebensdauer binden
def _open_settings_standalone():
    root = tk.Tk()
    root.withdraw()
    win = SettingsWindow(root)
    win.bind("<Destroy>", lambda e: root.quit() if e.widget is win else None)
    root.mainloop()
    root.destroy()

# ============================================================
# ENTRY POINT
# ============================================================

def main():
    global tray_icon, _TRAY_FRAMES
    load_settings()
    _TRAY_FRAMES = generate_tray_frames(10)
    write_log("START",
              f"Daemon started. "
              f"DataDir: {_APP_DATA}  |  "
              f"Mods: {get_mods_folder()}  |  "
              f"Interval: {settings.get('check_interval')}h  |  "
              f"Lang: {settings.get('language')}  |  "
              f"FontSize: {settings.get('font_size')}pt  |  "
              f"Maintenance: {settings.get('maintenance_enabled')}")
    threading.Thread(target=background_loop, daemon=True).start()
    tray_icon = build_tray_icon()
    tray_icon.run()


if __name__ == "__main__":
    main()
