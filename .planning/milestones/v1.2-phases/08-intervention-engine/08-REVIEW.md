---
phase: 08-intervention-engine
reviewed: 2026-04-18T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - main.js
  - preload.js
  - renderer.html
  - flash.html
  - vignette.html
  - terminate.html
  - simulate.js
findings:
  critical: 3
  warning: 4
  info: 4
  total: 11
status: issues_found
---

# Phase 08: Code Review Report

**Reviewed:** 2026-04-18
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

This phase adds the intervention engine: an escalation state machine in the main process, four escalation paths (`runWeakRegular`, `runWeakADHD`, `runStrongRegular`, `runStrongADHD`), overlay infrastructure (`flash.html`, `vignette.html`, `terminate.html`), and a dev CLI tool (`simulate.js`). The architecture is sound — all state lives in the main process, timers are tracked centrally, and overlay windows are reused via `overlayWin`. The most significant issues are an irreversible system-volume mutation, a wrong-direction dwell logic in the terminate screen, and a crash path in the `resize-window` IPC handler.

---

## Critical Issues

### CR-01: `fadeAudioOver30s` mutates system volume and never restores it

**File:** `main.js:182-192`

**Issue:** `fadeAudioOver30s` uses `osascript` to lower the user's global macOS output volume to 0 over 30 seconds. If `clearAllTimers()` is called mid-fade (e.g. the user hits refocus), the already-enqueued `trackTimeout` callbacks for remaining steps are cleared, but the volume stays permanently at whatever step it last reached (e.g. 40%). There is no restore path anywhere. A user who regains focus early will be left with a silent system until they manually adjust volume.

**Fix:** Record the pre-fade volume with `osascript -e 'output volume of (get volume settings)'` before starting, and restore it in `clearAllTimers()`:

```js
let preFadeVolume = null

function fadeAudioOver30s () {
  // Snapshot volume before fading
  execFile('osascript', ['-e', 'output volume of (get volume settings)'], {}, (err, stdout) => {
    if (!err) preFadeVolume = parseInt(stdout.trim(), 10)
  })
  const steps = 10
  const stepMs = 3000
  for (let i = 1; i <= steps; i++) {
    const targetVol = Math.max(0, 100 - i * 10)
    trackTimeout(() => {
      execFile('osascript', ['-e', `set volume output volume ${targetVol}`], () => {})
    }, i * stepMs)
  }
}

function clearAllTimers () {
  while (escalationTimers.length) {
    const ref = escalationTimers.pop()
    if (ref && ref._isInterval) clearInterval(ref)
    else clearTimeout(ref)
  }
  // Restore volume if a fade was in progress
  if (preFadeVolume !== null) {
    execFile('osascript', ['-e', `set volume output volume ${preFadeVolume}`], () => {})
    preFadeVolume = null
  }
  if (overlayWin && !overlayWin.isDestroyed()) {
    overlayWin.close()
    overlayWin = null
  }
}
```

---

### CR-02: Dwell-to-dismiss logic is inverted — dismisses on mouse stillness, not movement

**File:** `terminate.html:50-66`

**Issue:** The comment says "5s continuous mousemove dwell-to-dismiss" but the implementation does the opposite. `mousemove` resets `dwellTimer` on every movement event; the `setTimeout` only fires after 5 seconds of **no** mouse movement. The ring activates on first movement and stays active — so the user sees feedback suggesting they are making progress while moving, but the overlay only dismisses when they stop moving completely for 5 seconds. This contradicts the intended UX and makes the dismiss feel random.

**Fix:** To dismiss after 5 seconds of continuous movement, track elapsed movement time rather than resetting a timeout on each event:

```js
let dwellStart = null
let dwellTimer = null
const DWELL_MS = 5000

document.addEventListener('mousemove', () => {
  if (!dwellStart) {
    dwellStart = Date.now()
    document.getElementById('dwell-ring').classList.add('active')
    // Dismiss after DWELL_MS of sustained movement
    dwellTimer = setTimeout(() => {
      window.glorb.closeOverlay()
    }, DWELL_MS)
  }
  // If mouse stops and restarts, mouseleave resets dwellStart
})

document.addEventListener('mouseleave', () => {
  dwellStart = null
  clearTimeout(dwellTimer)
  dwellTimer = null
  document.getElementById('dwell-ring').classList.remove('active')
})
```

