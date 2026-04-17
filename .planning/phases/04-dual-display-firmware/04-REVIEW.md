---
phase: 04-dual-display-firmware
reviewed: 2026-04-17T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - firmware/platformio.ini
  - firmware/src/display.h
  - firmware/src/display.cpp
  - firmware/src/main.cpp
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-04-17
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Reviewed four firmware files for an Arduino UNO driving two SSD1306 OLED displays via U8g2. The code is concise and the dual-display architecture (hardware I2C + software I2C, 2-page buffer mode) is sound. The rotation constants (`U8G2_R1` / `U8G2_R3`) are correctly chosen to present portrait canvases from landscape-oriented OLEDs, and the pin assignments match the inline comments.

Two warnings are present: `begin()` return values are silently discarded, which makes initialization failures invisible at runtime; and the smile glyph baseline is hardcoded without comment, making it fragile if the font is ever changed. Two info items cover magic numbers and a redundant first `showDisplay` call in `loop()`.

---

## Warnings

### WR-01: Silent I2C initialization failure — `begin()` return values discarded

**File:** `firmware/src/display.cpp:27-28`
**Issue:** `u8g2_hw.begin()` and `u8g2_sw.begin()` both return `bool` — `false` when the display does not ACK on the I2C bus (wrong address, missing pull-ups, wiring issue). The return values are discarded, so a failing display silently produces no output and `showDisplay()` enters the page-flip loop against an unresponsive peripheral with no diagnostic.

**Fix:**
```cpp
void displaySetup() {
    if (!u8g2_hw.begin()) {
        Serial.println(F("ERROR: HW I2C display (D1) init failed"));
        // optionally: halt or set a flag
    }
    if (!u8g2_sw.begin()) {
        Serial.println(F("ERROR: SW I2C display (D2) init failed"));
    }
}
```
Since `Serial.begin(115200)` is called before `displaySetup()` in `main.cpp`, the port is available. Logging the failure makes field debugging possible without an oscilloscope.

---

### WR-02: Hardcoded font baseline in `drawSmilePage` is fragile

**File:** `firmware/src/display.cpp:23`
**Issue:** The Y baseline `80` is a magic number tuned to `u8g2_font_logisoso32_tr` (ascent ~32px, so the glyph top lands near y=48). If the font is swapped the glyph will shift or clip with no compiler warning.

**Fix:** Derive the position from the font metrics at runtime, or add a comment that locks the value to the current font:
```cpp
// Baseline y=80 tuned for logisoso32 (ascent ~32px → glyph top ~y48, centered on 128h canvas)
u8g2.drawStr((64 - charW) / 2, 80, "^");
```
Alternatively use `u8g2.getAscent()` to compute the baseline dynamically:
```cpp
int baseline = (128 + u8g2.getAscent()) / 2;
u8g2.drawStr((64 - charW) / 2, baseline, "^");
```

---

## Info

### IN-01: Magic numbers in `drawEyePage` without comments

**File:** `firmware/src/display.cpp:17`
**Issue:** `drawFilledEllipse(32, 64, 20, 30, U8G2_DRAW_ALL)` — the center (32, 64), x-radius 20, and y-radius 30 are all bare literals. On a 64×128 canvas (32, 64) is the center, which is intentional, but the radii carry no explanation. This makes it harder to adjust the eye shape without guessing what to change.

**Fix:** Add a brief comment or named constants:
```cpp
// Ellipse centered on 64x128 canvas; rx=20 px, ry=30 px gives a tall oval eye
u8g2.drawFilledEllipse(32, 64, 20, 30, U8G2_DRAW_ALL);
```

---

### IN-02: `loop()` renders OPEN_EYES twice per full cycle without comment

**File:** `firmware/src/main.cpp:11`
**Issue:** `loop()` begins with `showDisplay(DisplayState::OPEN_EYES)` before any delay. Because `loop()` is called again immediately after the second `delay(2000)`, the sequence is: OPEN_EYES → 2 s → SMILE → 2 s → (loop restart) OPEN_EYES → ... The OPEN_EYES render at the top of `loop()` is redundant on all iterations after the first — the display already shows OPEN_EYES from `setup()`. This is harmless in a demo but suggests the loop is a placeholder rather than intentional state machine logic.

**Fix:** If this is a demo loop, no change needed — just add a comment:
```cpp
void loop() {
    // Demo cycle: alternate eyes and smile every 2 s
    showDisplay(DisplayState::OPEN_EYES);
    delay(2000);
    showDisplay(DisplayState::SMILE);
    delay(2000);
}
```
If production logic will replace this, the redundant first call can be dropped once a proper state machine is introduced.

---

_Reviewed: 2026-04-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
