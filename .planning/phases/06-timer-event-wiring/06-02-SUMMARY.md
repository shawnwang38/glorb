---
phase: 06-timer-event-wiring
plan: 02
subsystem: renderer-serial-events
tags: [renderer, serial, timer, ipc, electron]
dependency_graph:
  requires: [Phase 06 Plan 01 — window.glorb.sendSerial(cmd) IPC bridge in preload.js/main.js]
  provides: [All timer events wired to sendSerial: start SMILE, cancel DEFAULT, complete latch, visibilitychange latch release]
  affects: [renderer.html]
tech_stack:
  added: []
  patterns: [setTimeout for timed revert, timestamp-based latch (latchEndTime), visibilitychange for window-open detection]
key_files:
  created: []
  modified:
    - renderer.html
decisions:
  - serialRevertTimer and latchEndTime declared after sessionStartTime in Phase 6 block (D-02, D-10)
  - sendSmile/sendDefault/clearSerialRevert extracted as named helpers for DRY call sites
  - Timer start SMILE inserted after timerState = running so state is consistent before serial fires
  - Cancel DEFAULT inserted before addFocusTime to ensure DEFAULT fires even if addFocusTime is slow
  - latchEndTime set before visibility check in tick() completion so D-07 branch can read and clear it cleanly
metrics:
  duration: ~8 min
  completed_date: 2026-04-17
  tasks_completed: 2
  files_modified: 1
---

# Phase 06 Plan 02: Timer Event Wiring to Serial Eye Commands Summary

Wired all four timer lifecycle events in renderer.html to serial eye commands via `window.glorb.sendSerial`: start fires SMILE with 5s revert (BEH-01), cancel fires DEFAULT and clears the revert (BEH-01), completion fires SMILE with a timestamp latch that survives window hide cycles (BEH-02/03), and visibilitychange releases the latch with the 5s minimum enforced (BEH-03).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add serial state variables and helper functions | fddd72c | renderer.html |
| 2 | Wire timer start, cancel, complete, and latch release events | c52d105 | renderer.html |

## What Was Built

**Task 1 — State + helpers (renderer.html ~line 185):**
- `let serialRevertTimer = null` — holds the setTimeout id for the 5s SMILE→DEFAULT revert after timer start
- `let latchEndTime = 0` — ms timestamp; >0 means a complete-latch is active
- `sendSmile()` — calls `window.glorb.sendSerial('SMILE\n')`
- `sendDefault()` — calls `window.glorb.sendSerial('DEFAULT\n')`
- `clearSerialRevert()` — clears `serialRevertTimer` if set, preventing double-fire

**Task 2 — Four integration points:**

- **Edit A (timer start):** In `btnStart` idle branch, immediately after `timerState = 'running'`: calls `clearSerialRevert()`, `sendSmile()`, schedules `serialRevertTimer = setTimeout(sendDefault, 5000)`. SMILE fires the same frame the user clicks Focus.

- **Edit B (timer cancel):** In `btnStart` running branch, before `addFocusTime`: calls `clearSerialRevert()`, clears `latchEndTime = 0`, calls `sendDefault()`. DEFAULT fires immediately on Unfocus regardless of any pending revert.

- **Edit C (timer complete):** In `tick()` completion block, before `resetTimer()`: calls `clearSerialRevert()`, `sendSmile()`, sets `latchEndTime = Date.now() + 5000`. If window is already visible (D-07), clears `latchEndTime` immediately and schedules a 5s `serialRevertTimer` instead (brief flash, no latch).

- **Edit D (latch release):** Extends the existing `visibilitychange` listener with a `visible && latchEndTime > 0` branch: if minimum 5s not yet elapsed, schedules `serialRevertTimer` for the remaining delta; otherwise sends DEFAULT immediately. Clears `latchEndTime` in both paths. The existing `hidden && settingsOpen` branch is untouched.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all serial calls are wired to the live `window.glorb.sendSerial` bridge established in Plan 01. No placeholder values.

## Threat Flags

No new security-relevant surface introduced. All `sendSerial` call sites use string literals (`'SMILE\n'`, `'DEFAULT\n'`); no user input reaches `sendSerial`. T-06-04, T-06-05, T-06-06 all accepted per plan threat model.

## Self-Check: PASSED

- renderer.html: `serialRevertTimer`, `latchEndTime`, `sendSmile`, `sendDefault`, `clearSerialRevert` all present
- renderer.html: `setTimeout(sendDefault, 5000)` present in start branch
- renderer.html: `latchEndTime = Date.now() + 5000` present in tick() completion block
- renderer.html: `visibilityState === 'visible' && latchEndTime > 0` present in visibilitychange
- renderer.html: `visibilityState === 'hidden' && settingsOpen` unchanged
- Commits fddd72c and c52d105 verified in git log
