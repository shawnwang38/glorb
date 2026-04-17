---
phase: quick
plan: 260417-fvf
type: execute
wave: 1
depends_on: []
files_modified:
  - firmware/src/bitmaps.h
  - firmware/src/display.cpp
autonomous: true
requirements: []
must_haves:
  truths:
    - "OPEN_EYES displays a hollow ellipse ring centered on each display"
    - "SMILE displays an upper arc centered on each display"
    - "Swapping graphics requires only editing bitmaps.h, not display.cpp"
  artifacts:
    - path: "firmware/src/bitmaps.h"
      provides: "XBM byte arrays for open_eyes_bits and smile_bits"
    - path: "firmware/src/display.cpp"
      provides: "drawXBM calls replacing the programmatic ellipse draws"
  key_links:
    - from: "firmware/src/bitmaps.h"
      to: "firmware/src/display.cpp"
      via: "#include and drawXBM(0, 0, 64, 128, open_eyes_bits)"
---

<objective>
Replace the programmatic U8g2 drawEllipse calls in display.cpp with XBM bitmap rendering so graphics are user-swappable by editing a single bitmap header file.

Purpose: The current draw calls (drawEllipse for OPEN_EYES and SMILE) are hardcoded math. Swapping visuals requires understanding U8g2 geometry. XBM arrays let the user replace graphics by editing pixel data directly.

Output: firmware/src/bitmaps.h containing two 64x128-pixel XBM arrays (open_eyes_bits, smile_bits), and display.cpp updated to use drawXBM instead of drawEllipse.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@firmware/src/display.cpp
@firmware/src/display.h
@firmware/src/main.cpp
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create bitmaps.h with XBM arrays matching current visuals</name>
  <files>firmware/src/bitmaps.h</files>
  <action>
