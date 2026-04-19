---
phase: 08-intervention-engine
plan: "04"
subsystem: intervention-engine
tags: [cli, ipc, unix-socket, simulate, dev-tool]
dependency_graph:
  requires: [08-01, 08-02, 08-03]
  provides: [CLI-01, CLI-02]
  affects: [main.js, simulate.js]
tech_stack:
  added: [node:net, node:fs]
  patterns: [unix-domain-socket, cli-client]
key_files:
  created: [simulate.js]
  modified: [main.js]
decisions:
  - "Used Unix domain socket at /tmp/glorb-ipc.sock per D-12 — lightweight, no HTTP overhead, dev-only"
  - "startSocketServer() dispatches only exact strings 'drift'/'refocus' — all other input gets 'unknown command' response (T-08-10 mitigated)"
  - "before-quit handler cleans up socket file to avoid EADDRINUSE on next launch"
metrics:
  duration: "~10 minutes"
  completed: "2026-04-19"
  tasks_completed: 2
  files_changed: 2
---

# Phase 08 Plan 04: CLI IPC Socket + simulate.js Summary

Unix domain socket server added to main.js and simulate.js CLI client created to trigger drift/refocus signals in the running Electron app over /tmp/glorb-ipc.sock without hardware.

## What Was Built

- **simulate.js** — standalone CLI tool (`node simulate.js drift` / `node simulate.js refocus`) that connects to the Unix socket, sends the command, and exits 0 on success or 1 on error
- **main.js socket server** — `startSocketServer()` listens at `/tmp/glorb-ipc.sock`, parses `drift`/`refocus` commands, dispatches to the same intervention logic as the renderer IPC handlers, responds `ok\n`, closes connection
- **Lifecycle management** — stale socket file removed at startup, socket file deleted on `before-quit`

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Unix socket server in main.js + simulate.js CLI client | 2c2e777 | main.js, simulate.js |
| 2 | End-to-end integration test (error-path verification) | — (no code change) | — |

## Verification Results

All automated checks passed:

- `node --check main.js` exits 0
- `node --check simulate.js` exits 0
- `node simulate.js drift` (no app running) → prints "Could not connect — is Glorb running?" and exits 1
- `node simulate.js refocus` (no app running) → exits 1
- `node simulate.js badcmd` → prints "Usage: node simulate.js <drift|refocus>" and exits 1
- `node simulate.js` (no args) → prints "Usage:" and exits 1

Happy-path test (requires running app) documented in plan — ready for manual verification with `npx electron .`.

## Deviations from Plan

None — plan executed exactly as written.

## Threat Surface

T-08-10 mitigated: socket server only dispatches on exact strings "drift" and "refocus"; all other input returns "unknown command" and socket is closed immediately. No arbitrary command execution possible.

T-08-11 accepted: `/tmp/glorb-ipc.sock` is world-accessible — dev-only tool, no production exposure.

T-08-12 accepted: socket only calls `runPath()` and `clearAllTimers()` — same capabilities as renderer IPC, no privilege escalation.

## Self-Check: PASSED

- simulate.js: FOUND
- main.js: FOUND
- 08-04-SUMMARY.md: FOUND
- commit 2c2e777: FOUND
