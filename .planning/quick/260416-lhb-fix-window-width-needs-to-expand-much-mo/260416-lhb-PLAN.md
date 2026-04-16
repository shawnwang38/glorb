---
phase: quick
plan: 260416-lhb
type: execute
wave: 1
depends_on: []
files_modified:
  - renderer.html
  - renderer.css
autonomous: true
requirements: []

must_haves:
  truths:
    - "Settings panel text ('Hi there, you've focused...') and buttons are not clipped or cramped when open"
    - "Countdown display shows minutes and seconds (e.g. 24m 59s) instead of hours and minutes"
    - "Timer ring has a draggable handle to set starting duration from 1 to 60 minutes"
    - "Dragging the ring handle updates the pre-start time display and ring position"
    - "Settings panel focus message still shows total time in hours and minutes format"
  artifacts:
    - path: "renderer.html"
      provides: "Updated DOM with SVG drag handle, revised formatTime logic, wider openSettings call"
    - path: "renderer.css"
      provides: "Wider settings panel width, drag handle SVG styles"
  key_links:
    - from: "openSettings() in renderer.html"
      to: "window.glorb.resize()"
      via: "IPC resize-window"
      pattern: "glorb\\.resize\\(6"
    - from: "SVG drag handle element"
      to: "startMinutes variable"
      via: "pointermove angle calculation"
      pattern: "startMinutes"
---

<objective>
Three focused improvements to the Glorb timer window:
1. Wider expanded window so settings panel text and buttons have comfortable room
2. Countdown display in XXm XXs format (was XXh XXm); settings panel keeps XXh XXm for totals
3. SVG ring arc slider handle to set starting duration (1–60 min, default 25m)

Purpose: The settings panel text was clipping at 440px expanded width; countdown seconds are more useful feedback; the ring slider gives intuitive duration control without extra UI elements.
Output: Updated renderer.html and renderer.css delivering all three changes.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@renderer.html
@renderer.css
@main.js
</context>

<tasks>

<task type="auto">
  <name>Task 1: Wider settings panel + countdown format change</name>
  <files>renderer.css, renderer.html</files>
  <action>
**CSS changes in renderer.css:**

1. Increase `#settings-panel` width from `154px` to `314px`. This makes the total expanded window 286 + 314 = 600px.

2. No change to `#timer-view` width (stays 286px).

**JS changes in renderer.html:**

3. In `openSettings()`, change the resize call from `window.glorb.resize(440, 468)` to `window.glorb.resize(600, 468)`.

4. In `closeSettings()`, keep `window.glorb.resize(286, 468)` unchanged.

5. Replace the `formatTime(secs)` function used by the timer countdown with a new version that returns `XXm XXs` format:

```js
function formatTime(secs) {
  const m = Math.floor(secs / 60)
  const s = secs % 60
  const mStr = String(m).padStart(2, '0')
  const sStr = String(s).padStart(2, '0')
  return `<span class="time-nums">${mStr}</span>m <span class="time-nums">${sStr}</span>s`
}
```

6. Add a separate `formatFocusTime(secs)` function used ONLY for the focus summary message in the settings panel (keeps XXh XXm format for total accumulated session time display):

```js
function formatFocusTime(secs) {
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  return `${h}h ${m}m`
}
```

Note: The initial `#time-display` HTML in the DOM currently reads `<span class="time-nums">00</span>h <span class="time-nums">25</span>m` — this must be updated to show the correct initial state. After the JS changes, `resetTimer()` calls `timeDisplay.innerHTML = formatTime(TOTAL_SECONDS)` which will render correctly, so also update the static HTML initial value in the DOM to match: `<span class="time-nums">25</span>m <span class="time-nums">00</span>s`.
  </action>
  <verify>Open Glorb app. Timer should read "25m 00s" at rest. Click Start — after a few seconds the display should count down showing seconds (e.g. "24m 57s"). Click hamburger — settings panel should slide in with comfortable text layout at ~600px total width, no text clipping. Focus message should read "0h 0m" format.</verify>
  <done>Timer shows XXm XXs, settings panel text not clipped, focus summary still shows XXh XXm, expanded width is 600px.</done>
</task>

<task type="auto">
  <name>Task 2: Ring arc slider for starting duration</name>
  <files>renderer.html, renderer.css</files>
  <action>
Add a draggable SVG handle on the ring that lets the user set the starting duration (1–60 min) before the timer starts. The handle is only interactive when `timerState === 'idle'`.

**SVG changes in renderer.html — inside the existing `<svg width="200" height="200" viewBox="0 0 200 200">`:**

Add after the existing two `<circle>` elements (track and progress):

```html
<!-- Duration handle — draggable dot on ring, visible only when idle -->
<circle
  id="ring-handle"
  cx="100" cy="8"
  r="7"
  fill="#FF6B35"
  stroke="#f0f0f0"
  stroke-width="2"
  style="cursor: grab; touch-action: none;"
/>
```

The handle starts at the 12 o'clock position (cx=100, cy=8 which is center 100 - radius 92 = 8).

**JS changes in renderer.html:**

Add a `startMinutes` variable (default 25) that controls the starting duration. This replaces the hard-coded `TOTAL_SECONDS = 25 * 60`:

```js
let startMinutes = 25
// TOTAL_SECONDS becomes a derived value
function getTotalSeconds() { return startMinutes * 60 }
```

Update all references to `TOTAL_SECONDS` to call `getTotalSeconds()` instead:
- `let remaining = getTotalSeconds()`
- `updateRing(remaining)` in tick uses `getTotalSeconds()` for the denominator — update `updateRing` signature:
  ```js
  function updateRing(secs) {
    const offset = CIRCUMFERENCE * (1 - secs / getTotalSeconds())
    ringProgress.style.strokeDashoffset = offset
  }
  ```
