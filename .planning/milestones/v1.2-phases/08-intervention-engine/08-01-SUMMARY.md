---
phase: 08-intervention-engine
plan: "01"
subsystem: intervention
tags: [electron, ipc, state-machine, intervention, drift, refocus]

requires:
  - phase: 07-onboarding-flow
    provides: ipcMain handler patterns, contextBridge preload structure, BrowserWindow creation patterns

provides:
  - driftCount state variable (main process)
  - escalationTimers[] registry with clearAllTimers() helper
  - trackTimeout() and trackInterval() wrappers for timer registration
  - runPath(pathId) dispatcher stub with four path stubs
  - ipcMain.handle('drift-detected') and ipcMain.handle('refocus-detected') handlers
  - window.glorb.driftDetected() and window.glorb.refocusDetected() contextBridge methods

affects:
  - 08-02-PLAN (weak path implementations use trackTimeout, trackInterval, runPath stubs)
  - 08-03-PLAN (strong path implementations use overlayWin, clearAllTimers)
  - 08-04-PLAN (CLI simulator calls drift-detected / refocus-detected IPC channels)
  - 09-routing (replaces hardcoded runPath('weak-regular') with dynamic store-based routing)

tech-stack:
  added: []
  patterns:
    - "Intervention state machine in main process only (D-09)"
    - "Timer registry pattern: push refs to escalationTimers[], clear all via clearAllTimers()"
    - "trackTimeout/trackInterval wrappers auto-register to escalationTimers array"
    - "runPath(pathId) dispatcher pattern for four intervention paths"

key-files:
  created: []
  modified:
    - main.js
    - preload.js

key-decisions:
  - "All intervention state (driftCount, timers) lives in main process per D-09"
  - "drift-detected handler hardcodes runPath('weak-regular') as temporary stub — Phase 9 wires dynamic routing"
  - "Timer refs stored in escalationTimers[] array so refocusDetected() can cancel all of them atomically"
  - "overlayWin ref declared alongside escalationTimers so clearAllTimers() handles overlay cleanup"

patterns-established:
  - "trackTimeout/trackInterval: always register timers through these wrappers, never bare setTimeout/setInterval"
  - "clearAllTimers: one call cancels all escalation state — used by refocus-detected and future path terminators"

requirements-completed:
  - INTERV-01
  - INTERV-02

duration: 15min
completed: "2026-04-18"
---

# Phase 8 Plan 01: Intervention Engine — State Machine Core Summary

**Drift counter, timer registry, and IPC entry points (drift-detected / refocus-detected) wired in main process with contextBridge exposure to renderer**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-04-18T00:00:00Z
- **Completed:** 2026-04-18T00:15:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added driftCount and escalationTimers[] state machine to main process (D-09)
- Implemented clearAllTimers(), trackTimeout(), trackInterval() helpers for safe timer lifecycle management
- Added runPath(pathId) dispatcher stub with four named path stubs ready for Plans 02 and 03 to fill
- Wired ipcMain.handle('drift-detected') and ipcMain.handle('refocus-detected') with correct semantics
- Exposed window.glorb.driftDetected() and window.glorb.refocusDetected() via contextBridge in preload.js

## Task Commits

Each task was committed atomically:

1. **Task 1: Intervention state machine in main.js** - `8de9fee` (feat)
2. **Task 2: Expose driftDetected / refocusDetected in preload.js** - `c7f9b3e` (feat)

## Files Created/Modified

- `main.js` - Added intervention state vars, timer helpers, runPath dispatcher, two ipcMain handlers
- `preload.js` - Added driftDetected and refocusDetected to contextBridge exposeInMainWorld

## Decisions Made

- Hardcoded `runPath('weak-regular')` in drift-detected handler as a temporary stub so the IPC chain is callable end-to-end immediately; Phase 9 will replace with store-based routing
- Declared `overlayWin = null` alongside escalationTimers so clearAllTimers() can handle overlay window cleanup in Plans 03/04 without requiring any refactor of clearAllTimers signature

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Worktree was reset to base commit `ecb9ba7` which placed source files at a pre-Phase 7 state (no onboarding IPC in preload.js). The plan only modifies drift/refocus concerns so the worktree's older preload.js was the correct starting point for this plan's diff. No missing functionality affected plan deliverables.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plans 02 and 03 can now implement `runWeakRegular`, `runWeakADHD`, `runStrongRegular`, `runStrongADHD` functions against the stable dispatcher convention
- `trackTimeout` and `trackInterval` are available for all path timers
- `clearAllTimers()` is available for refocus and terminate actions
- `overlayWin` ref slot is declared for Plan 03's overlay BrowserWindow logic

---
*Phase: 08-intervention-engine*
*Completed: 2026-04-18*
