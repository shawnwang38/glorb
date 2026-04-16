---
phase: 01-app-shell
plan: 01
subsystem: infra
tags: [electron, tray, browserwindow, ipc, macos, menu-bar]

# Dependency graph
requires: []
provides:
  - Electron main process with macOS menu bar Tray icon
  - Frameless BrowserWindow 220x360px hidden on startup
  - Tray click toggle (show/hide) with position anchored below tray icon
  - Blur-to-hide behavior
  - Secure IPC preload bridge exposing window.glorb.quit()
  - Cmd+Q globalShortcut for direct quit
affects: [02-timer-ui, 03-settings-panel]

# Tech tracking
tech-stack:
  added: [electron@^29.0.0]
  patterns:
    - contextBridge.exposeInMainWorld for renderer-to-main IPC (never raw ipcRenderer)
    - app.dock.hide() + setActivationPolicy('accessory') for pure menu bar app
    - nativeImage.resize + setTemplateImage(true) for menu bar icon
    - module-level let tray/win for shared state across handlers

key-files:
  created:
    - package.json
    - main.js
    - preload.js
    - .gitignore
  modified: []

key-decisions:
  - "Use glorb.png resized to 18x18 as template image for automatic dark/light menu bar inversion"
  - "window-all-closed preventDefault keeps app alive as tray-only app (no quit on window close)"
  - "IPC channel named quit-app shared between ipcMain.handle (main.js) and ipcRenderer.invoke (preload.js)"
  - "contextIsolation: true + nodeIntegration: false enforces security boundary in BrowserWindow"

patterns-established:
  - "IPC bridge: expose named functions only via contextBridge.exposeInMainWorld, never raw ipcRenderer"
  - "Window visibility: tray click toggles show/hide; blur always hides"
  - "Quit paths: Cmd+Q (globalShortcut) or window.glorb.quit() from renderer"

requirements-completed: [SHELL-01, SHELL-02, SHELL-03, SHELL-04]

# Metrics
duration: 8min
completed: 2026-04-16
---

# Phase 01 Plan 01: App Shell — Electron Main Process Summary

**Electron menu bar app bootstrapped: Tray icon toggles a frameless 220x360px BrowserWindow with IPC quit bridge and Cmd+Q shortcut**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-04-16T20:42:45Z
- **Completed:** 2026-04-16T20:50:00Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- package.json with electron ^29.0.0 and `npm install` completing successfully
- main.js implementing full Electron main process: Tray, BrowserWindow (frameless, 220x360, contextIsolation), click toggle, blur-to-hide, globalShortcut Cmd+Q, IPC quit handler, window-all-closed prevention
- preload.js exposing only `window.glorb.quit()` via contextBridge — no raw ipcRenderer

## Task Commits

Each task was committed atomically:

1. **Task 1: Create package.json and install Electron** - `40488d4` (chore)
2. **Task 2: Create main.js — Electron main process** - `706aa1e` (feat)
3. **Task 3: Create preload.js — secure IPC bridge** - `90c838b` (feat)

**Extras:** `5c4048c` (chore: .gitignore for node_modules)

## Files Created/Modified

- `package.json` - Electron project config, `"main": "main.js"`, electron ^29.0.0 devDependency
- `main.js` - Full Electron main process: Tray, BrowserWindow, IPC, globalShortcut
- `preload.js` - Secure IPC bridge exposing window.glorb.quit() only
- `.gitignore` - Excludes node_modules from version control

## Decisions Made

- Used 18x18 tray icon size with `setTemplateImage(true)` for dark/light menu bar inversion
- `window-all-closed` event calls `e.preventDefault()` to keep app alive as tray-only (no Dock)
- IPC channel name `quit-app` is the single shared constant between main.js and preload.js
- Both `contextIsolation: true` and `nodeIntegration: false` set per threat model T-01-02

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added .gitignore for node_modules**
- **Found during:** Post-task cleanup (git status check)
- **Issue:** node_modules/ was untracked — would pollute repo without .gitignore
- **Fix:** Created .gitignore excluding node_modules/
- **Files modified:** .gitignore
- **Verification:** `git status --short | grep '^??'` returns nothing for node_modules
- **Committed in:** 5c4048c

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Minor housekeeping addition. No scope creep.

## Issues Encountered

- Verification script from PLAN.md had an unescaped regex character (`tray.on(` without escaping the `(`). Rewrote check inline with properly escaped regex. main.js verified correct.

## User Setup Required

None - no external service configuration required. `npm install && npm start` is the only setup needed.

## Next Phase Readiness

- Electron main process is complete and ready for Plan 02 (renderer.html + timer UI)
- renderer.html not yet created — the window shows a "file not found" error on launch, which is expected and will be resolved in Plan 02
- glorb.png is present at project root and used as tray icon; will also be used in Phase 2 ring timer

---
*Phase: 01-app-shell*
*Completed: 2026-04-16*
