# Phase 5: Serial Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-17
**Phase:** 05-serial-integration
**Areas discussed:** Firmware command parser, Connection lifecycle

---

## Firmware Command Parser

| Option | Description | Selected |
|--------|-------------|----------|
| Non-blocking accumulator | loop() checks Serial.available() each iteration, appends chars, processes on '\n' | |
| Blocking readStringUntil | Serial.readStringUntil('\n') blocks until newline arrives | ✓ |

**User's choice:** Blocking readStringUntil
**Notes:** Fine since loop() does nothing else.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Replace entirely | loop() becomes serial listener only. OPEN_EYES on startup, waits for commands | ✓ |
| Keep as fallback | Resume cycling if no serial data for N seconds | |

**User's choice:** Replace entirely
**Notes:** Animations are very jittery — display should stay static as much as possible. No demo cycling.

---

| Option | Description | Selected |
|--------|-------------|----------|
| OPEN_EYES on power-up | Default awake state with oval eyes | |
| SMILE on power-up (closed eyes) | Closed eyes `^ ^` arc shape | ✓ |

**User's choice:** SMILE (closed eyes) on power-up
**Notes:** User also specified visual updates to both states:
- OPEN_EYES: ovals should be dark in center (hollow ring, not filled) — use drawEllipse outline
- SMILE: `^` character too small; replace with upper ~30% of ellipse outline using drawEllipse quadrant flags, same width as OPEN_EYES. Reference glorb_icon.png.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Upper half of large circle | drawCircle with UPPER_LEFT\|UPPER_RIGHT quadrant flags | |
| Upper portion of ellipse outline | drawEllipse with quadrant flags, matching OPEN_EYES dimensions | ✓ |
| Polyline / manual arc | Draw individual points for curve | |

**User's choice:** Upper ~30% of ellipse outline
**Notes:** Use drawEllipse with U8G2_DRAW_UPPER_LEFT | U8G2_DRAW_UPPER_RIGHT. Match width of OPEN_EYES ellipse. Exact tuning: Claude's discretion.

---

## Connection Lifecycle

| Option | Description | Selected |
|--------|-------------|----------|
| Silent — app starts normally | No error, no dialog | |
| Log to console only | console.log/warn in main process | |
| Show status in UI | Small indicator that eyes are disconnected | ✓ |

**User's choice:** Show a status somewhere in UI

---

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-reconnect with polling | Scan every few seconds, reconnect automatically | ✓ |
| No reconnect — require app restart | Once disconnected, serial stays closed | |

**User's choice:** Auto-reconnect with polling (3 seconds)

---

| Option | Description | Selected |
|--------|-------------|----------|
| Small dot in settings panel | Green/red dot in hamburger settings panel, unobtrusive | ✓ |
| In the main timer window | Always visible alongside timer | |
| Claude decides | Least intrusive location | |

**User's choice:** Small dot in settings panel

---

| Option | Description | Selected |
|--------|-------------|----------|
| Every 3 seconds | Fast enough to feel responsive | ✓ |
| Every 10 seconds | More conservative delay | |
| Every 1 second | Near-instant but frequent scanning | |

**User's choice:** Every 3 seconds

---

## Claude's Discretion

- Exact pixel coordinates for SMILE arc (radius, center — tune for 64×128 portrait canvas)
- Exact dot styling (size, color, position in settings panel)
- Whether to push connection changes reactively vs poll on panel open
- platformio.ini: no changes needed

## Deferred Ideas

None — discussion stayed within phase scope.
