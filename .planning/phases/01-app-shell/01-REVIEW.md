---
phase: 01-app-shell
reviewed: 2026-04-16T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - package.json
  - main.js
  - preload.js
  - renderer.css
  - renderer.html
findings:
  critical: 1
  warning: 4
  info: 1
  total: 6
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-04-16
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Reviewed the Phase 1 app shell: Electron main process, preload bridge, renderer HTML/CSS, and package manifest. The architecture is sound — contextIsolation is on, nodeIntegration is off, and the preload bridge is minimal. Most issues are in `main.js` (two correctness bugs, one security/UX concern) and `renderer.html` (one security weakness, one viewport misconfiguration). The `preload.js` and `renderer.css` are clean.

---

## Critical Issues

### CR-01: `'unsafe-inline'` in `script-src` CSP due to inline script block

**File:** `renderer.html:5`
**Issue:** The Content-Security-Policy includes `'unsafe-inline'` in `script-src` because the event-handling logic lives in an inline `<script>` block (lines 28–51). This defeats XSS protection from the CSP. While the attack surface in a local Electron app is smaller than a web app, Electron's renderer process has access to IPC and can call `window.glorb.quit()` — any injected script gains that capability too.
**Fix:** Move the inline script to an external file (e.g., `renderer.js`) and update the CSP to remove `'unsafe-inline'` from `script-src`:

```html
<!-- renderer.html -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'">
<!-- ... -->
<script src="renderer.js"></script>
```

```js
// renderer.js (new file — extract lines 29-49 from renderer.html verbatim)
const btnClose = document.getElementById('btn-close')
const btnQuit  = document.getElementById('btn-quit')
const btnKeep  = document.getElementById('btn-keep')
const overlay  = document.getElementById('quit-overlay')

function showOverlay() {
  overlay.classList.add('visible')
  btnQuit.focus()
}

function hideOverlay() {
  overlay.classList.remove('visible')
}

btnClose.addEventListener('click', showOverlay)
btnQuit.addEventListener('click', () => { window.glorb.quit() })
btnKeep.addEventListener('click', hideOverlay)
```

---

## Warnings

### WR-01: `app.dock.hide()` called before `app.whenReady()`

**File:** `main.js:53`
**Issue:** `app.dock.hide()` and `app.setActivationPolicy('accessory')` are called at module load time, before the `app` is ready. On some Electron versions (and per Electron docs), `app.dock` APIs must be called after the app is ready. This can throw or silently no-op, causing the dock icon to remain visible.
**Fix:** Move both calls inside the `whenReady` callback:

```js
app.whenReady().then(() => {
  app.dock.hide()
  app.setActivationPolicy('accessory')
  createWindow()
  createTray()
  globalShortcut.register('Command+Q', () => { app.quit() })
})
```

### WR-02: `window-all-closed` handler calls `e.preventDefault()` which does nothing

**File:** `main.js:65-67`
**Issue:** `window-all-closed` does not receive a cancelable event — `e.preventDefault()` is silently a no-op. The intent appears to be preventing the app from quitting when all windows are closed (correct for a menu bar app), but the actual mechanism here does nothing. The app stays alive only because no `app.quit()` is explicitly called, not because of `preventDefault`. The misleading code could confuse future maintainers into thinking this is the guard.
**Fix:** Remove the misleading handler, or replace it with a clear comment explaining the behavior:

```js
// Menu bar apps must not quit when the window is hidden.
// Electron's default behavior on macOS is to NOT quit on window-all-closed,
// so no handler is needed here. Explicitly remove or clarify:
app.on('window-all-closed', () => {
  // intentionally do nothing — app lives in the menu bar
})
```

### WR-03: Missing null guard on `win` inside tray click handler

**File:** `main.js:39`
**Issue:** The tray `click` handler references `win` directly. If `createWindow()` were to fail (e.g., missing `renderer.html`), `win` would remain `null` and `win.isVisible()` would throw an uncaught exception in the tray click callback, crashing the renderer process with no user-visible feedback.
**Fix:** Add a null guard:

```js
tray.on('click', () => {
  if (!win) return
  if (win.isVisible()) {
    win.hide()
  } else {
    const bounds = tray.getBounds()
    win.setPosition(
      Math.round(bounds.x + bounds.width / 2 - 143),
      Math.round(bounds.y + bounds.height)
    )
    win.show()
    win.focus()
  }
})
```

### WR-04: Viewport width mismatch — `220` vs actual window width `286`

**File:** `renderer.html:6`
**Issue:** The viewport meta tag sets `width=220`, but the `BrowserWindow` is `286px` wide and the CSS declares `html, body { width: 286px }`. The browser will size the viewport to 220px and then scale content to fill 286px, causing blurry or incorrectly laid-out rendering — especially visible on Retina displays.
**Fix:**

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

---

## Info

### IN-01: Global `Command+Q` shortcut overrides system-wide quit behavior

**File:** `main.js:60-62`
**Issue:** `globalShortcut.register('Command+Q', ...)` intercepts Cmd+Q system-wide, meaning the shortcut will be consumed by Glorb even when other apps are focused. This violates macOS conventions and will confuse users trying to quit other apps. Global shortcuts in Electron are captured regardless of focus.
**Fix:** Either remove the global shortcut entirely (the quit flow is already handled via the UI overlay), or scope it to a local accelerator on a context menu attached to the tray, or at minimum unregister it when the window is hidden:

```js
win.on('show', () => globalShortcut.register('Command+Q', () => app.quit()))
win.on('hide', () => globalShortcut.unregister('Command+Q'))
```

---

_Reviewed: 2026-04-16_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