Alternatively, if "still for 5s" is the actual intended UX, update the comment to say "dismiss after 5s of mouse stillness" so it matches the code.

---

### CR-03: `resize-window` IPC handler dereferences `win` and `tray` without null guards

**File:** `main.js:513-519`

**Issue:** The `resize-window` handler directly calls `win.setSize(...)` and `tray.getBounds()`. Both `win` and `tray` can be null or destroyed if the handler is invoked from an overlay renderer during a window-close race or from a stale IPC call. This will throw an unhandled exception that crashes the main process event loop silently.

```js
ipcMain.handle('resize-window', (event, { width, height }) => {
  win.setSize(Math.round(width), Math.round(height))   // win could be null
  const bounds = tray.getBounds()                       // tray could be null
  ...
})
```

**Fix:**

```js
ipcMain.handle('resize-window', (event, { width, height }) => {
  if (!win || win.isDestroyed() || !tray) return
  win.setSize(Math.round(width), Math.round(height))
  const bounds = tray.getBounds()
  win.setPosition(
    Math.round(bounds.x + bounds.width / 2 - width / 2),
    Math.round(bounds.y + bounds.height)
  )
})
```

---

## Warnings

### WR-01: Already-spawned `afplay` child processes are not killed by `clearAllTimers`

**File:** `main.js:20-22`, `main.js:43-53`

**Issue:** `clearAllTimers()` cancels pending `setTimeout`/`setInterval` refs, preventing future `playSound` calls. However, `playSound` uses `execFile('afplay', ...)` which spawns a child process. Any `afplay` process that has already been launched continues playing audio even after `clearAllTimers()` returns. Calling `refocus-detected` during active chiming will clear future sounds but leave the current one playing.

**Fix:** Track spawned child processes and kill them in `clearAllTimers`:

```js
const activeAudioProcesses = []

function playSound (filePath) {
  const child = execFile('afplay', [filePath], { timeout: 10000 }, () => {
    const idx = activeAudioProcesses.indexOf(child)
    if (idx !== -1) activeAudioProcesses.splice(idx, 1)
  })
  activeAudioProcesses.push(child)
}

function clearAllTimers () {
  while (escalationTimers.length) {
    const ref = escalationTimers.pop()
    if (ref && ref._isInterval) clearInterval(ref)
    else clearTimeout(ref)
  }
  // Kill any in-flight audio
  while (activeAudioProcesses.length) {
    const child = activeAudioProcesses.pop()
    try { child.kill() } catch (_) {}
  }
  if (overlayWin && !overlayWin.isDestroyed()) {
    overlayWin.close()
    overlayWin = null
  }
}
```

---

### WR-02: `serialRevertTimer` in renderer uses bare `setTimeout` in the latch-release path — cannot be cleared

**File:** `renderer.html:430`, `renderer.html:436`

**Issue:** In the `visibilitychange` handler, the second `setTimeout(sendDefault, 2000)` at lines 430 and 436 is a bare `setTimeout`, not assigned to `serialRevertTimer`. If the window is hidden again within those 2 seconds, `clearSerialRevert()` clears `serialRevertTimer` (the outer one) but the inner bare `setTimeout` is not tracked and cannot be cancelled. This causes a stale `sendDefault` command to fire 2 seconds later even after the timer has been restarted or a new session begun.

**Fix:** Assign the inner `setTimeout` to `serialRevertTimer` as well:

```js
// Replace bare setTimeout(sendDefault, 2000) in both branches with:
serialRevertTimer = setTimeout(sendDefault, 2000)
```

---

### WR-03: `runWeakADHD` and `runStrongADHD` register overlapping timers when `pingCount === 5`

**File:** `main.js:133-148`, `main.js:254-276`

**Issue:** At `pingCount === 5`, the interval is self-cleared and a burst of `trackTimeout` calls are registered immediately inside the same interval callback. If `clearAllTimers()` is called at the exact moment the interval fires (before those inner `trackTimeout` IDs are pushed to `escalationTimers`), the IDs are added to the array after the array has already been drained. They will never be cleared in subsequent `clearAllTimers()` calls unless a new intervention fires.

