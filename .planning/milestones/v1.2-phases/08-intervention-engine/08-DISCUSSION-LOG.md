# Phase 8: Intervention Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-18
**Phase:** 08-intervention-engine
**Areas discussed:** Audio, Strong path visuals, Escalation state location, CLI IPC mechanism

---

## Audio

| Option | Description | Selected |
|--------|-------------|----------|
| Real audio files | Bundle .mp3/.wav chime files with the app | |
| macOS system sounds | Use `afplay` with system sound files | ✓ |
| Skip/stub | Log only, no real audio for now | |

**User's choice:** macOS system sounds  
**Notes:** Use `afplay` to play system sounds. No bundled audio files.

---

## Strong Path Visuals

| Option | Description | Selected |
|--------|-------------|----------|
| CSS overlay on existing window | Apply vignette/flash as DOM overlay on 286px popup | |
| New full-screen BrowserWindow | Separate always-on-top window covering full screen | ✓ |

**User's choice:** New full-screen BrowserWindow  
**Notes:** Existing window is 286×468 — too small for full-screen effects. Overlay window covers full screen.

---

## Escalation State Location

| Option | Description | Selected |
|--------|-------------|----------|
| Renderer | Drift counter and timers in renderer.js | |
| Main process | Drift counter and timers in main.js | ✓ |

**User's choice:** Main process  
**Notes:** More reliable — renderer can close/reopen; main process always running.

---

## CLI IPC Mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Named pipe (Unix socket) | Lightweight, dev-only socket | ✓ (Claude's discretion) |
| HTTP server | Express server in main | |
| Electron remote | electron-connect or similar | |

**User's choice:** Claude's discretion — it's temporary for testing  
**Notes:** Claude chose Unix domain socket at `/tmp/glorb-ipc.sock` — lightweight and no external dependencies.

---

## Deferred Ideas

- Strength/hasADHD routing → Phase 9
- Eye-tracking / app-tracking auto-drift detection → post-v1.2
