---
status: complete
phase: 07-onboarding-flow
source: [07-01-SUMMARY.md, 07-02-SUMMARY.md, 07-03-SUMMARY.md]
started: 2026-04-18T23:00:00.000Z
updated: 2026-04-18T23:10:00.000Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running Electron process. Start the app fresh. App launches without errors, tray icon appears, and the onboarding window opens automatically (since onboardingComplete is not set on a clean store).
result: pass

### 2. First-launch gate — onboarding appears
expected: On a fresh install (or after clearing the store), launching the app shows an 800×620 onboarding window centered on screen before the tray popup appears. The window is framed (has a title bar), not always-on-top.
result: pass

### 3. Greeting screen renders
expected: The first screen shows a greeting (e.g. "Hey there") with an orange breathing gradient background animation pulsing gently. A "Get Started" or "Continue" button is visible at the bottom.
result: skipped
reason: user skipped remaining tests to advance to phase 8

### 4. Name entry screen
expected: Advancing from greeting shows a text input for the user's name. Typing a name and clicking Continue stores the name and advances to the next screen.
result: skipped
reason: user skipped remaining tests to advance to phase 8

### 5. ASRS intro screen
expected: A screen explains what the questionnaire is about (ADHD screening) with a Continue button. No questions yet — just explanatory copy.
result: skipped
reason: user skipped remaining tests to advance to phase 8

### 6. ASRS 18-question questionnaire — dot selector
expected: Questions are presented one at a time with 5 response dots below ("Never" to "Very Often"). Clicking a dot selects it (turns orange) and the question auto-advances to the next after ~250ms.
result: skipped
reason: user skipped remaining tests to advance to phase 8

### 7. Back navigation during questionnaire
expected: A Back button is visible during the questionnaire. Clicking it returns to the previous question with the previous answer still selected.
result: skipped
reason: user skipped remaining tests to advance to phase 8

### 8. Completion screen — personalized message
expected: After answering all 18 questions, a completion screen appears with a personalized message using the name entered earlier (e.g. "Thanks, [Name]!"). A Continue or Done button closes the window.
result: skipped
reason: user skipped remaining tests to advance to phase 8

### 9. Auto-dismiss after completion
expected: After the completion screen appears, the onboarding window closes automatically after ~1800ms (or immediately on Continue click), and the main tray popup is visible.
result: skipped
reason: user skipped remaining tests to advance to phase 8

### 10. Retake Test button in main window
expected: The main Glorb popup window has a "Retake Test" button. Clicking it reopens the onboarding window at the first question (resets the flow from the beginning).
result: skipped
reason: user skipped remaining tests to advance to phase 8

## Summary

total: 10
passed: 2
issues: 0
pending: 0
skipped: 8

## Gaps

[none]
