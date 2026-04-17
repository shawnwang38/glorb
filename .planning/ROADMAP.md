# Roadmap: Glorb

## Milestones

- ✅ **v1.0 MVP** — Phases 1–3 (shipped 2026-04-16) · [archive](.planning/milestones/v1.0-ROADMAP.md)
- 🚧 **v1.1 Hardware Eyes** — Phases 4–6 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1–3) — SHIPPED 2026-04-16</summary>

- [x] Phase 1: App Shell (2/2 plans) — completed 2026-04-16
- [x] Phase 2: Timer + Design (3/3 plans) — completed 2026-04-16
- [x] Phase 3: Settings Panel (4/4 plans) — completed 2026-04-16

</details>

### 🚧 v1.1 Hardware Eyes (In Progress)

**Milestone Goal:** Wire the Glorb Electron app to two SSD1306 OLEDs on an Arduino UNO so Glorb's physical eyes react to timer events.

- [ ] **Phase 4: Dual Display Firmware** - Extend firmware to drive two independent OLED displays with shared eye states
- [ ] **Phase 5: Serial Integration** - Add USB serial listener to firmware and auto-detecting serial connection in Electron
- [ ] **Phase 6: Timer Event Wiring** - Connect timer start/complete events to serial eye commands with timing and latch logic

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
- [ ] 04-01-PLAN.md — Create firmware source files (platformio.ini, display.h, display.cpp, main.cpp) for two-display architecture
- [ ] 04-02-PLAN.md — Upload firmware to Arduino and visually verify both OLED displays

### Phase 5: Serial Integration
**Goal**: Firmware accepts "DEFAULT\n" and "SMILE\n" commands over USB serial, and the Electron app auto-detects the Arduino port and maintains a live connection
**Depends on**: Phase 4
**Requirements**: SER-01, SER-02, SER-03, SER-04
**Success Criteria** (what must be TRUE):
  1. Sending "DEFAULT\n" over serial transitions both displays to OPEN_EYES
  2. Sending "SMILE\n" over serial transitions both displays to SMILE
  3. On app startup, Electron finds and opens the Arduino serial port without any manual configuration
  4. Electron maintains the serial connection while the Arduino remains plugged in
**Plans**: TBD

### Phase 6: Timer Event Wiring
**Goal**: Timer start and timer complete events drive the eye displays with the correct timing and latch behavior
**Depends on**: Phase 5
**Requirements**: BEH-01, BEH-02, BEH-03
**Success Criteria** (what must be TRUE):
  1. Starting the timer sends SMILE to the displays, which revert to DEFAULT after 5 seconds
  2. Timer completion latches SMILE on the displays until the user opens the Glorb window
  3. If the window is opened before 5 seconds have elapsed after timer complete, SMILE persists for the remainder of that 5-second minimum
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. App Shell | v1.0 | 2/2 | Complete | 2026-04-16 |
| 2. Timer + Design | v1.0 | 3/3 | Complete | 2026-04-16 |
| 3. Settings Panel | v1.0 | 4/4 | Complete | 2026-04-16 |
| 4. Dual Display Firmware | v1.1 | 0/2 | Not started | - |
| 5. Serial Integration | v1.1 | 0/? | Not started | - |
| 6. Timer Event Wiring | v1.1 | 0/? | Not started | - |
