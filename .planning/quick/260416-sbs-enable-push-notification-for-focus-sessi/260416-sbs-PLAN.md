---
phase: quick
plan: 260416-sbs
type: execute
wave: 1
depends_on: []
files_modified:
  - main.js
  - preload.js
  - renderer.html
autonomous: true
requirements: []
must_haves:
  truths:
    - "When the focus session countdown reaches zero, a macOS system notification appears"
    - "Notification title is 'Glorb' and body is 'Focus session complete.'"
  artifacts:
    - path: "main.js"
      provides: "IPC handler 'notify' using Electron Notification API"
    - path: "preload.js"
      provides: "window.glorb.notify(title, body) bridge method"
    - path: "renderer.html"
      provides: "notify() call at remaining <= 0 branch in tick()"
  key_links:
    - from: "renderer.html tick()"
      to: "main.js notify handler"
      via: "window.glorb.notify IPC invoke"
      pattern: "window\\.glorb\\.notify"
---

<objective>
Fire a macOS system notification when a Glorb focus session completes.

Purpose: Give the user a reliable heads-up when the timer expires, even if the window is hidden.
Output: Notification with title "Glorb" and body "Focus session complete." triggered on countdown zero.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@renderer.html
@main.js
@preload.js
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add IPC notify handler in main.js and expose via preload.js</name>
  <files>main.js, preload.js</files>
  <action>
In main.js:
1. Add `Notification` to the existing destructured require at the top: `const { app, BrowserWindow, Tray, nativeImage, ipcMain, globalShortcut, Notification } = require('electron')`
2. At the bottom of the file (after the existing ipcMain.handle calls), add:

```js
ipcMain.handle('notify', (event, { title, body }) => {
  new Notification({ title, body }).show()
})
```

In preload.js:
Add `notify: (title, body) => ipcRenderer.invoke('notify', { title, body })` to the `contextBridge.exposeInMainWorld('glorb', { ... })` object, alongside the existing methods (quit, resize, storeGet, storeSet).
  </action>
  <verify>
    <automated>node -e "const src = require('fs').readFileSync('main.js','utf8'); if (!src.includes(\"ipcMain.handle('notify'\")) || !src.includes('Notification')) throw new Error('main.js missing notify handler'); const pre = require('fs').readFileSync('preload.js','utf8'); if (!pre.includes('notify')) throw new Error('preload.js missing notify'); console.log('OK')"</automated>
  </verify>
  <done>main.js exports a working 'notify' IPC handler using Electron Notification; preload.js exposes window.glorb.notify(title, body)</done>
</task>

<task type="auto">
  <name>Task 2: Call notify at session completion in renderer.html</name>
  <files>renderer.html</files>
  <action>
In renderer.html, inside the `tick()` function, at the `if (remaining <= 0) {` branch, insert a notification call immediately after `remaining = 0` and before `updateRing(0)`. The final branch should look like:

```js
if (remaining <= 0) {
  remaining = 0
  window.glorb.notify('Glorb', 'Focus session complete.')
  updateRing(0)
  timeDisplay.innerHTML = formatTime(0)
  addFocusTime(getTotalSeconds())
  resetTimer()
  return
}
```

Only add the single `window.glorb.notify(...)` line — do not change any other lines in tick().
  </action>
  <verify>
    <automated>node -e "const src = require('fs').readFileSync('renderer.html','utf8'); if (!src.includes(\"window.glorb.notify('Glorb', 'Focus session complete.')\")) throw new Error('notify call missing'); console.log('OK')"</automated>
  </verify>
  <done>renderer.html calls window.glorb.notify with the correct title and body when the timer reaches zero</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| renderer→main (IPC) | Notification title/body originates in renderer; crosses to main process |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-sbs-01 | Tampering | notify IPC handler | accept | Title and body are hardcoded string literals in renderer; no user input involved |
| T-sbs-02 | Denial of Service | Notification spam | accept | Notification fires only on countdown zero (once per session); no loop risk |
</threat_model>

<verification>
Run the app with `npm start` (or `npx electron .`), start a timer, and verify the macOS notification appears when countdown completes.
For a quick smoke-test: temporarily set `startMinutes = 1/60` (i.e., 1 second) in renderer.html to trigger it immediately.
</verification>

<success_criteria>
- When a focus session countdown reaches zero, macOS displays a notification with title "Glorb" and body "Focus session complete."
- No errors thrown in main process or renderer console
- Existing timer, settings, theme, and persistence behaviour unchanged
</success_criteria>

<output>
After completion, create `.planning/quick/260416-sbs-enable-push-notification-for-focus-sessi/260416-sbs-SUMMARY.md`
</output>
