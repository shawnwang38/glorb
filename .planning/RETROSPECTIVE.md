# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.2 — Focus Intelligence

**Shipped:** 2026-04-19
**Phases:** 3 (7–9) | **Plans:** 10 | **Commits:** 29

### What Was Built
- Full-screen onboarding window: Glorb greeting → name entry → ASRS 1.1 (18 questions, 5-dot selector) → ADHD diagnosis persisted to store
- Intervention state machine with 4 escalation paths (Weak×Regular, Weak×ADHD, Strong×Regular, Strong×ADHD), timer registry, and `runPath()` dispatcher
- Strong path overlay windows (flash.html, vignette.html, terminate.html) with audio fade
- Unix domain socket CLI simulator (`node simulate.js drift/refocus`) for hardware-free testing
- Dynamic store-based drift routing — strength selector and hasADHD flag automatically select intervention path

### What Worked
- Parallel wave execution (09-01 and 09-02 ran concurrently on different files) — zero conflicts
- Audit step caught two bugs the individual phase verifiers missed (btn-retake unwired, stopTimer→resetTimer)
- Inline 3-line routing block (no helper function) kept drift entry points greppable and auditable
- Dropping Auto strength option simplified the selector with no UX loss

### What Was Inefficient
- Integration bugs (ONBOARD-06, INTERV-03/04) slipped through phase verification and were only caught by the milestone audit — verifiers should do cross-file linkage checks, not just file-internal checks
- Phase 7 shipped without a VERIFICATION.md — artifact gap that required manual audit to resolve
- `.planning/` in .gitignore caused planning commits to silently skip; required `git add -f` workaround

### Patterns Established
- Intervention state machine belongs in main process only — timers survive renderer window lifecycle
- Unix domain socket is the right CLI simulator transport for Electron (no port, no HTTP, local-only)
- Milestone audit is a required gate before completion — catches integration gaps individual phase verifiers miss

### Key Lessons
1. Phase verifiers check file-internal correctness; only milestone audit checks cross-file wiring. Don't skip it.
2. When two plans touch different files with no overlap, parallel execution is safe and fast.
3. Advisory gaps (name display refresh, strength-not-persisted-on-onboarding) should be triaged at audit time, not deferred silently.

### Cost Observations
- Model: Claude Sonnet 4.6 throughout
- Sessions: 2 (one main execution session + this completion session)
- Notable: Autonomous execution ran phases 7–9 with minimal intervention; only 2 lines of code needed manual gap closure

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 3 (1–3) | 9 | Initial GSD setup; sequential execution |
| v1.1 | 3 (4–6) | 8 | Hardware phases added; Arduino firmware in scope |
| v1.2 | 3 (7–9) | 10 | Autonomous execution; parallel wave; milestone audit gate |

### Top Lessons (Verified Across Milestones)

1. Vanilla JS + Electron stays fast to iterate — no build toolchain saves significant overhead per phase
2. electron-store as KV persistence handles all Glorb state needs cleanly (no DB required through v1.2)
3. Milestone audit catches cross-phase integration gaps that per-phase verification misses — always run it
