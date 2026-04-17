# Requirements: Glorb v1.1 — Hardware Eyes

**Defined:** 2026-04-16
**Core Value:** The timer counts down reliably and the app stays out of the way until needed.

## v1.1 Requirements

### Firmware

- [ ] **FW-01**: Firmware initializes Display 1 on hardware I2C (SDA=A4, SCL=A5) and Display 2 on software I2C (SDA=A2, SCL=A3)
- [ ] **FW-02**: User can see OPEN_EYES state as a centered oval on each display
- [ ] **FW-03**: User can see SMILE state as a centered ^ arc on each display
- [ ] **FW-04**: Calling showDisplay(DisplayState) updates both displays simultaneously with a single call

### Serial

- [ ] **SER-01**: Firmware receives "DEFAULT\n" over USB serial and transitions both displays to OPEN_EYES
- [ ] **SER-02**: Firmware receives "SMILE\n" over USB serial and transitions both displays to SMILE
- [ ] **SER-03**: Electron app auto-detects the Arduino serial port on startup (no manual port configuration)
- [ ] **SER-04**: Electron app maintains a persistent serial connection while Arduino is plugged in

### Behavior

- [ ] **BEH-01**: Timer start event sends SMILE command; displays revert to DEFAULT after 5 seconds
- [ ] **BEH-02**: Timer complete event latches SMILE until the Glorb window is opened by the user
- [ ] **BEH-03**: Timer complete SMILE persists for a minimum of 5 seconds even if the window is opened sooner

## Deferred Requirements

### App Features

- **APP-01**: Break timer (5-min / 15-min) after work session
- **APP-02**: Session count tracker (4 pomodoros = long break)
- **APP-03**: Configurable timer durations via settings panel
- **APP-04**: Focus history persisted across app restarts
- **APP-05**: Strength setting wired to actual behavior

## Out of Scope

| Feature | Reason |
|---------|--------|
| Wireless (BT/WiFi) Arduino connection | USB serial sufficient; adds complexity and cost |
| Additional eye expressions beyond 2 | Keep it minimal for v1.1 |
| Multiple display sizes / resolutions | Single SSD1306 128x64 hardware spec |
| Graceful degradation when Arduino unplugged mid-session | Nice-to-have; app works fine without hardware |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FW-01 | Phase 4 | Pending |
| FW-02 | Phase 4 | Pending |
| FW-03 | Phase 4 | Pending |
| FW-04 | Phase 4 | Pending |
| SER-01 | Phase 5 | Pending |
| SER-02 | Phase 5 | Pending |
| SER-03 | Phase 5 | Pending |
| SER-04 | Phase 5 | Pending |
| BEH-01 | Phase 6 | Pending |
| BEH-02 | Phase 6 | Pending |
| BEH-03 | Phase 6 | Pending |

**Coverage:**
- v1.1 requirements: 11 total
- Mapped to phases: 11 ✓
- Unmapped: 0

---
*Requirements defined: 2026-04-16*
*Last updated: 2026-04-16 after roadmap creation*
