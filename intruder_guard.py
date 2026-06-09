import sys
import os
import site
import datetime

# ── SITE-PACKAGES INJECTION (Must be absolute FIRST for SYSTEM user) ──
def inject_site_packages():
    # MUST be root-anchored for SYSTEM user (C:\Users instead of C:Users)
    users_dir = r"C:\Users"
    if os.path.exists(users_dir):
        # Scan all user folders to find potentially installed site-packages
        for user in os.listdir(users_dir):
            user_path = os.path.join(users_dir, user)
            if not os.path.isdir(user_path):
                continue
            
            base_paths = [
                os.path.join(user_path, r"AppData\Roaming\Python"),
                os.path.join(user_path, r"AppData\Local\Programs\Python")
            ]
            for bp in base_paths:
                if os.path.exists(bp):
                    try:
                        for sub in os.listdir(bp):
                            for sub_sp in ["site-packages", "Lib\\site-packages"]:
                                sp = os.path.join(bp, sub, sub_sp)
                                if os.path.exists(sp) and sp not in sys.path:
                                    sys.path.append(sp)
                                    # Log for diagnostics
                                    try:
                                        os.makedirs(r"C:\ProgramData\IntruderGuard", exist_ok=True)
                                        with open(r"C:\ProgramData\IntruderGuard\path_log.txt", "a") as f:
                                            f.write(f"Injected Path (Scan): {sp}\n")
                                    except: pass
                    except: continue

            # Windows Store Python path (AppData\Local\Packages\PythonSoftwareFoundation.Python.*\LocalCache\local-packages\PythonXX\site-packages)
            packages_dir = os.path.join(user_path, r"AppData\Local\Packages")
            if os.path.exists(packages_dir):
                try:
                    for sub in os.listdir(packages_dir):
                        if sub.startswith("PythonSoftwareFoundation.Python"):
                            local_cache = os.path.join(packages_dir, sub, "LocalCache", "local-packages")
                            if os.path.exists(local_cache):
                                for py_folder in os.listdir(local_cache):
                                    sp = os.path.join(local_cache, py_folder, "site-packages")
                                    if os.path.exists(sp) and sp not in sys.path:
                                        sys.path.append(sp)
                                        # Log for diagnostics
                                        try:
                                            os.makedirs(r"C:\ProgramData\IntruderGuard", exist_ok=True)
                                            with open(r"C:\ProgramData\IntruderGuard\path_log.txt", "a") as f:
                                                f.write(f"Injected Path (Store): {sp}\n")
                                        except: pass
                except: continue

    # Also inject paths passed via command line --inject-paths
    if "--inject-paths" in sys.argv:
        try:
            idx = sys.argv.index("--inject-paths")
            if idx + 1 < len(sys.argv):
                paths = sys.argv[idx + 1].split(";")
                for p in paths:
                    if os.path.exists(p) and p not in sys.path:
                        sys.path.append(p)
                        try:
                            os.makedirs(r"C:\ProgramData\IntruderGuard", exist_ok=True)
                            with open(r"C:\ProgramData\IntruderGuard\path_log.txt", "a") as f:
                                f.write(f"Injected Path (Args): {p}\n")
                        except: pass
        except Exception:
            pass

inject_site_packages()

# Absolute absolute first log to check if script even starts as SYSTEM
try:
    os.makedirs(r"C:\ProgramData\IntruderGuard", exist_ok=True)
    with open(r"C:\ProgramData\IntruderGuard\startup_id.txt", "a") as f:
        f.write(f"[{datetime.datetime.now()}] Booting with ARGS: {sys.argv}\n")
except: pass

import ctypes
import subprocess
import time
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk # type: ignore
    from PIL import Image, ImageTk, ImageDraw # type: ignore
except ImportError as e:
    import ctypes
    # Show error dialog using Windows API (MessageBoxW) as GUI packages may not be loaded
    ctypes.windll.user32.MessageBoxW(
        0,
        f"Initialization Error: Missing critical libraries.\n\n"
        f"Error details: {str(e)}\n\n"
        f"Please run 'Setup_Python.bat' to install all required dependencies.",
        "IntruderGuard Error",
        0x10
    )
    sys.exit(1)


# ── FALLBACKS & CONSTANTS ──
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
WINDLL = getattr(ctypes, "windll", None)

APP_NAME = "IntruderGuard"
INSTALL_DIR = r"C:\ProgramData\IntruderGuard"
GALLERY_DEFAULT = os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), r"Pictures\FailedLogin")
TASK_NAME = "IntruderGuard_Capture"
CONFIG_FILE = os.path.join(INSTALL_DIR, "config.txt")
CONFIG_JSON_FILE = os.path.join(INSTALL_DIR, "config.json")

DEFAULT_CONFIG = {
    "gallery_path": GALLERY_DEFAULT,
    "enable_monitoring": True,
    "run_on_startup": False,
    "death_mode": False,
    "camera_index": 0,
    "photo_quality": "Original (Highest)",
    "capture_delay": 150,
    "event_ids": ["4625"],
    "retention_policy": "Delete after 30 days"
}

import json

def load_config():
    try:
        if os.path.exists(CONFIG_JSON_FILE):
            with open(CONFIG_JSON_FILE, "r") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
    except Exception:
        pass
    # Legacy config.txt check
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                path = f.read().strip()
                if os.path.exists(path):
                    config = DEFAULT_CONFIG.copy()
                    config["gallery_path"] = path
                    return config
    except Exception:
        pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        os.makedirs(INSTALL_DIR, exist_ok=True)
        with open(CONFIG_JSON_FILE, "w") as f:
            json.dump(config, f, indent=4)
        # Write to legacy file as well
        if "gallery_path" in config:
            with open(CONFIG_FILE, "w") as f:
                f.write(config["gallery_path"])
    except Exception:
        pass

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
    return load_config().get("gallery_path", GALLERY_DEFAULT)

def set_gallery_path(path):
    config = load_config()
    config["gallery_path"] = path
    save_config(config)

def enable_auditing():
    """
    TRIGGER EVENT SETUP - STEP 1: Windows Security Auditing
    -------------------------------------------------------
    This function configures Windows Local Security Policy via the 'auditpol' command to log
    failed logon attempts and failed credential validations to the Windows Security Event Log.
    
    Why: By default, Windows does not log failed logon attempts. We must enable auditing
    for these subcategories so that Event ID 4625 (Logon Failure) will be recorded.
    
    Subcategories audited (using language-independent GUIDs for absolute localization support):
    - Logon: {0cce0612-0000-0000-0000-000000000000} -> Triggers when someone tries to log in.
    - Credential Validation: {0cce0610-0000-0000-0000-000000000000} -> Triggers when credentials are authenticated.
    """
    subprocess.run(["auditpol", "/set", "/subcategory:{0cce0612-0000-0000-0000-000000000000}", "/failure:enable"], capture_output=True, creationflags=CREATE_NO_WINDOW)
    subprocess.run(["auditpol", "/set", "/subcategory:{0cce0610-0000-0000-0000-000000000000}", "/failure:enable"], capture_output=True, creationflags=CREATE_NO_WINDOW)

def disable_auditing():
    """
    Disables Windows Security Auditing for logons and credential validation.
    Restores default system state when monitoring is paused or disabled.
    """
    subprocess.run(["auditpol", "/set", "/subcategory:{0cce0612-0000-0000-0000-000000000000}", "/failure:disable"], capture_output=True, creationflags=CREATE_NO_WINDOW)
    subprocess.run(["auditpol", "/set", "/subcategory:{0cce0610-0000-0000-0000-000000000000}", "/failure:disable"], capture_output=True, creationflags=CREATE_NO_WINDOW)

def register_task():
    """
    TRIGGER EVENT SETUP - STEP 2: Windows Scheduled Task Registration
    -----------------------------------------------------------------
    Creates a persistent Windows Scheduled Task ('IntruderGuard_Capture') that automatically triggers
    when any of the target Event IDs are logged in the Windows Security Event Log.
    
    How this forms the trigger event mechanism:
    1. schtasks parameters used:
       - /sc onevent: Specifies that the task runs on a specific Windows Event Log entry.
       - /ec Security: Monitors the Windows 'Security' event channel.
       - /mo xpath: An XPath filter query (e.g. *[System[(EventID=4625)]]) that filters for target event IDs.
       - /ru SYSTEM: Runs the task under the local 'SYSTEM' security context. This is CRITICAL
         because normal user accounts cannot access webcam hardware when the Windows screen is locked.
         The SYSTEM account has raw system privileges and bypasses desktop session limitations.
         
    2. Execution payload:
       - Rather than running python directly, the task invokes 'launch_worker.bat'.
       - 'launch_worker.bat' executes pythonw.exe with the target script path and the '/capture' argument.
       - It also injects user site-packages paths so third-party packages (like customtkinter, cv2)
         can be loaded correctly by the SYSTEM account.
    """
    config = load_config()
    event_ids = config.get("event_ids", ["4625"])
    
    # Resolve physical pythonw.exe path (bypasses Windows Store alias restriction under SYSTEM user)
    python_exe = os.path.join(sys.base_exec_prefix, "pythonw.exe")
    if not os.path.exists(python_exe):
        python_exe = os.path.join(sys.base_exec_prefix, "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable
        if "python.exe" in python_exe.lower():
            python_exe = python_exe.lower().replace("python.exe", "pythonw.exe")
            
    os.makedirs(INSTALL_DIR, exist_ok=True)
    target_script = os.path.join(INSTALL_DIR, "intruder_guard.py")
    batch_file = os.path.join(INSTALL_DIR, "launch_worker.bat")
    shutil.copy2(__file__, target_script)
    
    # Grab current user's packages paths to inject into background worker running as SYSTEM
    user_paths = [p for p in sys.path if p and isinstance(p, str) and p.lower().startswith("c:\\users\\")]
    inject_args = ""
    if user_paths:
        inject_args = f' --inject-paths "{";".join(user_paths)}"'
        
    # Create a batch wrapper for robust environment execution
    with open(batch_file, "w") as f:
        f.write("@echo off\n")
        f.write(f"pushd \"{INSTALL_DIR}\"\n")
        f.write(f"\"{python_exe}\" \"{target_script}\" /capture{inject_args} >> debug_log.txt 2>&1\n")
        f.write("popd\n")

    # Build dynamic Event ID XPath query
    query_parts = [f"EventID={eid}" for eid in event_ids]
    event_query = " or ".join(query_parts)
    xpath = f"*[System[({event_query})]]"

    # Register task under SYSTEM account to bypass locked-screen webcam access restrictions
    create_cmd = [
        "schtasks", "/create", "/tn", TASK_NAME,
        "/tr", f"\"{batch_file}\"",
        "/sc", "onevent", "/ec", "Security",
        "/mo", xpath,
        "/ru", "SYSTEM", "/rl", "HIGHEST", "/f"
    ]
    subprocess.run(create_cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)

def unregister_task():
    """
    Removes the Windows Scheduled Task 'IntruderGuard_Capture' from Task Scheduler.
    Fires when protection is paused or the application is uninstalled.
    """
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

def get_last_security_event_info(event_ids=None):
    """
    TRIGGER EVENT PROCESSING - STEP 1: Querying the Security Event Log
    ------------------------------------------------------------------
    When a security event triggers the scheduled task, this function queries the Windows 
    Security Log using the 'wevtutil' utility to extract metadata of the most recent event.
    
    Key Actions:
    1. Calls 'wevtutil qe Security' with an XML query that filters by the targeted Event IDs.
    2. Uses flags:
       - /c:1 -> Fetches only the 1 most recent event.
       - /rd:true -> Reads the log in reverse direction (newest first).
       - /f:xml -> Outputs the log details in XML format.
    3. Parses the XML structure to fetch:
       - Event ID (e.g. 4625)
       - TargetUserName (The username involved in the event)
       - WorkstationName (The host workstation name)
       - TimeCreated SystemTime (Timestamp converted to local time zone)
    
    Returns:
        dict: A dictionary containing 'event_id', 'target_user', 'workstation', and 'timestamp'.
    """
    if not event_ids:
        event_ids = ["4625"]
    try:
        import xml.etree.ElementTree as ET
        query_parts = [f"EventID={eid}" for eid in event_ids]
        query = "*[System[(" + " or ".join(query_parts) + ")]]"
        cmd = ["wevtutil", "qe", "Security", f"/q:{query}", "/c:1", "/rd:true", "/f:xml"]
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        if res.returncode == 0 and res.stdout.strip():
            xml_str = res.stdout.strip()
            if "</Event>" in xml_str:
                idx = xml_str.find("</Event>")
                xml_str = xml_str[:idx + 8]
            root = ET.fromstring(xml_str)
            ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
            event_id = "Unknown"
            system = root.find("ns:System", ns)
            if system is not None:
                eid_elem = system.find("ns:EventID", ns)
                if eid_elem is not None:
                    event_id = eid_elem.text or "Unknown"
            target_user = "Unknown"
            workstation = "Local"
            event_data = root.find("ns:EventData", ns)
            if event_data is not None:
                for data in event_data.findall("ns:Data", ns):
                    name = data.attrib.get("Name")
                    if name == "TargetUserName":
                        target_user = data.text or "Unknown"
                    elif name == "WorkstationName":
                        workstation = data.text or "Local"
            system_time = None
            if system is not None:
                tc = system.find("ns:TimeCreated", ns)
                if tc is not None:
                    system_time = tc.attrib.get("SystemTime")
            timestamp_str = None
            if system_time:
                try:
                    clean_time = system_time.split(".")[0].replace("T", " ")
                    if clean_time.endswith("Z"):
                        clean_time = clean_time[:-1]
                    utc_dt = datetime.datetime.strptime(clean_time, "%Y-%m-%d %H:%M:%S")
                    now = datetime.datetime.now()
                    utcnow = datetime.datetime.utcnow()
                    offset = now - utcnow
                    local_dt = utc_dt + offset
                    timestamp_str = local_dt.strftime("%Y-%m-%d  %H:%M:%S")
                except:
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
            else:
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
            return {
                "event_id": event_id,
                "target_user": target_user,
                "workstation": workstation,
                "timestamp": timestamp_str
            }
    except Exception as e:
        try:
            os.makedirs(INSTALL_DIR, exist_ok=True)
            with open(os.path.join(INSTALL_DIR, "debug_log.txt"), "a") as f:
                f.write(f"[{datetime.datetime.now()}] EventLog Query Error: {str(e)}\n")
        except: pass
    return {
        "event_id": "4625",
        "target_user": "Unknown User",
        "workstation": "Localhost",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    }

def write_activity_log(timestamp, event_id, target_user, workstation, action, status, image_name=None, capture_success=True):
    activity_log_file = os.path.join(INSTALL_DIR, "activity_logs.json")
    try:
        os.makedirs(INSTALL_DIR, exist_ok=True)
        logs = []
        if os.path.exists(activity_log_file):
            try:
                with open(activity_log_file, "r") as f:
                    logs = json.load(f)
            except: pass
        for log in logs:
            if log.get("timestamp") == timestamp and log.get("target_user") == target_user and log.get("event_id") == event_id:
                return
        new_entry = {
            "timestamp": timestamp,
            "event_id": str(event_id),
            "target_user": target_user,
            "workstation": workstation,
            "action": action,
            "status": status,
            "image_name": image_name,
            "capture_success": capture_success
        }
        logs.append(new_entry)
        try:
            logs.sort(key=lambda x: x.get("timestamp", ""), reverse=False)
        except: pass
        with open(activity_log_file, "w") as f:
            json.dump(logs, f, indent=4)
    except Exception as e:
        try:
            with open(os.path.join(INSTALL_DIR, "debug_log.txt"), "a") as f:
                f.write(f"[{datetime.datetime.now()}] Failed writing activity log: {str(e)}\n")
        except: pass

def capture_photo(is_sim=False):
    """
    TRIGGER EVENT PROCESSING - STEP 2: Camera Capture & Logging Action
    ------------------------------------------------------------------
    This function is executed by the background worker when a trigger event is detected.
    It takes a photo from the system's webcam and writes details to the activity log.
    
    Mechanism:
    1. Setup Output: Determines filename structure (Intruder_YYYYMMDD_HHMMSS.jpg) inside the gallery folder.
    2. Fetch Event Context: If it's a simulated trigger, dummy info is created. Otherwise, it calls 
       'get_last_security_event_info()' to retrieve details of the actual Windows security event.
    3. Determine Security State: Maps the event ID to status tags and actions:
       - Event 4625: "Failed Logon" -> Status: "BLOCKED ATTEMPT"
       - Event 4624: "Successful Logon" -> Status: "SUCCESS AUDIT"
       - Event 4735: "Security Group Changed" -> Status: "WARNING"
       - Event 4720: "User Created" -> Status: "WARNING"
    4. Webcam Initialization: Attempts to open the webcam at the specified camera index. It iterates
       through different OpenCV capture backends (DSHOW, MSMF) to guarantee compatibility in background processes.
    5. Delay: Wait for 'capture_delay' (ms) to allow the camera sensor auto-exposure to adjust.
    6. Image Capture & Storage: Reads a frame, writes the image file, and logs results via 'write_activity_log'.
       If the camera fails to initialize, it records a failure entry in the activity log.
    """
    import cv2 # type: ignore
    config = load_config()
    gallery = config.get("gallery_path", GALLERY_DEFAULT)
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
    
    if is_sim:
        event_info = {
            "event_id": "4625",
            "target_user": "Simulated_Intruder",
            "workstation": "SEC-SIM-01",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        }
    else:
        event_ids = config.get("event_ids", ["4625"])
        event_info = get_last_security_event_info(event_ids)
        if not event_info:
            event_info = {
                "event_id": "4625",
                "target_user": "Unknown User",
                "workstation": "Localhost",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
            }

    # Resolve dynamic action description and status based on Event ID
    eid = event_info.get("event_id", "4625")
    if eid == "4625":
        evt_desc = "Failed Logon"
        status_text = "BLOCKED ATTEMPT"
    elif eid == "4624":
        evt_desc = "Successful Logon"
        status_text = "SUCCESS AUDIT"
    elif eid == "4735":
        evt_desc = "Security Group Changed"
        status_text = "WARNING"
    elif eid == "4720":
        evt_desc = "User Created"
        status_text = "WARNING"
    else:
        evt_desc = f"Event {eid}"
        status_text = "DOCUMENTED"

    try:
        cam_id = config.get("camera_index", 0)
        delay_ms = config.get("capture_delay", 150)
        
        cap = None
        for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, None]:
            try:
                if backend is not None:
                    cap = cv2.VideoCapture(cam_id, backend)
                else:
                    cap = cv2.VideoCapture(cam_id)
                if cap and cap.isOpened(): # type: ignore
                    log(f"Cam success with backend index: {backend}")
                    break
            except: continue
        
        if cap is None or not cap.isOpened(): # type: ignore
            log("ABORT: Camera could not be opened. Check hardware permissions.")
            write_activity_log(
                timestamp=event_info["timestamp"],
                event_id=event_info["event_id"],
                target_user=event_info["target_user"],
                workstation=event_info["workstation"],
                action=f"{evt_desc} detected - Camera could not be opened",
                status=status_text,
                image_name=None,
                capture_success=False
            )
            return False
            
        assert cap is not None # type: ignore
        time.sleep(max(0.1, delay_ms / 1000.0)) 
        ret, frame = cap.read() # type: ignore
        if ret:
            cv2.imwrite(filename, frame)
            log("SUCCESS: Image saved.")
            write_activity_log(
                timestamp=event_info["timestamp"],
                event_id=event_info["event_id"],
                target_user=event_info["target_user"],
                workstation=event_info["workstation"],
                action=f"{evt_desc} capture event - {os.path.basename(filename)}",
                status=status_text,
                image_name=os.path.basename(filename),
                capture_success=True
            )
        else:
            log("ERROR: Frame read failed after opening.")
            write_activity_log(
                timestamp=event_info["timestamp"],
                event_id=event_info["event_id"],
                target_user=event_info["target_user"],
                workstation=event_info["workstation"],
                action=f"{evt_desc} detected - Frame read failed",
                status=status_text,
                image_name=None,
                capture_success=False
            )
            
        if cap is not None:
            cap.release() # type: ignore
        return ret
    except Exception as e:
        log(f"CRITICAL WORKER ERROR: {str(e)}")
        write_activity_log(
            timestamp=event_info["timestamp"],
            event_id=event_info["event_id"],
            target_user=event_info["target_user"],
            workstation=event_info["workstation"],
            action=f"{evt_desc} detected - Exception: {str(e)[:40]}",
            status=status_text,
            image_name=None,
            capture_success=False
        )
        return False

