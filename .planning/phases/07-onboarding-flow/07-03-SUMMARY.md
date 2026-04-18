---
phase: 07-onboarding-flow
plan: "03"
subsystem: electron-main
tags: [onboarding, ipc, electron, main-process, preload]
dependency_graph:
  requires: ["07-01", "07-02"]
  provides: ["onboarding-gate", "onboarding-ipc-lifecycle"]
  affects: [main.js, preload.js, renderer.html]
tech_stack:
  added: []
  patterns: ["ipcMain.handle for onboarding lifecycle", "BrowserWindow gate on store flag"]
key_files:
  created: []
  modified:
    - main.js
    - preload.js
    - renderer.html
decisions:
  - "Onboarding window is framed (frame: true), 800x620, centered, not always-on-top — distinct from tray popup"
  - "open-onboarding IPC resets onboardingComplete flag so retake starts from Q1"
  - "close-onboarding checks isDestroyed() before calling close() to prevent double-close errors (T-07-07 mitigation)"
metrics:
  duration: "~5 min"
  completed: "2026-04-18T22:00:23Z"
  tasks_completed: 2
  tasks_total: 3
  files_modified: 3
---

# Phase 07 Plan 03: Onboarding Window Wiring Summary

**One-liner:** Electron main process wired with createOnboardingWindow() gate on first launch, open/close IPC channels, and Retake Test button in renderer.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Add createOnboardingWindow, gate logic, and IPC handlers to main.js | a3d5d1c | main.js |
| 2 | Extend preload.js with closeOnboarding/openOnboarding; wire Retake Test in renderer.html | b959181 | preload.js, renderer.html |

## What Was Built

### Task 1 — main.js changes

- Added `let onboardingWin = null` module-level variable
- Added `createOnboardingWindow()` function: 800x620 framed window, centered, not always-on-top, loads `onboarding.html`
- Updated `app.whenReady()` to check `store.get('onboardingComplete', false)` and call `createOnboardingWindow()` if not set
- Added `ipcMain.handle('open-onboarding', ...)` — resets `onboardingComplete` flag, creates or focuses window
- Added `ipcMain.handle('close-onboarding', ...)` — safely closes window with `isDestroyed()` guard

### Task 2 — preload.js + renderer.html changes

- Added `closeOnboarding` and `openOnboarding` properties to `window.glorb` contextBridge API
- Added click handler for `#btn-retake` in renderer.html that calls `window.glorb.openOnboarding()`

## Deviations from Plan

None — plan executed exactly as written.

## Threat Model Coverage

| Threat | Mitigation | Status |
|--------|-----------|--------|
| T-07-07: close-onboarding called multiple times | `!onboardingWin.isDestroyed()` guard before close() | Implemented |
| T-07-06: open-onboarding channel | Only opens BrowserWindow, no privileged ops | Accepted |
| T-07-08: onboardingComplete store flag | Local store, no remote trust boundary | Accepted |

## Known Stubs

None — all wiring is functional. `onboarding.html` must exist for the window to load (provided by plan 07-02).

## Checkpoint

Task 3 is a `checkpoint:human-verify` requiring manual testing of the full onboarding flow end-to-end. See verification steps in 07-03-PLAN.md Task 3.

## Self-Check

## Self-Check: PASSED

- main.js: FOUND
- preload.js: FOUND
- renderer.html: FOUND
- 07-03-SUMMARY.md: FOUND
- commit a3d5d1c: FOUND
- commit b959181: FOUND
