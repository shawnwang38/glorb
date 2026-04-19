# Roadmap: Glorb

## Milestones

- ✅ **v1.0 MVP** — Phases 1–3 (shipped 2026-04-16) · [archive](.planning/milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Hardware Eyes** — Phases 4–6 (shipped 2026-04-17)
- 🚧 **v1.2 Focus Intelligence** — Phases 7–9 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1–3) — SHIPPED 2026-04-16</summary>

- [x] Phase 1: App Shell (2/2 plans) — completed 2026-04-16
- [x] Phase 2: Timer + Design (3/3 plans) — completed 2026-04-16
- [x] Phase 3: Settings Panel (4/4 plans) — completed 2026-04-16

</details>

<details>
<summary>✅ v1.1 Hardware Eyes (Phases 4–6) — SHIPPED 2026-04-17</summary>

- [x] Phase 4: Dual Display Firmware (2/2 plans) — completed 2026-04-17
- [x] Phase 5: Serial Integration (4/4 plans) — completed 2026-04-17
- [x] Phase 6: Timer Event Wiring (2/2 plans) — completed 2026-04-17

</details>

### 🚧 v1.2 Focus Intelligence (In Progress)

**Milestone Goal:** Personalize Glorb's focus interventions via an ADHD onboarding questionnaire, then deliver strength-tiered nudges when drift is detected.

- [ ] **Phase 7: Onboarding Flow** - Full-screen onboarding window with greeting, name entry, ASRS 1.1 questionnaire, and ADHD diagnosis persistence
- [ ] **Phase 8: Intervention Engine** - driftDetected/refocusDetected API with all four strength × profile escalation paths and CLI simulator
- [ ] **Phase 9: Focus Wiring** - Wire strength selector and hasADHD flag to route drift events to the correct intervention path

## Phase Details

### Phase 4: Dual Display Firmware
**Goal**: The Arduino drives two SSD1306 OLEDs simultaneously with both OPEN_EYES and SMILE states via a single call
**Depends on**: Phase 3 (v1.0 complete); existing single-display showDisplay() from quick task 260416-w1c
**Requirements**: FW-01, FW-02, FW-03, FW-04
**Success Criteria** (what must be TRUE):
  1. Both displays initialize on power-up — Display 1 on hardware I2C (A4/A5), Display 2 on software I2C (A2/A3)
  2. Calling showDisplay(OPEN_EYES) renders a centered oval on each display simultaneously
  3. Calling showDisplay(SMILE) renders a centered ^ arc on each display simultaneously
  4. A single showDisplay() call updates both displays with no extra call required
**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md — Create firmware source files (platformio.ini, display.h, display.cpp, main.cpp) for two-display architecture
- [x] 04-02-PLAN.md — Upload firmware to Arduino and visually verify both OLED displays

### Phase 5: Serial Integration
**Goal**: Firmware accepts "DEFAULT\n" and "SMILE\n" commands over USB serial, and the Electron app auto-detects the Arduino port and maintains a live connection
**Depends on**: Phase 5
**Requirements**: SER-01, SER-02, SER-03, SER-04
**Success Criteria** (what must be TRUE):
  1. Sending "DEFAULT\n" over serial transitions both displays to OPEN_EYES
  2. Sending "SMILE\n" over serial transitions both displays to SMILE
  3. On app startup, Electron finds and opens the Arduino serial port without any manual configuration
  4. Electron maintains the serial connection while the Arduino remains plugged in
**Plans**: 4 plans

Plans:
- [x] 05-01-PLAN.md — Update firmware: serial command parser in main.cpp + updated display graphics in display.cpp
- [x] 05-02-PLAN.md — Electron serial core: install serialport, auto-detect + reconnect lifecycle in main.js, IPC in preload.js
- [x] 05-03-PLAN.md — Settings panel status dot: hardware connection indicator in renderer
- [x] 05-04-PLAN.md — Upload firmware and verify full end-to-end serial integration (hardware checkpoint)

### Phase 6: Timer Event Wiring
**Goal**: Timer start and timer complete events drive the eye displays with the correct timing and latch behavior
**Depends on**: Phase 5
**Requirements**: BEH-01, BEH-02, BEH-03
**Success Criteria** (what must be TRUE):
  1. Starting the timer sends SMILE to the displays, which revert to DEFAULT after 5 seconds
  2. Timer completion latches SMILE on the displays until the user opens the Glorb window
  3. If the window is opened before 5 seconds have elapsed after timer complete, SMILE persists for the remainder of that 5-second minimum
**Plans**: 2 plans

Plans:
- [x] 06-01-PLAN.md — IPC plumbing: add send-serial handler in main.js and sendSerial in preload.js
- [x] 06-02-PLAN.md — Renderer wiring: timer start/cancel/complete hooks and latch release logic in renderer.html

