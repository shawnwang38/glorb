# Phase 3: Settings Panel - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire the existing `#btn-hamburger` stub to expand the window from 286×468px to 440×468px and slide in a settings panel from the right. The panel shows static placeholder content and collapses back to 286×468px when toggled. No data persistence — all v2.

</domain>

<decisions>
## Implementation Decisions

### Window Dimensions
- Expanded state: 440×468px (width increases by 154px, height unchanged)
- Collapsed state: 286×468px (current timer window — unchanged)
- Resize via Electron `win.setSize()` called through IPC from renderer

### Content
- Static placeholder text: "Hi there, you've focused for 0h 0m with Glorb."
- Strength selector: three buttons or radio-style — Auto / Weak / Strong (UI only, no behavior)
- "Retake Test" button (UI only, no behavior)

### Animation
- CSS transition on `#app` width (or panel transform): smooth slide-in from right
- Timer view stays at 286px width — settings panel occupies the extra 154px
- Hamburger click toggles open/closed state; both open and close use same CSS transition
- Panel hidden off-screen when collapsed (translateX(100%) or overflow: hidden)

### IPC
- New IPC channel: `resize-window` with payload `{ width, height }`
- Renderer sends resize request; main.js calls `win.setSize(width, height)` and re-centers near tray
- Existing IPC channel `quit-app` unchanged

### Claude's Discretion
- Exact panel layout within the 154px panel column (padding, spacing, font sizes)
- Strength selector visual treatment (button group vs radio)
- Whether collapse uses hamburger re-click or separate × in panel header (ROADMAP SC#5 says "same hamburger or a close control" — pick whichever looks cleaner)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `#btn-hamburger` already in DOM at top-right (28×28px), wired as no-op — just add click handler
- `renderer.css`: `#btn-start` button style reusable for "Retake Test" button
- IPC bridge: `preload.js` exposes `window.glorb.quit()` — extend to add `window.glorb.resize(w, h)`
- `main.js`: `ipcMain.handle('quit-app', ...)` pattern — add `ipcMain.handle('resize-window', ...)`

### Established Patterns
- Vanilla JS event listeners in `<script>` block at bottom of renderer.html
- CSS in renderer.css (no inline styles except error fallback on glorb-img)
- Colors: `#f0f0f0` bg, `#1a1a1a` for all accents/text, `rgba(0,0,0,0.15)` for subtle borders
- Button style: `#btn-start` and `#btn-quit` patterns

### Integration Points
- `renderer.html`: add `#settings-panel` div inside `#app`, alongside `#timer-view`
- `renderer.css`: add panel styles, slide animation, expanded/collapsed states
- `preload.js`: expose `window.glorb.resize(w, h)` via contextBridge
- `main.js`: handle `resize-window` IPC, call `win.setSize()` + reposition

</code_context>

<specifics>
## Specific Ideas

- Window expands to 440×468px (not 440×360px per ROADMAP — height stays at 468px)
- Static "Hi there, you've focused for 0h 0m with Glorb." — no runtime data
- CSS transition on width for smooth slide-in

</specifics>

<deferred>
## Deferred Ideas

- Dynamic username: wait for v2 profile feature
- Actual session time tracking that persists: v2
- Strength selector wired to behavior: v2 (FUNC-06)
- Retake Test flow: v2 (FUNC-07)

</deferred>
