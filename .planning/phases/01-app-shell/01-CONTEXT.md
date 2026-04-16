# Phase 1: App Shell - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up the Electron app skeleton: main process, Tray icon in the macOS menu bar, and a frameless window (~220×360px, #f0f0f0 background) that shows when the tray icon is clicked and hides on blur or tray click. No timer UI, no design system — just the container that everything else will live in.

</domain>

<decisions>
## Implementation Decisions

### Window Dismiss Behavior
- **D-01:** Window hides when the user clicks anywhere outside it (blur event) — same behavior as Spotlight, Fantastical, and native macOS menu bar apps.
- **D-02:** Clicking the tray icon also toggles the window (show if hidden, hide if visible).

### Quit Mechanism
- **D-03:** The window is frameless with no native title bar. A minimal × button sits in the top-left corner of the window, always visible.
- **D-04:** Clicking × does NOT immediately quit — it shows an in-window overlay asking the user to confirm. The overlay must communicate that this quits the app, not just hides the window.
- **D-05:** Cmd+Q also quits the app directly (no confirmation needed — standard macOS shortcut behavior).
- **D-06:** No right-click tray context menu. The only quit paths are × button (with confirmation overlay) and Cmd+Q.

### Window Position
- **D-07:** Window appears directly below the tray icon, anchored to its horizontal position — standard macOS menu bar app behavior (not fixed top-right or centered).

### Tray Icon
- **D-08:** (Not discussed — Claude's discretion.) Use glorb.png scaled to 16×16 or 18×18 as a template image. If it doesn't render cleanly at that size, fall back to a simple text/emoji placeholder for Phase 1 (can be refined later).

### Claude's Discretion
- Tray icon exact size and whether to use a template image or regular PNG
- Exact styling of the × quit button (size, color, hover state) — must fit the #f0f0f0 / black / orange palette
- Exact wording and layout of the in-window quit confirmation overlay
- Window animation (fade in vs. instant appear) — keep it simple for Phase 1

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — SHELL-01 through SHELL-04 define the acceptance criteria for this phase
- `.planning/PROJECT.md` — Stack constraints (Electron + vanilla HTML/CSS/JS), design tokens (#f0f0f0, #FF6B35), window constraints (frameless, always-on-top)

No external specs or ADRs — all requirements are captured above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `glorb.png` — Available at project root. Use as the tray icon (scaled) and will be used in Phase 2 for the ring timer center.

### Established Patterns
- None yet — this is the first phase. Patterns established here will carry forward.

### Integration Points
- Phase 2 will add its UI into the window created here. Keep the renderer HTML minimal — a container div the timer UI can populate.
- Phase 3 settings panel will expand the window width; window sizing logic established here should be easy to mutate later.

</code_context>

<specifics>
## Specific Ideas

- The quit flow is important UX: × button → in-window overlay that explicitly says this will quit (not hide). This distinction matters because hiding is the default dismiss behavior.
- "Frameless window" means no native macOS title bar — all chrome must be custom HTML/CSS.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-app-shell*
*Context gathered: 2026-04-16*
