# Milestones

## v1.2 Focus Intelligence (Shipped: 2026-04-19)

**Phases completed:** 3 phases, 10 plans, 7 tasks

**Key accomplishments:**

- One-liner:
- Complete 5-screen onboarding BrowserWindow (greeting → name → ASRS intro → 18 questions → completion) with Part A scoring, store writes, and 1800ms auto-dismiss
- One-liner:
- Drift counter, timer registry, and IPC entry points (drift-detected / refocus-detected) wired in main process with contextBridge exposure to renderer
- `playSound(filePath)`
- One-liner:
- Two-button strength selector (Weak/Strong) replacing three-button Auto/Weak/Strong, with a store migration guard that rewrites legacy 'auto' values to 'weak' on load

---

## v1.0 MVP (Shipped: 2026-04-17)

**Phases completed:** 3 phases, 9 plans, 7 tasks

**Key accomplishments:**

- Electron menu bar app bootstrapped: Tray icon toggles a frameless 220x360px BrowserWindow with IPC quit bridge and Cmd+Q shortcut
- Renderer layer complete: frameless window styled with #f0f0f0 background, × close button with orange hover, and quit confirmation overlay wired to window.glorb.quit() IPC bridge
- One-liner:
- One-liner:
- One-liner:
- One-liner:
- One-liner:
- Human QA confirmed all 6 SETT requirements: hamburger toggle, panel slide animation, focus summary, strength selector, Retake Test button, and panel collapse all working correctly

---
