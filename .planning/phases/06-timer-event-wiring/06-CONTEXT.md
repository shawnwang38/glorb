# Phase 6: Timer Event Wiring - Context

**Gathered:** 2026-04-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire timer start and timer complete events in the Electron renderer to the Arduino serial displays. Phase 6 delivers:
- Timer start → sends SMILE, reverts to DEFAULT after 5 seconds
- Timer complete → sends SMILE, latched until user opens the Glorb window (minimum 5s)
- Cancel (Unfocus) → sends DEFAULT immediately, clears any pending timeout
- No-hardware graceful degradation — all serial calls no-op when disconnected

This is purely Electron-side wiring. Firmware and serial plumbing are complete (Phase 4–5). No new firmware changes.

</domain>

<decisions>
## Implementation Decisions

### Serial IPC Architecture

- **D-01:** Expose `sendSerial(cmd)` in `preload.js` → `ipcMain.handle('send-serial', ...)` in `main.js`. Consistent with existing IPC pattern (`serialStatus`, `notify`, etc.).
- **D-02:** 5-second SMILE→DEFAULT timeout lives in the renderer (simple `setTimeout` after sending SMILE). Renderer already owns `timerState` context.
- **D-03:** `sendSerial` is a silent no-op in `main.js` when `isConnected === false`. No error, no log — consistent with existing no-hardware behavior.
- **D-04:** API shape: `glorb.sendSerial(cmd)` with string arg — `'SMILE\n'` or `'DEFAULT\n'`. Single method, not separate `sendSmile()`/`sendDefault()`.

### Timer Start & Cancel Timing

- **D-05:** SMILE fires immediately on start button click (same moment `timerState = 'running'`), not deferred to first tick.
- **D-06:** On cancel (Unfocus button): send DEFAULT immediately + clear the pending 5s revert timeout (if any).
- **D-07:** If the Glorb window is already visible when timer completes: still send SMILE for 5s then DEFAULT — no latch (window is already open). Behavior is "brief SMILE flash" not a latch.
- **D-08:** On serial disconnect mid-timer: all `sendSerial` calls silently no-op. Timer state continues normally in app.

### Latch Release Mechanics

- **D-09:** Renderer detects window opening via `document.addEventListener('visibilitychange', ...)` — no new IPC needed.
- **D-10:** Latch stored as `latchEndTime` (timestamp) in renderer. On visibilitychange to `visible`: if `Date.now() < latchEndTime`, schedule `setTimeout(sendDEFAULT, latchEndTime - Date.now())`; else send DEFAULT immediately. Then clear `latchEndTime`.
- **D-11:** Latch is volatile — lost on app restart. No electron-store persistence. Hardware holds last state; will sync on next command.
- **D-12:** Latch survives window hide/show cycles — only resolves on the next window-open (visibilitychange to `visible`). Hiding the window does NOT send DEFAULT.

### Claude's Discretion

- Exact variable names and placement within renderer.html script block
- Whether to extract sendSmile/sendDefault as named local helpers inside renderer for clarity
- Timer-complete SMILE flow: whether to set `latchEndTime` before or after checking visibility

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets

- `main.js`: `serialPort`, `isConnected`, `notifyConnectionState()` — serial plumbing complete. Add `ipcMain.handle('send-serial', ...)` here.
- `preload.js`: `contextBridge.exposeInMainWorld('glorb', {...})` — add `sendSerial` method here.
- `renderer.html`: `timerState`, `intervalId`, `btnStart` click handler, `tick()`, `resetTimer()` — all timer hooks are in the inline `<script>` block.
- `openSettings()` / `closeSettings()` — settings panel logic (for reference, latch release is on window show, not settings open).

### Established Patterns

- IPC: renderer calls `window.glorb.X()` → preload invokes `ipcRenderer.invoke('x', ...)` → main handles via `ipcMain.handle('x', ...)`.
- Serial: main.js checks `isConnected` before any serial write — no special caller-side guards needed.
- Timer state machine: `timerState` = `'idle' | 'running' | 'paused'` (note: pause is defined but not currently wired to a button — cancel goes straight to idle).

### Integration Points

- `main.js`: add `ipcMain.handle('send-serial', (event, cmd) => { if (serialPort && serialPort.isOpen) serialPort.write(cmd) })`
- `preload.js`: add `sendSerial: (cmd) => ipcRenderer.invoke('send-serial', cmd)` inside the exposeInMainWorld object
- `renderer.html` script: wire into `btnStart` click handler (start → send SMILE), `tick()` completion block (complete → send SMILE + set latchEndTime), `resetTimer()` call sites (cancel path → send DEFAULT), and `visibilitychange` listener (release latch)

</code_context>

<specifics>
## Specific Ideas

- Commands must include the newline: `'SMILE\n'` and `'DEFAULT\n'` (firmware uses `readStringUntil('\n')`).
- The 5s revert after timer **start** and the 5s minimum after timer **complete** are independent timeouts with the same duration but different behaviors (revert vs latch).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
