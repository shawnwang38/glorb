# Glorb

A macOS menu-bar Pomodoro that actually notices when you drift — and does something about it.

Set a timer, type what you're working on, and start. Glorb watches two channels in parallel:

- **Camera (USB only)** — a headless Python detector tracks head pose and eye strain via MediaPipe. Looking away, leaving your desk, or sustained abnormal blink rate all register.
- **Active app** — a small Node polling loop asks a local Ollama model ("which apps are actually needed for this task?") and flags switches to apps outside that set.

When either channel decides you've drifted, Glorb escalates through a configurable path — soft chimes, notifications, screen dim, full-screen vignette — tuned to your onboarding profile (Weak/Strong × Neurotypical/ADHD). Refocus, and everything quietly clears.

An optional Arduino companion (an SSD1306 OLED pair) renders Glorb's eyes over serial — blinking, smiling, or closed depending on session state.

## Stack

- **App:** Electron 29, vanilla HTML/CSS/JS (no bundler)
- **Camera detection:** Python 3.9–3.13 + MediaPipe 0.10.14 + OpenCV (runs as a managed subprocess)
- **App detection:** Ollama (`qwen3:1.7b`) + `osascript`
- **Hardware (optional):** Arduino + SSD1306 OLED × 2, firmware in `firmware/` (PlatformIO)
- **Persistence:** `electron-store`

## Setup

```bash
npm install          # installs Electron deps + auto-provisions camera_detect/.venv
npm start            # launches the menu-bar app
```

The postinstall step (`scripts/setup-python.cjs`) finds a compatible Python on your machine and installs the detection deps into `camera_detect/.venv`. If no Python is found, app detection still works — camera detection is silently disabled.

For app-based distraction detection:

```bash
brew install ollama
ollama serve
ollama pull qwen3:1.7b
```

On first run, macOS will prompt for:
- **Camera** access (for USB focus tracking)
- **Automation** access (Electron → System Events, for active-app polling)

## Repo layout

```
main.js / preload.js / renderer.html / onboarding.html   Electron app
renderer.css / onboarding.css                            Styles
assets/                                                  Mascot + icon pngs
camera_detect/                                           Python tracking pipeline
  run.py                                                   headless entrypoint
  camera.py detector.py focus.py fatigue.py ...            modules
app_detect/                                              Node app classifier
  src/predict.js appDetection.js normalize.js ollama.js    pure modules
  config/overrides.json                                    always/manual allow/block
firmware/                                                Arduino OLED firmware
scripts/setup-python.cjs                                 postinstall bootstrap
```

## How the pieces talk

```
  renderer.html          preload.js          main.js
  ┌──────────┐  setTask  ┌─────┐  IPC   ┌────────────────┐
  │ task box ├──────────►│     ├───────►│ app-detect     │──┐
  └──────────┘           └─────┘        │ polling (1s)   │  │
                                        │                │  ├─► dispatchDrift()
                                        │ camera Python ◄┼──┤   (escalation)
                                        │  subprocess    │  │
                                        └────────────────┘  └─► dispatchRefocus()
                                        (AF_UNIX socket           (clear timers)
                                        @ /tmp/glorb-ipc.sock
                                        — drift/refocus/fatigue)
```

Both channels feed one dispatcher, so a single drift from either source starts the escalation and a single refocus clears it.

## Constraints

- macOS only.
- Camera detection never opens the built-in FaceTime HD camera — only USB webcams.
- All detection is edge-triggered (per state transition, not per frame/tick).
