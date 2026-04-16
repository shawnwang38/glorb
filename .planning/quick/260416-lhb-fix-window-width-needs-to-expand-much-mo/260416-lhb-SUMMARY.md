---
phase: quick
plan: 260416-lhb
subsystem: renderer
tags: [ui, timer, settings, svg, drag]
dependency_graph:
  requires: []
  provides: [wider-settings-panel, minutes-seconds-countdown, ring-arc-slider]
  affects: [renderer.html, renderer.css]
tech_stack:
  added: []
  patterns: [SVG pointer events drag, angle-to-value math, function hoisting]
key_files:
  created: []
  modified:
    - renderer.html
    - renderer.css
decisions:
  - startMinutes variable replaces TOTAL_SECONDS constant so duration is mutable before start
  - getTotalSeconds() used everywhere instead of cached constant so ring math stays correct after drag
  - syncHandleVisibility() called at every timerState change point (btnStart click + resetTimer)
  - formatFocusTime() kept separate from formatTime() to preserve XXh XXm in settings panel
  - SVG ring-handle placed after ring-progress so it renders on top without z-index hacks
metrics:
  duration_seconds: 420
  completed_date: "2026-04-16"
  tasks_completed: 2
  files_modified: 2
---

# Phase quick Plan 260416-lhb: Window Width + Countdown Format + Ring Slider Summary

One-liner: Expanded settings panel to 600px, switched countdown to XXm XXs, and added an orange SVG drag handle on the ring to set starting duration from 1-60 minutes.

## Tasks Completed

| # | Name | Commit | Files |
|---|------|--------|-------|
| 1 | Wider settings panel + countdown format change | c041c4f | renderer.css, renderer.html |
| 2 | Ring arc slider for starting duration | c041c4f | renderer.html |

## Changes Made

### renderer.css
- `#settings-panel` width changed from `154px` to `314px` (total expanded window: 286 + 314 = 600px)
- Added `#ring-handle` and `#ring-handle:active` cursor rules (grab/grabbing)

### renderer.html
- Static `#time-display` initial HTML updated to `25m 00s` format
- `TOTAL_SECONDS` constant removed; replaced with `let startMinutes = 25` and `getTotalSeconds()` function
- `formatTime(secs)` rewritten to return `XXm XXs` HTML spans
- `formatFocusTime(secs)` added for settings panel focus summary (XXh XXm, not yet wired to accumulated time — focus message currently static)
- `updateRing()` updated to use `getTotalSeconds()` as denominator
- `resetTimer()` updated to use `getTotalSeconds()` throughout; calls `syncHandleVisibility()`
- `btnStart` click handler calls `syncHandleVisibility()` after each state change
- `openSettings()` resize call updated from `440` to `600`
- SVG `#ring-handle` circle element added after ring-progress circle
- Full drag logic added: `angleToMinutes`, `minutesToAngle`, `minutesToHandlePos`, `updateHandlePosition`, `getSVGPoint`, pointerdown/pointermove/pointerup handlers
- `syncHandleVisibility()` function added
- `updateHandlePosition(startMinutes)` and `syncHandleVisibility()` called on page load

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

- `formatFocusTime()` is defined but the `#focus-message` paragraph still has static text "Hi there, you've focused for 0h 0m with Glorb." — accumulated session time tracking is not yet implemented. This is intentional for this plan; wiring real accumulated time is a future task.

## Threat Flags

None — changes are purely client-side renderer UI with no new IPC surface or network endpoints.

## Self-Check: PASSED

- renderer.html exists and contains all changes (verified by read)
- renderer.css exists and contains settings panel width 314px and ring-handle rules
- Commit c041c4f exists in git log
