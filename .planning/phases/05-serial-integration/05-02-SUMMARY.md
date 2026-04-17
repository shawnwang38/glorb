---
phase: 05-serial-integration
plan: "02"
subsystem: electron-serial
tags: [serialport, ipc, arduino, electron, native-bindings]
dependency_graph:
  requires: []
  provides: [serial-auto-detect, serial-reconnect, serial-ipc]
  affects: [main.js, preload.js, package.json]
tech_stack:
  added: [serialport@12, "@electron/rebuild@4"]
  patterns: [native-node-addon, ipc-bridge, polling-reconnect]
key_files:
  created: []
  modified:
    - package.json
    - main.js
    - preload.js
decisions:
  - "@electron/rebuild used instead of electron-rebuild — Python 3.14 removed distutils which electron-rebuild@3.2.9 requires via node-gyp; @electron/rebuild ships newer node-gyp that works without distutils"
  - "Postinstall script kept as 'electron-rebuild' — @electron/rebuild installs that binary name so the script resolves correctly"
metrics:
  duration_minutes: 8
  completed_date: "2026-04-17"
  tasks_completed: 2
  files_modified: 3
---

# Phase 5 Plan 2: Serial Auto-Detect and IPC Lifecycle Summary

**One-liner:** Arduino serial auto-detect with VID/PID matching, 3-second reconnect polling, and renderer IPC bridge via serialStatus/onSerialStatus.

## What Was Built

Added full serial connection lifecycle to the Glorb Electron app:

1. **package.json** — Added `serialport ^12.0.0` as runtime dep and `@electron/rebuild ^4.0.3` as devDep with a `postinstall` script. Native bindings compiled successfully.

2. **main.js** — Added the complete serial module:
   - `ARDUINO_VIDS` set covering genuine Arduino (2341), CH340 clone (1a86), and Arduino.org (2a03)
   - `findArduinoPort()` — lists ports, matches by VID/PID first, falls back to manufacturer string containing "arduino" or "ch340"
   - `openPort(portPath)` — opens at 115200 baud, handles open error and unexpected close/error events silently (no dialogs), starts reconnect loop on failure
   - `startReconnectLoop()` — polls every 3 seconds, has `if (reconnectTimer) return` guard (T-05-05 mitigation), clears itself when connected
   - `notifyConnectionState()` — sends `serial-status-changed` IPC event to renderer when state changes
   - `initSerial()` — called inside `app.whenReady()`, attempts port detection on startup, falls back to reconnect loop if no Arduino found
   - `ipcMain.handle('serial-status')` — returns `{ connected: boolean }` only (no port path, no PII — T-05-04 accepted)

3. **preload.js** — Added two entries to `window.glorb`:
   - `serialStatus()` — invoke-style query for current connection state
   - `onSerialStatus(callback)` — subscribes to push notifications of state changes

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Add serialport and @electron/rebuild to package.json, install and rebuild native bindings | dd9abc9 |
| 2 | Add serial auto-detect, lifecycle management, and IPC to main.js and preload.js | b262fc9 |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used @electron/rebuild instead of electron-rebuild**
- **Found during:** Task 1
- **Issue:** `electron-rebuild@3.2.9` uses `node-gyp` that imports Python `distutils`, which was removed in Python 3.12+. System runs Python 3.14.3. Rebuild failed with `ModuleNotFoundError: No module named 'distutils'`.
- **Fix:** Installed `@electron/rebuild@4.0.3` (the official successor, same API/CLI). Kept `postinstall` script as `"electron-rebuild"` since `@electron/rebuild` installs that binary name. Removed deprecated `electron-rebuild` from devDependencies.
- **Files modified:** package.json, package-lock.json
- **Commit:** dd9abc9

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes beyond what the threat model covers. The `serial-status` IPC returns boolean only (T-05-04 accepted). The reconnect loop interval guard is in place (T-05-05 mitigated).

## Known Stubs

None — serial layer is functional. No data flows to UI yet (Plan 03 adds the status dot indicator).

## Self-Check: PASSED

- main.js: `grep "require('serialport')" main.js` — 1 match at line 4
- main.js: `grep "initSerial()" main.js` — 1 match inside whenReady at line 151
- main.js: `grep "ARDUINO_VIDS" main.js` — matches with all 3 VIDs
- main.js: `grep "3000" main.js` — setInterval at line 99
- main.js: `grep "ipcMain.handle('serial-status'" main.js` — 1 match at line 183
- preload.js: `grep "serialStatus\|onSerialStatus" preload.js` — 2 matches
- native bindings: `ls node_modules/@serialport/bindings-cpp/build/Release/*.node` — bindings.node present
- commits: dd9abc9 and b262fc9 verified in git log