Create firmware/src/bitmaps.h with two XBM-format byte arrays for the 64x128 logical canvas (64 pixels wide, 128 pixels tall, matching U8g2's logical coordinate space after R1/R3 rotation is applied).

XBM format: bits packed LSB-first, row by row. 64px wide = 8 bytes per row. 128 rows = 1024 bytes per bitmap.

The logical coordinate space is 64 wide × 128 tall (portrait, after rotation transform).

**open_eyes_bits:** Hollow ellipse outline centered at (32, 64) with rx=20, ry=30. Mirrors drawEllipse(32, 64, 20, 30, U8G2_DRAW_ALL). Generate the 1024-byte array by iterating all (x, y) where 0 ≤ x < 64, 0 ≤ y < 128 and checking if the point is on the ellipse boundary:
  - A pixel is ON if: abs(((x-32)^2 / 20^2) + ((y-64)^2 / 30^2) - 1.0) < threshold
  - Use threshold ~0.12 so the ring is 1-2px thick (tuned for the small radii)
  - Pack bits: for row y, byte index = y*8 + (x/8), bit = x%8, bit value = 1 if pixel ON

**smile_bits:** Upper arc only — the upper half of the same ellipse centered at (32, 90) with rx=20, ry=30. Mirrors drawEllipse(32, 90, 20, 30, U8G2_DRAW_UPPER_LEFT | U8G2_DRAW_UPPER_RIGHT). Same pixel-on-boundary check but only when y < 90 (upper half). Pixels below center (y ≥ 90) are always 0.

Compute the arrays programmatically during plan creation (write the actual byte values, not a generator comment). Use a generation script mentally or inline — the executor must write real hex bytes.

**Implementation approach for executor:**
Write a small Python/JS snippet mentally, or use the following literal approach:

For each row y in 0..127:
  For each byte b in 0..7 (covering x = b*8 .. b*8+7):
    byte_val = 0
    For bit i in 0..7:
      x = b*8 + i
      dx = x - 32; dy = y - 64
      on_ellipse = abs(dx*dx/400.0 + dy*dy/900.0 - 1.0) < 0.12
      if on_ellipse: byte_val |= (1 << i)
    open_eyes row y, byte b = byte_val

For smile: same but center is (32, 90), only set bit if y < 90.

Output the arrays as C static const uint8_t arrays in the header. Add a comment block at the top explaining: "To swap graphics: replace the byte arrays below. Format: XBM, 64px wide × 128px tall, LSB-first, 8 bytes per row, 128 rows = 1024 bytes per image."

File structure:
```cpp
#pragma once
#include <stdint.h>

// XBM bitmap data for U8g2 drawXBM(0, 0, 64, 128, bitmap)
// Logical canvas: 64px wide x 128px tall (portrait after R1/R3 rotation)
// Format: LSB-first, 8 bytes per row, 128 rows = 1024 bytes per image
//
// To swap graphics: replace the byte arrays below.
// Each row is 8 bytes covering 64 pixels, LSB = leftmost pixel.

// OPEN_EYES: hollow ellipse ring, center (32,64), rx=20, ry=30
static const uint8_t open_eyes_bits[] PROGMEM = {
  // 1024 bytes, 8 per row x 128 rows
  ... computed values ...
};

// SMILE: upper arc, center (32,90), rx=20, ry=30, lower half empty
static const uint8_t smile_bits[] PROGMEM = {
  // 1024 bytes, 8 per row x 128 rows
  ... computed values ...
};
```

**CRITICAL:** The executor must compute the actual byte values. Write a Python script in a scratch area to generate the values if needed, then paste the resulting hex into the header. Do not write placeholder "..." — the file must contain valid byte arrays.

Python reference script to generate values (executor runs this mentally or literally):
```python
import math

def make_ellipse_xbm(cx, cy, rx, ry, upper_only=False, threshold=0.12):
    data = []
    for y in range(128):
        row = []
        for b in range(8):
            byte_val = 0
            for i in range(8):
                x = b*8 + i
                dx = x - cx
                dy = y - cy
                on = abs(dx*dx/(rx*rx) + dy*dy/(ry*ry) - 1.0) < threshold
                if upper_only and y >= cy:
                    on = False
                if on:
                    byte_val |= (1 << i)
            row.append(byte_val)
        data.append(row)
    return data

open_eyes = make_ellipse_xbm(32, 64, 20, 30)
smile = make_ellipse_xbm(32, 90, 20, 30, upper_only=True)
```

Run this (or equivalent) to produce actual byte values.
  </action>
  <verify>
    <automated>python3 -c "
import re, sys
with open('firmware/src/bitmaps.h') as f:
    content = f.read()
assert 'open_eyes_bits' in content, 'open_eyes_bits missing'
assert 'smile_bits' in content, 'smile_bits missing'
assert 'PROGMEM' in content, 'PROGMEM missing'
# Count commas as rough byte-count proxy (1024 bytes = ~1023 commas per array)
segs = content.split('open_eyes_bits')
assert len(segs) > 1
inner = segs[1].split('smile_bits')[0]
commas = inner.count(',')
assert commas > 900, f'open_eyes_bits looks too short: {commas} commas'
print('bitmaps.h looks valid')
"
</automated>
  </verify>
  <done>bitmaps.h exists with two 1024-byte PROGMEM arrays (open_eyes_bits, smile_bits) containing real computed byte values that visually match the current ellipse/arc draw calls.</done>
</task>

<task type="auto">
  <name>Task 2: Update display.cpp to use drawXBM instead of drawEllipse</name>
  <files>firmware/src/display.cpp</files>
  <action>
Replace the programmatic draw functions in display.cpp with XBM bitmap rendering.

Changes:
1. Add `#include "bitmaps.h"` after `#include "display.h"`
2. Remove the `drawEyePage` and `drawSmilePage` static functions entirely
3. Rewrite `showDisplay` to call `drawXBM(0, 0, 64, 128, bitmap)` for each display, selecting the correct bitmap based on state

New showDisplay implementation:
```cpp
void showDisplay(DisplayState state) {
    const uint8_t* bmp = (state == DisplayState::OPEN_EYES)
        ? open_eyes_bits
        : smile_bits;

    u8g2_hw.firstPage();
    do {
        u8g2_hw.drawXBM(0, 0, 64, 128, bmp);
    } while (u8g2_hw.nextPage());

    u8g2_sw.firstPage();
    do {
        u8g2_sw.drawXBM(0, 0, 64, 128, bmp);
    } while (u8g2_sw.nextPage());
}
```

Remove `setDrawColor(1)` calls — drawXBM uses foreground color by default.
Remove the `typedef void (*DrawFn)(U8G2 &)` pattern entirely since the function pointer indirection is no longer needed.

The file should have no remaining references to drawEllipse, drawEyePage, or drawSmilePage after this change.
  </action>
  <verify>
    <automated>cd /Users/ouen/slop/glorb && grep -c "drawEllipse\|drawEyePage\|drawSmilePage" firmware/src/display.cpp && echo "FAIL: old draw calls remain" || echo "PASS: old draw calls removed"; grep -c "drawXBM" firmware/src/display.cpp | grep -q "^[1-9]" && echo "PASS: drawXBM present" || echo "FAIL: drawXBM missing"; grep -q "bitmaps.h" firmware/src/display.cpp && echo "PASS: bitmaps.h included" || echo "FAIL: bitmaps.h not included"</automated>
  </verify>
  <done>display.cpp includes bitmaps.h, uses drawXBM for both displays, and contains no remaining drawEllipse or draw helper function calls. Firmware compiles without errors (pio run or equivalent).</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| bitmaps.h → flash | XBM arrays placed in PROGMEM — accessed via pgm_read_byte by U8g2 |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-fvf-01 | Tampering | bitmaps.h byte arrays | accept | Local firmware file, no network surface, user controls file |
| T-fvf-02 | Denial | PROGMEM overflow | mitigate | 2x1024=2048 bytes in flash; UNO R3 has 32KB flash — verify pio size output stays within limits |
</threat_model>

<verification>
1. `grep -n "drawXBM" firmware/src/display.cpp` — should show exactly 2 calls (one per display)
2. `grep -c "open_eyes_bits\|smile_bits" firmware/src/bitmaps.h` — should return 2
3. `pio run` (or `pio run -e uno`) from firmware/ — should compile without errors
4. Flash to hardware and verify: DEFAULT command shows ellipse ring, SMILE command shows upper arc
</verification>

<success_criteria>
- bitmaps.h exists with two fully-computed 1024-byte PROGMEM arrays
- display.cpp uses drawXBM(0, 0, 64, 128, bitmap) — no programmatic draw calls remain
- Firmware compiles (pio run succeeds)
- Graphics on hardware visually match the previous ellipse/arc shapes
- A user can swap visuals by editing only bitmaps.h
</success_criteria>

<output>
After completion, create .planning/quick/260417-fvf-replace-programmatic-u8g2-draw-calls-wit/260417-fvf-SUMMARY.md with what was done, files changed, and any notes about the XBM generation approach.
</output>
