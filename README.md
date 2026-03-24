# 🛡️ IntruderGuard: The Ghost in the Kernel

**Automatic physical security for Windows.**  
IntruderGuard is a high-performance system utility that monitors your Windows Lock Screen. It captures photographic evidence the moment someone tries to guess your password—silently, instantly, and persistently.

---

## 🚀 One-Click Setup (Quick Start)

We have simplified the installation into a single automated script. **No manual library installs or complex command-line work required.**

1.  **Download & Extract**
    - [Download the ZIP](https://github.com/OneforAll-Deku/Intruder-Guard/archive/refs/heads/main.zip) and extract it to a folder on your Windows PC.
2.  **Run the Installer**
    - Locate the file named **`Setup_Python.bat`**.
    - **Right-click it** and select **"Run as Administrator"**.
    - *The script will automatically install Python libraries and launch the Manager.*
3.  **Activate & Lock**
    - In the Dashboard, click **"ACTIVATE PROTECTION"**.
    - **Lock your screen (Win + L)** and test it with a wrong password!

---

## 📂 Understanding the Structure

This repository is designed to be lean and powerful. Here is what you are using:

| Component | The "Why" |
| :--- | :--- |
| **`Setup_Python.bat`** | **The Entry Point.** Handles Python detection, pip dependency installation, and GUI startup. |
| **`intruder_guard.py`** | **The Heart.** Contains the management dashboard and the backend camera logic. |
| **`requirements.txt`** | **The Checklist.** Tells Python exactly which libraries (OpenCV, CustomTkinter) to fetch. |
| **`landing-page/`** | **The Showcase.** A custom React + Vite product page for high-end project display. |

---

## 📚 What to Learn (How it Works)

If you're a developer or a student curious about how this works, here is the technical "Secret Sauce":

### 1. Kernel Hooking (The Trigger)
Instead of "polling" or "guessing," we hook into the **Windows Security Kernel**. When a login fails, Windows generates **Event ID 4625**. We register a listener with the **Task Scheduler** that fires only when that specific ID appears. This means **0% CPU usage** while your PC is idling.

### 2. Ghost Process (The Capture)
The actual photo capture runs as a `pythonw.exe` process under the **SYSTEM** user account. 
- **SYSTEM account**: Allows camera access even when no one is logged in.
- **`pythonw`**: Suppresses the terminal window so an intruder never sees a "popup."

### 3. Forensic Gallery (The Management)
We use a high-contrast **UI (CustomTkinter)** to browse the photos. These are stored with restricted permissions, so they can't be easily found or deleted by casual users.

---

## 📋 Requirements & Privacy
- **OS**: Windows 10 / 11 (Admin rights required).
- **Hardward**: Any integrated or USB webcam.
- **Privacy**: **Everything is local.** No photos are uploaded to the cloud or sent to our servers. Your security is your own.

---

## ⚠️ Disclaimer
Used for personal security and educational research. Please comply with local privacy laws regarding surveillance.

---
© 2026 IntruderGuard | [v2.0.0 Release Notes](https://github.com/OneforAll-Deku/Intruder-Guard/releases)
