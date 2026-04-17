---
phase: 06-timer-event-wiring
plan: 01
subsystem: ipc-serial-bridge
tags: [ipc, serial, electron, preload, main-process]
dependency_graph:
  requires: [Phase 05 serial port setup — serialPort variable and isConnected flag in main.js]
  provides: [window.glorb.sendSerial(cmd) callable from renderer; routes to serialPort.write(cmd) in main process]
  affects: [main.js, preload.js]
tech_stack:
  added: []
  patterns: [ipcMain.handle + contextBridge.exposeInMainWorld IPC pattern]
key_files:
  created: []
  modified:
    - main.js
    - preload.js
decisions:
  - Silent no-op when serialPort is null or closed — no throw, no log (D-03)
  - cmd must include newline, e.g. 'SMILE\n' or 'DEFAULT\n' (D-04)
metrics:
  duration: ~3 min
  completed_date: 2026-04-17
  tasks_completed: 2
  files_modified: 2
---

# Phase 06 Plan 01: Send-Serial IPC Channel Summary

Established the `send-serial` IPC plumbing between renderer and main process: `window.glorb.sendSerial(cmd)` in the renderer routes through contextBridge to `ipcMain.handle('send-serial')` in main.js, which writes to `serialPort` when open and silently no-ops when disconnected.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add send-serial IPC handler in main.js | e424b24 | main.js |
| 2 | Expose sendSerial on window.glorb in preload.js | 4a1eed2 | preload.js |

## What Was Built

- `ipcMain.handle('send-serial', (event, cmd) => { ... })` appended to main.js after the existing `serial-status` handler
- Handler guards with `serialPort && serialPort.isOpen` before calling `serialPort.write(cmd)` — silent no-op when disconnected
- `sendSerial: (cmd) => ipcRenderer.invoke('send-serial', cmd)` added to the `window.glorb` contextBridge object in preload.js
- Channel name `'send-serial'` is exact match between handler and invoker

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — this plan adds pure IPC plumbing with no UI rendering or data stubs.

## Threat Flags

No new security-relevant surface introduced beyond what is documented in the plan's threat model. All three threats (T-06-01, T-06-02, T-06-03) were reviewed and accepted as per plan.

## Self-Check: PASSED

- main.js: `ipcMain.handle('send-serial'` present, `serialPort.isOpen` guard present, `serialPort.write(cmd)` present
- preload.js: `sendSerial` present, `invoke('send-serial'` present, syntax clean
- Commits e424b24 and 4a1eed2 verified in git log
