# Phase 4: Dual Display Firmware - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Rebuild the firmware display layer to drive two SSD1306 OLEDs simultaneously — Display 1 on hardware I2C (A4/A5), Display 2 on software I2C (A2/A3) — each showing one eye. A single `showDisplay(DisplayState)` call updates both displays. The two states are OPEN_EYES (centered oval on each) and SMILE (centered ^ arc on each).

Prior art: quick task 260416-w1c built a single-display layer (now deleted from worktree) using U8g2. Phase 4 replaces it with a two-display architecture.

</domain>

<decisions>
## Implementation Decisions

### Display Orientation
- Both displays are physically portrait (pins on top, wide display face-on) but at opposite rotations
- Display 1 (A4/A5 hardware I2C): physically tilted 90° CCW → correct with U8G2_R1 (90° CW software rotation)
- Display 2 (A2/A3 software I2C): physically tilted 90° CW → correct with U8G2_R3 (270° CW software rotation)
- After correction, both displays effectively have a 64×128 portrait drawable canvas
- Exact rotation values must be verified empirically after hardware upload

### OPEN_EYES Graphics
- Primitive: `drawEllipse` — true oval shape, matches ROADMAP "oval" description
- Dimensions: ~40w × 60h, centered on the 64×128 portrait canvas (~x=32, y=64)
- Style: filled (bold, visible at OLED scale)
- Same coordinates on both displays (identical portrait canvas)

### SMILE Graphics
- Draw method: `"^"` character drawn with logisoso32 font (32px, already a dependency)
- Both displays use same character — identical closed-eye smile on each
- Centered on 64×128 portrait canvas — exact x/y to be tuned during implementation
- logisoso32 is already listed in platformio.ini dependency

### Code Architecture
- Two separate U8g2 instances in display.cpp: `u8g2_hw` (hardware I2C) and `u8g2_sw` (software I2C)
- `displaySetup()` calls `.begin()` on both instances
- `showDisplay(DisplayState)` clears, draws, and sends buffer to both instances in one call
- SW I2C constructor: `U8G2_SSD1306_128X64_NONAME_F_SW_I2C(U8G2_R3, /*clock=*/A3, /*data=*/A2, U8X8_PIN_NONE)`
- HW I2C constructor: `U8G2_SSD1306_128X64_NONAME_F_HW_I2C(U8G2_R1, U8X8_PIN_NONE)`

### Claude's Discretion
- Exact pixel coordinates for oval and ^ arc (tune for visual centering on portrait 64×128)
- Whether to call `u8g2_hw` or `u8g2_sw` first in showDisplay (no specified order)
- platformio.ini: no changes needed beyond existing U8g2 dep (SW I2C is built into U8g2)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- U8g2 library (olikraus/U8g2@^2.35.7) — already in platformio.ini dep, no additions needed
- DisplayState enum (OPEN_EYES, SMILE) — keep interface identical
- displaySetup() / showDisplay() function signatures — keep for serial integration compatibility

### Established Patterns
- Full-buffer mode (F variant constructors) — already chosen, keep
- U8g2 draw API: drawEllipse, drawStr, setFont, clearBuffer, sendBuffer
- SW I2C in U8g2 uses `U8G2_SSD1306_128X64_NONAME_F_SW_I2C(rotation, clock_pin, data_pin, reset)`
- Arduino pin numbers for analog: A2=16, A3=17 on UNO R3

### Integration Points
- Phase 5 (Serial Integration) will call showDisplay() from a serial command handler — keep same API
- main.cpp demo loop can remain for standalone hardware verification before serial integration
- platformio.ini: env:uno, atmelavr platform — no changes needed

</code_context>

<specifics>
## Specific Ideas

- Displays physically oriented as portrait eyes in the Glorb device enclosure
- Display 1 (A4/A5): CCW 90° physical rotation → U8G2_R1
- Display 2 (A2/A3): CW 90° physical rotation → U8G2_R3
- User must rewire Display 2 SDA/SCL from A4/A5 to A2/A3 before upload (noted in STATE.md blockers)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
