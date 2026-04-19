# Glorb

## What This Is

Glorb is a macOS menu bar Pomodoro timer app. It lives in the system menu bar and surfaces a small portrait window with a ring countdown timer, displaying a custom mascot (glorb.png) at its center. The aesthetic is minimalist — black, white, and orange — with Apple-native product sensibility.

## Core Value

The timer counts down reliably and the app stays out of the way until needed.

## Current State: v1.2 shipped 2026-04-19

Glorb v1.2 Focus Intelligence is complete. The app now personalizes focus interventions via an ADHD onboarding questionnaire (ASRS 1.1, 18 questions) and delivers strength-tiered escalating nudges when drift is detected. Four intervention paths (Weak×Regular, Weak×ADHD, Strong×Regular, Strong×ADHD) are fully wired to the onboarding profile and strength selector.

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

### Validated (v1.1)

- ✓ Firmware drives two SSD1306 OLEDs simultaneously (hardware I2C A4/A5, software I2C A2/A3) — v1.1 Phase 4
- ✓ OPEN_EYES and SMILE states rendered on both displays via single showDisplay() call — v1.1 Phase 4
- ✓ Firmware accepts "DEFAULT\n" / "SMILE\n" / "ANGRY\n" over USB serial — v1.1 Phase 5
- ✓ Electron auto-detects Arduino serial port; status dot in settings — v1.1 Phase 5
- ✓ Timer start → SMILE 5s → DEFAULT; timer complete → ANGRY latch until window opened — v1.1 Phase 6

### Validated (v1.2)

- ✓ Onboarding window shown on first launch when user profile is empty — v1.2 Phase 7
- ✓ Onboarding: Glorb greeting with breathing gradient background — v1.2 Phase 7
- ✓ Onboarding: name entry step — v1.2 Phase 7
- ✓ Onboarding: ASRS 1.1 questionnaire (18 questions, one per screen, 5-dot response selector) — v1.2 Phase 7
- ✓ Onboarding: ADHD diagnosis logic persisted to store (hasADHD flag) — v1.2 Phase 7
- ✓ "Retake Test" button restarts onboarding from within settings panel — v1.2 Phase 7
- ✓ driftDetected() / refocusDetected() intervention API in renderer — v1.2 Phase 8
- ✓ Drift counter increments on drift; resets on refocus — v1.2 Phase 8
- ✓ Weak × Regular intervention escalation path — v1.2 Phase 8
- ✓ Weak × ADHD intervention escalation path — v1.2 Phase 8
- ✓ Strong × Regular intervention escalation path (with overlay windows) — v1.2 Phase 8
- ✓ Strong × ADHD intervention escalation path (with overlay windows) — v1.2 Phase 8
- ✓ Strength selector (Weak/Strong) wired to intervention path selection — v1.2 Phase 9
- ✓ CLI tool (`node simulate.js drift/refocus`) for testing without hardware — v1.2 Phase 8

### Active (v1.3+)

(None yet — start /gsd-new-milestone to define next milestone requirements)

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
- Ring timer uses SVG stroke-dashoffset animation for smooth countdown
- Window expands horizontally (220px → 440px) when settings panel opens
- #f0f0f0 background with radial gradient vignette around glorb.png inside ring
- v1.2: ~3,900 LOC added across 23 files (main.js, renderer.html, onboarding.html, onboarding.css, simulate.js, overlay HTMLs)
- Intervention state machine lives entirely in main process; four escalation paths with timer registry
- ADHD profile (hasADHD) + strength preference (weak/strong) persisted in electron-store; routing is fully automatic

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
| ASRS 1.1 questionnaire for ADHD detection | Clinical screening tool; self-reported but well-validated | ✓ Good — 18 questions, Part A scoring |
| Intervention state machine in main process only | Avoids renderer/main sync issues; timers survive window close | ✓ Good — clean separation |
| Four paths (Weak/Strong × Regular/ADHD) | Combinatorial coverage without per-user branching logic | ✓ Good — covers all profiles |
| Unix domain socket for CLI simulator | Simpler than HTTP, no port conflicts, local-only | ✓ Good — `node simulate.js drift` works |
| Inline routing (no helper) at both drift entry points | Explicit, greppable, avoids indirection for 3-line block | ✓ Good — easy to audit |
| Drop Auto strength option | Auto was undefined behavior; Weak/Strong are the real choices | ✓ Good — simpler UI, clean defaults |

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
*Last updated: 2026-04-19 — v1.2 milestone complete: Focus Intelligence (onboarding, intervention engine, focus wiring)*
