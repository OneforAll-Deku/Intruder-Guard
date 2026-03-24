# 🎤 IntruderGuard — Hackathon Presentation Guide
### Complete PPT Storyboard, Slide-by-Slide Script & Design Notes

> **Project:** IntruderGuard v2.0 — *The Ghost in the Kernel*
> **Author:** Pratyaksh Raj | **GitHub:** [@OneforAll-Deku](https://github.com/OneforAll-Deku)
> **Contact:** newraj990@gmail.com | **Twitter:** @PRATYAKSHRAJ11
> **Recommended Slides:** 12–15 | **Talk Time:** 5–7 minutes

---

## 📐 Presentation Overview

| Slide # | Title | Purpose |
|:-------:|:------|:--------|
| 1 | Title Slide | Hook the audience |
| 2 | The Problem | Establish pain point |
| 3 | The Market Gap | Why existing tools fail |
| 4 | Our Solution | Introduce IntruderGuard |
| 5 | How It Works (Pipeline) | Technical architecture |
| 6 | Key Feature: Ghost Process | Wow factor — stealth |
| 7 | Key Feature: Kernel Event Hook | Wow factor — 0% CPU |
| 8 | Live Demo / Screenshots | Proof of concept |
| 9 | Tech Stack | Credibility |
| 10 | Security & Privacy Model | Trust building |
| 11 | Future Roadmap | Vision & scalability |
| 12 | Impact & Stats | Quantify success |
| 13 | Team / About | Personal touch |
| 14 | Call to Action | GitHub, Demo, QR Code |

---

## 🎨 Design Theme & Color Palette

> Match the brutalist design language of the landing page.

| Element | Value | Usage |
|:--------|:------|:------|
| **Primary** | `#CC0000` (Crimson) | Headings, accents, borders |
| **Background** | `#0A0A0A` (Near Black) | Dark slides |
| **Text Light** | `#FFFFFF` | On dark slides |
| **Accent** | `#FFD700` (Gold) | Stats, callouts |
| **Terminal Green** | `#00FF41` | Code blocks, CLI screenshots |
| **Paper White** | `#F5F0E8` | Light slides |

**Fonts:**
- **Headings:** Space Grotesk Bold / Bebas Neue
- **Body:** Inter / IBM Plex Sans (readable)
- **Code/Mono:** IBM Plex Mono / JetBrains Mono

**Slide Style:**
- Bold thick borders (8–12px solid black or crimson)
- High contrast — no subtle grays
- Terminal-style labels in monospace (e.g., `[SEC_STATUS: ACTIVE]`)
- Use ASCII/box art for pipelines

---

## 📊 Slide-by-Slide Breakdown

---

### 🟥 SLIDE 1 — Title Slide

**Layout:** Full bleed dark background, centered

**Visual Design:**
- Background: `#0A0A0A`
- Large bold title in two lines:
  - `INTRUDER` (crimson, solid)
  - `GUARD` (outline only — white stroke, transparent fill)
- Tagline below: *"The Ghost in the Kernel"*
- Thin ticker tape at bottom: `[SEC_STATUS: ACTIVE] // V2.0 DEPLOYED // GHOST_PROCESS //`

**Content:**
```
INTRUDER
GUARD

— The Ghost in the Kernel —

Automatic physical security for Windows.
Captures photographic proof on every failed login attempt.

[ Pratyaksh Raj | Hackathon 2026 ]
```

**Speaker Note:**
> "Before I start — I want you to imagine this: you step away from your laptop, you're in a public library or a café, and someone picks it up and starts guessing your password. What happens? Nothing. Windows just waits. **IntruderGuard changes that.** In the next 5 minutes, I'll show you how we hooked into the Windows Security Kernel to make your PC silently photograph every intruder."

---

### 🟥 SLIDE 2 — The Problem

**Layout:** Two-column — Left: Problem text, Right: Infographic or icon grid

**Content:**
```
THE PROBLEM

Every day, millions of PCs are physically vulnerable.

❌  Stolen laptops — no photographic evidence
❌  Shared PCs — no unauthorized access logs
❌  College labs / offices — zero deterrence
❌  Law enforcement — cannot prove who accessed what

Windows has NO built-in mechanism to LOG or PHOTOGRAPH
failed physical login attempts.
```

**Infographic Idea:** 3 icons in a row
- 🔓 Unlocked Lock → ❓ Unknown User → 🚫 No Evidence

**Speaker Note:**
> "93% of all data breaches start physically. Someone picks up a device, tries a few passwords — and if they fail, they walk away clean. There is no record. There is no face. Windows gives you a failed login count, but not *who*."

---

### 🟥 SLIDE 3 — The Market Gap

**Layout:** Comparison table on dark background

**Content:**
```
EXISTING SOLUTIONS — AND WHY THEY FAIL
```

| Tool | What It Does | The Problem |
|:-----|:------------|:------------|
| Windows Antivirus | Scans files/malware | Can't detect *physical* intruders |
| BitLocker | Encrypts disk | Doesn't stop password guessing |
| Prey / LoJack | Remote tracking (paid) | Requires internet + subscription |
| Camera Apps | Always-on recording | Huge CPU drain, no integration |
| **IntruderGuard** ✅ | Event-driven + kernel-hooked | **Zero CPU, fully local, free** |

**Speaker Note:**
> "Existing commercial tools either burn CPU with 24/7 recording, require expensive subscriptions, or simply don't work at the lock screen level. **We operate at the Kernel level — which means we only activate when Windows itself signals a failure.** No polling. No constant camera feed."

---

### 🟥 SLIDE 4 — Our Solution

**Layout:** Split — Left bold text, Right screenshot of the app GUI

**Content:**
```
INTRODUCING: INTRUDERGUARD V2.0

When someone types the wrong password on your locked PC:

  1.  Windows Kernel logs Event ID 4625
  2.  IntruderGuard fires a ghost process (invisible)
  3.  Your webcam silently captures the intruder's face
  4.  Photo is saved to a secure local vault
  5.  You review the forensic evidence later

SILENT. INSTANT. PERSISTENT.
No window flashes. No popups. No hints.
```

**Visual:** Arrow flow diagram or screenshot of the CustomTkinter GUI dashboard showing the "ACTIVATE PROTECTION" button and green status indicator.

**Speaker Note:**
> "The moment an incorrect password is entered, in under 200 milliseconds, a silent Python process wakes up, opens the webcam, waits 2.5 seconds for the sensor to adjust to light conditions, snaps a photo, saves it, and goes back to sleep. **The intruder sees absolutely nothing.**"

---

### 🟥 SLIDE 5 — How It Works (The Pipeline)

**Layout:** Dark background, large terminal-style ASCII diagram

**Content:**
```
SYSTEM_FLOW // PIPELINE

[ OS KERNEL ] ──────► [ EVENT LOG: 4625 ] ──────► [ TASK SCHEDULER: ADMIN ]
                                                              │
                                                              ▼
[ GALLERY FOLDER ] ◄── [ PYTHON GHOST WORKER ] ◄── [ TRIGGER: BOOTSTRAP ]
       │                          │
       ▼                          ▼
[ SECURE VAULT ]        [ CV2_CAPTURE // 2.5s DELAY ]
```

**Three Pillars (icons below):**

| 🔍 Event Listener | 👻 Ghost Process | 🗄️ Forensic Vault |
|:-----------------|:----------------|:-----------------|
| Windows Event ID 4625 triggers the chain. Zero CPU usage while idle. | `pythonw.exe` under SYSTEM account — no UI, no terminal, invisible. | Photos saved with restricted ACL permissions. Admin-only access. |

**Speaker Note:**
> "This is the full pipeline. Notice how there are **three separate, decoupled components**: the OS Kernel does the detection, Task Scheduler does the bridging, and Python does the capture. If any one component is tampered with, the others remain intact. It's resilient by design."

---

### 🟥 SLIDE 6 — Key Feature: Ghost Process

**Layout:** Dark slide, terminal green text, monospace font throughout

**Content:**
```
FEATURE 01 // GHOST_PROCESS

The intruder sees: nothing.

  • Worker runs as:   pythonw.exe (no terminal window)
  • User account:     NT AUTHORITY\SYSTEM
  • Visibility:       ZERO — styled as standard system process
  • Trigger:          Windows Task Scheduler (not user-space)

SYSTEM ACCOUNT allows webcam access
even when NO user is logged in.

"pythonw" suppresses the console window.
An intruder browsing Task Manager sees
only standard system activity."
```

**Highlight box:**
```
⚡ LATENCY: < 200ms FROM EVENT TO CAPTURE
```

**Speaker Note:**
> "This is the core innovation. By running under the SYSTEM account, we bypass the normal user-session limitation — the camera is accessible. By using `pythonw` instead of `python`, we suppress every visual indicator. A sophisticated attacker who opens Task Manager will see nothing unusual."

---

### 🟥 SLIDE 7 — Key Feature: Kernel Event Hooking (0% CPU)

**Layout:** Light slide, clean infographic on left, text on right

**Content:**
```
FEATURE 02 // KERNEL_HOOK

Traditional apps "poll" — they check every second:
  ► "Has anything happened?" → NO
  ► "Has anything happened?" → NO  (repeat forever)

IntruderGuard registers with the OS Kernel:
  ► "Call me when Event ID 4625 fires."

RESULT: 0% CPU while your PC is idle.
         0 MB extra RAM consumed while locked.
         Only activates when a REAL event occurs.

This is the same mechanism used by enterprise
SIEM tools — built into a single Python script.
```

**Comparison Bar (visual):**
```
Traditional Camera Apps:   ████████████████████  ~15% CPU always
IntruderGuard:             ░░░░░░░░░░░░░░░░░░░░   0% CPU (event-driven)
```

**Speaker Note:**
> "We're not a background service chewing up your battery. We are an event-driven hook — exactly how enterprise Security Information and Event Management systems work. We just democratized that for personal users."

---

### 🟥 SLIDE 8 — Live Demo / Screenshots

**Layout:** Gallery grid — 4 screenshots with labels

**Screenshot Suggestions:**
1. **The Dashboard** — CustomTkinter GUI showing "PROTECTION: ACTIVE" status in green
2. **The Setup** — `Setup_Python.bat` running in a terminal (auto-install flow)
3. **The Vault** — Gallery folder with timestamped `CAPTURE_20260322_XXXX.jpg` files
4. **The Terminal Log** — `debug_log.txt` output showing capture events

**Content:**
```
DEMO // FORENSIC_OUTPUT

[ 01 DASHBOARD ]     [ 02 BAT INSTALLER ]
   Manager GUI          One-click setup

[ 03 GALLERY VAULT ] [ 04 TERMINAL LOG ]
   Timestamped JPGs     Capture events
```

**Speaker Note:**
> "Here are the four interfaces of IntruderGuard. The dashboard is where you activate protection. The BAT file is genuinely one right-click to full installation. The vault shows you your forensic gallery. And the log shows exactly when and why a capture was triggered."

---

### 🟥 SLIDE 9 — Tech Stack

**Layout:** Dark slide, icon grid with labels

**Content:**
```
TECH_STACK // BUILD_MANIFEST

CORE ENGINE
  ► Python 3.13+         [ Cross-version compatible ]
  ► OpenCV (CV2)         [ Multi-backend camera: DSHOW, MSMF ]
  ► CustomTkinter        [ High-contrast dark mode GUI ]
  ► Pillow (PIL)         [ Image post-processing ]

SYSTEM INTEGRATION
  ► Windows Task Scheduler  [ schtasks.exe / XML task creation ]
  ► Audit Policy (auditpol)  [ GUID-based failure auditing ]
  ► SYSTEM Account           [ Kernel-level process privilege ]
  ► Windows Security EventLog [ Event ID 4625 monitor ]

LANDING PAGE
  ► React + Vite             [ Frontend SPA ]
  ► Vanilla CSS              [ Brutalist design system ]
  ► CounterAPI               [ Live visit & download tracking ]
```

**Speaker Note:**
> "No cloud dependencies. No paid APIs. No framework bloat. The entire engine is 42KB of pure Python. Installation requires only three pip packages. The landing page is a Vite-compiled React SPA — fast, scalable, and hosted statically."

---

### 🟥 SLIDE 10 — Security & Privacy Model

**Layout:** Light slide, two-column (What we collect / What we DON'T)

**Content:**
```
SECURITY & PRIVACY // ZERO_EXFIL

WHAT WE CAPTURE:
  ✅ Webcam snapshot at time of failed login
  ✅ Timestamp embedded in filename
  ✅ Stored LOCALLY in /gallery with admin-only ACLs

WHAT WE DON'T DO:
  ❌ Upload photos to any server
  ❌ Track your keystrokes or clipboard
  ❌ Share data with third parties
  ❌ Require internet connection to function
  ❌ Persist between reboots without explicit activation

YOUR SECURITY IS YOUR OWN.
Everything stays on your machine.
```

**Speaker Note:**
> "Privacy was non-negotiable for us. Every photo is yours. The tool works fully offline. There are no telemetry calls except for the public page visit counter on the landing page. The only outbound request the app ever makes is your deliberate click on 'Download.'"

---

### 🟥 SLIDE 11 — Future Roadmap

**Layout:** Timeline / phased roadmap

**Content:**
```
ROADMAP // ENHANCEMENT_VECTORS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[PHASE I — CURRENT]  v2.0 Stable (Released March 2026)
  ✅ Event-driven Kernel hook
  ✅ Ghost process capture
  ✅ Automated one-click installer
  ✅ Forensic gallery viewer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[PHASE II — Q2 2026] Cloud Sync + Alerts
  🔲 Telegram Bot / Email notification on capture
  🔲 Cloud backup (Firebase / Supabase)
  🔲 Dashboard password protection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[PHASE III — Q3 2026] AI Integration
  🔲 Face recognition with embeddings (Pinecone)
  🔲 Known-intruder alert system
  🔲 Multi-device sync
  🔲 Stealth mode (disguised process name + folder)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Speaker Note:**
> "The current version is fully functional and our core innovation is already shipped. Phase II adds cloud and notifications so even if an intruder deletes local photos, you'd already have them in the cloud. Phase III introduces face embeddings — so if the same person tries twice, you'll be alerted immediately."

---

### 🟥 SLIDE 12 — Impact & Stats

**Layout:** Dark gold-accent slide, large numbers

**Content:**
```
IMPACT // BY_THE_NUMBERS

  400+         PAGE VISITS since launch
  5+           INSTALLATIONS in 48hrs post-release
  0.2s         TRIGGER LATENCY (event to capture)
  0%           CPU usage while system is idle
  1            Script — complete setup
  42KB         Total engine size
  3            pip packages (the entire dependency tree)

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

"The most aggressive physical security tool for Windows."
```

**Speaker Note:**
> "We launched publicly within 48 hours of writing the first line of code. Live page visit stats are being tracked in real time. The fact that we hit this purely through organic GitHub sharing in two days validates the need for this tool."

---

### 🟥 SLIDE 13 — Team / About

**Layout:** Clean centered layout on light background

**Content:**
```
THE BUILDER

[ PRATYAKSH RAJ ]

Full-Stack Developer | Security Enthusiast | Hackathon Builder

  🐙 GitHub:   github.com/OneforAll-Deku
  🐦 Twitter:  @PRATYAKSHRAJ11
  📧 Email:    newraj990@gmail.com

Built with: Python 3.13 | React + Vite | Windows API

"Built solo in under 72 hours as a hackathon submission,
 starting from a single question:
 What happens to my laptop when I walk away?"
```

**Speaker Note:**
> "This was built by me, solo, in under 72 hours — from concept to working product to the landing page you saw in the demo. The entire codebase is open source on GitHub. Every file, every design decision, every bug — documented and transparent."

---

### 🟥 SLIDE 14 — Call to Action (Final Slide)

**Layout:** Dark full-bleed, centered, crimson accents

**Content:**
```
TRY IT. STAR IT. STEAL THE IDEA.
(Just credit us.)

  ◉  GITHUB: github.com/OneforAll-Deku/Intruder-Guard

  ◉  INSTALL: Download ZIP → Right-click Setup_Python.bat
              → Run as Administrator → ACTIVATE → Win+L

  ◉  LANDING PAGE: [Your deployed URL here]

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

[QR CODE → GitHub Repo]

INTRUDERGUARD V2.0
"SILENT. INSTANT. PERSISTENT."
© 2026 Pratyaksh Raj
```

**Speaker Note:**
> "The link is live. The code is open. You can be running this on your own PC in literally 3 steps and 2 minutes. If you're a judge — try it. Lock your screen. Type a wrong password. See what shows up in the gallery. I'll be here to answer questions. Thank you."

---

## 🛠️ PPT Creation Tips

### Tools to Use
| Tool | Why |
|:-----|:----|
| **Canva** | Easiest — use dark "Pitch Deck" templates, custom colors |
| **Google Slides** | Collaborative, free, fast |
| **PowerPoint** | Most control — best for pixel-perfect brutalist layouts |
| **Figma** (export PNG slides) | Best quality, design-centric |

### Design Rules to Follow
1. **One idea per slide** — never crowd slides
2. **Max 3 fonts** — Heading / Body / Mono only
3. **Use crimson borders** (`#CC0000`) as visual anchors
4. **Terminal-style labels** in monospace at top small: `SECTION // SUBSECTION`
5. **Never use drop shadows on cards** — use hard offset box shadows (`offset-x offset-y 0px color`)
6. **Animate sparingly** — entrance animations on key facts only, no spinning logos

### Slide Transitions
- **Build slides:** Fade or appear (text builds line by line is powerful for pipeline slides)
- **Slide change:** Cut or Push — no dissolve or wipe
- **Terminal/code slides:** Typewriter animation if supported

### Common Hackathon Mistakes to Avoid
- ❌ Reading off the slide — the slide is a visual aid, you talk
- ❌ Too much text on one slide — use `< 30 words per slide` as a rule
- ❌ No live demo / screenshot — always show the product running
- ❌ Forgetting the problem statement — judges want to see the pain point first
- ❌ No roadmap — shows you've only thought short-term
- ❌ Tiny fonts — minimum 28pt for body, 48pt+ for headings

---

## 📋 Hackathon Judging Criteria Alignment

| Judging Criterion | Where IntruderGuard Shines | Slide(s) |
|:-----------------|:--------------------------|:---------|
| **Innovation** | Kernel-level hook, ghost process | 5, 6, 7 |
| **Technical Complexity** | `auditpol`, GUID-based auditing, SYSTEM account | 5, 9 |
| **Real-World Impact** | Physical security gap, open source, free | 2, 3, 12 |
| **Completeness** | Fully working v2.0, installer, GUI, gallery | 4, 8 |
| **Presentation Quality** | Brutalist design, clear narrative arc | All |
| **Scalability / Vision** | AI face recognition, cloud sync, multi-device | 11 |
| **Privacy / Ethics** | 100% local, no server uploads, disclaimer | 10 |

---

## 🗣️ 5-Minute Talk Track (Speed Run Version)

| Time | Content |
|:-----|:--------|
| 0:00–0:30 | Hook: "What happens to your laptop when you walk away?" |
| 0:30–1:00 | Problem + Market Gap (Slides 2–3) |
| 1:00–2:00 | Solution + Pipeline demo (Slides 4–5) |
| 2:00–3:00 | Two key features: Ghost + Kernel (Slides 6–7) |
| 3:00–4:00 | Live demo / screenshots + stats (Slides 8, 12) |
| 4:00–4:30 | Roadmap (Slide 11) |
| 4:30–5:00 | CTA + QR Code (Slide 14) |

---

## 📁 Assets Checklist

Before you present, have these ready:

- [ ] Screenshot of dashboard GUI (CustomTkinter app running)
- [ ] Screenshot of Setup_Python.bat running in terminal
- [ ] Sample gallery folder with CAPTURE_*.jpg files
- [ ] QR code linking to `github.com/OneforAll-Deku/Intruder-Guard`
- [ ] Live landing page URL (if deployed via Vercel/Netlify)
- [ ] Short screen-recorded demo video (optional, 30 seconds max)
- [ ] `debug_log.txt` output showing a successful capture event log

---

*This guide was written specifically for IntruderGuard v2.0 — March 2026 Hackathon Submission.*
*© Pratyaksh Raj | newraj990@gmail.com*