### Phase 7: Onboarding Flow
**Goal**: New users are guided through a full-screen onboarding experience that captures their name and ADHD profile before they ever see the timer
**Depends on**: Phase 6 (v1.1 complete)
**Requirements**: ONBOARD-01, ONBOARD-02, ONBOARD-03, ONBOARD-04, ONBOARD-05, ONBOARD-06
**Success Criteria** (what must be TRUE):
  1. On first launch (no name or ADHD status in store), the app opens the onboarding window instead of going straight to the timer
  2. User sees a Glorb greeting screen with a breathing gradient background before any questions are asked
  3. User enters their name and proceeds to the ASRS 1.1 questionnaire (18 questions, one per screen, with a 5-dot response selector and a Back button)
  4. After completing all 18 questions, the app computes and persists the hasADHD diagnosis to store
  5. Clicking "Retake Test" in the settings panel relaunches the onboarding questionnaire from the beginning
**Plans**: 3 plans

Plans:
- [x] 07-01-PLAN.md — ASRS-SCORING.md reference doc + onboarding.css (all components, breathing animation, dark mode)
- [x] 07-02-PLAN.md — onboarding.html: 5-screen state machine, questionnaire engine, Part A scoring, store writes
- [x] 07-03-PLAN.md — main.js gate + IPC handlers + preload.js extensions + Retake Test wiring in renderer.html

### Phase 8: Intervention Engine
**Goal**: Calling driftDetected() triggers escalating nudges along the correct path, and refocusDetected() cleanly cancels all active timers; a CLI tool lets the developer trigger both signals without hardware
**Depends on**: Phase 7
**Requirements**: INTERV-01, INTERV-02, INTERV-03, INTERV-04, INTERV-05, INTERV-06, CLI-01, CLI-02
**Success Criteria** (what must be TRUE):
  1. Calling driftDetected() increments the drift counter; calling refocusDetected() resets it to 0 and cancels all pending escalation timers
  2. refocusDetected() sends a "Focus regained." push notification for any non-terminal drift event
  3. Each of the four escalation paths (Weak×Regular, Weak×ADHD, Strong×Regular, Strong×ADHD) runs its full sequence of notifications, chimes, and terminate actions when driftDetected() is called under the matching configuration
  4. Running `node simulate.js drift` from the terminal triggers driftDetected() in the running Electron app
  5. Running `node simulate.js refocus` from the terminal triggers refocusDetected() in the running Electron app
**Plans**: 4 plans

Plans:
- [x] 08-01-PLAN.md — Intervention state machine core: drift/refocus IPC handlers, timer registry, runPath dispatcher, preload.js exposure
- [x] 08-02-PLAN.md — Weak paths: Weak×Regular and Weak×ADHD escalation sequences with push notifications, audio, in-window terminate popup
- [x] 08-03-PLAN.md — Strong paths + overlay windows: Strong×Regular and Strong×ADHD, flash/vignette/terminate HTML files, audio fade
- [x] 08-04-PLAN.md — CLI simulator: simulate.js Unix socket client, main.js socket server, end-to-end test

### Phase 9: Focus Wiring
**Goal**: The strength selector and ADHD diagnosis stored during onboarding automatically route every drift event to the correct intervention path with no manual configuration
**Depends on**: Phase 8
**Requirements**: WIRE-01, WIRE-02, WIRE-03
**Success Criteria** (what must be TRUE):
  1. With Strength set to "Weak", triggering drift runs the Weak intervention path
  2. With Strength set to "Strong", triggering drift runs the Strong intervention path
  3. With hasADHD: true in store, the ADHD variant of the active path is selected; with hasADHD: false, the Regular variant is selected
**Plans**: 2 plans

Plans:
- [ ] 09-01-PLAN.md — main.js: replace both hardcoded runPath('weak-regular') calls with dynamic store-based routing
- [ ] 09-02-PLAN.md — renderer.html: remove Auto button, set Weak as default active, add legacy 'auto' migration guard

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. App Shell | v1.0 | 2/2 | Complete | 2026-04-16 |
| 2. Timer + Design | v1.0 | 3/3 | Complete | 2026-04-16 |
| 3. Settings Panel | v1.0 | 4/4 | Complete | 2026-04-16 |
| 4. Dual Display Firmware | v1.1 | 2/2 | Complete | 2026-04-17 |
| 5. Serial Integration | v1.1 | 4/4 | Complete | 2026-04-17 |
| 6. Timer Event Wiring | v1.1 | 2/2 | Complete | 2026-04-17 |
| 7. Onboarding Flow | v1.2 | 0/3 | Not started | - |
| 8. Intervention Engine | v1.2 | 0/4 | Not started | - |
| 9. Focus Wiring | v1.2 | 0/2 | Not started | - |
