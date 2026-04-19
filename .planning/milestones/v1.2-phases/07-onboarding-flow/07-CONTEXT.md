# Phase 7: Onboarding Flow - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 7 delivers the full onboarding experience: a separate full-screen BrowserWindow that guides new users through Glorb greeting → name entry → 18-question ASRS 1.1 questionnaire → ADHD diagnosis → close to timer. Triggered on first launch when `onboardingComplete` is absent from store. Retakeable via "Retake Test" button in settings.

</domain>

<decisions>
## Implementation Decisions

### Window Architecture
- 800×620 centered fixed BrowserWindow — Mac-native feel, not true fullscreen
- Separate `onboarding.html` + `onboarding.css` files — mirrors main app structure
- Trigger condition: `!store.get('onboardingComplete')` — explicit flag, checked in `app.whenReady()`
- Post-completion: close onboarding window → user clicks tray to open main timer (clean separation)

### Greeting Screen
- CSS keyframe animation — radial gradient pulsing scale/opacity for "breathing" effect
- Breathing gradient adapts to dark/light theme: light mode = orange→#f0f0f0 pulse; dark mode = orange→#1a1a1a pulse
- Glorb image: glorb.png (neutral, matches main timer)
- Continue mechanic: explicit "Let's get started" button click
- Greeting text exactly per spec: "Hi, I'm Glorbus Pallidus. You can call me Glorb."

### Questionnaire UX
- 5-dot selector: 48px circles, orange fill on selected, outline on unselected — matches selection-menu.png reference
- Auto-advance after 250ms delay on selection — fluid, no extra tap
- Back button: always visible; disabled (greyed) on Q1 — per ROADMAP spec
- Progress: thin orange bar at top + "Question X of 18" text counter

### Diagnosis & Storage
- Diagnosis based on Part A only (first 6 questions) — WHO-validated clinical screening threshold
- Standard ASRS v1.1 Part A scoring: Q1-3 positive if ≥ Sometimes(2); Q4-6 positive if ≥ Often(3); ≥4 of 6 positive = likely ADHD
- Document scoring logic in `ASRS-SCORING.md` for user reference
- Store schema: `{ userName: string, hasADHD: bool, asrsAnswers: int[18], onboardingComplete: bool }`

### Claude's Discretion
- Exact animation easing curves and durations for breathing gradient
- Layout spacing/padding within onboarding screens
- Name entry input styling (placeholder text, validation, max length)
- Transition animations between questionnaire screens

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `electron-store` via IPC: `store-get` / `store-set` handlers in main.js (lines 174-175) — use same pattern
- `ipcMain.handle('resize-window')` pattern for window sizing — reference for onboarding window creation
- `renderer.css` — existing design tokens (colors, fonts) to import or mirror in onboarding.css
- `glorb.png` — neutral mascot image already in project root
- Push notification: `ipcMain.handle('notify')` already wired

### Established Patterns
- BrowserWindow creation in `createWindow()` (main.js:15-36) — follow same pattern for `createOnboardingWindow()`
- Store access always via IPC (contextIsolation: true, nodeIntegration: false)
- Dark/light theme: stored in `store.get('theme')` — check this key to adapt gradient colors
- All IPC channels registered via `ipcMain.handle` with kebab-case names

### Integration Points
- `app.whenReady()` (main.js:147) — add onboarding check here before/instead of `createWindow()`
- "Retake Test" button in `renderer.html` settings panel — wire to new `open-onboarding` IPC channel
- `preload.js` — add `openOnboarding` wrapper alongside existing `glorb` API methods

</code_context>

<specifics>
## Specific Ideas

- onboarding-ui.md in project root has user's own description of desired flow — read it during planning
- adhd-questionnaire-ASRS111.pdf in project root — read during planning to extract all 18 questions and correct scoring thresholds
- selection-menu.png in project root shows the 5-dot selector visual reference
- "breathing gradient" should feel alive — not just a color change, but a radial pulse expanding/contracting
- Onboarding should feel distinct from the main timer (bigger, more expressive, less minimal)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
