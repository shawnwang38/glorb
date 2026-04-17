# Roadmap: Glorb

## Overview

Glorb is a macOS menu bar Pomodoro timer. Three phases take it from an Electron shell to a fully styled, interactive timer with an expandable settings panel. Phase 1 stands up the app container. Phase 2 delivers the core timer experience — the only thing that must work perfectly. Phase 3 adds the settings panel that makes the app feel complete.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: App Shell** - Electron app running in macOS menu bar with togglable window
- [ ] **Phase 2: Timer + Design** - Animated ring timer counting down with full design system applied
- [ ] **Phase 3: Settings Panel** - Expandable settings panel with hamburger toggle and focus summary

## Phase Details

### Phase 1: App Shell
**Goal**: The Electron app lives in the macOS menu bar and shows a window when clicked
**Depends on**: Nothing (first phase)
**Requirements**: SHELL-01, SHELL-02, SHELL-03, SHELL-04
**Success Criteria** (what must be TRUE):
  1. App launches with no Dock icon — only a Tray icon appears in the macOS menu bar
  2. Clicking the Tray icon shows the main window; clicking again hides it
  3. Window is frameless, positioned near the menu bar icon, and has a #f0f0f0 background at ~220x360px
**Plans**: 2 plans

Plans:
- [x] 01-01-PLAN.md — Electron main process: package.json, main.js, preload.js (Tray, BrowserWindow, IPC)
- [x] 01-02-PLAN.md — Renderer: renderer.html + renderer.css (close button, quit overlay, app container)

**UI hint**: yes

### Phase 2: Timer + Design
**Goal**: Users can run a 25-minute Pomodoro timer with the glorb mascot at center, styled to spec
**Depends on**: Phase 1
**Requirements**: TIMER-01, TIMER-02, TIMER-03, TIMER-04, TIMER-05, TIMER-06, TIMER-07, DSGN-01, DSGN-02, DSGN-03, DSGN-04
**Success Criteria** (what must be TRUE):
  1. An SVG ring timer displays around glorb.png with an orange animated stroke that shrinks as time passes
  2. Time below the ring shows in "XXh XXm" format, starting at "00h 25m"
  3. Clicking Start begins the countdown; clicking Pause freezes it; the button label reflects current state
  4. When the timer reaches 00:00 it resets to 25:00 automatically
  5. The entire window uses the correct palette (#f0f0f0, black/dark-gray text, #FF6B35 accents) with Inter/system-ui font and consistent button styling
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — Timer HTML structure + CSS styles (ring, glorb, time display, buttons, hamburger)
- [x] 02-02-PLAN.md — Timer JavaScript engine (countdown, pause/resume, auto-reset, ring animation)
- [x] 02-03-PLAN.md — Human visual and functional QA checkpoint

**UI hint**: yes

### Phase 3: Settings Panel
**Goal**: Users can open an expanded settings panel from the timer view and close it to return
**Depends on**: Phase 2
**Requirements**: SETT-01, SETT-02, SETT-03, SETT-04, SETT-05, SETT-06
**Success Criteria** (what must be TRUE):
  1. A hamburger button is visible in the top-right corner of the timer view
  2. Clicking the hamburger expands the window to 440×468px and slides in the settings panel from the right
  3. Settings panel shows a focus summary message ("Hi there, you've focused for 0h 0m with Glorb.")
  4. Strength selector (Auto/Weak/Strong) and "Retake Test" button are present in the panel (UI only)
  5. Clicking the hamburger again (or the × in panel header) collapses the panel and restores the window to 286×468px
**Plans**: 4 plans

Plans:
- [x] 03-01-PLAN.md — IPC bridge: extend preload.js + main.js with resize-window channel
- [x] 03-02-PLAN.md — HTML + CSS: settings panel DOM, slide animation, strength selector, Retake Test button
- [x] 03-03-PLAN.md — JS wiring: hamburger + close button toggle handlers calling IPC resize
- [x] 03-04-PLAN.md — Human visual and functional QA checkpoint

**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. App Shell | 0/2 | Not started | - |
| 2. Timer + Design | 0/3 | Not started | - |
| 3. Settings Panel | 3/4 | In Progress|  |
