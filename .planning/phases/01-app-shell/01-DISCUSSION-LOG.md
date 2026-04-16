# Phase 1: App Shell - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-16
**Phase:** 01-app-shell
**Areas discussed:** Window Dismiss Behavior, Quit Mechanism, Window Position

---

## Window Dismiss Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Blur to hide | Window auto-hides when clicking outside — native macOS feel | ✓ |
| Tray click only | Window stays until tray icon clicked again | |
| Both + Escape key | Blur hides AND Escape key hides | |

**User's choice:** Blur to hide
**Notes:** Standard macOS menu bar app pattern.

---

## Quit Mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Right-click tray → Quit | Standard right-click context menu | |
| No explicit quit | Kill via Activity Monitor only | |
| Right-click → Quit + About | Context menu with About and Quit | |
| Custom (user described) | Minimal × top-left + in-window confirm overlay | ✓ |

**User's choice:** Minimal × button in the top-left of the window (frameless — no native title bar). Clicking × shows an in-window overlay asking for confirmation; the overlay must communicate this quits (not hides). Cmd+Q also quits directly. No right-click tray menu.

---

## Window Position

| Option | Description | Selected |
|--------|-------------|----------|
| Below the tray icon, anchored | Standard macOS menu bar app behavior | ✓ |
| Top-right corner, fixed offset | Fixed position regardless of tray icon location | |
| Center of screen | Appears in middle of display | |

**User's choice:** Anchored below the tray icon.
**Notes:** Matches macOS conventions (Fantastical, Dato, etc.).

---

## Claude's Discretion

- Tray icon implementation (size, template vs regular PNG)
- × button exact styling (hover state, size, colors)
- In-window quit overlay layout and wording
- Window appear/hide animation (if any)
