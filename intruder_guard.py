import sys
import os
import site

# ── SITE-PACKAGES INJECTION (Must be absolute FIRST for SYSTEM user) ──
def inject_site_packages():
    # MUST be root-anchored for SYSTEM user (C:\Users instead of C:Users)
    users_dir = r"C:\Users"
    if os.path.exists(users_dir):
        # Scan all user folders to find potentially installed site-packages
        for user in os.listdir(users_dir):
            base_paths = [
                os.path.join(users_dir, user, r"AppData\Roaming\Python"),
                os.path.join(users_dir, user, r"AppData\Local\Programs\Python")
            ]
            for bp in base_paths:
                if os.path.exists(bp):
                    try:
                        for sub in os.listdir(bp):
                            sp = os.path.join(bp, sub, "site-packages")
                            if os.path.exists(sp) and sp not in sys.path:
                                sys.path.append(sp)
                                # Log for diagnostics
                                with open(r"C:\ProgramData\IntruderGuard\path_log.txt", "a") as f:
                                    f.write(f"Injected Path: {sp}\n")
                    except: continue

inject_site_packages()

# Absolute absolute first log to check if script even starts as SYSTEM
try:
    with open(r"C:\ProgramData\IntruderGuard\startup_id.txt", "a") as f:
        f.write(f"[{datetime.datetime.now()}] Booting with ARGS: {sys.argv}\n")
except: pass

import ctypes
import subprocess
import datetime
import time
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk # type: ignore
from PIL import Image, ImageTk # type: ignore

# ── FALLBACKS & CONSTANTS ──
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
WINDLL = getattr(ctypes, "windll", None)

APP_NAME = "IntruderGuard"
INSTALL_DIR = r"C:\ProgramData\IntruderGuard"
GALLERY_DEFAULT = os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), r"Pictures\FailedLogin")
TASK_NAME = "IntruderGuard_Capture"
CONFIG_FILE = os.path.join(INSTALL_DIR, "config.txt")

def open_file(path):
    if hasattr(os, "startfile"):
        os.startfile(path) # type: ignore
    else:
        # Fallback for linter or non-windows (though this is a windows app)
        subprocess.run(["explorer", path] if os.path.isdir(path) else ["start", "", path], shell=True)


# ── BACKEND LOGIC ──

def is_admin():
    try:
        if WINDLL and hasattr(WINDLL, "shell32"):
            return WINDLL.shell32.IsUserAnAdmin()
        return False
    except:
        return False

def get_gallery_path():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                path = f.read().strip()
                if os.path.exists(path):
                    return path
    except:
        pass
    return GALLERY_DEFAULT

def set_gallery_path(path):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            f.write(path)
    except:
        pass

def enable_auditing():
    # Use language-independent GUIDs for absolute localization support
    # Logon: {0cce0612-0000-0000-0000-000000000000}
    # Credential Validation: {0cce0610-0000-0000-0000-000000000000}
    subprocess.run(["auditpol", "/set", "/subcategory:{0cce0612-0000-0000-0000-000000000000}", "/failure:enable"], capture_output=True, creationflags=CREATE_NO_WINDOW)
    subprocess.run(["auditpol", "/set", "/subcategory:{0cce0610-0000-0000-0000-000000000000}", "/failure:enable"], capture_output=True, creationflags=CREATE_NO_WINDOW)

def disable_auditing():
    subprocess.run(["auditpol", "/set", "/subcategory:{0cce0612-0000-0000-0000-000000000000}", "/failure:disable"], capture_output=True, creationflags=CREATE_NO_WINDOW)
    subprocess.run(["auditpol", "/set", "/subcategory:{0cce0610-0000-0000-0000-000000000000}", "/failure:disable"], capture_output=True, creationflags=CREATE_NO_WINDOW)

def register_task():
    python_exe = sys.executable
    if "python.exe" in python_exe.lower():
        python_exe = python_exe.lower().replace("python.exe", "pythonw.exe")
    
    os.makedirs(INSTALL_DIR, exist_ok=True)
    target_script = os.path.join(INSTALL_DIR, "intruder_guard.py")
    batch_file = os.path.join(INSTALL_DIR, "launch_worker.bat")
    shutil.copy2(__file__, target_script)
    
    # Create a batch wrapper for robust environment execution
    with open(batch_file, "w") as f:
        f.write("@echo off\n")
        f.write(f"pushd \"{INSTALL_DIR}\"\n")
        f.write(f"\"{python_exe}\" \"{target_script}\" /capture >> debug_log.txt 2>&1\n")
        f.write("popd\n")

    create_cmd = [
        "schtasks", "/create", "/tn", TASK_NAME,
        "/tr", f"\"{batch_file}\"",
        "/sc", "onevent", "/ec", "Security",
        "/mo", "*[System[(EventID=4625)]]",
        "/ru", "SYSTEM", "/rl", "HIGHEST", "/f"
    ]
    subprocess.run(create_cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)

def unregister_task():
    subprocess.run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"], capture_output=True, creationflags=CREATE_NO_WINDOW)

