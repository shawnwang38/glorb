# Phase 9: Focus Wiring - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 9 wires the `strength` selector and `hasADHD` store value to route every `driftDetected()` call to the correct intervention path. This includes:
1. Removing the "Auto" strength option from the UI and store defaults
2. Replacing the two hardcoded `runPath('weak-regular')` calls in main.js with dynamic path selection based on store values

</domain>

<decisions>
## Implementation Decisions

### Auto Strength Removal
- Remove the "Auto" `<button>` from the strength selector in `renderer.html`
- Default stored strength becomes `'weak'` (not `'auto'`)
- When loading saved strength, if value is `'auto'` (legacy), treat as `'weak'`

### Path Selection
- Inline in both `drift-detected` IPC handler and socket server `drift` branch
- Logic: `const strength = store.get('strength', 'weak'); const hasADHD = store.get('hasADHD', false); const pathId = \`${strength === 'strong' ? 'strong' : 'weak'}-${hasADHD ? 'adhd' : 'regular'}\``
- No helper function extraction needed

### Claude's Discretion
- Exact placement of legacy 'auto' guard in renderer (e.g., fallback in storeGet callback or remove the stored value on load)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `store.get('strength', 'auto')` — synchronous in main process; change default to `'weak'`
- `store.get('hasADHD', false)` — already the right type
- `runPath(pathId)` in main.js — accepts `'weak-regular'`, `'weak-adhd'`, `'strong-regular'`, `'strong-adhd'`

### Established Patterns
- `store.get(key, default)` — synchronous, called directly in ipcMain handlers
- All escalation state stays in main process (D-09 from Phase 8)

### Integration Points
- `main.js` line 452: socket server drift branch — `runPath('weak-regular')` → dynamic
- `main.js` line 572: `ipcMain.handle('drift-detected')` → dynamic
- `renderer.html`: strength buttons — remove `data-strength="auto"` button; update fallback default

</code_context>

<specifics>
## Specific Ideas

- Remove the "Auto" button so the selector shows only "Weak" and "Strong"
- Legacy guard: if `savedStrength === 'auto'`, treat as `'weak'` and write `'weak'` to store

</specifics>

<deferred>
## Deferred Ideas

- "Auto" mode (auto-select Weak/Strong based on ADHD profile) — post-v1.2 (APP-05)
- Eye-tracking / app-tracking to auto-call driftDetected() — post-v1.2

</deferred>

---

*Phase: 09-focus-wiring*
*Context gathered: 2026-04-18*
