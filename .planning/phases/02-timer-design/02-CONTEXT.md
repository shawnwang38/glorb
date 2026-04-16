# Phase 2: Timer + Design - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the Pomodoro timer UI inside the #app container created in Phase 1. Deliver: SVG ring countdown timer with glorb.png mascot at center, time display below ring, Start/Pause button, and full design system implementation (#f0f0f0, orange accents, Inter font). The hamburger button for Phase 3's settings panel is placed but not wired.

</domain>

<decisions>
## Implementation Decisions

### Ring Timer Layout
- Ring outer diameter: 200px (70% of 286px window width)
- Ring stroke width: 8px
- Background track color: rgba(26, 26, 26, 0.1) — subtle ghost ring
- Countdown direction: clockwise depletion from 12 o'clock (stroke-dashoffset decreases as time passes)

### glorb.png Handling
- Missing image: orange circle placeholder with subtle "G" text — renders fully, swap in glorb.png when ready
- Image clip shape: circular (border-radius: 50%)
- Vignette technique: CSS radial-gradient from transparent center to #f0f0f0 edges
- Image size: 65% of ring interior diameter

### Timer Controls
- Start/Pause button: filled #FF6B35 (orange) — primary action, consistent with quit overlay "Quit Glorb" button
- Button width: full-width with 24px side padding
- Time display placement: below ring, above button (top-to-bottom: ring → time → start)
- Ring idle state: full orange ring at 100% — indicates "ready, full session available"

### Settings Panel (Phase 3 Dependency)
- Expanded window width when settings open: 572px (2× base 286px)
- Hamburger button: top-right corner at 8px margin, mirrors × close button on top-left
- Settings panel: slides in from right; window grows rightward, timer stays in left column

### Claude's Discretion
- SVG ring implementation details (viewBox, stroke-linecap, dasharray calculation)
- CSS animation timing function for smooth stroke-dashoffset transitions
- Timer tick interval (1s setInterval is standard)
- Exact vertical spacing/padding distribution within the 468px height
- Hamburger icon implementation (3 lines via CSS or SVG)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- renderer.html: #app container (empty, ready for Phase 2 injection)
- renderer.css: full design system — #f0f0f0, #FF6B35, Inter font stack, button styles, #1a1a1a text
- preload.js: window.glorb.quit() IPC bridge (no new IPC needed for timer)
- main.js: BrowserWindow 286×468px, always-on-top, blur-to-hide

### Established Patterns
- CSS class toggle (.visible) for show/hide — JS adds/removes class, CSS owns display logic
- Inline script in renderer with CSP permitting 'unsafe-inline'
- All styles in renderer.css (no inline style attributes)
- IDs for interactive elements (btn-close, btn-quit, btn-keep — use same convention: btn-start, btn-hamburger)

### Integration Points
- Phase 2 injects all timer HTML into #app (renderer.html)
- Phase 2 adds timer styles to renderer.css
- Phase 3 will read the hamburger button by ID and animate the window width

</code_context>

<specifics>
## Specific Ideas

- Window size is 286×468px (user-adjusted from original 220×360px — 30% larger)
- Settings expansion: 286→572px (proportional doubling, user confirmed)
- Time format: "XXh XXm" per REQUIREMENTS.md TIMER-03 (not "MM:SS")
- glorb.png will be placed at assets/glorb.png when provided by user

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