def check_system_state():
    try:
        check_task = subprocess.run(["schtasks", "/query", "/tn", TASK_NAME], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        if check_task.returncode != 0:
            return False
        audit_check = subprocess.run(["auditpol", "/get", "/subcategory:Logon"], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        return "Failure" in audit_check.stdout or "Success and Failure" in audit_check.stdout
    except:
        return False

def capture_photo():
    import cv2 # type: ignore
    gallery = get_gallery_path()
    os.makedirs(gallery, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(gallery, f"Intruder_{timestamp}.jpg")
    log_file = os.path.join(INSTALL_DIR, "debug_log.txt")

    def log(msg):
        try:
            os.makedirs(INSTALL_DIR, exist_ok=True)
            with open(log_file, "a") as f:
                f.write(f"[{datetime.datetime.now()}] {msg}\n")
        except: pass

    log(f"CAPTURE STARTED: {filename}")
    try:
        # Check all possible camera backends
        cap = None
        for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, None]:
            try:
                if backend is not None:
                    cap = cv2.VideoCapture(0, backend)
                else:
                    cap = cv2.VideoCapture(0)
                if cap and cap.isOpened(): # type: ignore
                    log(f"Cam success with backend index: {backend}")
                    break
            except: continue
        
        if cap is None or not cap.isOpened(): # type: ignore
            log("ABORT: Camera could not be opened. Check hardware permissions.")
            return False
            
        assert cap is not None # type: ignore
        # Give more time for the camera sensor to adapt to lockscreen lighting
        time.sleep(2.5) 
        ret, frame = cap.read() # type: ignore
        if ret:
            cv2.imwrite(filename, frame)
            log("SUCCESS: Image saved.")
        else:
            log("ERROR: Frame read failed after opening.")
            
        if cap is not None:
            cap.release() # type: ignore
        return ret
    except Exception as e:
        log(f"CRITICAL WORKER ERROR: {str(e)}")
        return False

# ── UI IMPLEMENTATION (NEW GUI REWRITE) ──

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class IntruderGuardApp(ctk.CTk):
    # ── Colour Palette ──
    BG          = "#1c1c1c"
    NAV_BG      = "#202020"
    SURFACE     = "#2b2b2b"
    SURFACE2    = "#333333"
    SURFACE3    = "#3d3d3d"
    BORDER      = "#404040"
    BORDER_DIM  = "#383838"
    ACCENT      = "#0067c0"
    ACCENT_HVR  = "#1a75cc"
    GREEN       = "#6ccb5f"
    GREEN_BG    = "#1a2e18"
    RED         = "#d13438"
    RED_BG      = "#2e1a1a"
    YELLOW      = "#ffd700"
    TEXT        = "#ffffff"
    TEXT_SEC    = "#ababab"
    TEXT_DIM    = "#6e6e6e"

    # ── Typography ──
    FONT_TITLE  = ("Segoe UI Variable Text", 20, "bold")
    FONT_HEAD   = ("Segoe UI Variable Text", 13, "bold")
    FONT_BODY   = ("Segoe UI Variable Text", 13, "normal")
    FONT_SMALL  = ("Segoe UI Variable Text", 11, "normal")
    FONT_MONO   = ("Consolas", 11, "normal")
    FONT_STAT   = ("Segoe UI Variable Text", 26, "bold")
    FONT_NAV    = ("Segoe UI Variable Text", 13, "normal")
    FONT_PILL   = ("Segoe UI Variable Text", 11, "bold")

    # ── Layout ──
    NAV_WIDTH   = 220
    RADIUS      = 8
    RADIUS_SM   = 5
    PAD         = 20
    PAD_SM      = 12

    def __init__(self):
        super().__init__()
        self.title("IntruderGuard")
        self.geometry("760x560")
        self.minsize(760, 560)
        self.resizable(True, True)
        self.configure(fg_color=self.BG)

        # State
        self._active = check_system_state()
        self._attempts = 0
        self._photos   = 0
        self._save_path = get_gallery_path()

        # Build layout
        self._build_titlebar()
        self._build_body()
        self._refresh_status()
        self._load_gallery()
        self._auto_refresh_loop()

    def _build_titlebar(self):
        bar = ctk.CTkFrame(self, fg_color=self.NAV_BG, height=32, corner_radius=0)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)
        ctk.CTkLabel(
            bar, text="  🛡  IntruderGuard",
            font=("Segoe UI Variable Text", 12, "normal"),
            text_color=self.TEXT_SEC, fg_color="transparent"
        ).pack(side="left", padx=4, pady=0)

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color=self.BG, corner_radius=0)
        body.pack(fill="both", expand=True)
        self._build_sidebar(body)
        self._build_main(body)

    def _build_sidebar(self, parent):
        nav = ctk.CTkFrame(
            parent, fg_color=self.NAV_BG, width=self.NAV_WIDTH,
            corner_radius=0, border_width=1, border_color=self.BORDER_DIM
        )
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        hdr = ctk.CTkFrame(nav, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(14, 0))
        logo = ctk.CTkFrame(hdr, fg_color=self.ACCENT, width=28, height=28, corner_radius=7)
        logo.pack(side="left")
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="🛡", font=("Segoe UI Emoji", 14), fg_color="transparent").pack(expand=True)
        name_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        name_frame.pack(side="left", padx=10)
        ctk.CTkLabel(name_frame, text="IntruderGuard", font=self.FONT_HEAD, text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(name_frame, text="v2.0.0", font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(anchor="w")

        ctk.CTkFrame(nav, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x", padx=8, pady=(12, 10))

        self._nav_buttons = {}
        nav_items = [("dashboard", "🏠", "Dashboard"), ("gallery", "🖼", "Gallery"), ("settings", "⚙", "Settings")]
        for key, icon, label in nav_items:
            btn = ctk.CTkButton(
                nav, text=f"  {icon}   {label}", font=self.FONT_NAV, anchor="w", height=38, corner_radius=6,
                fg_color="transparent", text_color=self.TEXT_SEC, hover_color=self.SURFACE3, border_width=0,
                command=lambda k=key: self._switch_page(k)
            )
            btn.pack(fill="x", padx=6, pady=2)
            self._nav_buttons[key] = btn

        # Badge: Notification dot with anti-alias correction
        self._gallery_badge = ctk.CTkLabel(self._nav_buttons["gallery"], text="0", font=("Segoe UI Variable Text", 9, "bold"), 
                                          text_color="white", fg_color="#e81123", 
                                          corner_radius=10, width=18, height=18,
                                          bg_color="transparent")
        self._gallery_badge.place(relx=0.88, rely=0.5, anchor="center")
        self._gallery_badge.place_forget()

        ctk.CTkFrame(nav, fg_color="transparent").pack(fill="both", expand=True)
        ctk.CTkFrame(nav, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x", padx=8, pady=4)

        ctk.CTkButton(
            nav, text="  ℹ   About", font=self.FONT_NAV, anchor="w", height=38, corner_radius=6,
            fg_color="transparent", text_color=self.TEXT_DIM, hover_color=self.SURFACE3, border_width=0,
            command=self._show_about
        ).pack(fill="x", padx=6, pady=(0, 8))

    def _switch_page(self, key: str):
        for k, btn in self._nav_buttons.items():
            btn.configure(fg_color="transparent", text_color=self.TEXT_SEC)
        self._nav_buttons[key].configure(fg_color="#0d3a6e", text_color=self.TEXT)
        for k, frame in self._pages.items():
            if k == key: frame.pack(fill="both", expand=True)
            else: frame.pack_forget()

    def _build_main(self, parent):
        container = ctk.CTkFrame(parent, fg_color=self.BG, corner_radius=0)
        container.pack(side="left", fill="both", expand=True)
        self._page_host = ctk.CTkFrame(container, fg_color=self.BG, corner_radius=0)
        self._page_host.pack(fill="both", expand=True)
        self._build_statusbar(container)
        self._photos = 0
        self._known_files = set() # Track files added to UI to avoid duplicates
        self._pages = {}
        self._build_page_dashboard()
        self._build_page_gallery()
        self._build_page_settings()
        self._switch_page("dashboard")

    def _build_page_dashboard(self):
        page = ctk.CTkFrame(self._page_host, fg_color=self.BG, corner_radius=0)
        self._pages["dashboard"] = page
        scroll = ctk.CTkScrollableFrame(page, fg_color=self.BG, corner_radius=0, scrollbar_button_color=self.BORDER)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", padx=self.PAD, pady=(self.PAD, 8))
        ctk.CTkLabel(hdr, text="Protection Status", font=self.FONT_TITLE, text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Monitor and control intruder detection", font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(anchor="w")

        self._status_card = ctk.CTkFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS, border_width=1, border_color=self.BORDER_DIM)
        self._status_card.pack(fill="x", padx=self.PAD, pady=(0, self.PAD_SM))
        inner = ctk.CTkFrame(self._status_card, fg_color="transparent")
        inner.pack(fill="x", padx=self.PAD, pady=self.PAD)

        self._status_icon_frame = ctk.CTkFrame(inner, fg_color=self.RED_BG, width=64, height=64, corner_radius=14)
        self._status_icon_frame.pack(side="left")
        self._status_icon_frame.pack_propagate(False)
        self._status_icon_label = ctk.CTkLabel(self._status_icon_frame, text="✗", font=("Segoe UI Variable Text", 28, "bold"), text_color=self.RED, fg_color="transparent")
        self._status_icon_label.place(relx=0.5, rely=0.5, anchor="center")

        txt = ctk.CTkFrame(inner, fg_color="transparent")
        txt.pack(side="left", fill="both", expand=True, padx=(16, 16))
        self._headline_lbl = ctk.CTkLabel(txt, text="Your device is not protected", font=("Segoe UI Variable Text", 15, "bold"), text_color=self.TEXT, anchor="w")
        self._headline_lbl.pack(anchor="w")
        self._detail_lbl = ctk.CTkLabel(txt, text="IntruderGuard is inactive. Wrong password\nattempts will not be captured.", font=self.FONT_SMALL, text_color=self.TEXT_SEC, anchor="w", justify="left")
        self._detail_lbl.pack(anchor="w", pady=(3, 0))

        self._pill_frame = ctk.CTkFrame(txt, fg_color=self.RED_BG, corner_radius=10)
        self._pill_frame.pack(anchor="w", pady=(8, 0))
        self._pill_dot = ctk.CTkLabel(self._pill_frame, text="●", font=("Segoe UI Variable Text", 8), text_color=self.RED)
        self._pill_dot.pack(side="left", padx=(8, 0))
        self._pill_text = ctk.CTkLabel(self._pill_frame, text="Monitoring disabled", font=self.FONT_PILL, text_color="#f08080")
        self._pill_text.pack(side="left", padx=(4, 10))

        self._main_btn = ctk.CTkButton(inner, text="  🛡  Activate", font=("Segoe UI Variable Text", 13, "bold"), fg_color=self.ACCENT, hover_color=self.ACCENT_HVR, text_color=self.TEXT, height=36, width=120, corner_radius=self.RADIUS_SM, command=self._toggle_protection)
        self._main_btn.pack(side="right", anchor="center")

        stats_row = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_row.pack(fill="x", padx=self.PAD, pady=(0, self.PAD_SM))
        stats_row.columnconfigure((0, 1, 2), weight=1, uniform="stats")

        def make_stat_card(col, label, value_text, meta_text):
            card = ctk.CTkFrame(stats_row, fg_color=self.SURFACE, corner_radius=self.RADIUS, border_width=1, border_color=self.BORDER_DIM)
            card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 4, 0 if col == 2 else 4))
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=self.PAD_SM, pady=(self.PAD_SM, 0))
            ctk.CTkLabel(top, text=label.upper(), font=("Segoe UI Variable Text", 10, "bold"), text_color=self.TEXT_DIM).pack(side="left")
            val = ctk.CTkLabel(card, text=value_text, font=self.FONT_STAT, text_color=self.TEXT)
            val.pack(anchor="w", padx=self.PAD_SM, pady=(6, 0))
            ctk.CTkLabel(card, text=meta_text, font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(anchor="w", padx=self.PAD_SM, pady=(2, self.PAD_SM))
            return val

        self._attempts_lbl = make_stat_card(0, "Attempts Today", "0", "Failed logons today")
        self._photos_lbl   = make_stat_card(1, "Photos Saved", "0", f"Stored in {os.path.basename(self._save_path)}")
        self._cam_lbl      = make_stat_card(2, "Camera", "Ready", "Device 0 · Auto-detected")

        ctk.CTkLabel(scroll, text="QUICK ACTIONS", font=("Segoe UI Variable Text", 10, "bold"), text_color=self.TEXT_DIM).pack(anchor="w", padx=self.PAD, pady=(4, 4))
        action_list = ctk.CTkFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS, border_width=1, border_color=self.BORDER_DIM)
        action_list.pack(fill="x", padx=self.PAD, pady=(0, self.PAD_SM))
        self._add_action_row(action_list, "📷", "Test Camera", "Preview webcam feed to verify capture is working", btn_text="Test", btn_cmd=self._test_camera)
        self._add_action_row(action_list, "📁", "Save Location", desc_var_name="_save_path_desc", btn_text="Browse", btn_cmd=self._change_folder, divider=False)

        ctk.CTkLabel(scroll, text="EVENT LOG", font=("Segoe UI Variable Text", 10, "bold"), text_color=self.TEXT_DIM).pack(anchor="w", padx=self.PAD, pady=(4, 4))
        self._log_frame = ctk.CTkScrollableFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS, border_width=1, border_color=self.BORDER_DIM, height=130, scrollbar_button_color=self.BORDER)
        self._log_frame.pack(fill="x", padx=self.PAD, pady=(0, self.PAD))
        self._add_log_entry("info", "auto", "IntruderGuard started", "INFO")

    def _add_action_row(self, parent, icon, title, desc="", desc_var_name=None, btn_text="", btn_cmd=None, divider=True):
        if divider: ctk.CTkFrame(parent, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x")
        row = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        row.pack(fill="x")
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=self.PAD_SM, pady=10)
        icon_box = ctk.CTkFrame(inner, fg_color=self.SURFACE2, width=32, height=32, corner_radius=8)
        icon_box.pack(side="left"); icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text=icon, font=("Segoe UI Emoji", 14), fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
        txt_frame = ctk.CTkFrame(inner, fg_color="transparent")
        txt_frame.pack(side="left", fill="both", expand=True, padx=12)
        ctk.CTkLabel(txt_frame, text=title, font=self.FONT_BODY, text_color=self.TEXT, anchor="w").pack(anchor="w")
        if desc_var_name:
            lbl = ctk.CTkLabel(txt_frame, text=self._save_path, font=self.FONT_SMALL, text_color=self.TEXT_DIM, anchor="w")
            lbl.pack(anchor="w")
            setattr(self, desc_var_name, lbl)
        else:
            ctk.CTkLabel(txt_frame, text=desc, font=self.FONT_SMALL, text_color=self.TEXT_DIM, anchor="w").pack(anchor="w")
        ctk.CTkButton(inner, text=btn_text, font=self.FONT_SMALL, text_color=self.TEXT_SEC, fg_color=self.SURFACE2, hover_color=self.SURFACE3, border_width=1, border_color=self.BORDER, height=28, width=72, corner_radius=self.RADIUS_SM, command=btn_cmd).pack(side="right")

    def _add_log_entry(self, dot_type: str, timestamp: str, message: str, tag: str):
        from datetime import datetime
        ts = datetime.now().strftime("%I:%M:%S %p") if timestamp == "auto" else timestamp
        dot_colors = {"info": "#60a8f0", "ok": self.GREEN, "warn": self.YELLOW}
        tag_colors  = {"info": ("#60a8f0", "#0d2a45"), "ok": (self.GREEN, self.GREEN_BG), "warn": (self.YELLOW, "#2e2500")}
        row = ctk.CTkFrame(self._log_frame, fg_color="transparent", corner_radius=0)
        row.pack(fill="x", pady=1)
        ctk.CTkLabel(row, text="●", font=("Segoe UI Variable Text", 8), text_color=dot_colors.get(dot_type, self.TEXT_DIM), width=12).pack(side="left")
        ctk.CTkLabel(row, text=ts, font=self.FONT_MONO, text_color=self.TEXT_DIM, width=80, anchor="w").pack(side="left", padx=(4, 0))
        ctk.CTkLabel(row, text=message, font=self.FONT_SMALL, text_color=self.TEXT_SEC, anchor="w").pack(side="left", padx=(8, 0), fill="x", expand=True)
        tc, bg = tag_colors.get(dot_type, (self.TEXT_DIM, self.SURFACE2))
        ctk.CTkLabel(row, text=tag, font=("Segoe UI Variable Text", 10, "bold"), text_color=tc, fg_color=bg, corner_radius=3, width=44, height=18).pack(side="right", padx=(0, 4))

    def _build_page_gallery(self):
        page = ctk.CTkFrame(self._page_host, fg_color=self.BG, corner_radius=0)
        self._pages["gallery"] = page
        hdr = ctk.CTkFrame(page, fg_color="transparent")
        hdr.pack(fill="x", padx=self.PAD, pady=(self.PAD, 8))
        ctk.CTkLabel(hdr, text="Captured Photos", font=self.FONT_TITLE, text_color=self.TEXT).pack(anchor="w")
        self._gallery_sub_lbl = ctk.CTkLabel(hdr, text="No captures yet", font=self.FONT_SMALL, text_color=self.TEXT_DIM)
        self._gallery_sub_lbl.pack(anchor="w")
        # Clear previous list if needed? Actually, let's just use the set effectively.
        self._gallery_empty = ctk.CTkFrame(page, fg_color=self.SURFACE, corner_radius=self.RADIUS, border_width=1, border_color=self.BORDER_DIM)
        self._gallery_empty.pack(fill="x", padx=self.PAD)
        ctk.CTkLabel(self._gallery_empty, text="🖼\n\nNo intruder photos captured yet.\nActivate protection to start monitoring.", font=self.FONT_BODY, text_color=self.TEXT_DIM, justify="center").pack(pady=40)
        self._gallery_list = ctk.CTkScrollableFrame(page, fg_color=self.SURFACE, corner_radius=self.RADIUS, border_width=1, border_color=self.BORDER_DIM, scrollbar_button_color=self.BORDER)

    def _add_gallery_item(self, filename: str, timestamp: str):
        if not hasattr(self, "_known_files"): self._known_files = set()
        if filename in self._known_files: return
        self._known_files.add(filename)

        self._gallery_empty.pack_forget()
        if not self._gallery_list.winfo_ismapped():
            self._gallery_list.pack(fill="both", expand=True, padx=self.PAD, pady=(0, self.PAD))
        
        row = ctk.CTkFrame(self._gallery_list, fg_color="transparent")
        row.pack(fill="x", pady=1)
        icon_box = ctk.CTkFrame(row, fg_color="#2e1a1a", width=32, height=32, corner_radius=8)
        icon_box.pack(side="left", padx=(4, 0), pady=6); icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="📸", font=("Segoe UI Emoji", 14), fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
        
        txt = ctk.CTkFrame(row, fg_color="transparent")
        txt.pack(side="left", fill="both", expand=True, padx=12)
        ctk.CTkLabel(txt, text=filename, font=self.FONT_BODY, text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(txt, text=f"Captured: {timestamp} · Security Violation", font=self.FONT_SMALL, text_color=self.TEXT_DIM, anchor="w").pack(anchor="w")
        
        btn_f = ctk.CTkFrame(row, fg_color="transparent")
        btn_f.pack(side="right", padx=8)
        
        def delete_img(p=os.path.join(self._save_path, filename), r=row, f=filename):
            try:
                if os.path.exists(p): os.remove(p)
                if f in self._known_files: self._known_files.remove(f)
                r.destroy()
                self._update_stats_count()
            except Exception as e:
                print(f"Delete failed: {e}")

        ctk.CTkButton(btn_f, text="View", width=60, height=24, fg_color=self.SURFACE2, font=self.FONT_SMALL, command=lambda p=os.path.join(self._save_path, filename): open_file(p)).pack(side="left", padx=2)
        ctk.CTkButton(btn_f, text="Delete", width=60, height=24, fg_color="#3d2121", hover_color="#5c2626", text_color="#ff9999", font=self.FONT_SMALL, command=delete_img).pack(side="left", padx=2)
        
        ctk.CTkFrame(self._gallery_list, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x")
        self._photos += 1
        self._gallery_sub_lbl.configure(text=f"{self._photos} photo{'s' if self._photos > 1 else ''} captured")
        self._gallery_badge.configure(text=str(self._photos))
        self._gallery_badge.place(relx=0.88, rely=0.5, anchor="center")

    def _load_gallery(self):
        if not os.path.exists(self._save_path): return
        files = [f for f in os.listdir(self._save_path) if f.endswith((".jpg", ".png", ".jpeg"))]
        files.sort(reverse=True) # Newest first
        for f in files:
            t = time.ctime(os.path.getmtime(os.path.join(self._save_path, f)))
            self._add_gallery_item(f, t)
        self._update_stats_count()

    def _update_stats_count(self):
        # Update dashboard stats from folder count
        try:
            if not os.path.exists(self._save_path): return
            count = len([f for f in os.listdir(self._save_path) if f.endswith((".jpg", ".png", ".jpeg"))])
            self._photos = count
            self._photos_lbl.configure(text=str(count))
            # Update gallery side indicators too
            if hasattr(self, "_gallery_badge"):
                self._gallery_badge.configure(text=str(count))
                if count > 0: self._gallery_badge.place(relx=0.88, rely=0.5, anchor="center")
                else: self._gallery_badge.place_forget()
            if hasattr(self, "_gallery_sub_lbl"):
                self._gallery_sub_lbl.configure(text=f"{count} photo{'s' if count != 1 else ''} captured")
                if count == 0: self._gallery_empty.pack(fill="x", padx=self.PAD)
            # Rough estimate of today's attempts by file timestamp
            today = datetime.date.today()
            today_count = 0 # type: int
            for f in os.listdir(self._save_path):
                if f.endswith((".jpg", ".png", ".jpeg")):
                    m_time_raw = os.path.getmtime(os.path.join(self._save_path, f))
                    mtime = datetime.date.fromtimestamp(m_time_raw)
                    if mtime == today: 
                        today_count += 1 # type: ignore
            self._attempts_lbl.configure(text=str(today_count))
        except: pass

    def _auto_refresh_loop(self):
        # Poll the folder for new changes every 5 seconds
        self._load_gallery()
        self.after(5000, self._auto_refresh_loop)

    def _build_page_settings(self):
        page = ctk.CTkFrame(self._page_host, fg_color=self.BG, corner_radius=0)
        self._pages["settings"] = page
        scroll = ctk.CTkScrollableFrame(page, fg_color=self.BG, corner_radius=0, scrollbar_button_color=self.BORDER)
        scroll.pack(fill="both", expand=True)
        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", padx=self.PAD, pady=(self.PAD, 8))
        ctk.CTkLabel(hdr, text="Settings", font=self.FONT_TITLE, text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Configure monitoring behavior", font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(anchor="w")

        # ── MONITORING section ──
        ctk.CTkLabel(scroll, text="MONITORING", font=("Segoe UI Variable Text", 10, "bold"), text_color=self.TEXT_DIM).pack(anchor="w", padx=self.PAD, pady=(8, 4))
        mon_list = ctk.CTkFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS, border_width=1, border_color=self.BORDER_DIM)
        mon_list.pack(fill="x", padx=self.PAD, pady=(0, self.PAD_SM))
        
        # We now create the row first, then place the widget in it to ensure perfect alignment
        self._add_setting_row(mon_list, "📷", "Camera Index", "Which webcam device to use for capture (default: 0)", 
                              {"type": "entry", "width": 44, "text": "0"}, divider=False)
        self._add_setting_row(mon_list, "🔒", "Start with Windows", "Launch IntruderGuard automatically at login", 
                              {"type": "switch"}, divider=True)
        self._add_setting_row(mon_list, "⏱", "Multi-Photo Burst", "Capture 3 photos per attempt (500ms apart)", 
                              {"type": "switch"}, divider=True)

        ctk.CTkLabel(scroll, text="STORAGE", font=("Segoe UI Variable Text", 10, "bold"), text_color=self.TEXT_DIM).pack(anchor="w", padx=self.PAD, pady=(4, 4))
        store_list = ctk.CTkFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS, border_width=1, border_color=self.BORDER_DIM)
        store_list.pack(fill="x", padx=self.PAD, pady=(0, self.PAD_SM))
        row = ctk.CTkFrame(store_list, fg_color="transparent")
        row.pack(fill="x", padx=self.PAD_SM, pady=10)
        icon_box = ctk.CTkFrame(row, fg_color=self.SURFACE2, width=32, height=32, corner_radius=8)
        icon_box.pack(side="left"); icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="📁", fg_color="transparent", font=("Segoe UI Emoji", 14)).place(relx=0.5, rely=0.5, anchor="center")
        txt_f = ctk.CTkFrame(row, fg_color="transparent")
        txt_f.pack(side="left", fill="both", expand=True, padx=12)
        ctk.CTkLabel(txt_f, text="Save Folder", font=self.FONT_BODY, text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(txt_f, text="Where captured photos are stored", font=self.FONT_SMALL, text_color=self.TEXT_DIM, anchor="w").pack(anchor="w")
        right_f = ctk.CTkFrame(row, fg_color="transparent")
        right_f.pack(side="right")
        self._path_entry = ctk.CTkEntry(right_f, width=155, height=28, fg_color=self.SURFACE2, border_color=self.BORDER, text_color=self.TEXT_SEC, font=self.FONT_MONO, corner_radius=self.RADIUS_SM)
        self._path_entry.insert(0, self._save_path); self._path_entry.pack(side="left", padx=(0, 6))
        ctk.CTkButton(right_f, text="Browse", height=28, width=64, fg_color=self.SURFACE2, hover_color=self.SURFACE3, border_width=1, border_color=self.BORDER, text_color=self.TEXT_SEC, font=self.FONT_SMALL, corner_radius=self.RADIUS_SM, command=self._change_folder).pack(side="left")

    def _add_setting_row(self, parent, icon, title, desc, widget_config, divider=True):
        if divider: ctk.CTkFrame(parent, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=self.PAD_SM, pady=10)
        ibox = ctk.CTkFrame(row, fg_color=self.SURFACE2, width=32, height=32, corner_radius=8)
        ibox.pack(side="left"); ibox.pack_propagate(False)
        ctk.CTkLabel(ibox, text=icon, fg_color="transparent", font=("Segoe UI Emoji", 14)).place(relx=0.5, rely=0.5, anchor="center")
        t = ctk.CTkFrame(row, fg_color="transparent")
        t.pack(side="left", fill="both", expand=True, padx=12)
        ctk.CTkLabel(t, text=title, font=self.FONT_BODY, text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(t, text=desc, font=self.FONT_SMALL, text_color=self.TEXT_DIM, anchor="w").pack(anchor="w")
        
        # Create widget with the row as parent
        if widget_config["type"] == "switch":
            w = ctk.CTkSwitch(row, text="", width=44, progress_color=self.ACCENT, button_color=self.TEXT)
        elif widget_config["type"] == "entry":
            w = ctk.CTkEntry(row, width=widget_config.get("width", 60), height=24, border_width=1, fg_color=self.SURFACE2)
            if "text" in widget_config: w.insert(0, widget_config["text"])
        
        w.pack(side="right", padx=10)

    def _build_statusbar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=self.NAV_BG, height=22, corner_radius=0)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        ctk.CTkFrame(bar, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x", side="top")
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14)
        self._sb_dot = ctk.CTkLabel(inner, text="●", font=("Segoe UI Variable Text", 8), text_color=self.RED, width=10)
        self._sb_dot.pack(side="left", pady=3)
        self._sb_status_lbl = ctk.CTkLabel(inner, text="Not protected", font=self.FONT_SMALL, text_color=self.TEXT_DIM)
        self._sb_status_lbl.pack(side="left", padx=(4, 16))
        ctk.CTkLabel(inner, text="🛡", font=("Segoe UI Emoji", 9), text_color=self.TEXT_DIM).pack(side="left")
        self._sb_task_lbl = ctk.CTkLabel(inner, text="Task: Not registered", font=self.FONT_SMALL, text_color=self.TEXT_DIM)
        self._sb_task_lbl.pack(side="left", padx=(4, 0))
        self._sb_audit_lbl = ctk.CTkLabel(inner, text="auditpol: Disabled", font=self.FONT_SMALL, text_color=self.TEXT_DIM)
        self._sb_audit_lbl.pack(side="right")
        ctk.CTkLabel(inner, text="🔒", font=("Segoe UI Emoji", 9), text_color=self.TEXT_DIM).pack(side="right", padx=(0, 4))

    def _refresh_status(self):
        if self._active:
            self._status_icon_frame.configure(fg_color=self.GREEN_BG)
            self._status_icon_label.configure(text="✓", text_color=self.GREEN)
            self._headline_lbl.configure(text="Your device is protected")
            self._detail_lbl.configure(text="IntruderGuard is monitoring for wrong\npassword attempts via Event ID 4625.")
            self._pill_frame.configure(fg_color=self.GREEN_BG)
            self._pill_dot.configure(text_color=self.GREEN)
            self._pill_text.configure(text="Monitoring active", text_color="#8ee280")
            self._main_btn.configure(text="  ✗  Deactivate", fg_color="#2e1212", hover_color=self.RED_BG, text_color="#f08080", border_width=1, border_color=self.RED)
            self._sb_dot.configure(text_color=self.GREEN)
            self._sb_status_lbl.configure(text="Protected")
            self._sb_task_lbl.configure(text="Task: IntruderGuard_Capture")
            self._sb_audit_lbl.configure(text="auditpol: Failure logging on")
        else:
            self._status_icon_frame.configure(fg_color=self.RED_BG)
            self._status_icon_label.configure(text="✗", text_color=self.RED)
            self._headline_lbl.configure(text="Your device is not protected")
            self._detail_lbl.configure(text="IntruderGuard is inactive. Wrong password\nattempts will not be captured.")
            self._pill_frame.configure(fg_color=self.RED_BG)
            self._pill_dot.configure(text_color=self.RED)
            self._pill_text.configure(text="Monitoring disabled", text_color="#f08080")
            self._main_btn.configure(text="  🛡  Activate", fg_color=self.ACCENT, hover_color=self.ACCENT_HVR, text_color=self.TEXT, border_width=0)
            self._sb_dot.configure(text_color=self.RED)
            self._sb_status_lbl.configure(text="Not protected")
            self._sb_task_lbl.configure(text="Task: Not registered")
            self._sb_audit_lbl.configure(text="auditpol: Disabled")

    def _toggle_protection(self):
        try:
            if not self._active:
                enable_auditing(); register_task()
                self._active = True
                self._add_log_entry("info", "auto", "Protection activated — Task registered", "INFO")
                self._add_log_entry("ok", "auto", "auditpol: Logon failure auditing enabled", "OK")
                self._show_toast("🛡️", "Protection Activated", "Monitoring for wrong password attempts via Event 4625.")
            else:
                disable_auditing(); unregister_task()
                self._active = False
                self._add_log_entry("info", "auto", "Protection deactivated — Task removed", "INFO")
                self._show_toast("⚠️", "Protection Deactivated", "Device is no longer being monitored.")
            self._refresh_status()
        except Exception as e:
            if "Access is denied" in str(e) or not is_admin():
                if WINDLL and hasattr(WINDLL, "shell32"):
                    WINDLL.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)
                sys.exit()

    def _show_toast(self, icon: str, title: str, message: str, duration_ms: int = 3200):
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True); toast.attributes("-topmost", True); toast.configure(fg_color=self.SURFACE2)
        self.update_idletasks()
        wx = self.winfo_x() + self.winfo_width() - 300
        wy = self.winfo_y() + self.winfo_height() - 100
        toast.geometry(f"280x72+{wx}+{wy}")
        outer = ctk.CTkFrame(toast, fg_color=self.SURFACE2, corner_radius=8, border_width=1, border_color=self.BORDER)
        outer.pack(fill="both", expand=True, padx=1, pady=1)
        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=10)
        ctk.CTkLabel(inner, text=icon, font=("Segoe UI Emoji", 18), fg_color="transparent", width=24).pack(side="left", anchor="n", pady=2)
        body = ctk.CTkFrame(inner, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, padx=(10, 0))
        ctk.CTkLabel(body, text=title, font=("Segoe UI Variable Text", 12, "bold"), text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(body, text=message, font=self.FONT_SMALL, text_color=self.TEXT_SEC, anchor="w", wraplength=200, justify="left").pack(anchor="w")
        toast.attributes("-alpha", 0.0)
        def _fade_in(alpha=0.0):
            alpha = min(alpha + 0.12, 1.0); toast.attributes("-alpha", alpha)
            if alpha < 1.0: toast.after(16, lambda: _fade_in(alpha))
        _fade_in()
        def _dismiss():
            def _fade_out(alpha=1.0):
                alpha = max(alpha - 0.12, 0.0)
                try:
                    toast.attributes("-alpha", alpha)
                    if alpha > 0: toast.after(16, lambda: _fade_out(alpha))
                    else: toast.destroy()
                except: pass
            _fade_out()
        toast.after(duration_ms, _dismiss)
        toast.bind("<Button-1>", lambda e: _dismiss())

    def _test_camera(self):
        preview_win = ctk.CTkToplevel(self)
        preview_win.title("Camera Preview"); preview_win.geometry("480x390"); preview_win.configure(fg_color=self.BG); preview_win.resizable(False, False)
        hdr = ctk.CTkFrame(preview_win, fg_color=self.NAV_BG, height=32, corner_radius=0); hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="  📷  Camera Preview", font=self.FONT_SMALL, text_color=self.TEXT_SEC, fg_color="transparent").pack(side="left", padx=8)
        canvas_frame = ctk.CTkFrame(preview_win, fg_color=self.SURFACE, corner_radius=self.RADIUS, border_width=1, border_color=self.BORDER_DIM); canvas_frame.pack(fill="both", expand=True, padx=self.PAD, pady=self.PAD)
        lbl = ctk.CTkLabel(canvas_frame, text="Starting camera…", font=self.FONT_BODY, text_color=self.TEXT_DIM); lbl.pack(expand=True)
        import cv2 # type: ignore
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        def update():
            if not preview_win.winfo_exists(): cap.release(); return
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb).resize((440, 310))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(440, 310))
                lbl.configure(image=ctk_img, text="")
                lbl._image = ctk_img
            preview_win.after(33, update)
        update()
        preview_win.protocol("WM_DELETE_WINDOW", lambda: (cap.release(), preview_win.destroy()))
        self._add_log_entry("ok", "auto", "Camera test — cv2.VideoCapture(0) OK", "OK")

    def _change_folder(self):
        path = filedialog.askdirectory(initialdir=self._save_path, title="Select Save Folder")
        if path:
            new_path = path.replace("/", "\\")
            set_gallery_path(new_path); self._save_path = new_path
            if hasattr(self, "_save_path_desc"): self._save_path_desc.configure(text=new_path)
            if hasattr(self, "_path_entry"): self._path_entry.delete(0, "end"); self._path_entry.insert(0, new_path)
            self._show_toast("📁", "Save Folder Updated", new_path)

    def _show_about(self):
        messagebox.showinfo("About IntruderGuard", "IntruderGuard v2.0.0\nA modern security utility to capture intruder photos.\nBuilt with Python & CustomTkinter.")

if __name__ == "__main__":
    if "/capture" in sys.argv:
        capture_photo()
    else:
        if not is_admin():
            if WINDLL:
                WINDLL.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)
            sys.exit()
        else:
            app = IntruderGuardApp()
            app.mainloop()
