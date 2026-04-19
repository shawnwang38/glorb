# Phase 8: Intervention Engine - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 8 delivers the driftDetected() / refocusDetected() API with all four escalation paths (Weak×Regular, Weak×ADHD, Strong×Regular, Strong×ADHD), and a CLI tool (`node simulate.js`) that sends drift/refocus signals to the running Electron app for testing. Strength and hasADHD routing are NOT wired in this phase — that is Phase 9.

</domain>

<decisions>
## Implementation Decisions

### Audio
- **D-01:** Use macOS system sounds for all chimes and notes — no bundled audio files. Play via `NSSound` through a shell command (e.g. `afplay /System/Library/Sounds/Glass.aiff`) or Electron's `shell.openPath`. One chime = one `afplay` invocation; increasing notes = sequential `afplay` calls with different system sounds.
- **D-02:** "Constant chiming for 10s" (Weak×ADHD terminate) = rapid repeated `afplay` in a loop for the duration.
- **D-03:** "Audio fades over 30s" (Strong paths) = adjust system volume via `osascript` (`set volume output volume N`) or use `afplay` with a decrementing amplitude. Claude's discretion on exact mechanism.

### Strong Path Visuals (Full-screen overlay)
- **D-04:** Full-screen flash and terminate screen use a **new always-on-top BrowserWindow** — separate from the 286×468 tray popup. The overlay window covers the full screen (use `screen.getPrimaryDisplay().workAreaSize` for dimensions), frame: false, transparent background where needed.
- **D-05:** "2s full-screen Glorb flash" (Strong×Regular) = overlay window loads a minimal HTML page showing glorb.png + "Still there?" text, auto-closes after 2s.
- **D-06:** "5s full-screen Glorb flash" (Strong×ADHD) = same pattern, 5s duration.
- **D-07:** Vignette effect (both Strong paths, 60s) = overlay window with a CSS radial-gradient vignette that dims/brightens from edges. In dark mode: brightens edges (white vignette). In light mode: dims edges (black vignette). Overlay window stays on screen until refocusDetected() or escalation terminates.
- **D-08:** Terminate screen (both Strong paths) = full-screen overlay with full black (dark mode) or full white (light mode) background, large glorb.png centered, "Focus." text. Dismissed after user looks at screen for 5s — implement as a 5s hover/mousemove dwell timer (mouse must stay over window for 5 continuous seconds to dismiss, as a proxy for "looking at screen").

### Escalation State Location
- **D-09:** All drift counter, escalation step tracking, and active timer references live in **main process** (`main.js`). Renderer has zero escalation state.
- **D-10:** `driftDetected()` and `refocusDetected()` are IPC handlers (`ipcMain.handle`) called from renderer or CLI tool. Main process owns the state machine.
- **D-11:** Escalation timers are `setTimeout`/`setInterval` references stored in main process variables so `refocusDetected()` can cancel them with `clearTimeout`/`clearInterval`.

### CLI IPC Mechanism
- **D-12:** Claude's discretion — use a **named pipe (Unix domain socket)** in main process. Main creates a server on a known path (e.g. `/tmp/glorb-ipc.sock`) when app starts. `simulate.js` connects, sends `"drift"` or `"refocus"` string, disconnects. This is lightweight, requires no HTTP server, and is dev-only.

### Escalation Path Specs (locked from REQUIREMENTS.md)
- **D-13:** Weak×Regular: 30s → push "Stay focused!" + 1 chime; every 10s → 2 chimes; then 3 chimes + "last reminder" push; terminate → open glorb window, end timer, in-window popup "Ready to continue focusing?"
- **D-14:** Weak×ADHD: 10s → push + 1 note; every 5s, up to 5 pings, increasing notes (1→5); then 10s constant chime; terminate → open glorb window, end timer, in-window popup "You lost focus."
- **D-15:** Strong×Regular: 15s → push + 1 chime; every 10s → 2 chimes, 3 chimes + "last reminder"; then 2s full-screen Glorb flash "Still there?"; audio fade 30s; vignette 60s; terminate screen.
- **D-16:** Strong×ADHD: 10s → push; every 5s up to 5 pings with increasing notes; 5s full-screen Glorb flash "Still there?"; audio fade 30s; vignette 60s; same terminate screen as Strong×Regular.

### Claude's Discretion
- Exact macOS system sound file paths for 1-chime, 2-chime, 3-chime, and increasing-notes sequences
- Volume fade implementation mechanism (osascript vs afplay amplitude flag)
- Named pipe path and protocol details
- Error handling if `simulate.js` is run when app is not open

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Intervention Spec
- `intervention-ui.md` — Original intervention design spec; authoritative for path behavior, timing, and UX copy ("Stay focused!", "Still there?", "Focus.", etc.)
- `.planning/REQUIREMENTS.md` §INTERV-01 through INTERV-06, CLI-01, CLI-02 — Acceptance criteria for all paths and CLI tool

### Existing Infrastructure
- `main.js` — IPC handler patterns (`ipcMain.handle`), Notification API, BrowserWindow creation, store usage
- `preload.js` — contextBridge pattern for exposing IPC to renderer
- `.planning/phases/07-onboarding-flow/07-CONTEXT.md` — BrowserWindow creation pattern (createOnboardingWindow) to follow for overlay windows

### Phase 9 Dependency Note
- `.planning/ROADMAP.md` §Phase 9 — Wiring strength/hasADHD to path selection is Phase 9. Phase 8 only needs the 4 paths callable directly (hardcoded or passable as params) — don't over-architect routing in Phase 8.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ipcMain.handle('notify', ...)` (main.js:208) — push notification, reuse for all push events
- `createOnboardingWindow()` pattern — reference for creating new BrowserWindows from main process
- `glorb.png`, `glorb_dark.png`, `glorb_light.png` — available for overlay screens
- `electron-store` via IPC — `store-get` for reading `theme` (dark/light) to adapt vignette direction

### Established Patterns
- All timer/interval state should follow the serial reconnect pattern (`reconnectTimer` in main.js) — store ref, check before clearing
- BrowserWindow creation: `show: true`, `frame: false`, `alwaysOnTop: true`, `skipTaskbar: true` for overlay windows

### Integration Points
- Renderer calls `window.glorb.driftDetected()` / `window.glorb.refocusDetected()` via preload contextBridge → `ipcMain.handle` in main process
- CLI `simulate.js` connects to Unix socket → triggers same main-process functions as IPC handlers
- Terminate action "open glorb window" = call `win.show()` and `tray.popUpContextMenu()` or equivalent

</code_context>

<specifics>
## Specific Ideas

- macOS system sounds only — no bundled audio files shipped with the app
- Full-screen overlay is a separate BrowserWindow (not the 286px tray popup), covers whole screen
- 5s "look at screen" dismiss = mousemove/hover dwell timer as proxy for eye contact
- CLI tool is dev-only and temporary — keep it simple (Unix socket, no auth, no protocol overhead)

</specifics>

<deferred>
## Deferred Ideas

- Strength + hasADHD routing (wiring driftDetected to correct path based on store) → Phase 9
- Eye-tracking or app-tracking to auto-call driftDetected() → post-v1.2 (DETECT-01, DETECT-02)
- Auto intervention strength setting → deferred (only Weak/Strong wired for now)

</deferred>

---

*Phase: 08-intervention-engine*
*Context gathered: 2026-04-18*
