# Glorb

## What This Is

Glorb is a macOS menu bar Pomodoro timer app. It lives in the system menu bar and surfaces a small portrait window with a ring countdown timer, displaying a custom mascot (glorb.png) at its center. The aesthetic is minimalist — black, white, and orange — with Apple-native product sensibility.

## Core Value

The timer counts down reliably and the app stays out of the way until needed.

## Current Milestone: v1.1 Hardware Eyes

**Goal:** Wire the Glorb Electron app to two SSD1306 OLEDs on an Arduino UNO so Glorb's physical eyes react to timer events.

**Target features:**
- Firmware: two displays (Display 1 = A4/A5 hardware I2C, Display 2 = A2/A3 software I2C), each showing one eye
- Two eye states: OPEN_EYES (centered oval) and SMILE (^ arc), one call updates both displays
- USB serial listener in firmware: accepts "DEFAULT\n" / "SMILE\n" commands
- Electron: auto-detect Arduino serial port, send state commands
- Timer start → SMILE for 5s → DEFAULT
- Timer complete → SMILE latched until window opened (min 5s)

## Requirements

### Validated

- ✓ App lives in macOS menu bar (no Dock icon) — v1.0 Phase 1
- ✓ Small portrait window with ring timer showing glorb.png at center — v1.0 Phase 2
- ✓ Ring timer counts down with animated progress (configurable 1–60 min) — v1.0 Phase 2
- ✓ Time display shows "XXh XXm XXs" format below ring — v1.0 Phase 2
- ✓ Start/Pause button below time display — v1.0 Phase 2
- ✓ Hamburger menu (top right) expands window to reveal settings panel — v1.0 Phase 3
- ✓ Settings panel: focus summary with persisted user name and time — v1.0 Phase 3
- ✓ Settings panel: Strength selector (Auto/Weak/Strong) with persistence — v1.0 Phase 3
- ✓ Settings panel: "Retake Test" button — v1.0 Phase 3
- ✓ Dark/light theme toggle with persistence — v1.0 quick tasks
- ✓ Push notification on focus session completion — v1.0 quick tasks

### Active (v1.1)

- [ ] Firmware updated for two displays: Display 1 on A4/A5 (hardware I2C), Display 2 on A2/A3 (software I2C)
- [ ] showDisplay(DisplayState) updates both displays simultaneously
- [ ] OPEN_EYES state: centered oval on each display
- [ ] SMILE state: centered ^ arc on each display
- [ ] Firmware serial listener: "DEFAULT\n" → OPEN_EYES, "SMILE\n" → SMILE
- [ ] Electron auto-detects Arduino serial port on startup
- [ ] Timer start triggers SMILE for 5s then DEFAULT
- [ ] Timer complete triggers SMILE latched until window opened (min 5s)

### Deferred

- [ ] Break timer (5-min / 15-min) after work session
- [ ] Session count tracker (4 pomodoros = long break)
- [ ] Configurable timer durations via settings panel
- [ ] Focus history persisted across app restarts
- [ ] Strength setting wired to actual behavior

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
| Electron over Tauri/SwiftUI | Fastest path to match exact UI spec; user can swap later | ✓ Good — shipped in 3 phases |
| Vanilla JS (no React/Vue) | Simple enough; avoids build toolchain overhead | ✓ Good — no build complexity |
| SVG ring timer | Smooth animation, full CSS control, no canvas needed | ✓ Good — smooth countdown |
| Horizontal window expansion | Settings panel feels native/spatial without a modal | ✓ Good — 720px expanded feels spacious |
| electron-store for persistence | Simple KV store for theme, name, strength, focus time | ✓ Good — no DB needed |
| Dark/light theme toggle | sun/moon icon, glorb_light/dark.png swap | ✓ Good — added post-Phase 3 |

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
*Last updated: 2026-04-16 — v1.1 milestone started: Hardware Eyes*