This is a narrow timing window (synchronous JS), but it means `clearAllTimers()` called from a `refocus-detected` IPC that arrives milliseconds after the 5th ping fires may not clean up the chime burst or the `weakTerminate` timeout.

**Fix:** Perform the self-clear and splice before registering new `trackTimeout` calls, and consider checking `escalationTimers.length === 0` is not a valid "nothing running" assumption.

---

### WR-04: Socket server data handler drops commands if buffer contains multiple newlines

**File:** `main.js:446-465`

**Issue:** The `data` handler checks `if (buf.includes('\n'))` and uses `buf.trim()` as the command, then calls `socket.end()`. If two commands arrive in the same TCP segment (e.g. `drift\nrefocus\n`), only the trimmed full buffer is processed, which would be `drift\nrefocus` — matched against neither `'drift'` nor `'refocus'`, so `socket.write(`unknown command: ...`)` is returned and both are dropped. While `simulate.js` sends one command per connection, other callers could trigger this.

**Fix:** Parse line-by-line:

```js
socket.on('data', (chunk) => {
  buf += chunk.toString()
  const lines = buf.split('\n')
  buf = lines.pop()  // keep partial last line
  for (const line of lines) {
    const cmd = line.trim()
    if (!cmd) continue
    if (cmd === 'drift') {
      driftCount++
      runPath('weak-regular')
      socket.write('ok\n')
    } else if (cmd === 'refocus') {
      if (driftCount > 0) {
        new Notification({ title: 'Glorb', body: 'Focus regained.' }).show()
      }
      driftCount = 0
      clearAllTimers()
      socket.write('ok\n')
    } else {
      socket.write(`unknown command: ${cmd}\n`)
    }
  }
  socket.end()
})
```

---

## Info

### IN-01: `flash.html` and `vignette.html` have no Content-Security-Policy

**File:** `flash.html:1-27`, `vignette.html:1-40`

**Issue:** `renderer.html` includes a CSP meta tag (`default-src 'self'; script-src 'self' 'unsafe-inline'`). The two overlay HTML files loaded in `BrowserWindow` contexts have no CSP at all. While neither file runs scripts, adding CSP is a defence-in-depth measure consistent with project conventions.

**Fix:** Add to both files inside `<head>`:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'">
```

---

### IN-02: `updateFocusMessage()` called twice on startup causing redundant IPC round-trips

**File:** `renderer.html:514-518`

**Issue:** At startup, `storeGet('userName', 'Ouen').then(...)` calls `updateFocusMessage()` at line 517, and then `updateFocusMessage()` is called unconditionally again at line 518 before the Promise resolves. This fires two sets of `storeGet` IPC calls for `focusTime` and `userName` before the first has resolved.

**Fix:** Remove the redundant standalone call at line 518; the call inside the `.then()` at line 517 is sufficient.

---

### IN-03: Hardcoded default name "Ouen" appears in multiple places

**File:** `renderer.html:115`, `renderer.html:459`, `renderer.html:514`

**Issue:** The string `'Ouen'` is used as the default user name in three locations. This is a developer's personal name embedded as a default in shipped code — it should be a generic placeholder.

**Fix:** Replace `'Ouen'` with `'You'` or `'Friend'` as the default fallback in `storeGet` calls and the HTML span content.

---

### IN-04: `drift-detected` IPC and socket `drift` command both hardcode `runPath('weak-regular')`

**File:** `main.js:452`, `main.js:572`

**Issue:** Both the CLI socket and the IPC handler unconditionally use `weak-regular` regardless of the user's saved `strength` setting or profile. The comments note "Phase 9 will replace with dynamic routing" — this is an intentional stub, but the `strength` store value set in `renderer.html` is never read by the intervention engine at any point in this phase.

**Fix (Phase 9 prep):** Read the `strength` store key when selecting the path:

```js
async function selectPath () {
  const strength = await store.get('strength', 'auto')
  // profile/ADHD detection TBD in Phase 9
  if (strength === 'strong') return 'strong-regular'
  return 'weak-regular'
}
```

---

_Reviewed: 2026-04-18_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
