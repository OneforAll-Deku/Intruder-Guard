# 🛡️ IntruderGuard: The Ghost in the Kernel

**Automatic physical security and Event Log auditing for Windows.**  
IntruderGuard is a high-performance system security utility that hooks directly into the Windows Security Kernel. It monitors critical Windows Security Event IDs (such as logon failures and unauthorized account creations) and instantly triggers webcam captures to document intruders—running silently, instantly, and persistently in the background.

---

## ✨ Features & Architecture

*   **🎨 Premium Security Console**: Built on a modern Material Design 3 theme utilizing CustomTkinter, featuring responsive status cards, real-time activity charts, and smooth UI animations.
*   **⚙️ Advanced Security Kernel**:
    *   Monitor multiple Windows Security Event IDs:
        *   `4625` (Failed Logon) — **DEFAULT ON** (Visual highlighting & visual card border).
        *   `4624` (Successful Logon) — For audit trails.
        *   `4735` (Security Group Modification) — For privilege escalation alerts.
        *   `4720` (User Account Created) — Detects unauthorized backdoors.
        *   `4647` (User-Initiated Logoff) — Monitors session exit events.
        *   `4648` (Explicit Credential Logon) — Detects lateral movement attempts.
    *   Dynamic **Edit Dialog** featuring modal switches, description tags, and live Task Scheduler XML configuration updates.
*   **📷 Lock-Screen Webcam Capture (SYSTEM Context)**:
    *   Runs as a background `pythonw.exe` task under local `SYSTEM` privileges.
    *   Allows webcam access even when the Windows screen is locked and no user session is active.
*   **🔒 Encrypted Forensic Gallery (Evidence Vault)**:
    *   Enforces custom file retention policies (auto-purge older photos after 7, 30, or 90 days).
    *   Secure storage permissions to prevent unauthorized deletion.
*   **🛠️ System Diagnostics & Logs Exporter**:
    *   Verify webcam detection, Logon Auditing state, Scheduled Task registration, and file system permissions with one click.
    *   Export comprehensive forensic reports and raw system audit logs.

---

## 🚀 One-Click Setup (Quick Start)

The installation process is automated. **No manual library installs or complex command-line configuration required.**

1.  **Download & Extract**
    *   Extract the ZIP folder containing the project files to a location on your PC.
2.  **Run the Installer**
    *   Locate the file named **`Setup_Python.bat`**.
    *   **Right-click it** and select **"Run as Administrator"**.
    *   *The installer will automatically detect Python, install dependency libraries, register the background worker, and launch the console.*
3.  **Activate & Test**
    *   Click **"ACTIVATE PROTECTION"** in the console.
    *   Lock your computer (**Win + L**) and enter an incorrect password.
    *   Log back in and open the **Evidence Vault** to view the snapshot!

---

## 📂 Project Structure

| Component | Description |
| :--- | :--- |
| **`Setup_Python.bat`** | **The Entry Point.** Installs Python dependencies, copies the runtime script to `%ProgramData%`, and launches the console. |
| **`intruder_guard.py`** | **The Core.** Houses the customtkinter UI dashboard, local database logic, webcam controllers, and Scheduled Task setup. |
| **`requirements.txt`** | **Dependencies.** Specifies libraries (`customtkinter`, `opencv-python`, `pillow`) required by the app. |
| **`landing-page/`** | **Product Showcase.** A custom React + Vite marketing page representing the project's features. |

---

## 🔬 How it Works (Under the Hood)

### 1. Kernel Hooking
Instead of running a heavy background loop, IntruderGuard hooks into the **Windows Event Log**. When the Windows Security channel registers a specified Event ID, the Windows Task Scheduler immediately fires the background trigger. This results in **0% CPU usage** while idle.

### 2. SYSTEM Service Execution
Windows restricts webcam access under standard locked-session user accounts. To bypass this, the Scheduled Task executes a batch wrapper (`launch_worker.bat`) pointing to the local `SYSTEM` account, which possesses raw hardware control access.

### 3. Local Isolation
All operations are **completely local**. Captured images are saved to local directories with restricted access rights. No data is ever transmitted over the network or uploaded to cloud storage.

---

## 📋 Requirements & Privacy
*   **Operating System**: Windows 10 or Windows 11 (requires Administrator rights).
*   **Hardware**: Built-in webcam or external USB camera.
*   **Privacy**: **100% Offline**. Data resides strictly on the local machine.

---

## 🔍 How to Check if it is Running

You can verify that IntruderGuard is actively monitoring and registered on your system in three ways:

1.  **Via the GUI Dashboard**:
    *   Launch the app. The main dashboard status will show a green checkmark stating **"Protection Engine Active"**.
    *   The status bar at the very bottom will read **`PROTECTED — MONITORING ACTIVE`** and show **`Task: IntruderGuard_Capture`**.
2.  **Via Windows Task Scheduler**:
    *   Open PowerShell and run:
        ```powershell
        schtasks /query /tn IntruderGuard_Capture
        ```
    *   If running, this command will print status details (e.g. `Status: Ready`) rather than an error.
3.  **Via Auditing Policy**:
    *   Open PowerShell as Administrator and run:
        ```powershell
        auditpol /get /subcategory:Logon
        ```
    *   Under the "Logon" subcategory, it should show **`Failure`** or **`Success and Failure`** enabled.

---

## 🧼 How to Turn Off & Uninstall (Delete)

### 1. Simple Turn Off (Deactivate)
*   Launch the GUI.
*   Click the red **"DEACTIVATE"** button on the main dashboard, or toggle **"Enable Monitoring"** off in the Settings tab and click **"Save Changes"**.
*   This will immediately unregister the scheduled task and disable the security auditing policies.

### 2. Complete Removal & Cleanup (Uninstall)
If you wish to completely wipe IntruderGuard from your system, execute the following steps:

1.  **Unregister Services**:
    Open PowerShell as **Administrator** and run the following commands to delete the task, disable policy auditing, and remove the startup registry entry:
    ```powershell
    # Force delete the scheduled task
    schtasks /delete /tn IntruderGuard_Capture /f

    # Restore default auditing behavior (disable logging failed attempts)
    auditpol /set /subcategory:"Logon" /failure:disable
    auditpol /set /subcategory:"Credential Validation" /failure:disable

    # Remove registry key for run-on-startup (if enabled)
    Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "IntruderGuard" -ErrorAction SilentlyContinue
    ```
2.  **Delete Local Program Data**:
    *   Press `Win + R`, type `C:\ProgramData`, and press Enter.
    *   Delete the **`IntruderGuard`** folder. (This removes logs, config cache, and background scripts).
3.  **Delete Source Folders**:
    *   Delete the directory where you extracted the project (e.g. `Downloads\Intruder-Guard-main` or `D:\Intruder-Guard-main`).

---

## ⚠️ Disclaimer
This utility is intended for personal computer security and educational research. Please consult local privacy and surveillance laws prior to deployment.

---
© 2026 IntruderGuard | Enterprise Security Utility
