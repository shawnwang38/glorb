---
phase: 08-intervention-engine
plan: "03"
subsystem: intervention-engine
tags: [electron, overlay, ipc, strong-paths, audio-fade]
dependency_graph:
  requires: [08-01, 08-02]
  provides: [runStrongRegular, runStrongADHD, createOverlayWindow, flash.html, vignette.html, terminate.html]
  affects: [main.js, preload.js]
tech_stack:
  added: [osascript-volume-fade, electron-screen-api, full-screen-overlay-window]
  patterns: [trackTimeout-chain, overlay-window-pattern, dwell-to-dismiss]
key_files:
  created: [flash.html, vignette.html, terminate.html]
  modified: [main.js, preload.js]
decisions:
  - "createOverlayWindow uses screen.getPrimaryDisplay().workAreaSize for full coverage"
  - "fadeAudioOver30s uses osascript set volume in 10 steps of 3s (D-03)"
  - "terminate.html uses mousemove dwell timer as proxy for looking at screen (D-08)"
  - "vignette.html uses CSS prefers-color-scheme for dark/light edge effect (D-07)"
metrics:
  duration_minutes: 25
  completed: "2026-04-18"
  tasks_completed: 2
  files_changed: 5
---

# Phase 8 Plan 03: Strong Escalation Paths Summary

Strong path overlay infrastructure with three full-screen BrowserWindow overlays (flash, vignette, terminate) and complete runStrongRegular() / runStrongADHD() implementations with notification, chime/note escalation, audio fade, and dwell-to-dismiss terminate screen.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Overlay infrastructure + HTML files | 8408ba8 | main.js, preload.js, flash.html, vignette.html, terminate.html |
| 2 | runStrongRegular() and runStrongADHD() | 8408ba8 | main.js |

## What Was Built

### createOverlayWindow(htmlFile, durationMs)
Helper in main.js that creates a full-screen, always-on-top, frameless, transparent BrowserWindow. Replaces any existing overlayWin before creating the new one. Auto-closes after durationMs if provided (null = dwell-to-dismiss only). Window ref cleared via `closed` event.

### fadeAudioOver30s()
Uses osascript to decrement system output volume from 100 to 0 in 10 steps of 3s each, all scheduled via trackTimeout() so refocusDetected() / clearAllTimers() will cancel them.

### runStrongRegular()
- 15s: push "Stay focused!" + 1 chime
- Every 10s: 2nd ping = 2 chimes; 3rd ping = 3 chimes + "Last reminder" push
- After 3rd ping: 1s delay → 2s flash overlay (flash.html), then 2s → audio fade 30s, then 500ms → 60s vignette, then 60s → terminate screen (dwell-to-dismiss)

### runStrongADHD()
- 10s: push "Stay focused!" + 1 note
- Every 5s up to 5 pings with increasing notes (1→5)
- After 5th ping: 5s flash overlay (flash.html), then 5s → audio fade 30s, then 500ms → 60s vignette, then 60s → terminate screen (dwell-to-dismiss)

### flash.html
Full-screen dark overlay (rgba 85% black) showing glorb.png + "Still there?" text. Auto-closes via main.js durationMs (2s for Regular, 5s for ADHD).

### vignette.html
Full-screen transparent overlay with pulsing CSS radial-gradient vignette. Light mode: darkens edges. Dark mode: brightens edges (white vignette). pointer-events: none so it doesn't capture clicks. Dismissed by clearAllTimers() or refocusDetected().

### terminate.html
Full-screen white/black (light/dark mode) background with large glorb.png and "Focus." text. 5s continuous mousemove dwell timer — mouse must stay over window for 5 continuous seconds to dismiss. Calls window.glorb.closeOverlay() which invokes close-overlay IPC.

### close-overlay IPC handler
Added to main.js after close-onboarding handler. Closes and nulls overlayWin.

### closeOverlay in preload.js
Added to contextBridge glorb object as `closeOverlay: () => ipcRenderer.invoke('close-overlay')`.

## Deviations from Plan

None - plan executed exactly as written. Both tasks were implemented in a single commit because the implementations depended on the infrastructure being in place simultaneously.

## Known Stubs

None. All Strong path functions are fully implemented.

## Threat Surface Scan

No new threat surface beyond what was documented in the plan's threat model (T-08-07, T-08-08, T-08-09).

## Self-Check: PASSED

- flash.html exists: FOUND
- vignette.html exists: FOUND
- terminate.html exists: FOUND
- Commit 8408ba8 exists: FOUND
- main.js contains createOverlayWindow: FOUND
- main.js contains runStrongRegular: FOUND
- main.js contains runStrongADHD: FOUND
- main.js contains fadeAudioOver30s: FOUND
- main.js contains close-overlay: FOUND
- preload.js contains closeOverlay: FOUND
- node --check main.js: PASSED
- node --check preload.js: PASSED
