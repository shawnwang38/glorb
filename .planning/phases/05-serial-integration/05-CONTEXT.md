# Phase 5: Serial Integration - Context

**Gathered:** 2026-04-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Add serial command parsing to the Arduino firmware, and wire the Electron app to auto-detect the Arduino serial port and maintain a live connection. Phase 5 also updates the display graphics (visual refinements to OPEN_EYES and SMILE) discovered during discussion.

Phase 5 delivers: firmware responds to "DEFAULT\n"/"SMILE\n" over USB serial; Electron finds and holds the port; a status dot in the settings panel reflects connection state.

Phase 6 handles: timer event wiring (BEH-01, BEH-02, BEH-03).

</domain>

<decisions>
## Implementation Decisions

### Firmware — Command Parser

- **D-01:** Use blocking `Serial.readStringUntil('\n')` in `loop()`. The loop does nothing else, so blocking is fine.
- **D-02:** Replace the cycling demo loop entirely. `setup()` calls `showDisplay(DisplayState::SMILE)` (closed eyes on power-up), then `loop()` just listens for commands. No demo cycling — static display = no jitter.
- **D-03:** Commands: `"DEFAULT\n"` → `showDisplay(OPEN_EYES)`, `"SMILE\n"` → `showDisplay(SMILE)`. Exact string match after trimming newline.
- **D-04:** Serial baud remains 115200 (already in setup()).

### Firmware — Display Graphics (visual update from Phase 4)

- **D-05:** **OPEN_EYES**: Change from `drawFilledEllipse` (solid) to `drawEllipse` (outline only). The center should be dark — hollow ring shape, not a filled oval. Same dimensions and position as Phase 4.
- **D-06:** **SMILE**: Replace the `^` character with the upper portion (~top 30%) of an ellipse outline, using `drawEllipse` with `U8G2_DRAW_UPPER_LEFT | U8G2_DRAW_UPPER_RIGHT`. Arc dimensions should roughly match the OPEN_EYES ellipse width. Exact radius and center position: Claude's discretion tuned for visual centering on 64×128 portrait canvas.
- **D-07:** Reference `glorb_icon.png` for the intended eye aesthetic (hollow ring eyes, curved-arc smile).
- **D-08:** Power-up default state: SMILE (closed eyes, `^ ^` arc shape), not OPEN_EYES.

### Electron — Serial Library

- **D-09:** Use the `serialport` npm package (standard Node.js serial library). It requires a native rebuild for Electron — add `electron-rebuild` as a dev dependency and run it after install. This is the only native dep in the project.
- **D-10:** Serial logic lives in `main.js` (main process only). Renderer never touches the port directly.

### Electron — Arduino Port Auto-Detection

- **D-11:** Scan available ports and filter by Arduino-known VID/PIDs: `0x2341` (genuine Arduino), `0x1A86` (CH340 clone), `0x2A03` (Arduino.org). If no VID/PID match, fall back to description/manufacturer string containing "Arduino" or "CH340".
- **D-12:** If no matching port is found on startup, proceed silently — app works without hardware.

### Electron — Connection Lifecycle

- **D-13:** On startup, attempt auto-detection. If found, open port at 115200 baud. If not found, remain disconnected.
- **D-14:** Poll every 3 seconds for a re-plugged Arduino. If detected and port not open, connect automatically.
- **D-15:** On unexpected disconnect (port error/close event), start polling loop to reconnect when Arduino returns.
- **D-16:** No user-facing error dialogs — connection state is communicated via status dot only.

### Electron — UI Status Indicator

- **D-17:** A small status dot in the settings panel (the hamburger panel that already exists). Green = connected, red/grey = disconnected. Appears only when settings panel is open — unobtrusive.
- **D-18:** Renderer learns connection state via IPC. Add `ipcMain.handle('serial-status', ...)` and expose `glorb.serialStatus()` in preload.js. Settings panel queries on open and listens for updates.

### Claude's Discretion

- Exact pixel coordinates for SMILE arc (radius, center x/y — tune for portrait 64×128 canvas, reference glorb_icon.png)
- Exact dot styling (size, color values, position within settings panel layout)
- Whether to push connection-change events to renderer reactively vs poll on panel open
- platformio.ini: no changes needed

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Firmware
- `firmware/src/display.h` — DisplayState enum and public API (displaySetup, showDisplay)
- `firmware/src/display.cpp` — Current two-display implementation (U8g2 instances, draw functions to update)
- `firmware/src/main.cpp` — Arduino setup/loop — demo loop to replace with serial listener
- `firmware/platformio.ini` — Build config, lib deps, baud rate

### Electron
- `main.js` — IPC handlers and app lifecycle — serial logic added here
- `preload.js` — contextBridge API — add serialStatus() handle here
- `renderer.html` / `renderer.css` — Settings panel DOM — where status dot is added
- `package.json` — Current deps — serialport and electron-rebuild added here

### Reference Art
- `glorb_icon.png` — Reference for intended eye aesthetic (hollow ring eyes, arc smile)

### Requirements
- `.planning/REQUIREMENTS.md` §Serial — SER-01 through SER-04 (all Phase 5)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ipcMain.handle` pattern (main.js) — serial-status IPC follows same pattern as store-get, notify
- `contextBridge.exposeInMainWorld` (preload.js) — add `serialStatus` alongside existing 5 handles
- U8g2 draw API (display.cpp) — `drawEllipse` with quadrant flags replaces `drawFilledEllipse`
- `displaySetup()` / `showDisplay(DisplayState)` — API kept exactly; serial handler calls showDisplay directly

### Established Patterns
- Electron IPC: renderer invokes via `window.glorb.*`, main handles via `ipcMain.handle`
- No build toolchain — `npm install` + `electron-rebuild` is the only build step added
- Vanilla JS in renderer — status dot implemented with a `<span>` or `<div>` + inline CSS

### Integration Points
- `loop()` in main.cpp: replace `showDisplay` demo cycle with `Serial.readStringUntil` listener
- `app.whenReady()` in main.js: serial auto-detect starts here (alongside createWindow/createTray)
- Settings panel HTML: dot element added near connection section or at top of panel

</code_context>

<specifics>
## Specific Ideas

- Eyes reference: glorb_icon.png — hollow ring eyes (not filled ovals), curved closed-eye arc smile
- OPEN_EYES visual: outline ellipse (drawEllipse, not drawFilledEllipse) — dark center, lit ring
- SMILE visual: upper ~30% arc of an ellipse matching OPEN_EYES width — no character fonts
- Arduino VID/PIDs: 0x2341 (genuine), 0x1A86 (CH340 clone), 0x2A03 (Arduino.org)
- Baud: 115200 (already in Serial.begin — no change)
- Polling interval: 3 seconds

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-serial-integration*
*Context gathered: 2026-04-17*