# ── ICON RENDERING HELPERS ──

def _draw_shield_icon(size: int, rgb=(255, 255, 255), alpha=220) -> ctk.CTkImage:
    """Crisp anti-aliased shield via 4× supersampling."""
    sc = 4
    s = size * sc
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    p = max(s // 9, 2)
    r, g, b = rgb
    pts = [(s//2, p), (s-p, p+s//5), (s-p, s*3//5), (s//2, s-p), (p, s*3//5), (p, p+s//5)]
    d.polygon(pts, fill=(r, g, b, alpha))
    img = img.resize((size, size), Image.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))


def _draw_cross_icon(size: int, rgb=(240, 128, 128), alpha=220) -> ctk.CTkImage:
    """Crisp anti-aliased × icon via 4× supersampling."""
    sc = 4
    s = size * sc
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    p = max(s // 6, 3)
    lw = max(s // 7, 3)
    r, g, b = rgb
    d.line([(p, p), (s-p, s-p)], fill=(r, g, b, alpha), width=lw)
    d.line([(s-p, p), (p, s-p)], fill=(r, g, b, alpha), width=lw)
    img = img.resize((size, size), Image.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))


# ── UI IMPLEMENTATION ──

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class IntruderGuardApp(ctk.CTk):
    # Enterprise Light Security Theme — Material Design 3
    BG          = "#fdf7ff"
    NAV_BG      = "#f8f2fa"
    SURFACE     = "#ffffff"
    SURFACE2    = "#f2ecf4"
    SURFACE3    = "#ece6ee"
    BORDER      = "#cbc4d2"
    BORDER_DIM  = "#e6e0e9"
    ACCENT      = "#4f378a"
    ACCENT_MED  = "#6750a4"
    ACCENT_LIGHT= "#e9ddff"
    ACCENT_HVR  = "#3d2870"
    GREEN       = "#1a7a3f"
    GREEN_BG    = "#d1fae5"
    RED         = "#ba1a1a"
    RED_BG      = "#ffdad6"
    AMBER       = "#765b00"
    AMBER_BG    = "#fff3cd"
    BLUE        = "#0284c7"
    BLUE_BG     = "#e0f2fe"
    TEXT        = "#1d1b20"
    TEXT_SEC    = "#494551"
    TEXT_DIM    = "#7a7582"

    # ── Typography ──
    FONT_TITLE  = ("Segoe UI Variable Display", 22, "bold")
    FONT_HEAD   = ("Segoe UI Variable Text", 14, "bold")
    FONT_BODY   = ("Segoe UI Variable Text", 13, "normal")
    FONT_SMALL  = ("Segoe UI Variable Text", 11, "normal")
    FONT_MONO   = ("Consolas", 11, "normal")
    FONT_STAT   = ("Segoe UI Variable Display", 26, "bold")
    FONT_NAV    = ("Segoe UI Variable Text", 13, "normal")
    FONT_PILL   = ("Segoe UI Variable Text", 11, "bold")
    FONT_LABEL  = ("Segoe UI Variable Text", 10, "bold")

    # ── Layout ──
    NAV_WIDTH   = 240
    RADIUS      = 8
    RADIUS_SM   = 6
    PAD         = 24
    PAD_SM      = 16

    def __init__(self):
        super().__init__()
        self.title("IntruderGuard")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.resizable(True, True)
        self.configure(fg_color=self.BG)

        # State
        self._active = check_system_state()
        self._attempts = 0
        self._photos   = 0
        self._save_path = get_gallery_path()
        self._initial_load_complete = False
        self._unread_notifications = 0
        self._bell_badges = []

        # Icons (pre-rendered for crisp HiDPI display)
        self._icon_shield_btn = _draw_shield_icon(14, (255, 255, 255))
        self._icon_shield_nav = _draw_shield_icon(16, (255, 255, 255))
        self._icon_shield_sm  = _draw_shield_icon(11, (79, 55, 138))
        self._icon_cross_btn  = _draw_cross_icon(14, (186, 26, 26))

        # Build layout
        self._build_body()
        self._refresh_status()
        self._load_gallery()
        self._apply_retention_policy()
        self._initial_load_complete = True
        self._auto_refresh_loop()

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color=self.BG, corner_radius=0)
        body.pack(fill="both", expand=True)
        self._build_sidebar(body)
        self._build_main(body)

    def _build_sidebar(self, parent):
        nav = ctk.CTkFrame(parent, fg_color=self.NAV_BG, width=self.NAV_WIDTH, corner_radius=0)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        # Right border line
        ctk.CTkFrame(nav, fg_color=self.BORDER_DIM, width=1, corner_radius=0).pack(side="right", fill="y")

        nav_inner = ctk.CTkFrame(nav, fg_color="transparent", corner_radius=0)
        nav_inner.pack(fill="both", expand=True, side="left")

        # Logo
        logo_f = ctk.CTkFrame(nav_inner, fg_color="transparent")
        logo_f.pack(fill="x", padx=20, pady=(22, 0))
        ctk.CTkLabel(logo_f, text="IntruderGuard",
                     font=("Segoe UI Variable Display", 17, "bold"),
                     text_color=self.ACCENT).pack(anchor="w")
        ctk.CTkLabel(logo_f, text="Admin Console",
                     font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(anchor="w")

        ctk.CTkFrame(nav_inner, fg_color=self.BORDER_DIM, height=1).pack(fill="x", padx=16, pady=(16, 10))

        # Nav items
        self._nav_buttons = {}
        nav_items = [
            ("dashboard", "⊞", "Dashboard"),
            ("gallery",   "⊡", "Evidence Gallery"),
            ("logs",      "☰", "System Logs"),
            ("settings",  "⚙", "Settings"),
        ]
        for key, icon, label in nav_items:
            btn = ctk.CTkButton(
                nav_inner, text=f"  {icon}   {label}", font=self.FONT_NAV, anchor="w",
                height=38, corner_radius=6,
                fg_color="transparent", text_color=self.TEXT_SEC,
                hover_color=self.SURFACE3, border_width=0,
                command=lambda k=key: self._switch_page(k)
            )
            btn.pack(fill="x", padx=10, pady=1)
            self._nav_buttons[key] = btn

        self._gallery_badge = ctk.CTkLabel(
            self._nav_buttons["gallery"], text="0",
            font=("Segoe UI Variable Text", 9, "bold"),
            text_color="white", fg_color=self.RED,
            corner_radius=10, width=18, height=18
        )
        self._gallery_badge.place(relx=0.88, rely=0.5, anchor="center")
        self._gallery_badge.place_forget()

        # Spacer
        ctk.CTkFrame(nav_inner, fg_color="transparent").pack(fill="both", expand=True)

        # Emergency Lock
        ctk.CTkButton(
            nav_inner, text="  🔒  Emergency Lock", anchor="w",
            font=("Segoe UI Variable Text", 12, "bold"),
            height=38, corner_radius=6,
            fg_color=self.RED_BG, hover_color="#f5c6c6",
            text_color=self.RED, border_width=0,
            command=self._emergency_lock
        ).pack(fill="x", padx=10, pady=(0, 4))

        ctk.CTkFrame(nav_inner, fg_color=self.BORDER_DIM, height=1).pack(fill="x", padx=16, pady=4)

        ctk.CTkButton(
            nav_inner, text="  ?   Help Center", font=self.FONT_NAV, anchor="w",
            height=30, corner_radius=6,
            fg_color="transparent", text_color=self.TEXT_DIM,
            hover_color=self.SURFACE3, border_width=0,
            command=self._show_about
        ).pack(fill="x", padx=10)
        ctk.CTkButton(
            nav_inner, text="  ↪   Logout", font=self.FONT_NAV, anchor="w",
            height=30, corner_radius=6,
            fg_color="transparent", text_color=self.TEXT_DIM,
            hover_color=self.SURFACE3, border_width=0,
            command=self._logout
        ).pack(fill="x", padx=10, pady=(0, 4))

        ctk.CTkFrame(nav_inner, fg_color=self.BORDER_DIM, height=1).pack(fill="x", padx=16, pady=4)

        # User info
        user_f = ctk.CTkFrame(nav_inner, fg_color="transparent")
        user_f.pack(fill="x", padx=14, pady=(4, 16))
        av = ctk.CTkFrame(user_f, fg_color=self.ACCENT_LIGHT, width=32, height=32, corner_radius=16)
        av.pack(side="left"); av.pack_propagate(False)
        ctk.CTkLabel(av, text="A", font=("Segoe UI Variable Text", 13, "bold"),
                     text_color=self.ACCENT).place(relx=0.5, rely=0.5, anchor="center")
        ut = ctk.CTkFrame(user_f, fg_color="transparent")
        ut.pack(side="left", padx=8)
        ctk.CTkLabel(ut, text="Admin Console", font=("Segoe UI Variable Text", 11, "bold"),
                     text_color=self.TEXT).pack(anchor="w")
        self._sidebar_status_lbl = ctk.CTkLabel(ut, text="VERIFIED SESSION", font=("Segoe UI Variable Text", 9),
                     text_color=self.GREEN)
        self._sidebar_status_lbl.pack(anchor="w")

    def _switch_page(self, key: str):
        for k, btn in self._nav_buttons.items():
            btn.configure(fg_color="transparent", text_color=self.TEXT_SEC)
        self._nav_buttons[key].configure(fg_color=self.ACCENT_LIGHT, text_color=self.ACCENT)
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
        self._known_files = set()
        self._pages = {}
        self._build_page_dashboard()
        self._build_page_gallery()
        self._build_page_logs()
        self._build_page_settings()
        self._switch_page("dashboard")

    def _build_topbar(self, parent, title, subtitle=None, btn1=None, btn2=None):
        bar = ctk.CTkFrame(parent, fg_color=self.SURFACE, corner_radius=0)
        bar.pack(fill="x")
        ctk.CTkFrame(bar, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=self.PAD, pady=10)
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")
        ctk.CTkLabel(left, text=title, font=self.FONT_HEAD, text_color=self.TEXT).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(left, text=subtitle, font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(anchor="w")
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right")
        av = ctk.CTkFrame(right, fg_color=self.ACCENT_LIGHT, width=28, height=28, corner_radius=14)
        av.pack(side="right", padx=(6, 0)); av.pack_propagate(False)
        ctk.CTkLabel(av, text="A", font=("Segoe UI Variable Text", 11, "bold"),
                     text_color=self.ACCENT).place(relx=0.5, rely=0.5, anchor="center")

        b1_w = None
        b2_w = None
        if btn2:
            b2_w = ctk.CTkButton(right, text=btn2[0], height=32, corner_radius=6,
                          fg_color=self.ACCENT, hover_color=self.ACCENT_HVR,
                          text_color="white", font=self.FONT_SMALL,
                          command=btn2[1])
            b2_w.pack(side="right", padx=(4, 0))
        if btn1:
            b1_w = ctk.CTkButton(right, text=btn1[0], height=32, corner_radius=6,
                          fg_color=self.SURFACE, hover_color=self.SURFACE2,
                          text_color=self.TEXT_SEC, font=self.FONT_SMALL,
                          border_width=1, border_color=self.BORDER,
                          command=btn1[1])
            b1_w.pack(side="right", padx=4)
        return bar, b1_w, b2_w

    def _build_page_dashboard(self):
        page = ctk.CTkFrame(self._page_host, fg_color=self.BG, corner_radius=0)
        self._pages["dashboard"] = page

        _, _, self._topbar_protection_btn = self._build_topbar(
            page, "Dashboard", "Protection status and system activity",
            btn1=("System Diagnostics", self._run_diagnostics),
            btn2=("⏸  Pause Protection", self._toggle_protection)
        )

        scroll = ctk.CTkScrollableFrame(page, fg_color=self.BG, corner_radius=0,
                                        scrollbar_button_color=self.BORDER_DIM)
        scroll.pack(fill="both", expand=True)

        # ── Hero status card ──
        self._status_card = ctk.CTkFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                                         border_width=1, border_color=self.BORDER_DIM)
        self._status_card.pack(fill="x", padx=self.PAD, pady=(self.PAD, 12))
        inner = ctk.CTkFrame(self._status_card, fg_color="transparent")
        inner.pack(fill="x", padx=self.PAD, pady=self.PAD)

        self._status_icon_frame = ctk.CTkFrame(inner, fg_color=self.RED_BG, width=56, height=56, corner_radius=28)
        self._status_icon_frame.pack(side="left")
        self._status_icon_frame.pack_propagate(False)
        self._status_icon_label = ctk.CTkLabel(
            self._status_icon_frame, text="✗",
            font=("Segoe UI Variable Text", 24, "bold"), text_color=self.RED, fg_color="transparent"
        )
        self._status_icon_label.place(relx=0.5, rely=0.5, anchor="center")

        txt = ctk.CTkFrame(inner, fg_color="transparent")
        txt.pack(side="left", fill="both", expand=True, padx=(16, 12))
        self._headline_lbl = ctk.CTkLabel(
            txt, text="Protection Engine Inactive",
            font=("Segoe UI Variable Display", 16, "bold"), text_color=self.TEXT, anchor="w"
        )
        self._headline_lbl.pack(anchor="w")
        meta = ctk.CTkFrame(txt, fg_color="transparent")
        meta.pack(anchor="w", pady=(4, 0))
        self._uptime_lbl = ctk.CTkLabel(meta, text="● Uptime: —", font=self.FONT_SMALL, text_color=self.TEXT_DIM)
        self._uptime_lbl.pack(side="left")
        self._scan_lbl = ctk.CTkLabel(meta, text="   ● Last scan: never", font=self.FONT_SMALL, text_color=self.TEXT_DIM)
        self._scan_lbl.pack(side="left")
        self._pill_frame = ctk.CTkFrame(txt, fg_color=self.RED_BG, corner_radius=12)
        self._pill_frame.pack(anchor="w", pady=(8, 0))
        self._pill_dot = ctk.CTkLabel(self._pill_frame, text="●", font=("Segoe UI Variable Text", 8), text_color=self.RED)
        self._pill_dot.pack(side="left", padx=(8, 0), pady=3)
        self._pill_text = ctk.CTkLabel(self._pill_frame, text="Monitoring disabled", font=self.FONT_PILL, text_color=self.RED)
        self._pill_text.pack(side="left", padx=(4, 10), pady=3)

        btn_col = ctk.CTkFrame(inner, fg_color="transparent")
        btn_col.pack(side="right", anchor="center")
        self._main_btn = ctk.CTkButton(
            btn_col, text="  Activate", image=self._icon_shield_btn, compound="left",
            font=("Segoe UI Variable Text", 13, "bold"),
            fg_color=self.ACCENT, hover_color=self.ACCENT_HVR,
            text_color="white", height=38, width=160, corner_radius=self.RADIUS_SM,
            command=self._toggle_protection
        )
        self._main_btn.pack()

        # ── Stats row ──
        stats_row = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_row.pack(fill="x", padx=self.PAD, pady=(0, 12))
        stats_row.columnconfigure((0, 1, 2), weight=1, uniform="st")

        def make_stat(col, label, value, sub):
            card = ctk.CTkFrame(stats_row, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                                border_width=1, border_color=self.BORDER_DIM)
            card.grid(row=0, column=col, sticky="nsew",
                      padx=(0 if col == 0 else 6, 0 if col == 2 else 6))
            ctk.CTkLabel(card, text=label.upper(), font=self.FONT_LABEL,
                         text_color=self.TEXT_DIM).pack(anchor="w", padx=self.PAD_SM, pady=(self.PAD_SM, 0))
            val = ctk.CTkLabel(card, text=value, font=self.FONT_STAT, text_color=self.TEXT)
            val.pack(anchor="w", padx=self.PAD_SM, pady=(2, 0))
            ctk.CTkLabel(card, text=sub, font=self.FONT_SMALL,
                         text_color=self.TEXT_DIM).pack(anchor="w", padx=self.PAD_SM, pady=(0, self.PAD_SM))
            return val

        self._attempts_lbl = make_stat(0, "Total Incidents (30d)", "0", "Failed login attempts captured")
        self._photos_lbl   = make_stat(1, "Photos Saved", "0", f"Stored in {os.path.basename(self._save_path)}")
        self._cam_lbl      = make_stat(2, "Camera Status", "Ready", "Device 0 · Auto-detected")

        # ── Recent Incidents ──
        inc_hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        inc_hdr.pack(fill="x", padx=self.PAD, pady=(4, 8))
        ctk.CTkLabel(inc_hdr, text="Recent Security Incidents", font=self.FONT_HEAD, text_color=self.TEXT).pack(side="left")
        ctk.CTkButton(inc_hdr, text="View All Gallery →", font=self.FONT_SMALL,
                      fg_color="transparent", text_color=self.ACCENT, hover_color=self.ACCENT_LIGHT,
                      height=28, corner_radius=6, border_width=0,
                      command=lambda: self._switch_page("gallery")).pack(side="right")

        self._incidents_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._incidents_frame.pack(fill="x", padx=self.PAD, pady=(0, 12))
        self._incidents_placeholder = ctk.CTkFrame(self._incidents_frame, fg_color=self.SURFACE,
                                                    corner_radius=self.RADIUS,
                                                    border_width=1, border_color=self.BORDER_DIM)
        self._incidents_placeholder.pack(fill="x")
        ctk.CTkLabel(self._incidents_placeholder,
                     text="No security incidents captured yet.\nActivate protection to begin monitoring.",
                     font=self.FONT_BODY, text_color=self.TEXT_DIM, justify="center").pack(pady=28)

        # ── Quick Actions ──
        ctk.CTkLabel(scroll, text="QUICK ACTIONS", font=self.FONT_LABEL,
                     text_color=self.TEXT_DIM).pack(anchor="w", padx=self.PAD, pady=(4, 4))
        action_list = ctk.CTkFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                                   border_width=1, border_color=self.BORDER_DIM)
        action_list.pack(fill="x", padx=self.PAD, pady=(0, 12))
        self._add_action_row(action_list, "📷", "Test Camera",
                             "Preview webcam feed to verify capture is working",
                             btn_text="Test", btn_cmd=self._test_camera, divider=False)
        self._add_action_row(action_list, "📁", "Save Location",
                             desc_var_name="_save_path_desc",
                             btn_text="Browse", btn_cmd=self._change_folder)

        # ── Live System Logs ──
        logs_hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        logs_hdr.pack(fill="x", padx=self.PAD, pady=(4, 4))
        ctk.CTkLabel(logs_hdr, text="Live System Logs", font=self.FONT_HEAD, text_color=self.TEXT).pack(side="left")
        badge_f = ctk.CTkFrame(logs_hdr, fg_color=self.GREEN_BG, corner_radius=10)
        badge_f.pack(side="left", padx=10)
        ctk.CTkLabel(badge_f, text="● AUTO-REFRESH ON",
                     font=("Segoe UI Variable Text", 9, "bold"), text_color=self.GREEN).pack(padx=8, pady=2)
        ctk.CTkButton(logs_hdr, text="View All Logs →", font=self.FONT_SMALL,
                      fg_color="transparent", text_color=self.ACCENT, hover_color=self.ACCENT_LIGHT,
                      height=28, corner_radius=6, border_width=0,
                      command=lambda: self._switch_page("logs")).pack(side="right")

        log_table = ctk.CTkFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                                 border_width=1, border_color=self.BORDER_DIM)
        log_table.pack(fill="x", padx=self.PAD, pady=(0, self.PAD))

        # Table header row
        th = ctk.CTkFrame(log_table, fg_color=self.SURFACE2, corner_radius=0)
        th.pack(fill="x")
        ctk.CTkFrame(th, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
        th_inner = ctk.CTkFrame(th, fg_color="transparent")
        th_inner.pack(fill="x", padx=self.PAD_SM, pady=6)
        for col_text, col_w in [("Timestamp", 150), ("Event ID", 72), ("Target User Account", 0), ("Action Taken", 130), ("Status", 95)]:
            lbl_kwargs = {"text": col_text, "font": self.FONT_LABEL, "text_color": self.TEXT_DIM, "anchor": "w"}
            if col_w > 0:
                lbl_kwargs["width"] = col_w
            ctk.CTkLabel(th_inner, **lbl_kwargs).pack(side="left", padx=(0, 6))

        self._log_rows_frame = ctk.CTkScrollableFrame(log_table, fg_color="transparent",
                                                       corner_radius=0, height=160,
                                                       scrollbar_button_color=self.BORDER_DIM)
        self._log_rows_frame.pack(fill="x")
        self._add_log_entry("info", "auto", "IntruderGuard started", "DOCUMENTED")

    def _add_action_row(self, parent, icon, title, desc="", desc_var_name=None, btn_text="", btn_cmd=None, divider=True):
        if divider:
            ctk.CTkFrame(parent, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x")
        row = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        row.pack(fill="x")
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=self.PAD_SM, pady=10)
        icon_box = ctk.CTkFrame(inner, fg_color=self.SURFACE2, width=34, height=34, corner_radius=6)
        icon_box.pack(side="left"); icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text=icon, font=("Segoe UI Emoji", 14),
                     fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
        txt_frame = ctk.CTkFrame(inner, fg_color="transparent")
        txt_frame.pack(side="left", fill="both", expand=True, padx=12)
        ctk.CTkLabel(txt_frame, text=title, font=self.FONT_BODY, text_color=self.TEXT, anchor="w").pack(anchor="w")
        if desc_var_name:
            lbl = ctk.CTkLabel(txt_frame, text=self._save_path, font=self.FONT_SMALL,
                               text_color=self.TEXT_DIM, anchor="w")
            lbl.pack(anchor="w")
            setattr(self, desc_var_name, lbl)
        else:
            ctk.CTkLabel(txt_frame, text=desc, font=self.FONT_SMALL,
                         text_color=self.TEXT_DIM, anchor="w").pack(anchor="w")
        ctk.CTkButton(inner, text=btn_text, font=self.FONT_SMALL, text_color=self.TEXT_SEC,
                      fg_color=self.SURFACE2, hover_color=self.SURFACE3, border_width=1,
                      border_color=self.BORDER, height=30, width=72, corner_radius=self.RADIUS_SM,
                      command=btn_cmd).pack(side="right")

    def _add_log_entry(self, dot_type: str, timestamp: str, message: str, tag: str, image_path: str = None):
        from datetime import datetime as _dt
        ts = _dt.now().strftime("%Y-%m-%d  %H:%M:%S") if timestamp == "auto" else timestamp
        badge_colors = {
            "DENIED":     (self.RED,   self.RED_BG),
            "BLOCKED":    (self.RED,   self.RED_BG),
            "FLAGGED":    (self.AMBER, self.AMBER_BG),
            "FAILURE":    (self.RED,   self.RED_BG),
            "ok":         (self.GREEN, self.GREEN_BG),
            "OK":         (self.GREEN, self.GREEN_BG),
            "DOCUMENTED": (self.BLUE,  self.BLUE_BG),
            "INFO":       (self.BLUE,  self.BLUE_BG),
        }
        tc, bg = badge_colors.get(tag, badge_colors.get(dot_type, (self.TEXT_DIM, self.SURFACE2)))
        row = ctk.CTkFrame(self._log_rows_frame, fg_color="transparent", corner_radius=0)
        row.pack(fill="x")
        ctk.CTkFrame(row, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=self.PAD_SM, pady=6)
        ctk.CTkLabel(inner, text=ts, font=self.FONT_MONO, text_color=self.TEXT_DIM,
                     width=148, anchor="w").pack(side="left")
        eid_f = ctk.CTkFrame(inner, fg_color=self.AMBER_BG, corner_radius=4)
        eid_f.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(eid_f, text="● 4625", font=("Segoe UI Variable Text", 10, "bold"),
                     text_color=self.AMBER).pack(padx=6, pady=1)
        ctk.CTkLabel(inner, text=message, font=self.FONT_SMALL, text_color=self.TEXT_SEC,
                     anchor="w").pack(side="left", fill="x", expand=True)
                     
        if image_path and os.path.exists(image_path):
            btn = ctk.CTkButton(inner, text="👁️ View Photo", font=self.FONT_SMALL, text_color=self.TEXT_SEC,
                                fg_color=self.SURFACE2, hover_color=self.SURFACE3, border_width=1,
                                border_color=self.BORDER, height=22, width=90, corner_radius=self.RADIUS_SM,
                                command=lambda p=image_path: open_file(p))
            btn.pack(side="left", padx=(0, 20))
        else:
            ctk.CTkLabel(inner, text="—", font=self.FONT_SMALL, text_color=self.TEXT_DIM,
                         width=110, anchor="w").pack(side="left")
                         
        ctk.CTkLabel(inner, text=tag, font=("Segoe UI Variable Text", 10, "bold"),
                     text_color=tc, fg_color=bg, corner_radius=4, width=85, height=20).pack(side="right", padx=4)

    def _build_page_gallery(self):
        page = ctk.CTkFrame(self._page_host, fg_color=self.BG, corner_radius=0)
        self._pages["gallery"] = page

        self._build_topbar(page, "Evidence Gallery", "Captured intruder photos and forensic data",
                           btn1=("Export Report", self._export_gallery_report),
                           btn2=("Deploy Agent", self._deploy_agent))

        # Sub-header bar
        fbar = ctk.CTkFrame(page, fg_color=self.SURFACE, corner_radius=0)
        fbar.pack(fill="x")
        ctk.CTkFrame(fbar, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
        fbar_inner = ctk.CTkFrame(fbar, fg_color="transparent")
        fbar_inner.pack(fill="x", padx=self.PAD, pady=8)
        self._gallery_sub_lbl = ctk.CTkLabel(fbar_inner, text="0 Incidents Captured",
                                              font=("Segoe UI Variable Text", 12, "bold"), text_color=self.TEXT)
        self._gallery_sub_lbl.pack(side="left")
        ctk.CTkLabel(fbar_inner, text="  |  Active Monitoring Enabled",
                     font=self.FONT_SMALL, text_color=self.ACCENT).pack(side="left")

        # Main split
        main_split = ctk.CTkFrame(page, fg_color=self.BG, corner_radius=0)
        main_split.pack(fill="both", expand=True)

        left_panel = ctk.CTkFrame(main_split, fg_color=self.BG, corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True)

        self._gallery_empty = ctk.CTkFrame(left_panel, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                                            border_width=1, border_color=self.BORDER_DIM)
        self._gallery_empty.pack(fill="x", padx=self.PAD, pady=self.PAD)
        ctk.CTkLabel(self._gallery_empty,
                     text="🖼\n\nNo intruder photos captured yet.\nActivate protection to start monitoring.",
                     font=self.FONT_BODY, text_color=self.TEXT_DIM, justify="center").pack(pady=36)

        self._gallery_list = ctk.CTkScrollableFrame(left_panel, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                                                     border_width=1, border_color=self.BORDER_DIM,
                                                     scrollbar_button_color=self.BORDER_DIM)

        # Right forensics panel
        right_panel = ctk.CTkFrame(main_split, fg_color=self.SURFACE, width=210, corner_radius=0)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        ctk.CTkFrame(right_panel, fg_color=self.BORDER_DIM, width=1, corner_radius=0).pack(side="left", fill="y")
        rp = ctk.CTkFrame(right_panel, fg_color="transparent")
        rp.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(rp, text="Forensic Analysis", font=self.FONT_HEAD, text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(rp, text="🔍", font=("Segoe UI Emoji", 36)).pack(pady=24)
        ctk.CTkLabel(rp, text="Select an incident to view\ndeep forensic metadata.",
                     font=self.FONT_SMALL, text_color=self.TEXT_DIM, justify="center").pack()

    def _delete_json_log_by_image(self, filename):
        activity_log_file = os.path.join(INSTALL_DIR, "activity_logs.json")
        if os.path.exists(activity_log_file):
            try:
                with open(activity_log_file, "r") as f:
                    logs = json.load(f)
                logs = [log for log in logs if log.get("image_name") != filename]
                with open(activity_log_file, "w") as f:
                    json.dump(logs, f, indent=4)
            except: pass

    def _clear_notifications(self):
        self._unread_notifications = 0
        self._update_bell_badges()
        self._show_toast("🔔", "Notifications Cleared", "All security alerts marked as read.")

    def _update_bell_badges(self):
        if hasattr(self, "_bell_badges") and hasattr(self, "_unread_notifications"):
            for badge in self._bell_badges:
                try:
                    if self._unread_notifications > 0:
                        badge.configure(text=str(self._unread_notifications))
                        badge.place(relx=0.75, rely=0.25, anchor="center")
                    else:
                        badge.place_forget()
                except: pass

    def _add_gallery_item(self, filename: str, timestamp: str, target_user: str = "SYSTEM", event_id: str = "4625", action: str = None, status: str = "BLOCKED ATTEMPT", from_json: bool = False):
        if not hasattr(self, "_known_files"): self._known_files = set()
        if filename in self._known_files: return
        self._known_files.add(filename)

        act = action or f"Intruder capture event - {filename}"

        if not from_json:
            self._add_log_entry(
                "ok",
                timestamp,
                act,
                "FAILURE" if status == "BLOCKED ATTEMPT" else "DOCUMENTED",
                image_path=os.path.join(self._save_path, filename)
            )
            self._add_full_log_entry(
                timestamp,
                event_id,
                "intruder_guard.py",
                target_user,
                act,
                status,
                image_path=os.path.join(self._save_path, filename)
            )

        self._gallery_empty.pack_forget()
        if not self._gallery_list.winfo_ismapped():
            self._gallery_list.pack(fill="both", expand=True, padx=self.PAD, pady=(0, self.PAD))

        row = ctk.CTkFrame(self._gallery_list, fg_color="transparent")
        row.pack(fill="x", pady=2)

        thumb = ctk.CTkFrame(row, fg_color="#1a1a2e", width=80, height=56, corner_radius=6)
        thumb.pack(side="left", padx=(4, 0), pady=4); thumb.pack_propagate(False)

        img_path = os.path.join(self._save_path, filename)
        loaded = False
        img_lbl = None
        if os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path)
                w, h = pil_img.size
                aspect = w / h
                target_aspect = 80 / 56
                if aspect > target_aspect:
                    new_w = int(h * target_aspect)
                    left = (w - new_w) // 2
                    pil_img = pil_img.crop((left, 0, left + new_w, h))
                else:
                    new_h = int(w / target_aspect)
                    top = (h - new_h) // 2
                    pil_img = pil_img.crop((0, top, w, top + new_h))

                pil_img = pil_img.resize((80, 56), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(80, 56))
                img_lbl = ctk.CTkLabel(thumb, image=ctk_img, text="")
                img_lbl.pack(fill="both", expand=True)
                thumb._img = ctk_img
                loaded = True
            except Exception as e:
                print(f"Error loading gallery thumbnail: {e}")

        if not loaded:
            ctk.CTkLabel(thumb, text="📸", font=("Segoe UI Emoji", 18),
                         text_color="#888").place(relx=0.5, rely=0.65, anchor="center")

        badge_f = ctk.CTkFrame(thumb, fg_color=self.RED, corner_radius=3)
        badge_f.place(x=4, y=4)
        ctk.CTkLabel(badge_f, text="HIGH PRIORITY",
                     font=("Segoe UI Variable Text", 7, "bold"), text_color="white").pack(padx=4, pady=1)

        thumb.bind("<Button-1>", lambda e, p=img_path: open_file(p))
        if img_lbl:
            img_lbl.bind("<Button-1>", lambda e, p=img_path: open_file(p))

        txt = ctk.CTkFrame(row, fg_color="transparent")
        txt.pack(side="left", fill="both", expand=True, padx=12)
        ctk.CTkLabel(txt, text=filename, font=self.FONT_BODY, text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(txt, text=f"Captured: {timestamp}",
                     font=self.FONT_SMALL, text_color=self.TEXT_DIM, anchor="w").pack(anchor="w")
        chip = ctk.CTkFrame(txt, fg_color=self.SURFACE2, corner_radius=4)
        chip.pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(chip, text=f"👤  {target_user}",
                     font=("Segoe UI Variable Text", 10), text_color=self.TEXT_SEC).pack(padx=6, pady=1)

        btn_f = ctk.CTkFrame(row, fg_color="transparent")
        btn_f.pack(side="right", padx=8, pady=4)

        def delete_img(p=os.path.join(self._save_path, filename), r=row, f=filename):
            try:
                if os.path.exists(p): os.remove(p)
                if f in self._known_files: self._known_files.remove(f)
                r.destroy()
                self._delete_json_log_by_image(f)
                self._update_stats_count()
                self._refresh_incident_tiles()
            except Exception as e:
                print(f"Delete failed: {e}")

        ctk.CTkButton(btn_f, text="View", width=58, height=26, corner_radius=6,
                      fg_color=self.SURFACE2, border_width=1, border_color=self.BORDER,
                      text_color=self.TEXT_SEC, font=self.FONT_SMALL,
                      command=lambda p=os.path.join(self._save_path, filename): open_file(p)).pack(side="left", padx=2)
        ctk.CTkButton(btn_f, text="Delete", width=58, height=26, corner_radius=6,
                      fg_color=self.RED_BG, hover_color="#f5c6c6",
                      text_color=self.RED, font=self.FONT_SMALL,
                      command=delete_img).pack(side="left", padx=2)

        ctk.CTkFrame(self._gallery_list, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x")
        self._photos += 1
        n = self._photos
        self._gallery_sub_lbl.configure(text=f"{n} Incident{'s' if n != 1 else ''} Captured")
        self._gallery_badge.configure(text=str(n))
        self._gallery_badge.place(relx=0.88, rely=0.5, anchor="center")
        self._refresh_incident_tiles()

    def _refresh_incident_tiles(self):
        for w in self._incidents_frame.winfo_children():
            w.destroy()
        if not self._known_files:
            ph = ctk.CTkFrame(self._incidents_frame, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                               border_width=1, border_color=self.BORDER_DIM)
            ph.pack(fill="x")
            ctk.CTkLabel(ph, text="No security incidents captured yet.\nActivate protection to begin monitoring.",
                         font=self.FONT_BODY, text_color=self.TEXT_DIM, justify="center").pack(pady=28)
            self._incidents_placeholder = ph
            return
        grid = ctk.CTkFrame(self._incidents_frame, fg_color="transparent")
        grid.pack(fill="x")
        
        newest_files = list(reversed(list(self._known_files)))[:4]
        for i, fname in enumerate(newest_files):
            card = ctk.CTkFrame(grid, fg_color="#1a1a2e", width=155, height=105, corner_radius=self.RADIUS)
            card.grid(row=0, column=i, padx=(0, 6), sticky="w")
            card.pack_propagate(False)
            
            img_frame = ctk.CTkFrame(card, fg_color="transparent", height=80, corner_radius=0)
            img_frame.pack(fill="x", side="top")
            img_frame.pack_propagate(False)
            
            lbl_frame = ctk.CTkFrame(card, fg_color="#1a1a2e", height=25, corner_radius=0)
            lbl_frame.pack(fill="x", side="bottom")
            lbl_frame.pack_propagate(False)
            
            ctk.CTkLabel(lbl_frame, text=fname[:18], font=("Segoe UI Variable Text", 9),
                         text_color="#aaa").place(relx=0.5, rely=0.5, anchor="center")
            
            img_path = os.path.join(self._save_path, fname)
            loaded = False
            if os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    w, h = pil_img.size
                    aspect = w / h
                    target_aspect = 155 / 80
                    if aspect > target_aspect:
                        new_w = int(h * target_aspect)
                        left = (w - new_w) // 2
                        pil_img = pil_img.crop((left, 0, left + new_w, h))
                    else:
                        new_h = int(w / target_aspect)
                        top = (h - new_h) // 2
                        pil_img = pil_img.crop((0, top, w, top + new_h))
                    
                    pil_img = pil_img.resize((155, 80), Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(155, 80))
                    img_lbl = ctk.CTkLabel(img_frame, image=ctk_img, text="")
                    img_lbl.pack(fill="both", expand=True)
                    card._img = ctk_img
                    loaded = True
                except Exception as e:
                    print(f"Error loading thumbnail: {e}")
            
            if not loaded:
                ctk.CTkLabel(img_frame, text="📸", font=("Segoe UI Emoji", 20),
                             text_color="#888").place(relx=0.5, rely=0.5, anchor="center")
            
            bf = ctk.CTkFrame(card, fg_color=self.RED, corner_radius=3)
            bf.place(x=6, y=6)
            ctk.CTkLabel(bf, text="HIGH PRIORITY", font=("Segoe UI Variable Text", 7, "bold"),
                          text_color="white").pack(padx=4, pady=1)
            
            card.bind("<Button-1>", lambda e, p=img_path: open_file(p))
            img_frame.bind("<Button-1>", lambda e, p=img_path: open_file(p))
            lbl_frame.bind("<Button-1>", lambda e, p=img_path: open_file(p))
            if loaded:
                img_lbl.bind("<Button-1>", lambda e, p=img_path: open_file(p))

    def _load_gallery(self):
        # Sync and handle deleted files
        if hasattr(self, "_known_files") and self._known_files:
            if os.path.exists(self._save_path):
                current_disk_files = set([f for f in os.listdir(self._save_path) if f.endswith((".jpg", ".png", ".jpeg"))])
                deleted_files = self._known_files - current_disk_files
                if deleted_files:
                    for f in deleted_files:
                        self._known_files.remove(f)
                    self._refresh_incident_tiles()
                    
                    # Clear gallery list widgets and reload them
                    for w in self._gallery_list.winfo_children():
                        w.destroy()
                    self._known_files.clear()
                    if hasattr(self, "_loaded_log_keys"):
                        self._loaded_log_keys.clear()

        activity_log_file = os.path.join(INSTALL_DIR, "activity_logs.json")
        json_logs = []
        if os.path.exists(activity_log_file):
            try:
                with open(activity_log_file, "r") as f:
                    json_logs = json.load(f)
            except: pass
            
        for log in json_logs:
            timestamp = log.get("timestamp")
            event_id = log.get("event_id", "4625")
            target_user = log.get("target_user", "Unknown")
            workstation = log.get("workstation", "Local")
            action = log.get("action", "")
            status = log.get("status", "BLOCKED ATTEMPT")
            image_name = log.get("image_name")
            capture_success = log.get("capture_success", True)
            
            image_path = None
            if image_name and capture_success:
                image_path = os.path.join(self._save_path, image_name)
            
            log_key = f"{timestamp}_{target_user}_{event_id}"
            if not hasattr(self, "_loaded_log_keys"):
                self._loaded_log_keys = set()
            if log_key in self._loaded_log_keys:
                continue
            self._loaded_log_keys.add(log_key)
            
            is_new = getattr(self, "_initial_load_complete", False)
            
            if image_name and capture_success and os.path.exists(image_path):
                self._add_gallery_item(
                    image_name, timestamp,
                    target_user=target_user, event_id=event_id,
                    action=action, status=status,
                    from_json=True
                )
            else:
                self._add_log_entry(
                    "ok" if capture_success else "info",
                    timestamp,
                    action,
                    "DOCUMENTED" if capture_success else "FAILURE",
                    image_path=None
                )
                self._add_full_log_entry(
                    timestamp,
                    event_id,
                    "intruder_guard.py",
                    target_user,
                    action,
                    status,
                    image_path=None
                )
            
            if is_new:
                self._show_toast(
                    "📸" if capture_success else "⚠️",
                    "Intruder Captured" if capture_success else "Access Attempt",
                    f"User: {target_user} @ {workstation}"
                )
        
        if os.path.exists(self._save_path):
            try:
                files = [f for f in os.listdir(self._save_path) if f.endswith((".jpg", ".png", ".jpeg"))]
                files.sort(reverse=True)
                for f in files:
                    if f not in self._known_files:
                        try:
                            mtime = os.path.getmtime(os.path.join(self._save_path, f))
                            t = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d  %H:%M:%S")
                        except:
                            t = time.ctime(os.path.getmtime(os.path.join(self._save_path, f)))
                        self._add_gallery_item(f, t, target_user="SYSTEM", from_json=False)
            except: pass
        self._update_stats_count()

    def _update_stats_count(self):
        try:
            if not os.path.exists(self._save_path): return
            count = len([f for f in os.listdir(self._save_path) if f.endswith((".jpg", ".png", ".jpeg"))])
            self._photos = count
            self._photos_lbl.configure(text=str(count))
            if hasattr(self, "_gallery_badge"):
                self._gallery_badge.configure(text=str(count))
                if count > 0: self._gallery_badge.place(relx=0.88, rely=0.5, anchor="center")
                else: self._gallery_badge.place_forget()
            if hasattr(self, "_gallery_sub_lbl"):
                n = count
                self._gallery_sub_lbl.configure(text=f"{n} Incident{'s' if n != 1 else ''} Captured")
                if count == 0 and hasattr(self, "_gallery_empty"):
                    self._gallery_empty.pack(fill="x", padx=self.PAD, pady=self.PAD)
            today = datetime.date.today()
            today_count = 0
            for f in os.listdir(self._save_path):
                if f.endswith((".jpg", ".png", ".jpeg")):
                    mtime = datetime.date.fromtimestamp(os.path.getmtime(os.path.join(self._save_path, f)))
                    if mtime == today:
                        today_count += 1
            self._attempts_lbl.configure(text=str(today_count))
        except: pass

    def _auto_refresh_loop(self):
        self._load_gallery()
        self.after(5000, self._auto_refresh_loop)

    def _build_page_logs(self):
        page = ctk.CTkFrame(self._page_host, fg_color=self.BG, corner_radius=0)
        self._pages["logs"] = page

        self._build_topbar(page, "System Logs", "Real-time enterprise event auditing and forensic monitoring",
                           btn1=("Clear History", self._clear_full_logs),
                           btn2=("Export Logs", self._export_system_logs))

        # Filter bar
        fbar = ctk.CTkFrame(page, fg_color=self.SURFACE, corner_radius=0)
        fbar.pack(fill="x")
        ctk.CTkFrame(fbar, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
        fb = ctk.CTkFrame(fbar, fg_color="transparent")
        fb.pack(fill="x", padx=self.PAD, pady=8)
        self._log_data = []
        self._log_filters = {"CRITICAL", "WARNING", "AUDIT"}
        self._filter_btns = {}
        for sev, color, bg in [("CRITICAL", self.RED, self.RED_BG),
                                ("WARNING",  self.AMBER, self.AMBER_BG),
                                ("AUDIT",    self.BLUE, self.BLUE_BG)]:
            btn = ctk.CTkButton(
                fb, text=sev,
                font=("Segoe UI Variable Text", 10, "bold"),
                text_color=color, fg_color=bg,
                hover_color=self.SURFACE3,
                border_width=2, border_color=color,
                height=26, corner_radius=4,
                command=lambda s=sev: self._toggle_log_filter(s)
            )
            btn.pack(side="left", padx=(0, 6))
            self._filter_btns[sev] = btn
        self._logs_count_lbl = ctk.CTkLabel(fb, text="Showing 0 events",
                                             font=self.FONT_SMALL, text_color=self.TEXT_DIM)
        self._logs_count_lbl.pack(side="right")

        # Table
        table_wrap = ctk.CTkFrame(page, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                                   border_width=1, border_color=self.BORDER_DIM)
        table_wrap.pack(fill="both", expand=True, padx=self.PAD, pady=(self.PAD_SM, 0))

        th = ctk.CTkFrame(table_wrap, fg_color=self.SURFACE2, corner_radius=0)
        th.pack(fill="x")
        ctk.CTkFrame(th, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
        th_inner = ctk.CTkFrame(th, fg_color="transparent")
        th_inner.pack(fill="x", padx=self.PAD_SM, pady=8)
        for col_text, col_w in [("Timestamp", 148), ("Event ID", 80), ("Source Process", 120),
                                  ("Target User", 130), ("Action Taken", 0), ("Status", 130)]:
            lbl_kwargs = {"text": col_text, "font": self.FONT_LABEL, "text_color": self.TEXT_DIM, "anchor": "w"}
            if col_w > 0:
                lbl_kwargs["width"] = col_w
            ctk.CTkLabel(th_inner, **lbl_kwargs).pack(side="left", padx=(0, 8))

        self._full_log_frame = ctk.CTkScrollableFrame(table_wrap, fg_color="transparent",
                                                       corner_radius=0,
                                                       scrollbar_button_color=self.BORDER_DIM)
        self._full_log_frame.pack(fill="both", expand=True)
        self._full_log_count = 0

        # Footer
        footer = ctk.CTkFrame(page, fg_color=self.SURFACE2, height=44, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkFrame(footer, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="top")
        fi = ctk.CTkFrame(footer, fg_color="transparent")
        fi.pack(fill="both", expand=True, padx=self.PAD)
        for label, value, color in [("⚠  Critical Alerts (28hr)", "0", self.RED),
                                      ("✓  Audit Success Rate", "—", self.GREEN),
                                      ("🗂  Retention Policy", "90 Days", self.TEXT_DIM)]:
            seg = ctk.CTkFrame(fi, fg_color="transparent")
            seg.pack(side="left", padx=(0, 28))
            ctk.CTkLabel(seg, text=label, font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(side="left")
            ctk.CTkLabel(seg, text=f"  {value}",
                         font=("Segoe UI Variable Text", 12, "bold"), text_color=color).pack(side="left")

    def _add_full_log_entry(self, timestamp, event_id, source, target, action, status, image_path: str = None):
        severity_map = {
            "BLOCKED ATTEMPT":      "CRITICAL",
            "IP QUARANTINE":        "CRITICAL",
            "SESSION TERMINATED":   "CRITICAL",
            "PRIVILEGE ESCALATION": "WARNING",
            "EVENT LOGGED":         "WARNING",
            "FLAGGED":              "WARNING",
            "SUCCESS AUDIT":        "AUDIT",
            "DOCUMENTED":           "AUDIT",
        }
        severity = severity_map.get(status, "AUDIT")
        if not hasattr(self, "_log_data"):
            self._log_data = []
        self._log_data.append({
            "timestamp": timestamp, "event_id": event_id,
            "source": source, "target": target,
            "action": action, "status": status,
            "severity": severity, "image_path": image_path,
        })
        self._render_logs()

    def _clear_full_logs(self):
        if not messagebox.askyesno("Confirm Clear Logs", "Are you sure you want to clear the logs history?"):
            return
        if hasattr(self, "_log_data"):
            self._log_data.clear()
        for w in self._full_log_frame.winfo_children():
            w.destroy()
        self._full_log_count = 0
        if hasattr(self, "_logs_count_lbl"):
            self._logs_count_lbl.configure(text="Showing 0 events")
        if hasattr(self, "_loaded_log_keys"):
            self._loaded_log_keys.clear()
        activity_log_file = os.path.join(INSTALL_DIR, "activity_logs.json")
        try:
            if os.path.exists(activity_log_file):
                os.remove(activity_log_file)
        except: pass
        self._show_toast("🗑️", "Logs Cleared", "Audit log database cleared successfully.")

    def _toggle_log_filter(self, severity: str):
        color_map = {
            "CRITICAL": (self.RED,   self.RED_BG),
            "WARNING":  (self.AMBER, self.AMBER_BG),
            "AUDIT":    (self.BLUE,  self.BLUE_BG),
        }
        btn = self._filter_btns.get(severity)
        if not btn:
            return
        if severity in self._log_filters:
            self._log_filters.discard(severity)
            btn.configure(fg_color=self.SURFACE2, border_color=self.BORDER,
                          text_color=self.TEXT_DIM)
        else:
            self._log_filters.add(severity)
            tc, bg = color_map.get(severity, (self.TEXT_DIM, self.SURFACE2))
            btn.configure(fg_color=bg, border_color=tc, text_color=tc)
        self._render_logs()

    def _render_logs(self):
        if not hasattr(self, "_full_log_frame"):
            return
        for w in self._full_log_frame.winfo_children():
            w.destroy()
        badge_map = {
            "BLOCKED ATTEMPT":      (self.RED,   self.RED_BG),
            "SUCCESS AUDIT":        (self.GREEN, self.GREEN_BG),
            "EVENT LOGGED":         (self.AMBER, self.AMBER_BG),
            "IP QUARANTINE":        (self.RED,   self.RED_BG),
            "SESSION TERMINATED":   (self.RED,   self.RED_BG),
            "PRIVILEGE ESCALATION": (self.AMBER, self.AMBER_BG),
            "DOCUMENTED":           (self.BLUE,  self.BLUE_BG),
            "FLAGGED":              (self.AMBER, self.AMBER_BG),
        }
        log_data = getattr(self, "_log_data", [])
        log_filters = getattr(self, "_log_filters", {"CRITICAL", "WARNING", "AUDIT"})
        visible = [e for e in log_data if e.get("severity", "AUDIT") in log_filters]
        for entry in visible:
            ts  = entry["timestamp"]
            eid = entry["event_id"]
            src = entry["source"]
            tgt = entry["target"]
            act = entry["action"]
            stat = entry["status"]
            img  = entry.get("image_path")
            tc, bg = badge_map.get(stat, (self.TEXT_DIM, self.SURFACE2))
            row = ctk.CTkFrame(self._full_log_frame, fg_color="transparent", corner_radius=0)
            row.pack(fill="x")
            ctk.CTkFrame(row, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=self.PAD_SM, pady=7)
            ctk.CTkLabel(inner, text=ts, font=self.FONT_MONO, text_color=self.TEXT_SEC,
                         width=140, anchor="w").pack(side="left")
            eid_f = ctk.CTkFrame(inner, fg_color=self.AMBER_BG, corner_radius=4)
            eid_f.pack(side="left", padx=(0, 12))
            ctk.CTkLabel(eid_f, text=f"● {eid}",
                         font=("Segoe UI Variable Text", 10, "bold"), text_color=self.AMBER).pack(padx=6, pady=2)
            ctk.CTkLabel(inner, text=src, font=self.FONT_MONO, text_color=self.TEXT_SEC,
                         width=110, anchor="w").pack(side="left")
            ctk.CTkLabel(inner, text=tgt, font=self.FONT_SMALL, text_color=self.TEXT_SEC,
                         width=120, anchor="w").pack(side="left")
            action_frame = ctk.CTkFrame(inner, fg_color="transparent")
            action_frame.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(action_frame, text=act, font=self.FONT_SMALL, text_color=self.TEXT,
                         anchor="w").pack(side="left", fill="x", expand=True)
            if img and os.path.exists(img):
                view_btn = ctk.CTkButton(
                    action_frame, text="👁️ View Photo", font=self.FONT_SMALL,
                    text_color=self.TEXT_SEC, fg_color=self.SURFACE2,
                    hover_color=self.SURFACE3, border_width=1,
                    border_color=self.BORDER, height=22, width=90,
                    corner_radius=self.RADIUS_SM,
                    command=lambda p=img: open_file(p))
                view_btn.pack(side="right", padx=10)
            ctk.CTkLabel(inner, text=stat, font=("Segoe UI Variable Text", 10, "bold"),
                         text_color=tc, fg_color=bg, corner_radius=4, height=22).pack(side="right", padx=4)
        self._full_log_count = len(visible)
        if hasattr(self, "_logs_count_lbl"):
            self._logs_count_lbl.configure(text=f"Showing {self._full_log_count} events")

    def _build_page_settings(self):
        page = ctk.CTkFrame(self._page_host, fg_color=self.BG, corner_radius=0)
        self._pages["settings"] = page

        self._build_topbar(page, "Settings", "Adjust security parameters and device capture behavior",
                           btn1=("Discard", self._discard_settings),
                           btn2=("Save Changes", self._save_settings))

        scroll = ctk.CTkScrollableFrame(page, fg_color=self.BG, corner_radius=0,
                                        scrollbar_button_color=self.BORDER_DIM)
        scroll.pack(fill="both", expand=True)

        # Two-column grid
        cols = ctk.CTkFrame(scroll, fg_color="transparent")
        cols.pack(fill="x", padx=self.PAD, pady=self.PAD)
        cols.columnconfigure(0, weight=3)
        cols.columnconfigure(1, weight=2)

        left_col = ctk.CTkFrame(cols, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # General Protection
        ctk.CTkLabel(left_col, text="GENERAL PROTECTION", font=self.FONT_LABEL,
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(0, 6))
        gp = ctk.CTkFrame(left_col, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                           border_width=1, border_color=self.BORDER_DIM)
        gp.pack(fill="x", pady=(0, 16))
        self._sw_monitoring = self._add_toggle_row(gp, "Enable Monitoring",
                             "Actively track unauthorized physical access.", default=True, divider=False)
        self._sw_startup = self._add_toggle_row(gp, "Run on Startup",
                             "Initialize IntruderGuard when the system boots.", default=False)
        self._sw_death = self._add_toggle_row(gp, "Death Mode",
                             "Hide application process from task manager and tray.", default=False)

        # Webcam Capture
        ctk.CTkLabel(left_col, text="WEBCAM CAPTURE", font=self.FONT_LABEL,
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(4, 6))
        wc = ctk.CTkFrame(left_col, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                           border_width=1, border_color=self.BORDER_DIM)
        wc.pack(fill="x", pady=(0, 16))
        wc_grid = ctk.CTkFrame(wc, fg_color="transparent")
        wc_grid.pack(fill="x", padx=self.PAD_SM, pady=self.PAD_SM)
        wc_grid.columnconfigure(0, weight=1)
        wc_grid.columnconfigure(1, weight=1)
        ctk.CTkLabel(wc_grid, text="Camera Selection", font=self.FONT_SMALL,
                     text_color=self.TEXT_DIM).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(wc_grid, text="Photo Quality", font=self.FONT_SMALL,
                     text_color=self.TEXT_DIM).grid(row=0, column=1, sticky="w", padx=(12, 0))
        self._combo_camera = ctk.CTkComboBox(wc_grid, values=["Integrated HD Webcam (ID: 0)", "USB Camera (ID: 1)"],
                        height=32, corner_radius=6, border_color=self.BORDER, fg_color=self.SURFACE,
                        button_color=self.BORDER, dropdown_fg_color=self.SURFACE,
                        text_color=self.TEXT, font=self.FONT_SMALL
                        )
        self._combo_camera.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self._combo_quality = ctk.CTkComboBox(wc_grid, values=["Original (Highest)", "High", "Medium"],
                        height=32, corner_radius=6, border_color=self.BORDER, fg_color=self.SURFACE,
                        button_color=self.BORDER, dropdown_fg_color=self.SURFACE,
                        text_color=self.TEXT, font=self.FONT_SMALL
                        )
        self._combo_quality.grid(row=1, column=1, sticky="ew", pady=(4, 0), padx=(12, 0))
        ctk.CTkFrame(wc, fg_color=self.BORDER_DIM, height=1).pack(fill="x")
        delay_row = ctk.CTkFrame(wc, fg_color="transparent")
        delay_row.pack(fill="x", padx=self.PAD_SM, pady=self.PAD_SM)
        ctk.CTkLabel(delay_row, text="Capture Delay", font=self.FONT_SMALL,
                     text_color=self.TEXT_DIM).pack(anchor="w")
        self._slider_delay = ctk.CTkSlider(delay_row, from_=0, to=500, number_of_steps=10,
                           progress_color=self.ACCENT, button_color=self.ACCENT,
                           fg_color=self.BORDER_DIM, command=self._on_slider_move)
        self._slider_delay.set(150); self._slider_delay.pack(fill="x", pady=(6, 0))
        dl = ctk.CTkFrame(delay_row, fg_color="transparent")
        dl.pack(fill="x")
        ctk.CTkLabel(dl, text="0ms", font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(side="left")
        
        self._slider_delay_lbl = ctk.CTkLabel(dl, text="150ms", font=("Segoe UI Variable Text", 10, "bold"),
                             text_color=self.ACCENT)
        self._slider_delay_lbl.pack(side="left", expand=True)
        ctk.CTkLabel(dl, text="500ms", font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(side="right")

        # Right column
        right_col = ctk.CTkFrame(cols, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")

        # Security Kernel — event ID selector with per-ID explanations
        # -----------------------------------------------------------
        # Here we define the Windows Event IDs that IntruderGuard monitors:
        # - Event ID 4625: Logon Failure (wrong password, PIN, face recognition, etc.)
        # - Event ID 4624: Logon Success (session started successfully)
        # - Event ID 4735: Security Group Changed (local Administrator group changes)
        # - Event ID 4720: User Account Created (attacker creating a backdoor account)
        ctk.CTkLabel(right_col, text="SECURITY KERNEL", font=self.FONT_LABEL,
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(0, 6))
        de = ctk.CTkFrame(right_col, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                           border_width=1, border_color=self.BORDER_DIM)
        de.pack(fill="x", pady=(0, 16))
        de_in = ctk.CTkFrame(de, fg_color="transparent")
        de_in.pack(fill="x", padx=self.PAD_SM, pady=self.PAD_SM)

        ctk.CTkLabel(de_in, text="Specify Windows Event IDs to trigger\nhigh-priority alerts.",
                     font=self.FONT_SMALL, text_color=self.TEXT_SEC,
                     justify="left", anchor="w").pack(anchor="w", pady=(0, 10))

        # Chip row — one pill per tracked event ID.
        # 4625 is shown first with a "PRIMARY TRIGGER" badge — it is the default ON event.
        chips_row = ctk.CTkFrame(de_in, fg_color="transparent")
        chips_row.pack(anchor="w", pady=(0, 10))
        for eid, bg, fg, is_primary in [
            ("4625", self.RED_BG,   self.RED,   True),
            ("4624", self.AMBER_BG, self.AMBER, False),
            ("4735", self.GREEN_BG, self.GREEN, False),
            ("4720", self.BLUE_BG,  self.BLUE,  False),
        ]:
            wrapper = ctk.CTkFrame(chips_row, fg_color="transparent")
            wrapper.pack(side="left", padx=(0, 8))
            chip = ctk.CTkFrame(wrapper, fg_color=bg, corner_radius=5,
                                border_width=2 if is_primary else 1,
                                border_color=fg)
            chip.pack()
            ctk.CTkLabel(chip, text=eid,
                         font=("Segoe UI Variable Text", 11, "bold"),
                         text_color=fg).pack(padx=8, pady=3)
            if is_primary:
                # Show a small label underneath the 4625 chip
                ctk.CTkLabel(wrapper, text="● DEFAULT ON",
                             font=("Segoe UI Variable Text", 8, "bold"),
                             text_color=self.RED).pack(pady=(2, 0))

        # Per-event descriptions — what each Windows Event ID actually triggers
        for eid, bg, fg, label, desc in [
            ("4625", self.RED_BG,   self.RED,
             "Failed Logon",
             "Fires on wrong password, PIN, or bad credentials — the primary capture trigger."),
            ("4624", self.AMBER_BG, self.AMBER,
             "Successful Logon",
             "Audit trail for successful logins — detects after-hours or unusual session starts."),
            ("4735", self.GREEN_BG, self.GREEN,
             "Security Group Changed",
             "Fires when a local group is modified — early warning for privilege escalation."),
            ("4720", self.BLUE_BG,  self.BLUE,
             "User Created",
             "Fires when a new user account is created — alerts you to unauthorized backdoor accounts."),
        ]:
            r = ctk.CTkFrame(de_in, fg_color="transparent")
            r.pack(fill="x", pady=(0, 6))
            badge = ctk.CTkFrame(r, fg_color=bg, corner_radius=3)
            badge.pack(side="left", anchor="n", pady=2)
            ctk.CTkLabel(badge, text=eid,
                         font=("Segoe UI Variable Text", 9, "bold"),
                         text_color=fg).pack(padx=5, pady=1)
            info = ctk.CTkFrame(r, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=(7, 0))
            ctk.CTkLabel(info, text=label,
                         font=("Segoe UI Variable Text", 10, "bold"),
                         text_color=self.TEXT, anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=desc,
                         font=self.FONT_SMALL, text_color=self.TEXT_SEC,
                         wraplength=200, justify="left", anchor="w").pack(anchor="w")

        ctk.CTkFrame(de, fg_color=self.BORDER_DIM, height=1).pack(fill="x")
        edit_row = ctk.CTkFrame(de, fg_color="transparent")
        edit_row.pack(fill="x", padx=self.PAD_SM, pady=6)
        # Edit button opens the event ID selection dialog (_edit_event_ids)
        ctk.CTkButton(edit_row, text="Edit", width=60, height=26, corner_radius=6,
                      fg_color=self.SURFACE2, hover_color=self.SURFACE3,
                      border_width=1, border_color=self.BORDER,
                      text_color=self.TEXT_SEC, font=self.FONT_SMALL,
                      command=self._edit_event_ids).pack(side="left")

        # Storage & Privacy
        ctk.CTkLabel(right_col, text="STORAGE & PRIVACY", font=self.FONT_LABEL,
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(4, 6))
        sp = ctk.CTkFrame(right_col, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                           border_width=1, border_color=self.BORDER_DIM)
        sp.pack(fill="x", pady=(0, 16))
        sp_in = ctk.CTkFrame(sp, fg_color="transparent")
        sp_in.pack(fill="x", padx=self.PAD_SM, pady=self.PAD_SM)
        ctk.CTkLabel(sp_in, text="Retention Policy", font=self.FONT_SMALL,
                     text_color=self.TEXT_DIM).pack(anchor="w")
        self._combo_retention = ctk.CTkComboBox(sp_in, values=["Delete after 30 days", "Delete after 7 days", "Never delete"],
                        height=32, corner_radius=6, border_color=self.BORDER, fg_color=self.SURFACE,
                        button_color=self.BORDER, dropdown_fg_color=self.SURFACE,
                        text_color=self.TEXT, font=self.FONT_SMALL)
        self._combo_retention.pack(fill="x", pady=(4, 10))
        ctk.CTkLabel(sp_in, text="Local Path", font=self.FONT_SMALL,
                     text_color=self.TEXT_DIM).pack(anchor="w")
        path_row = ctk.CTkFrame(sp_in, fg_color="transparent")
        path_row.pack(fill="x", pady=(4, 10))
        self._path_entry = ctk.CTkEntry(path_row, height=32, corner_radius=6,
                                        fg_color=self.SURFACE, border_color=self.BORDER,
                                        text_color=self.TEXT_SEC, font=self.FONT_MONO)
        self._path_entry.insert(0, self._save_path)
        self._path_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(path_row, text="📁", width=36, height=32, corner_radius=6,
                      fg_color=self.SURFACE2, hover_color=self.SURFACE3, border_width=1,
                      border_color=self.BORDER, text_color=self.TEXT_SEC, font=("Segoe UI Emoji", 13),
                      command=self._change_folder).pack(side="left", padx=(4, 0))
        ctk.CTkButton(sp_in, text="🗑  Wipe Local Evidence Vault", height=32, corner_radius=6,
                      fg_color=self.RED_BG, hover_color="#f5c6c6",
                      text_color=self.RED, font=self.FONT_SMALL,
                      command=self._wipe_vault).pack(fill="x")

        # Version footer
        ver_f = ctk.CTkFrame(scroll, fg_color=self.SURFACE2, corner_radius=self.RADIUS,
                              border_width=1, border_color=self.BORDER_DIM)
        ver_f.pack(fill="x", padx=self.PAD, pady=(0, self.PAD))
        ver_in = ctk.CTkFrame(ver_f, fg_color="transparent")
        ver_in.pack(fill="x", padx=self.PAD_SM, pady=10)
        ctk.CTkLabel(ver_in, text="BUILD: v4.2 • STABLE",
                     font=self.FONT_LABEL, text_color=self.TEXT_SEC).pack(side="left")
        ctk.CTkLabel(ver_in, text="ENCRYPTION: AES-256",
                     font=self.FONT_LABEL, text_color=self.ACCENT).pack(side="right")
        
        # Load the configuration data into inputs
        self._load_settings_into_ui()

    def _edit_event_ids(self):
        """
        Opens a modal dialog that lets the user toggle which Windows Event IDs
        IntruderGuard monitors. Each ID is shown with its name and a description
        of what security event it represents.

        Available Event IDs and their purposes:
        - 4625 : Failed Logon           — Wrong password/PIN attempt (primary capture trigger)
        - 4624 : Successful Logon       — Any successful login session (audit trail)
        - 4735 : Security Group Changed — A local security group was modified (privilege escalation warning)
        - 4720 : User Account Created   — A new user account was created (backdoor detection)
        - 4647 : User-Initiated Logoff  — A user explicitly logged off (session audit)
        - 4648 : Explicit Credential Use— A process ran using explicit alternate credentials (lateral movement)

        Changes are saved immediately to config.json when the user clicks 'Save'.
        The scheduled task is re-registered so the new XPath event filter takes effect.
        """
        config = load_config()
        current_ids = set(config.get("event_ids", ["4625"]))

        # All known event IDs with metadata.
        # is_default=True marks Event ID 4625 as the primary required trigger.
        # It is always pre-toggled ON in the dialog, and cannot be turned off alone.
        ALL_EVENT_IDS = [
            ("4625", "Failed Logon",
             "Wrong password, PIN, or bad credentials.\nPrimary webcam capture trigger.",
             self.RED_BG, self.RED, True),   # <-- is_default=True
            ("4624", "Successful Logon",
             "Any successful login session started.\nDetects after-hours or unusual access.",
             self.AMBER_BG, self.AMBER, False),
            ("4735", "Security Group Changed",
             "A local security group was modified.\nEarly warning for privilege escalation.",
             self.GREEN_BG, self.GREEN, False),
            ("4720", "User Account Created",
             "A new local user account was created.\nAlerts on unauthorized backdoor accounts.",
             self.BLUE_BG, self.BLUE, False),
            ("4647", "User-Initiated Logoff",
             "A user explicitly logged off their session.\nUseful for session audit trails.",
             self.SURFACE2, self.TEXT_SEC, False),
            ("4648", "Explicit Credential Logon",
             "A process ran using alternate credentials.\nDetects lateral movement attacks.",
             self.AMBER_BG, self.AMBER, False),
        ]

        dlg = ctk.CTkToplevel(self)
        dlg.title("Edit Monitored Event IDs")
        dlg.geometry("480x560")
        dlg.configure(fg_color=self.BG)
        dlg.resizable(False, False)
        dlg.attributes("-topmost", True)
        dlg.grab_set()  # Make modal

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color=self.SURFACE, height=52, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkFrame(hdr, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
        ctk.CTkLabel(hdr, text="  🛡️  Monitored Windows Event IDs",
                     font=self.FONT_HEAD, text_color=self.TEXT,
                     fg_color="transparent").pack(side="left", padx=16, pady=14)

        # Subtitle
        sub = ctk.CTkFrame(dlg, fg_color=self.SURFACE2, corner_radius=0)
        sub.pack(fill="x")
        ctk.CTkLabel(sub,
                     text="Toggle which security events trigger IntruderGuard. Changes apply on Save.",
                     font=self.FONT_SMALL, text_color=self.TEXT_DIM,
                     fg_color="transparent").pack(anchor="w", padx=16, pady=8)

        # Scrollable list of event IDs
        scroll = ctk.CTkScrollableFrame(dlg, fg_color=self.BG, corner_radius=0,
                                        scrollbar_button_color=self.BORDER_DIM)
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        switches = {}  # eid -> CTkSwitch

        for eid, name, desc, bg, fg, is_default in ALL_EVENT_IDS:
            # 4625 (Failed Logon) always gets a highlighted card — it is the default primary trigger
            card_border = self.RED if is_default else self.BORDER_DIM
            card = ctk.CTkFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                                border_width=2 if is_default else 1,
                                border_color=card_border)
            card.pack(fill="x", pady=(0, 8))
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)

            # Colored Event ID badge
            badge = ctk.CTkFrame(inner, fg_color=bg, corner_radius=4)
            badge.pack(side="left", anchor="n", pady=2)
            ctk.CTkLabel(badge, text=eid,
                         font=("Segoe UI Variable Text", 11, "bold"),
                         text_color=fg).pack(padx=8, pady=3)

            # Name + description
            info = ctk.CTkFrame(inner, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=(10, 0))

            # Name row with optional DEFAULT pill
            name_row = ctk.CTkFrame(info, fg_color="transparent")
            name_row.pack(anchor="w", fill="x")
            ctk.CTkLabel(name_row, text=name,
                         font=("Segoe UI Variable Text", 12, "bold"),
                         text_color=self.TEXT, anchor="w").pack(side="left")
            if is_default:
                # Show a "DEFAULT ON" pill to signal this is the primary trigger
                pill = ctk.CTkFrame(name_row, fg_color=self.RED, corner_radius=4)
                pill.pack(side="left", padx=(8, 0))
                ctk.CTkLabel(pill, text="DEFAULT ON",
                             font=("Segoe UI Variable Text", 8, "bold"),
                             text_color="white").pack(padx=5, pady=1)

            ctk.CTkLabel(info, text=desc,
                         font=self.FONT_SMALL, text_color=self.TEXT_SEC,
                         wraplength=240, justify="left", anchor="w").pack(anchor="w")

            # Toggle switch
            sw = ctk.CTkSwitch(inner, text="", width=44,
                               progress_color=fg,
                               button_color="white", button_hover_color=self.SURFACE3)
            if eid in current_ids:
                sw.select()
            sw.pack(side="right", anchor="center")
            switches[eid] = sw

        # Footer buttons
        ctk.CTkFrame(dlg, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x")
        btn_row = ctk.CTkFrame(dlg, fg_color=self.SURFACE, corner_radius=0)
        btn_row.pack(fill="x", padx=16, pady=10)

        def _save():
            # Collect toggled event IDs
            selected = [eid for eid, sw in switches.items() if sw.get() == 1]
            if not selected:
                # Enforce at least one event ID is selected
                self._show_toast("⚠️", "No Event IDs Selected",
                                 "At least one Event ID must be enabled.")
                return
            cfg = load_config()
            cfg["event_ids"] = selected
            save_config(cfg)
            # Re-register task with updated XPath filter if currently active
            if self._active:
                try:
                    unregister_task()
                    register_task()
                except Exception:
                    pass
            self._add_log_entry("ok", "auto",
                                f"Event IDs updated: {', '.join(selected)}", "DOCUMENTED")
            self._show_toast("✅", "Event IDs Saved",
                             f"Now monitoring: {', '.join(selected)}")
            dlg.destroy()

        ctk.CTkButton(btn_row, text="Cancel", width=90, height=32, corner_radius=6,
                      fg_color=self.SURFACE2, hover_color=self.SURFACE3,
                      text_color=self.TEXT_SEC, font=self.FONT_SMALL,
                      border_width=1, border_color=self.BORDER,
                      command=dlg.destroy).pack(side="right", padx=(6, 0))
        ctk.CTkButton(btn_row, text="Save", width=90, height=32, corner_radius=6,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_HVR,
                      text_color="white", font=("Segoe UI Variable Text", 12, "bold"),
                      command=_save).pack(side="right")

    def _add_toggle_row(self, parent, title, desc, default=False, divider=True):
        if divider:
            ctk.CTkFrame(parent, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=self.PAD_SM, pady=10)
        txt = ctk.CTkFrame(row, fg_color="transparent")
        txt.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(txt, text=title, font=self.FONT_BODY, text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(txt, text=desc, font=self.FONT_SMALL, text_color=self.TEXT_DIM, anchor="w").pack(anchor="w")
        sw = ctk.CTkSwitch(row, text="", width=44, progress_color=self.ACCENT,
                           button_color="white", button_hover_color=self.SURFACE3)
        if default: sw.select()
        sw.pack(side="right")
        return sw

    def _build_statusbar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=self.SURFACE, height=32, corner_radius=0)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        ctk.CTkFrame(bar, fg_color=self.BORDER_DIM, height=1, corner_radius=0).pack(fill="x", side="top")
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=self.PAD)
        self._sb_dot = ctk.CTkLabel(inner, text="●", font=("Segoe UI Variable Text", 8),
                                    text_color=self.RED, width=10)
        self._sb_dot.pack(side="left", pady=6)
        self._sb_status_lbl = ctk.CTkLabel(inner, text="LOCAL ISOLATION MODE ACTIVE",
                                            font=("Segoe UI Variable Text", 10, "bold"), text_color=self.TEXT_DIM)
        self._sb_status_lbl.pack(side="left", padx=(4, 16))
        ctk.CTkLabel(inner, text="Evidence data remains encrypted on this terminal.",
                     font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(side="left")
        self._sb_audit_lbl = ctk.CTkLabel(inner, text="Encryption: AES-256-XTS",
                                           font=self.FONT_SMALL, text_color=self.TEXT_DIM)
        self._sb_audit_lbl.pack(side="right")
        ctk.CTkLabel(inner, text=" | Vault Integrity: 100%  |  ",
                     font=self.FONT_SMALL, text_color=self.TEXT_DIM).pack(side="right")
        self._sb_task_lbl = ctk.CTkLabel(inner, text="Task: Not registered",
                                          font=self.FONT_SMALL, text_color=self.TEXT_DIM)
        self._sb_task_lbl.pack(side="right")

    def _refresh_status(self):
        if self._active:
            self._status_icon_frame.configure(fg_color=self.GREEN_BG)
            self._status_icon_label.configure(text="✓", text_color=self.GREEN)
            self._headline_lbl.configure(text="Protection Engine Active")
            self._uptime_lbl.configure(text="● Uptime: Running", text_color=self.GREEN)
            self._scan_lbl.configure(text="   ● Last scan: Just now", text_color=self.TEXT_DIM)
            self._pill_frame.configure(fg_color=self.GREEN_BG)
            self._pill_dot.configure(text_color=self.GREEN)
            self._pill_text.configure(text="Monitoring active", text_color=self.GREEN)
            self._main_btn.configure(text="  Deactivate", image=self._icon_cross_btn, compound="left",
                                     fg_color=self.RED_BG, hover_color="#f5c6c6", text_color=self.RED,
                                     border_width=1, border_color=self.BORDER)
            self._sb_dot.configure(text_color=self.GREEN)
            self._sb_status_lbl.configure(text="PROTECTED — MONITORING ACTIVE")
            self._sb_task_lbl.configure(text="Task: IntruderGuard_Capture")
            self._sb_audit_lbl.configure(text="Encryption: AES-256-XTS")
            
            if hasattr(self, "_topbar_protection_btn") and self._topbar_protection_btn:
                self._topbar_protection_btn.configure(
                    text="⏸  Pause Protection",
                    fg_color=self.ACCENT,
                    hover_color=self.ACCENT_HVR
                )
            if hasattr(self, "_sidebar_status_lbl") and self._sidebar_status_lbl:
                self._sidebar_status_lbl.configure(text="MONITORING ACTIVE", text_color=self.GREEN)
        else:
            self._status_icon_frame.configure(fg_color=self.RED_BG)
            self._status_icon_label.configure(text="✗", text_color=self.RED)
            self._headline_lbl.configure(text="Protection Engine Inactive")
            self._uptime_lbl.configure(text="● Uptime: —", text_color=self.TEXT_DIM)
            self._scan_lbl.configure(text="   ● Last scan: never", text_color=self.TEXT_DIM)
            self._pill_frame.configure(fg_color=self.RED_BG)
            self._pill_dot.configure(text_color=self.RED)
            self._pill_text.configure(text="Monitoring disabled", text_color=self.RED)
            self._main_btn.configure(text="  Activate", image=self._icon_shield_btn, compound="left",
                                     fg_color=self.ACCENT, hover_color=self.ACCENT_HVR,
                                     text_color="white", border_width=0)
            self._sb_dot.configure(text_color=self.RED)
            self._sb_status_lbl.configure(text="LOCAL ISOLATION MODE ACTIVE")
            self._sb_task_lbl.configure(text="Task: Not registered")
            self._sb_audit_lbl.configure(text="Encryption: AES-256-XTS")
            
            if hasattr(self, "_topbar_protection_btn") and self._topbar_protection_btn:
                self._topbar_protection_btn.configure(
                    text="▶  Activate Protection",
                    fg_color=self.GREEN,
                    hover_color="#156333"
                )
            if hasattr(self, "_sidebar_status_lbl") and self._sidebar_status_lbl:
                self._sidebar_status_lbl.configure(text="MONITORING PAUSED", text_color=self.RED)

    def _toggle_protection(self):
        try:
            if not self._active:
                enable_auditing(); register_task()
                self._active = True
                self._add_log_entry("ok", "auto", "Protection activated — Task registered", "DOCUMENTED")
                self._add_full_log_entry(
                    datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S"),
                    "4625", "schtasks.exe", "SYSTEM", "Monitoring service initialized", "DOCUMENTED"
                )
                self._show_toast("🛡️", "Protection Activated", "Monitoring for wrong password attempts via Event 4625.")
            else:
                disable_auditing(); unregister_task()
                self._active = False
                self._add_log_entry("info", "auto", "Protection deactivated — Task removed", "DOCUMENTED")
                self._show_toast("⚠️", "Protection Deactivated", "Device is no longer being monitored.")
            self._refresh_status()
        except Exception as e:
            if "Access is denied" in str(e) or not is_admin():
                if WINDLL and hasattr(WINDLL, "shell32"):
                    abs_script = os.path.abspath(__file__)
                    WINDLL.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{abs_script}"', os.path.dirname(abs_script), 1)
                sys.exit()

    def _emergency_lock(self):
        self._show_toast("🔒", "Emergency Lock", "Initiating system lockdown...")
        if WINDLL and hasattr(WINDLL, "user32"):
            WINDLL.user32.LockWorkStation()

    def _show_toast(self, icon: str, title: str, message: str, duration_ms: int = 3200):
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True); toast.attributes("-topmost", True)
        toast.configure(fg_color=self.SURFACE)
        self.update_idletasks()
        wx = self.winfo_x() + self.winfo_width() - 314
        wy = self.winfo_y() + self.winfo_height() - 104
        toast.geometry(f"304x82+{wx}+{wy}")
        outer = ctk.CTkFrame(toast, fg_color=self.SURFACE, corner_radius=10,
                              border_width=1, border_color=self.BORDER)
        outer.pack(fill="both", expand=True, padx=1, pady=1)
        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=10)
        ctk.CTkLabel(inner, text=icon, font=("Segoe UI Emoji", 18),
                     fg_color="transparent", width=24).pack(side="left", anchor="n", pady=2)
        body = ctk.CTkFrame(inner, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, padx=(10, 0))
        ctk.CTkLabel(body, text=title, font=("Segoe UI Variable Text", 12, "bold"),
                     text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(body, text=message, font=self.FONT_SMALL, text_color=self.TEXT_SEC,
                     anchor="w", wraplength=210, justify="left").pack(anchor="w")
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
        preview_win.title("Camera Preview")
        preview_win.geometry("500x420")
        preview_win.configure(fg_color=self.BG)
        preview_win.resizable(False, False)
        hdr = ctk.CTkFrame(preview_win, fg_color=self.SURFACE, height=40, corner_radius=0)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkFrame(hdr, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
        ctk.CTkLabel(hdr, text="  📷  Camera Preview", font=self.FONT_SMALL,
                     text_color=self.TEXT_SEC, fg_color="transparent").pack(side="left", padx=12, pady=10)
        canvas_frame = ctk.CTkFrame(preview_win, fg_color=self.SURFACE, corner_radius=self.RADIUS,
                                    border_width=1, border_color=self.BORDER_DIM)
        canvas_frame.pack(fill="both", expand=True, padx=self.PAD, pady=self.PAD)
        lbl = ctk.CTkLabel(canvas_frame, text="Starting camera…", font=self.FONT_BODY, text_color=self.TEXT_DIM)
        lbl.pack(expand=True)
        import cv2  # type: ignore
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        def update():
            if not preview_win.winfo_exists(): cap.release(); return
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb).resize((456, 320))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(456, 320))
                lbl.configure(image=ctk_img, text="")
                lbl._image = ctk_img
            preview_win.after(33, update)
        update()
        preview_win.protocol("WM_DELETE_WINDOW", lambda: (cap.release(), preview_win.destroy()))
        self._add_log_entry("ok", "auto", "Camera test — cv2.VideoCapture(0) OK", "DOCUMENTED")

    def _change_folder(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(initialdir=self._save_path, title="Select Save Folder")
        if path:
            new_path = path.replace("/", "\\")
            set_gallery_path(new_path); self._save_path = new_path
            if hasattr(self, "_save_path_desc"): self._save_path_desc.configure(text=new_path)
            if hasattr(self, "_path_entry"):
                self._path_entry.delete(0, "end"); self._path_entry.insert(0, new_path)
            self._show_toast("📁", "Save Folder Updated", new_path)

    def _show_about(self):
        from tkinter import messagebox
        messagebox.showinfo("About IntruderGuard",
                            "IntruderGuard v4.2.0 — Enterprise Security Console\n"
                            "Real-time physical intrusion detection via Windows Event ID 4625.\n\n"
                            "Build: STABLE  |  Encryption: AES-256-XTS\n"
                            "Built with Python & CustomTkinter.")

    def _logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to exit IntruderGuard?"):
            self.destroy()

    def _run_diagnostics(self):
        diag_win = ctk.CTkToplevel(self)
        diag_win.title("System Diagnostics")
        diag_win.geometry("520x450")
        diag_win.configure(fg_color=self.BG)
        diag_win.resizable(False, False)
        diag_win.attributes("-topmost", True)
        
        hdr = ctk.CTkFrame(diag_win, fg_color=self.SURFACE, height=45, corner_radius=0)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkFrame(hdr, fg_color=self.BORDER_DIM, height=1).pack(fill="x", side="bottom")
        ctk.CTkLabel(hdr, text="  🛠️  IntruderGuard Diagnostics", font=self.FONT_HEAD,
                     text_color=self.TEXT, fg_color="transparent").pack(side="left", padx=16, pady=10)
                     
        scroll = ctk.CTkScrollableFrame(diag_win, fg_color=self.BG, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=16, pady=16)
        
        # 1. Camera check
        import cv2 # type: ignore
        config = load_config()
        cam_id = config.get("camera_index", 0)
        cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
        cam_ok = cap.isOpened()
        if cam_ok:
            cap.release()
            cam_str, cam_col = "CONNECTED & READY", self.GREEN
        else:
            cam_str, cam_col = "NOT DETECTED or BUSY", self.RED
            
        # 2. Audit check
        audit_ok = False
        try:
            audit_check = subprocess.run(["auditpol", "/get", "/subcategory:Logon"], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            if "Failure" in audit_check.stdout or "Success and Failure" in audit_check.stdout:
                audit_ok = True
        except: pass
        audit_str, audit_col = ("ENABLED", self.GREEN) if audit_ok else ("DISABLED (Logon Failure Audit inactive)", self.RED)
        
        # 3. Task check
        task_ok = False
        try:
            check_task = subprocess.run(["schtasks", "/query", "/tn", TASK_NAME], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            if check_task.returncode == 0:
                task_ok = True
        except: pass
        task_str, task_col = ("REGISTERED (Runs as SYSTEM on Event 4625)", self.GREEN) if task_ok else ("NOT REGISTERED", self.RED)
        
        # 4. Storage check
        gallery_path = config.get("gallery_path", GALLERY_DEFAULT)
        write_ok = False
        try:
            os.makedirs(gallery_path, exist_ok=True)
            test_file = os.path.join(gallery_path, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            write_ok = True
        except: pass
        store_str, store_col = ("WRITABLE & SECURED", self.GREEN) if write_ok else ("ACCESS DENIED or INVALID PATH", self.RED)
        
        def add_item(label, value, color):
            f = ctk.CTkFrame(scroll, fg_color=self.SURFACE, corner_radius=self.RADIUS_SM, border_width=1, border_color=self.BORDER_DIM)
            f.pack(fill="x", pady=6)
            ctk.CTkLabel(f, text=label, font=self.FONT_BODY, text_color=self.TEXT).pack(anchor="w", padx=12, pady=(8, 2))
            ctk.CTkLabel(f, text=value, font=self.FONT_PILL, text_color=color).pack(anchor="w", padx=12, pady=(0, 8))
            
        add_item("Webcam Detection", cam_str, cam_col)
        add_item("Windows Logon Failure Auditing", audit_str, audit_col)
        add_item("Task Scheduler Hook", task_str, task_col)
        add_item("Evidence Gallery Path Permissions", store_str, store_col)
        
        ctk.CTkButton(scroll, text="Close Diagnostics", height=32, corner_radius=6,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_HVR, text_color="white",
                      command=diag_win.destroy).pack(pady=12)
        self._add_log_entry("ok", "auto", "System diagnostics completed", "DOCUMENTED")

    def _deploy_agent(self):
        import threading
        self._show_toast("🛡️", "Agent Deploying", "Simulating mock login failure...")
        
        def run_sim():
            success = capture_photo(is_sim=True)
            if success:
                self.after(100, lambda: self._show_toast("📸", "Mock Capture Success", "Intruder snapshot saved in gallery."))
                self.after(200, lambda: self._load_gallery())
            else:
                self.after(100, lambda: self._show_toast("❌", "Simulation Failed", "Webcam could not be opened."))
                
        t = threading.Thread(target=run_sim)
        t.daemon = True
        t.start()

    def _export_gallery_report(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            initialfile="forensic_report.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Forensic Report"
        )
        if not path:
            return
            
        try:
            config = load_config()
            gallery = config.get("gallery_path", GALLERY_DEFAULT)
            files = [f for f in os.listdir(gallery) if f.endswith((".jpg", ".png", ".jpeg"))]
            
            with open(path, "w") as f:
                f.write("=========================================\n")
                f.write("      INTRUDERGUARD FORENSIC REPORT\n")
                f.write("=========================================\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Active Gallery Path: {gallery}\n")
                f.write(f"Total Incidents: {len(files)}\n\n")
                f.write(f"{'Filename':<30} | {'Date Created':<24} | {'Size (Bytes)':<12}\n")
                f.write("-" * 75 + "\n")
                for fn in files:
                    fp = os.path.join(gallery, fn)
                    mtime = time.ctime(os.path.getmtime(fp))
                    sz = os.path.getsize(fp)
                    f.write(f"{fn:<30} | {mtime:<24} | {sz:<12}\n")
            self._show_toast("📋", "Report Exported", f"Forensics report saved successfully.")
            self._add_log_entry("ok", "auto", "Forensics report exported", "DOCUMENTED")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not write forensic report:\n{str(e)}")

    def _export_system_logs(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            initialfile="system_logs.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export System Logs"
        )
        if not path:
            return
        try:
            log_data = getattr(self, "_log_data", [])
            with open(path, "w", encoding="utf-8") as out:
                out.write("=========================================\n")
                out.write("      INTRUDERGUARD SYSTEM AUDIT LOGS\n")
                out.write("=========================================\n")
                out.write(f"Export Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                out.write(f"Total Events: {len(log_data)}\n\n")
                out.write(f"{'Timestamp':<22} {'EventID':<10} {'Severity':<10} {'Source':<18} "
                          f"{'Target':<20} {'Action':<40} {'Status'}\n")
                out.write("-" * 130 + "\n")
                for entry in log_data:
                    out.write(
                        f"{entry.get('timestamp',''):<22} "
                        f"{entry.get('event_id',''):<10} "
                        f"{entry.get('severity',''):<10} "
                        f"{entry.get('source',''):<18} "
                        f"{entry.get('target',''):<20} "
                        f"{entry.get('action',''):<40} "
                        f"{entry.get('status','')}\n"
                    )
                out.write("\n--- System Debug Files ---\n")
                for lf in ["debug_log.txt", "startup_id.txt", "path_log.txt"]:
                    fp = os.path.join(INSTALL_DIR, lf)
                    if os.path.exists(fp):
                        out.write(f"\n[{lf}]\n")
                        try:
                            with open(fp, "r", encoding="utf-8", errors="replace") as src:
                                out.write(src.read())
                        except Exception:
                            pass
            self._show_toast("📋", "Logs Exported", "Audit logs saved successfully.")
            self._add_log_entry("ok", "auto", "System logs exported", "DOCUMENTED")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export audit logs:\n{str(e)}")

    def _wipe_vault(self):
        if not messagebox.askyesno("Confirm Vault Wipe", "WARNING: This will permanently delete all captured intruder photos inside the Evidence Vault.\n\nAre you sure you want to proceed?"):
            return
        try:
            gallery = self._save_path
            count = 0
            if os.path.exists(gallery):
                for f in os.listdir(gallery):
                    if f.endswith((".jpg", ".png", ".jpeg")):
                        os.remove(os.path.join(gallery, f))
                        count += 1
            self._known_files.clear()
            if hasattr(self, "_loaded_log_keys"):
                self._loaded_log_keys.clear()
            activity_log_file = os.path.join(INSTALL_DIR, "activity_logs.json")
            if os.path.exists(activity_log_file):
                try:
                    os.remove(activity_log_file)
                except: pass
            self._photos = 0
            self._load_gallery()
            self._update_stats_count()
            self._refresh_incident_tiles()
            
            for w in self._gallery_list.winfo_children():
                w.destroy()
            self._gallery_empty.pack(fill="x", padx=self.PAD, pady=self.PAD)
            self._gallery_list.pack_forget()
            
            self._show_toast("🗑️", "Vault Wiped", f"Permanently deleted {count} evidence items.")
            self._add_log_entry("ok", "auto", f"Evidence vault wiped ({count} items deleted)", "DOCUMENTED")
        except Exception as e:
            messagebox.showerror("Wipe Failed", f"Could not wipe local evidence vault:\n{str(e)}")

    def _on_slider_move(self, val):
        val_ms = int(val)
        if hasattr(self, "_slider_delay_lbl"):
            self._slider_delay_lbl.configure(text=f"{val_ms}ms")

    def _apply_retention_policy(self):
        config = load_config()
        policy = config.get("retention_policy", "Delete after 30 days")
        days_map = {
            "Delete after 7 days":  7,
            "Delete after 30 days": 30,
            "Delete after 90 days": 90,
            "Never delete":         0,
        }
        days = days_map.get(policy, 0)
        if days == 0:
            return
        cutoff = time.time() - (days * 86400)
        gallery = self._save_path
        if not os.path.exists(gallery):
            return
        deleted = 0
        for fn in os.listdir(gallery):
            if fn.endswith((".jpg", ".png", ".jpeg")):
                fp = os.path.join(gallery, fn)
                try:
                    if os.path.getmtime(fp) < cutoff:
                        os.remove(fp)
                        deleted += 1
                except Exception:
                    pass
        if deleted > 0:
            self._load_gallery()
            self._add_log_entry("info", "auto",
                                f"Retention policy applied: {deleted} file(s) purged", "DOCUMENTED")

    def _load_settings_into_ui(self):
        config = load_config()

        if hasattr(self, "_sw_monitoring"):
            if config.get("enable_monitoring", True):
                self._sw_monitoring.select()
            else:
                self._sw_monitoring.deselect()
                
        if hasattr(self, "_sw_startup"):
            if config.get("run_on_startup", False):
                self._sw_startup.select()
            else:
                self._sw_startup.deselect()
                
        if hasattr(self, "_sw_death"):
            if config.get("death_mode", False):
                self._sw_death.select()
            else:
                self._sw_death.deselect()
            
        if hasattr(self, "_combo_camera"):
            cam_idx = config.get("camera_index", 0)
            val = f"Integrated HD Webcam (ID: {cam_idx})" if cam_idx == 0 else f"USB Camera (ID: {cam_idx})"
            self._combo_camera.set(val)
            
        if hasattr(self, "_combo_quality"):
            self._combo_quality.set(config.get("photo_quality", "Original (Highest)"))
            
        if hasattr(self, "_combo_retention"):
            self._combo_retention.set(config.get("retention_policy", "Delete after 30 days"))
            
        if hasattr(self, "_slider_delay"):
            val_ms = config.get("capture_delay", 150)
            self._slider_delay.set(val_ms)
            if hasattr(self, "_slider_delay_lbl"):
                self._slider_delay_lbl.configure(text=f"{val_ms}ms")
                
        if hasattr(self, "_path_entry"):
            self._path_entry.delete(0, "end")
            self._path_entry.insert(0, config.get("gallery_path", GALLERY_DEFAULT))

    def _discard_settings(self):
        self._load_settings_into_ui()
        self._show_toast("⚙️", "Settings Discarded", "Reverted input fields to last saved configuration.")
        self._add_log_entry("info", "auto", "Settings changes discarded", "DOCUMENTED")

    def _save_settings(self):
        config = load_config()
        
        config["enable_monitoring"] = self._sw_monitoring.get() == 1
        config["run_on_startup"] = self._sw_startup.get() == 1
        config["death_mode"] = self._sw_death.get() == 1
        
        cam_str = self._combo_camera.get()
        cam_idx = 0
        if "ID: " in cam_str:
            try:
                cam_idx = int(cam_str.split("ID: ")[1].replace(")", ""))
            except: pass
        config["camera_index"] = cam_idx
        config["photo_quality"] = self._combo_quality.get()
        config["retention_policy"] = self._combo_retention.get()
        
        config["capture_delay"] = int(self._slider_delay.get())
        
        new_path = self._path_entry.get().strip()
        if new_path:
            config["gallery_path"] = new_path
            self._save_path = new_path

        # NOTE: event_ids are managed exclusively by the Edit dialog (_edit_event_ids).
        # Do NOT overwrite them here — preserve whatever the user set via the Edit button.
        # config["event_ids"] is already loaded from disk at the top of this function.

        save_config(config)
        
        if config["enable_monitoring"] != self._active:
            self._toggle_protection()
            
        import winreg
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            if config["run_on_startup"]:
                python_exe = sys.executable
                if "python.exe" in python_exe.lower():
                    python_exe = python_exe.lower().replace("python.exe", "pythonw.exe")
                cmd = f'"{python_exe}" "{os.path.abspath(__file__)}"'
                winreg.SetValueEx(key, "IntruderGuard", 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, "IntruderGuard")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Failed to set startup registry key: {e}")
            
        self._show_toast("⚙️", "Settings Saved", "Configuration updated and applied successfully.")
        self._add_log_entry("ok", "auto", "Settings changes saved and applied", "DOCUMENTED")

if __name__ == "__main__":
    # TRIGGER EVENT DISPATCHER & APP ENTRY POINT
    # ------------------------------------------
    # When this script is invoked, it checks command-line arguments to determine execution mode:
    # 
    # 1. '/capture' Mode (Background Trigger Action):
    #    If '/capture' is present in arguments, it means this run was triggered by the Windows Task
    #    Scheduler (which runs when one of the configured security events, e.g. Event ID 4625, is logged).
    #    In this mode, there is no GUI. It executes 'capture_photo()' to take a photo using the webcam
    #    and record the event details to the logs, then exits.
    #
    # 2. Console Mode (Admin Panel GUI):
    #    Otherwise, the user is starting the main application panel. 
    #    - First, it ensures the process is running with Administrator privileges (required to enable/disable
    #      auditing policies and register/modify scheduled tasks). 
    #    - If it's not admin, it uses ShellExecuteW to prompt UAC for elevated privileges, passes any user
    #      site-packages paths to inject, and restarts itself.
    #    - If it is admin, it initializes and opens the IntruderGuard GUI Console.
    if "/capture" in sys.argv:
        capture_photo()
    else:
        if not is_admin():
            if WINDLL:
                abs_script = os.path.abspath(__file__)
                user_paths = [p for p in sys.path if p and isinstance(p, str) and p.lower().startswith("c:\\users\\")]
                args = f'"{abs_script}"'
                if user_paths:
                    args += f' --inject-paths "{";".join(user_paths)}"'
                WINDLL.shell32.ShellExecuteW(None, "runas", sys.executable, args, os.path.dirname(abs_script), 1)
            sys.exit()
        else:
            try:
                app = IntruderGuardApp()
                app.mainloop()
            except Exception as e:
                import traceback
                temp_dir = os.environ.get("TEMP", r"C:\Temp")
                err_file = os.path.join(temp_dir, "intruder_guard_crash.txt")
                try:
                    os.makedirs(temp_dir, exist_ok=True)
                    with open(err_file, "w") as f:
                        traceback.print_exc(file=f)
                except:
                    pass
                
                if WINDLL:
                    WINDLL.user32.MessageBoxW(
                        0,
                        f"An unhandled error occurred while running IntruderGuard:\n\n{str(e)}\n\n"
                        f"Details have been saved to:\n{err_file}",
                        "IntruderGuard Crash",
                        0x10
                    )
                sys.exit(1)
