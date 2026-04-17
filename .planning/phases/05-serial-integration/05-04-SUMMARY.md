---
phase: 05-serial-integration
plan: "04"
subsystem: verification
tags: [serial, hardware-verify, firmware, electron, status-dot, bug-fix]
dependency_graph:
  requires: [05-01, 05-02, 05-03]
  provides: [phase-05-complete]
  affects: [main.js, renderer.html, renderer.css]
key_files:
  created: []
  modified:
    - main.js
    - renderer.html
    - renderer.css
decisions:
  - "Hamburger button was broken: double function declaration caused hoisting to overwrite original — fixed by merging serial status query directly into original openSettings and removing the broken wrapper"
  - "Disconnect detection added to polling loop — macOS does not reliably fire SerialPort close event on USB unplug; poll now checks port presence while connected and forces disconnect if gone"
  - "startReconnectLoop now always starts on initSerial (not just on no-port-found) to enable continuous connect/disconnect monitoring"
metrics:
  duration_minutes: 15
  completed_date: "2026-04-17"
  tasks_completed: 3
  files_modified: 3
---

# Phase 5 Plan 4: Hardware Verification Summary

**One-liner:** Firmware and Electron serial integration verified end-to-end; three bugs found and fixed during verification gate.

## What Was Verified

All four SER requirements passed human verification:

| Req | Description | Result |
|-----|-------------|--------|
| SER-01 | DEFAULT → both displays OPEN_EYES (hollow ring) | ✓ PASS |
| SER-02 | SMILE → both displays SMILE (upper arc) | ✓ PASS |
| SER-03 | Electron auto-detects Arduino port, green dot on connect | ✓ PASS |
| SER-04 | Dot reacts to unplug/replug within ~3s | ✓ PASS |

## Bugs Fixed During Verification

### 1. `serialport` not installed
`npm install` had not been run after Plan 02 added the dependency. Fixed by running `npm install` (postinstall hook also ran `electron-rebuild`).

### 2. Hamburger button unresponsive
Plan 03's wrapper pattern (`const _origOpenSettings = openSettings; function openSettings() {...}`) created infinite recursion due to JavaScript function declaration hoisting — both declarations were hoisted, so `_origOpenSettings` captured the second (recursive) definition. Fixed by folding the serial status query directly into the original `openSettings` body and removing the wrapper.

### 3. Disconnect not updating status dot
macOS does not reliably fire the SerialPort `close` event on USB unplug. The polling loop only ran while disconnected, leaving no mechanism to detect unplug while connected. Fixed by making the poll loop run continuously: while connected it checks whether the Arduino port is still listed; if not, it forces disconnect and notifies the renderer.
