---
phase: 07-onboarding-flow
plan: "01"
subsystem: onboarding
tags: [css, asrs, onboarding, scoring, dark-mode, animation]
dependency_graph:
  requires: []
  provides:
    - ASRS-SCORING.md (18-question text + Part A scoring reference)
    - onboarding.css (all visual component classes for onboarding window)
  affects:
    - plan 07-02 (imports onboarding.css, references ASRS question text)
tech_stack:
  added: []
  patterns:
    - vanilla CSS with section comments matching UI-SPEC component inventory
    - dark mode via body.dark selector (mirrors renderer.css pattern)
    - CSS keyframe animation for breathing gradient
    - prefers-reduced-motion media query for accessibility
key_files:
  created:
    - ASRS-SCORING.md
    - onboarding.css
  modified:
    - .gitignore (added !ASRS-SCORING.md exception)
decisions:
  - Added !ASRS-SCORING.md exception to .gitignore — project reference docs should be tracked
metrics:
  duration: "3 min"
  completed: "2026-04-18"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 1
---

# Phase 07 Plan 01: ASRS Scoring Reference and Onboarding CSS — Summary

**One-liner:** ASRS v1.1 18-question reference with Part A 4-of-6 threshold scoring and full onboarding CSS (breathing gradient, dot selector, dark mode, screen transitions).

---

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create ASRS-SCORING.md | 659269b | ASRS-SCORING.md, .gitignore |
| 2 | Create onboarding.css | 4eff970 | onboarding.css |

---

## What Was Built

### ASRS-SCORING.md

Full text of all 18 ASRS v1.1 questions organized as Part A (Q1–Q6, screening) and Part B (Q7–Q18, supplementary). Documents the scoring algorithm: Q1–Q3 positive if answer ≥ 2 (Sometimes), Q4–Q6 positive if answer ≥ 3 (Often), `hasADHD = (positiveCount >= 4)`. Includes a JavaScript scoring function example, full store schema, and WHO references.

### onboarding.css

All visual components for the 800×620 onboarding window:

- **Base/Reset** — 16px body, Inter font stack, dark mode body.dark switch
- **Breathing gradient** — `.breathing-bg` with `@keyframes breathe` (3.6s ease-in-out, scale 0.85↔1.15, opacity 0.55↔0.80), dark mode radial variant, prefers-reduced-motion static fallback
- **Screen system** — `.screen` / `.screen.active` display toggle; `.screen-exit` / `.screen-enter` 120ms fade transitions
- **Typography helpers** — `.text-display` (28px/600), `.text-heading` (20px/600), `.text-body` (16px/400), `.text-label` (14px/400), `.text-muted` with dark overrides
- **Progress bar** — 3px orange fill at absolute top, 200ms width transition, dark mode track
- **Response dots** — 48px circles, orange fill on `.selected`, hover border-color, `:focus-visible` ring, dark mode border
- **Dot selector** — flex row with 20px gap, labels beneath, dark mode label colors
- **Primary button** — orange #FF6B35 background, hover #e55a24, 0.4 opacity disabled
- **Text input** — 48px height, 1.5px border, focus #FF6B35 border, placeholder, dark mode overrides
- **Back button** — transparent, muted color, 0.35 opacity disabled with pointer-events: none, dark mode
- **Screen layouts** — dedicated layout classes for all 5 screens (greeting, name entry, intro, question, completion)

---

## Deviations from Plan

None — plan executed exactly as written.

Minor addition: added `.gitignore` exception `!ASRS-SCORING.md` to allow the reference document to be tracked in git (the existing `*.md` rule excluded all markdown files, but this is a functional project artifact that downstream plans depend on).

---

## Known Stubs

None — both files are complete standalone deliverables with no placeholder or TODO content.

---

## Threat Flags

None — both files are static local assets (no network endpoints, no auth paths, no secrets).

---

## Self-Check: PASSED

- [x] ASRS-SCORING.md exists at `/Users/ouen/slop/glorb/ASRS-SCORING.md`
- [x] onboarding.css exists at `/Users/ouen/slop/glorb/onboarding.css`
- [x] Commit 659269b exists (Task 1)
- [x] Commit 4eff970 exists (Task 2)
- [x] 18 questions verified (`grep -c "^[0-9]\+\." ASRS-SCORING.md` → 18)
- [x] `hasADHD = (positiveCount >= 4)` present in ASRS-SCORING.md
- [x] `@keyframes breathe` present in onboarding.css
- [x] All 11 acceptance criteria for onboarding.css verified
