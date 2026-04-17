---
plan: 04-02
phase: 04-dual-display-firmware
status: complete
completed: 2026-04-17
---

# Plan 04-02: Hardware Upload & Visual Verification — Summary

## What Was Built

Both OLED displays verified cycling OPEN_EYES ↔ SMILE simultaneously on hardware.

## Tasks Completed

1. **Hardware rewire** — Display 2 SDA/SCL moved from A4/A5 to A2/A3 (SW I2C pins)
2. **Firmware upload** — `pio run --target upload` succeeded, avrdude flash verified
3. **Visual verification** — Both displays cycling synchronized states every 2 seconds

## Issues Encountered and Resolved

### D2 blank despite begin() OK — RAM overflow
Two `_F_` (full-buffer) U8g2 instances require 2×1024B = 2048B SRAM — exactly the UNO's total. The second display buffer silently failed at runtime. Fix: switched both to `_2_` (two-page) variant. RAM dropped from 94.9% to 54.7%.

### D2 power — breadboard VCC wires crossed
After rewiring Display 2, VCC jumpers were accidentally crossed between displays. Resolved by tracing each display's SDA/SCL wire to confirm D1 (A4/A5) vs D2 (A2/A3) identity, then reconnecting both VCC wires to a shared 5V rail.

## Final Architecture

| Display | I2C | Pins | U8g2 Constructor | Rotation |
|---------|-----|------|-----------------|----------|
| D1 | Hardware | A4(SDA)/A5(SCL) | `_2_HW_I2C` | U8G2_R1 |
| D2 | Software | A2(SDA)/A3(SCL) | `_2_SW_I2C` | U8G2_R3 |

## Key Files

- `firmware/src/display.cpp` — two-display driver, 2-page buffer, `firstPage`/`nextPage` drawing
- `firmware/src/display.h` — `DisplayState` enum, `displaySetup()`, `showDisplay()` API
- `firmware/platformio.ini` — UNO target, U8g2 2.35.7+
- `firmware/src/main.cpp` — demo loop cycling both states

## Self-Check: PASSED

- Both displays initialize on power-up ✓
- `showDisplay(OPEN_EYES)` renders filled ellipse on both simultaneously ✓
- `showDisplay(SMILE)` renders centered `^` on both simultaneously ✓
- Single `showDisplay()` call drives both displays ✓