- In `resetTimer()`: `remaining = getTotalSeconds()`, then call `updateRing(getTotalSeconds())` and `timeDisplay.innerHTML = formatTime(getTotalSeconds())`
- In `btnStart` click handler: no change needed since it reads `remaining`

**Handle drag logic — add after the Phase 3 settings panel toggle block:**

```js
// === Duration ring slider ===

const ringHandle = document.getElementById('ring-handle')
const SVG_CX = 100  // SVG center x
const SVG_CY = 100  // SVG center y
const RING_R = 92   // ring radius

let draggingHandle = false

function angleToMinutes(angleDeg) {
  // angleDeg: 0 = 12 o'clock, clockwise positive
  // clamp to 1–60 minutes
  const mins = Math.round((angleDeg / 360) * 60)
  return Math.min(60, Math.max(1, mins === 0 ? 60 : mins))
}

function minutesToAngle(mins) {
  return (mins / 60) * 360
}

function minutesToHandlePos(mins) {
  const angleDeg = minutesToAngle(mins)
  const angleRad = (angleDeg - 90) * (Math.PI / 180)
  return {
    cx: SVG_CX + RING_R * Math.cos(angleRad),
    cy: SVG_CY + RING_R * Math.sin(angleRad)
  }
}

function updateHandlePosition(mins) {
  const pos = minutesToHandlePos(mins)
  ringHandle.setAttribute('cx', pos.cx)
  ringHandle.setAttribute('cy', pos.cy)
}

function getSVGPoint(e, svgEl) {
  const rect = svgEl.getBoundingClientRect()
  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const clientY = e.touches ? e.touches[0].clientY : e.clientY
  // Scale from client coords to SVG viewBox coords
  const scaleX = 200 / rect.width
  const scaleY = 200 / rect.height
  return {
    x: (clientX - rect.left) * scaleX,
    y: (clientY - rect.top) * scaleY
  }
}

ringHandle.addEventListener('pointerdown', (e) => {
  if (timerState !== 'idle') return
  draggingHandle = true
  ringHandle.style.cursor = 'grabbing'
  e.preventDefault()
  e.target.setPointerCapture(e.pointerId)
})

ringHandle.addEventListener('pointermove', (e) => {
  if (!draggingHandle) return
  const svg = ringHandle.closest('svg')
  const pt = getSVGPoint(e, svg)
  const dx = pt.x - SVG_CX
  const dy = pt.y - SVG_CY
  // atan2 from -90deg offset so 0deg = 12 o'clock
  let angleDeg = Math.atan2(dy, dx) * (180 / Math.PI) + 90
  if (angleDeg < 0) angleDeg += 360
  const mins = angleToMinutes(angleDeg)
  startMinutes = mins
  updateHandlePosition(mins)
  // Update display without resetting timer state
  remaining = getTotalSeconds()
  updateRing(getTotalSeconds())
  timeDisplay.innerHTML = formatTime(getTotalSeconds())
  e.preventDefault()
})

ringHandle.addEventListener('pointerup', (e) => {
  draggingHandle = false
  ringHandle.style.cursor = 'grab'
})

// Hide handle while timer is running or paused; show when idle
function syncHandleVisibility() {
  ringHandle.style.display = timerState === 'idle' ? '' : 'none'
}
```

Call `syncHandleVisibility()` at the end of `resetTimer()`, inside the `btnStart` click handler after state changes, and once on init.

Also call `updateHandlePosition(startMinutes)` once on page load (after the handle element exists) so the handle starts at the correct 25-minute position (top of ring, 12 o'clock = 25/60 * 360 = 150deg from 12 o'clock).

**CSS changes in renderer.css:**

Add a rule so the handle cursor shows correctly and the ring SVG doesn't steal pointer events when dragging:

```css
/* Ring slider handle */
#ring-handle {
  cursor: grab;
}
#ring-handle:active {
  cursor: grabbing;
}
```
  </action>
  <verify>With timer idle: drag the orange dot on the ring clockwise — time display updates (e.g. "30m 00s"), ring fills to the new position. Click Start — timer counts down from the set duration. After timer completes or is reset, handle reappears. Handle is not visible or interactive while timer is running.</verify>
  <done>Ring handle draggable when idle, updates startMinutes and display correctly, hidden while running/paused, timer starts from dragged duration.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| renderer (untrusted) → main via IPC | resize-window receives width/height integers; main.js already applies Math.round() |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-lhb-01 | Tampering | ring slider angle math | accept | Purely client-side cosmetic; clamped to 1–60 minutes; no external data |
| T-lhb-02 | DoS | resize IPC call | accept | Only triggered by user gesture; already rate-limited by Electron's IPC handler |
</threat_model>

<verification>
1. Run `npm start` (or `electron .`) and open the Glorb window
2. Timer display reads "25m 00s" at idle
3. Click hamburger — panel slides in, "Hi there, you've focused for 0h 0m" text fully visible, no overflow
4. Total expanded width is approximately 600px (check via Electron DevTools window.outerWidth if needed)
5. Close settings, drag the orange ring handle to a new position — display updates to new duration
6. Click Start — timer counts down in XXm XXs, seconds decrement each second
7. Handle disappears while running, reappears after reset
</verification>

<success_criteria>
- Settings panel fits all text without wrapping or clipping at 600px expanded width
- Timer countdown shows minutes and seconds (not hours and minutes)
- Settings focus message still shows hours and minutes
- Ring handle drag updates starting duration (1–60 min) visually and functionally
- Timer correctly counts down from whatever duration was set via the handle
</success_criteria>

<output>
After completion, create `.planning/quick/260416-lhb-fix-window-width-needs-to-expand-much-mo/260416-lhb-SUMMARY.md`
</output>
