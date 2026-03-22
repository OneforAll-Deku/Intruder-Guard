# IntruderGuard (Python Version)

**A Windows security application that captures webcam photos on failed login attempts.**

IntruderGuard monitors your Windows Lock Screen and automatically snaps a picture of anyone who enters an incorrect password. It runs silently in the background as a SYSTEM service, ensuring it works **even after a system restart** before anyone logs in.

## 🎯 Features
- **Automatic Webcam Capture**: Takes a photo instantly when a wrong password is entered at the Lock Screen.
- **Boot-Persistent Protection**: Runs via Windows Task Scheduler as `SYSTEM`, so it works immediately after booting up.
- **Modern UI**: Built with `customtkinter` for a sleek, dark-themed management interface.
- **Event-Driven**: Uses Windows Event Log (Event ID 4625) for zero-latency triggers.
- **Privacy Focused**: All photos are stored locally on your machine.

## 🌐 Landing Page

The project also includes a modern, responsive landing page built with **React** and **Vite**. You can find it in the `landing-page/` directory.

### 🛠️ How to Run the Landing Page Locally:
1. Navigate to the folder: `cd landing-page`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`

## 🚀 Installation

1. **Run `Setup_Python.bat`**
   - This script will install the required Python dependencies (`opencv-python`, `customtkinter`, `pillow`) and launch the application.
   - You must have Python installed and added to your PATH.

2. **Activate Protection**
   - In the GUI that opens, click **"ACTIVATE PROTECTION"**.
   - This will configure the Windows Audit Policy and create the background trigger.

## 🧪 How to Test

1. **Lock your computer** (Win + L).
2. At the Windows Login Screen, **enter a WRONG password**.
3. Log in with your correct password.
4. Open the **Gallery**:
   - Run the IntruderGuard app and click **"VIEW GALLERY"**.

## 🔧 Technical Details

- **Trigger**: The background task waits for **Event ID 4625** (Account failed to log on).
- **Execution**: When triggered, it runs `python intruder_guard.py /capture` as the **SYSTEM** account.
- **Capture Backend**: Uses OpenCV with the DirectShow (`CAP_DSHOW`) backend for reliable camera access in background sessions.

## 📋 Requirements

- Windows 10 or Windows 11.
- Python 3.10+.
- A functional Webcam.
- Administrator rights (to install the scheduled task).

## ❓ Troubleshooting

- **No photos captured?**
  - Check `C:\ProgramData\IntruderGuard\debug_log.txt` for errors.
  - Verify your webcam is connected and not blocked by a privacy shutter.
  - Ensure "Logon" auditing is enabled (the app tries to do this automatically).

## ⚠️ Disclaimer

This tool is for **personal security / educational purposes only**. You are responsible for complying with all local laws regarding privacy and surveillance.
