---
phase: 06-timer-event-wiring
reviewed: 2026-04-17T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - main.js
  - preload.js
  - renderer.html
findings:
  critical: 0
  warning: 1
  info: 3
  total: 4
status: issues_found
---

# Phase 6: Code Review Report

**Reviewed:** 2026-04-17
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Phase 6 adds the `send-serial` IPC handler in `main.js`, exposes `sendSerial` in `preload.js`, and wires serial eye state commands (`SMILE`/`DEFAULT`) into the timer start, cancel, and completion events in `renderer.html`. The security posture is sound: the IPC handler does a silent no-op when disconnected (D-03), context isolation is enforced, and no user input is interpolated into the serial command. The latch logic for the completion path (D-09/D-10) is mostly correct, but one defensive gap exists in the `visibilitychange` handler. Three lower-severity items are noted below.

## Warnings

### WR-01: `visibilitychange` latch-release sets `serialRevertTimer` without clearing any prior timer

**File:** `renderer.html:423`
**Issue:** When the window becomes visible and `latchEndTime > 0`, the handler schedules a new `serialRevertTimer` timeout without first calling `clearSerialRevert()`. If `serialRevertTimer` happens to be non-null on entry — possible if a future code path (e.g., a new caller of `resetTimer()`) leaves it set — the old timeout is orphaned. The current control-flow makes this benign today because `clearSerialRevert()` is always called before `latchEndTime` is set, but the assumption is fragile.

**Fix:**
```js
if (document.visibilityState === 'visible' && latchEndTime > 0) {
  const remaining5s = latchEndTime - Date.now()
  clearSerialRevert()   // <-- add this before any new setTimeout
  if (remaining5s > 0) {
    serialRevertTimer = setTimeout(() => {
      sendDefault()
      latchEndTime = 0
    }, remaining5s)
  } else {
    sendDefault()
  }
  latchEndTime = 0
}
```

## Info

### IN-01: `serialPort.write()` called without an error callback

**File:** `main.js:188`
**Issue:** `serialPort.write(cmd)` is invoked without a callback. The `serialport` library will emit a general `'error'` event for port-level errors (handled at line 127), but write-specific errors (e.g., partial write, EAGAIN) may not trigger the port `'error'` event and will be silently swallowed. Per D-03 this is intentional, but the current `'error'` handler destroys the port and resets `isConnected`, which is a heavier response than a transient write failure warrants.

**Fix:** Either accept the current behavior and document it explicitly, or use the write callback to handle transient errors without tearing down the connection:
```js
ipcMain.handle('send-serial', (event, cmd) => {
  if (serialPort && serialPort.isOpen) {
    serialPort.write(cmd, (err) => {
      // D-03: silent — transient write errors do not trigger reconnect
    })
  }
})
```

### IN-02: `ipcRenderer.on` listener in `preload.js` is never removed

**File:** `preload.js:10`
**Issue:** `onSerialStatus` registers a listener via `ipcRenderer.on(...)` with no corresponding `ipcRenderer.removeListener` or `ipcRenderer.removeAllListeners`. If the renderer page is reloaded (e.g., via DevTools), each reload stacks an additional listener for `serial-status-changed`. In production this is a single-page app that never reloads, so the risk is low, but it can cause unexpected double-firing during development.

**Fix:**
```js
onSerialStatus: (callback) => {
  ipcRenderer.removeAllListeners('serial-status-changed')
  ipcRenderer.on('serial-status-changed', (_event, data) => callback(data))
}
```

### IN-03: `resetTimer()` does not call `clearSerialRevert()`

**File:** `renderer.html:252-267`
**Issue:** `resetTimer()` fully resets timer state but does not clear `serialRevertTimer`. Currently all callers handle this correctly (the `tick()` completion branch deliberately leaves the revert timer running; the cancel branch clears it before calling `resetTimer()`). If `resetTimer()` gains additional call sites in the future, the serial revert timer will silently survive the reset and fire `sendDefault()` at an unexpected time.

**Fix:** Add `clearSerialRevert()` at the top of `resetTimer()` and document any callers that intentionally need the timer to survive:
```js
function resetTimer() {
  clearSerialRevert()  // clear any pending serial revert unless caller re-arms it
  clearInterval(intervalId)
  intervalId = null
  // ... rest unchanged
}
```
Note: the `tick()` completion branch would then need to re-arm `serialRevertTimer` after calling `resetTimer()`, which is the safer explicit pattern.

---

_Reviewed: 2026-04-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
