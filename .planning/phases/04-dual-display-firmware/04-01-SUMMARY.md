---
phase: 04-dual-display-firmware
plan: "01"
subsystem: firmware
tags: [firmware, arduino, u8g2, oled, display]
dependency_graph:
  requires: []
  provides: [firmware/platformio.ini, firmware/src/display.h, firmware/src/display.cpp, firmware/src/main.cpp]
  affects: [phase-05-serial-integration]
tech_stack:
  added: [U8g2@2.36.18, PlatformIO atmelavr, U8G2_SSD1306_128X64_NONAME_F_SW_I2C]
  patterns: [two-instance U8g2 architecture, portrait rotation via U8G2_R1/R3, full-buffer mode F variant]
key_files:
  created: []
  modified:
    - firmware/platformio.ini
    - firmware/src/display.h
    - firmware/src/display.cpp
    - firmware/src/main.cpp
decisions:
  - "Used drawFilledEllipse(32, 64, 20, 30) for OPEN_EYES — confirmed available in U8g2 2.36.x (resolved plan's uncertainty)"
  - "u8g2_sw pin order: clock=A3=17, data=A2=16 per UNO R3 analog pin numbering"
  - "SMILE baseline y=80 on 128px tall portrait canvas — centers the 32px logisoso32 glyph vertically"
metrics:
  duration_minutes: 12
  completed_date: "2026-04-17"
  tasks_completed: 2
  files_modified: 4
requirements: [FW-01, FW-02, FW-03, FW-04]
---

# Phase 4 Plan 01: Two-Display Firmware Architecture Summary

Two-display U8g2 firmware layer driving SSD1306 OLEDs on hardware I2C (A4/A5, U8G2_R1) and software I2C (A2/A3, U8G2_R3), compiling cleanly for Arduino UNO R3 with a single showDisplay() call updating both portrait displays.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create firmware directory structure and base files | (pre-existing at base commit — display.h and platformio.ini already correct) | firmware/platformio.ini, firmware/src/display.h |
| 2 | Implement two-display driver and demo main loop | 4f11865 | firmware/src/display.cpp, firmware/src/main.cpp |

## What Was Built

**firmware/platformio.ini** — PlatformIO build config targeting Arduino UNO R3 (atmelavr platform) with `olikraus/U8g2@^2.35.7` dependency and 115200 baud serial monitor. Unchanged from prior quick-task (SW I2C is built into U8g2, no extra deps needed).

**firmware/src/display.h** — Public API: `DisplayState` enum (OPEN_EYES, SMILE), `displaySetup()`, `showDisplay(DisplayState)`. Interface kept identical to prior single-display quick-task for Phase 5 serial integration compatibility.

**firmware/src/display.cpp** — Two-display implementation:
- `u8g2_hw`: `U8G2_SSD1306_128X64_NONAME_F_HW_I2C(U8G2_R1, U8X8_PIN_NONE)` — Display 1, A4/A5, CCW physical rotation corrected to portrait
- `u8g2_sw`: `U8G2_SSD1306_128X64_NONAME_F_SW_I2C(U8G2_R3, 17, 16, U8X8_PIN_NONE)` — Display 2, A3(clock)/A2(data), CW physical rotation corrected to portrait
- `displaySetup()` calls `.begin()` on both instances
- `showDisplay()` clears, draws, and sends buffer to both instances in one call
- OPEN_EYES: `drawFilledEllipse(32, 64, 20, 30, U8G2_DRAW_ALL)` — filled oval centered on 64×128 portrait canvas
- SMILE: `u8g2_font_logisoso32_tr` "^" character, x-centered via `getStrWidth`, baseline at y=80

**firmware/src/main.cpp** — Arduino demo loop: `displaySetup()` on start, then alternates OPEN_EYES/SMILE with 2s delay for standalone hardware verification before Phase 5 serial integration.

**Compilation result:** `pio run` exits 0. Flash: 45.1% (14544/32256 bytes), RAM: 92.2% (1889/2048 bytes). U8g2 2.36.18 installed (satisfies `^2.35.7` constraint).

## Deviations from Plan

None — plan executed exactly as written. `drawFilledEllipse` was available in U8g2 2.36.18 (no fallback needed). The plan's uncertainty about this method was resolved at compile time.

**Note on Task 1:** The firmware files (display.h, platformio.ini) were already present at the base commit from the prior quick task (cb11ee4) with identical content. No changes were needed — the task's creation intent was already satisfied.

## Known Stubs

None. Both display states are fully implemented and will produce real output on hardware.

## Threat Flags

None. Pure output-only firmware; no new network endpoints, auth paths, file access, or schema changes introduced.

## Self-Check

Files exist:
- firmware/platformio.ini: FOUND
- firmware/src/display.h: FOUND
- firmware/src/display.cpp: FOUND
- firmware/src/main.cpp: FOUND

Commits exist:
- 4f11865 (feat(04-01): implement two-display driver and demo main loop): FOUND

## Self-Check: PASSED
