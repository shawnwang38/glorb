# Glorb

## What This Is

Glorb is a macOS menu bar Pomodoro timer app. It lives in the system menu bar and surfaces a small portrait window with a ring countdown timer, displaying a custom mascot (glorb.png) at its center. The aesthetic is minimalist — black, white, and orange — with Apple-native product sensibility.

## Core Value

The timer counts down reliably and the app stays out of the way until needed.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] App lives in macOS menu bar (no Dock icon)
- [ ] Small portrait window with ring timer showing glorb.png at center
- [ ] Ring timer counts down 25 minutes with animated progress
- [ ] Time display shows "00h 00m" format below ring
- [ ] Start/Pause button below time display
- [ ] Hamburger menu (top right) expands window to reveal settings panel
- [ ] Settings panel: focus summary ("Hi Name, you've focused for xxh xxm with Glorb.")
- [ ] Settings panel: Strength selector (Auto/Weak/Strong) — UI only
- [ ] Settings panel: "Retake Test" button — UI only
- [ ] Minimalist B&W design with orange highlights, modern sans serif font

### Out of Scope

- Break timer — not in v1 (focus on work session only)
- Sound/notifications — not in v1
- Data persistence across app restarts — not in v1
- Cross-platform (Windows/Linux) — macOS only

## Context

- Built with Electron for rapid UI development matching exact design spec
- glorb.png will be provided by user; assets/ slot reserved
- Ring timer uses SVG stroke-dashoffset animation for smooth countdown
- Window expands horizontally (220px → 440px) when settings panel opens
- #f0f0f0 background with radial gradient vignette around glorb.png inside ring

## Constraints

- **Platform**: macOS only — menu bar Tray API is the primary entry point
- **Stack**: Electron + vanilla HTML/CSS/JS — no build framework required for v1
- **Design**: #f0f0f0 background, orange (#FF6B35 or similar) for accents, Inter/SF Pro-style sans serif
- **Window**: Frameless window, always-on-top, positioned near menu bar icon

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Electron over Tauri/SwiftUI | Fastest path to match exact UI spec; user can swap later | — Pending |
| Vanilla JS (no React/Vue) | Simple enough; avoids build toolchain overhead | — Pending |
| SVG ring timer | Smooth animation, full CSS control, no canvas needed | — Pending |
| Horizontal window expansion | Settings panel feels native/spatial without a modal | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-16 after initialization*
