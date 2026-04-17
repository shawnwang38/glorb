---
phase: 05-serial-integration
plan: 01
subsystem: firmware
tags: [arduino, serial, display, u8g2, platformio]
dependency_graph:
  requires: []
  provides: [serial-command-parser, outline-ellipse-display]
  affects: [firmware/src/main.cpp, firmware/src/display.cpp]
tech_stack:
  added: []
  patterns: [Serial.readStringUntil blocking parser, U8G2 drawEllipse outline]
key_files:
  created: []
  modified:
    - firmware/src/main.cpp
    - firmware/src/display.cpp
decisions:
  - "Power-up default is SMILE (closed eyes) per D-08"
  - "readStringUntil blocking pattern is intentional (D-01) — loop does nothing else"
  - "drawEllipse outline (not drawFilledEllipse) gives hollow ring eye aesthetic (D-05)"
  - "Smile arc: cx=32, cy=72, rx=20, ry=10 with UPPER_LEFT|UPPER_RIGHT — matches eye width"
metrics:
  duration: "~5 minutes"
  completed: "2026-04-17"
  tasks_completed: 2
  files_modified: 2
---

# Phase 05 Plan 01: Serial Command Parser and Display Graphics Update Summary

Firmware updated with a blocking serial command parser (replacing the cycling demo loop) and corrected display draw functions using U8G2 ellipse primitives instead of a filled ellipse and font character.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Replace demo loop with serial command parser | 7cb82b5 | firmware/src/main.cpp |
| 2 | Update display draw functions to outline ellipse and arc smile | 933e6ef | firmware/src/display.cpp |

## What Was Built

**main.cpp** — `setup()` initializes serial at 115200 baud, calls `displaySetup()`, then calls `showDisplay(DisplayState::SMILE)` (closed eyes on power-up, D-08). `loop()` calls `Serial.readStringUntil('\n')`, trims whitespace, and dispatches: "DEFAULT" → `showDisplay(DisplayState::OPEN_EYES)`, "SMILE" → `showDisplay(DisplayState::SMILE)`. Unknown commands silently ignored. No delays, no cycling demo.

**display.cpp** — `drawEyePage` replaced `drawFilledEllipse` with `drawEllipse(32, 64, 20, 30, U8G2_DRAW_ALL)` — hollow outline ring, dark center. `drawSmilePage` removed font rendering entirely; replaced with `drawEllipse(32, 72, 20, 10, U8G2_DRAW_UPPER_LEFT | U8G2_DRAW_UPPER_RIGHT)` — upper arc shape matching eye width. All other display.cpp code (U8G2 instances, `displaySetup`, `showDisplay`, two-display render loop) left untouched.

## Verification Results

- `grep "readStringUntil" firmware/src/main.cpp` — 1 code call (line 12)
- `grep "delay" firmware/src/main.cpp` — 0 matches
- `grep "DEFAULT" firmware/src/main.cpp` — if-branch dispatch present
- `drawFilledEllipse` code calls — 0 (only in comment text)
- `drawStr` / `setFont` — 0 matches
- `drawEllipse` code calls — exactly 2 (lines 18 and 25 of display.cpp)
- `pio run` — SUCCESS (RAM: 55.8% / 2048 bytes, Flash: 39.3% / 32256 bytes)

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — both commands are wired to real display state transitions.

## Threat Flags

No new security surface introduced. Serial command dispatch is display-only as documented in threat register (T-05-01, T-05-02 — both accepted).

## Self-Check: PASSED

- firmware/src/main.cpp: FOUND
- firmware/src/display.cpp: FOUND
- Commit 7cb82b5: verified via git log
- Commit 933e6ef: verified via git log
- pio run: SUCCESS
