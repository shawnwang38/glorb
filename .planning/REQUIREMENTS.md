# Requirements: Glorb

**Defined:** 2026-04-16
**Core Value:** The timer counts down reliably and the app stays out of the way until needed.

## v1 Requirements

### App Shell

- [ ] **SHELL-01**: App runs as macOS menu bar app (no Dock icon, Tray icon in menu bar)
- [ ] **SHELL-02**: Clicking the Tray icon shows/hides the main window
- [ ] **SHELL-03**: Window is frameless, positioned near the menu bar icon
- [ ] **SHELL-04**: Window background is #f0f0f0; compact size ~220×360px

### Timer UI

- [ ] **TIMER-01**: Ring timer rendered as SVG circle with animated stroke-dashoffset countdown
- [ ] **TIMER-02**: glorb.png displayed at center of ring with #f0f0f0 radial vignette blending edges
- [ ] **TIMER-03**: Time display below ring shows "XXh XXm" format (e.g. "00h 25m")
- [ ] **TIMER-04**: Start/Pause button below time display; same style as all other buttons
- [ ] **TIMER-05**: Timer counts down from 25:00 to 00:00 when started
- [ ] **TIMER-06**: Timer pauses/resumes on button click; button label toggles Start/Pause
- [ ] **TIMER-07**: Timer resets to 25:00 when it reaches 00:00

### Settings Panel

- [x] **SETT-01**: Hamburger (3-line) button in top-right of main view
- [x] **SETT-02**: Clicking hamburger expands window to ~440×360px and slides in settings panel from right
- [x] **SETT-03**: Settings panel shows "Hi [username], you've focused for Xh Xm with Glorb."
- [x] **SETT-04**: Strength selector with three options: Auto / Weak / Strong (UI only, no behavior)
- [x] **SETT-05**: "Retake Test" button in settings panel (UI only, no behavior)
- [x] **SETT-06**: Close button or same hamburger click collapses settings and shrinks window back

### Design System

- [ ] **DSGN-01**: Color palette: #f0f0f0 background, black/dark-gray text, orange (#FF6B35) for active states and accents
- [ ] **DSGN-02**: Font: Inter or system-ui (Apple-native sans serif)
- [ ] **DSGN-03**: All buttons share a consistent style (outlined or filled, same border-radius, same font size)
- [ ] **DSGN-04**: Minimalist layout — no decorative elements beyond the ring timer

## v2 Requirements

### Extended Functionality

- **FUNC-01**: Break timer (short 5-min / long 15-min) after work session
- **FUNC-02**: Session count tracker (4 pomodoros = long break)
- **FUNC-03**: Sound/notification when timer completes
- **FUNC-04**: Focus history persisted across app restarts
- **FUNC-05**: Configurable timer durations
- **FUNC-06**: Strength setting wired to actual behavior (session/break ratio)
- **FUNC-07**: Retake Test flow to determine focus strength

## Out of Scope

| Feature | Reason |
|---------|--------|
| Windows/Linux support | macOS-only app for v1 |
| Data persistence | Not needed until v2 history feature |
| OAuth/accounts | No cloud sync planned |
| Notifications/sounds | Not in v1 scope |
| Mobile app | macOS desktop only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SHELL-01 | Phase 1 | Pending |
| SHELL-02 | Phase 1 | Pending |
| SHELL-03 | Phase 1 | Pending |
| SHELL-04 | Phase 1 | Pending |
| TIMER-01 | Phase 2 | Pending |
| TIMER-02 | Phase 2 | Pending |
| TIMER-03 | Phase 2 | Pending |
| TIMER-04 | Phase 2 | Pending |
| TIMER-05 | Phase 2 | Pending |
| TIMER-06 | Phase 2 | Pending |
| TIMER-07 | Phase 2 | Pending |
| SETT-01 | Phase 3 | Complete |
| SETT-02 | Phase 3 | Complete |
| SETT-03 | Phase 3 | Complete |
| SETT-04 | Phase 3 | Complete |
| SETT-05 | Phase 3 | Complete |
| SETT-06 | Phase 3 | Complete |
| DSGN-01 | Phase 2 | Pending |
| DSGN-02 | Phase 2 | Pending |
| DSGN-03 | Phase 2 | Pending |
| DSGN-04 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-16*
*Last updated: 2026-04-16 after initial definition*
