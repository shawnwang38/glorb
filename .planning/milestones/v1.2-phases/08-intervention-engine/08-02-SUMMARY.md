---
phase: 08-intervention-engine
plan: "02"
subsystem: intervention-engine
tags: [intervention, audio, ipc, weak-path, escalation]
dependency_graph:
  requires: [08-01]
  provides: [runWeakRegular, runWeakADHD, weakTerminate, showInterventionPopup, onInterventionTerminate]
  affects: [main.js, preload.js, renderer.html]
tech_stack:
  added: [child_process.execFile, afplay macOS system sounds]
  patterns: [trackTimeout/trackInterval escalation state, IPC webContents.send to renderer]
key_files:
  modified:
    - main.js
    - preload.js
    - renderer.html
decisions:
  - "playNotes uses 300ms spacing between sequential afplay calls to produce distinct tones"
  - "constant chime in runWeakADHD uses 600ms interval loop (16 ticks over 10s) via trackTimeout"
  - "renderer popup uses inline string concatenation to avoid template literal CSP issues"
  - "stopTimer() guarded with typeof check — integration deferred to Phase 9"
metrics:
  duration: "~15 min"
  completed: "2026-04-18"
  tasks_completed: 2
  files_modified: 3
---

# Phase 08 Plan 02: Weak Escalation Paths Summary

Implements both Weak intervention paths (Weak×Regular and Weak×ADHD) in main.js, plus the renderer-side intervention-terminate event handler and popup overlay. Delivers INTERV-03 and INTERV-04 — the less-intrusive intervention tier using push notifications and macOS system audio only.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Implement runWeakRegular() in main.js | 957ec40 | main.js |
| 2 | Implement runWeakADHD() + renderer terminate listener | 95febbe | preload.js, renderer.html |

## What Was Built

### main.js additions

**`playSound(filePath)`** — fire-and-forget `afplay` wrapper via `execFile`. Silently ignores errors.

**`SND` constants** — hardcoded macOS system sound paths (Glass, Tink, Pop, Morse, Blow, Sosumi). No bundled audio files (D-01).

**`playNotes(count)`** — plays first `count` increasing notes with 300ms spacing via `trackTimeout`.

**`weakTerminate(message)`** — shared termination action: calls `win.show()`, `win.focus()`, sends `intervention-terminate` IPC event to renderer with message string.

**`runWeakRegular()`** — full Weak×Regular path (D-13):
- 30s: push "Stay focused!" + 1 chime
- Every 10s interval: ping 2 → 2 chimes; ping 3 → 3 chimes + "Last reminder — Stay focused!" push
- After ping 3: interval self-terminates, `weakTerminate('Ready to continue focusing?')` after 10s

**`runWeakADHD()`** — full Weak×ADHD path (D-14):
- 10s: push "Stay focused!" + 1 note
- Every 5s interval up to 5 pings with increasing notes (1→5)
- After ping 5: interval self-terminates, 10s constant chime loop (600ms × 16 ticks), then `weakTerminate('You lost focus.')`

### preload.js additions

**`onInterventionTerminate`** — contextBridge listener that forwards `intervention-terminate` IPC events to renderer callbacks.

### renderer.html additions

**`showInterventionPopup(message)`** — creates or reuses `#intervention-popup` overlay div with centered card, message text, and orange OK dismiss button.

**`onInterventionTerminate` handler** — calls `stopTimer()` (if defined) then `showInterventionPopup(data.message)`.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

- `stopTimer()` call in `onInterventionTerminate` handler is guarded with `typeof` check — actual timer-stop integration deferred to Phase 9 (noted in plan).

## Threat Flags

None — all sound paths are hardcoded SND constants (T-08-04 accepted), interval self-terminates at pingCount 5 (T-08-05 mitigated), message strings are hardcoded literals (T-08-06 accepted).

## Self-Check: PASSED

- main.js: contains runWeakRegular, runWeakADHD, weakTerminate, playSound, SND, playNotes, intervention-terminate, Stay focused!, Last reminder, Ready to continue focusing?, You lost focus.
- preload.js: contains onInterventionTerminate
- renderer.html: contains showInterventionPopup, intervention-popup, onInterventionTerminate
- Commits verified: 957ec40, 95febbe
- node --check main.js: exits 0
- node --check preload.js: exits 0
