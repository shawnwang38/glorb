---
phase: quick
plan: 260416-msy
type: execute
wave: 1
depends_on: []
files_modified:
  - renderer.html
  - renderer.css
autonomous: true
requirements: []

must_haves:
  truths:
    - "Sun/moon icon button appears next to hamburger in top-right area"
    - "Clicking the icon toggles between light and dark themes"
    - "Light theme: #f0f0f0 background, glorb_light.png mascot"
    - "Dark theme: #171719 background, glorb_dark.png mascot"
    - "Theme persists across app restarts via electron-store"
  artifacts:
    - path: "renderer.html"
      provides: "Theme toggle button with inline SVG sun/moon icon"
    - path: "renderer.css"
      provides: "Dark theme CSS overrides via body.dark class"
  key_links:
    - from: "btn-theme toggle click"
      to: "body.dark class + glorb-img src"
      via: "JS event listener"
    - from: "theme state"
      to: "electron-store"
      via: "window.glorb.storeSet/storeGet('theme')"
---

<objective>
Add a dark/light theme toggle button (sun/moon SVG icon) next to the hamburger button. Clicking it swaps the app between light (#f0f0f0) and dark (#171719) themes, updates the glorb mascot image between glorb_light.png and glorb_dark.png, and persists the selection via electron-store.

Purpose: User-requested aesthetic customisation without changing the app's core function.
Output: Theme toggle button wired to CSS class + image swap + persistence.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@renderer.html
@renderer.css
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add theme toggle button to HTML</name>
  <files>renderer.html</files>
  <action>
Insert a `<button id="btn-theme">` immediately BEFORE `#btn-hamburger` (which is at line ~26). The button must contain an inline SVG that shows a sun icon in dark mode and a moon icon in light mode. Use a single SVG with two `<g>` elements — `#icon-sun` and `#icon-moon` — toggled by display:none. Initial state is light mode so `#icon-moon` is visible (moon = "switch to dark") and `#icon-sun` is hidden.

Sun SVG (16×16, currentColor): circle cx=8 cy=8 r=3.5 with 8 short ray lines radiating outward.
Moon SVG (16×16, currentColor): crescent made from two overlapping circles — path d="M11 4a6 6 0 1 0 0 8 4.5 4.5 0 1 1 0-8z".

Also update `glorb-img` src attribute from `glorb.png` to `glorb_light.png` since the file has been renamed.

Also update the onerror handler on `glorb-img` to reference the correct fallback (remove the glorb.png reference, keep the placeholder logic).
  </action>
  <verify>Open renderer.html — btn-theme button exists before btn-hamburger; glorb-img src is glorb_light.png</verify>
  <done>Button present in DOM with sun+moon SVG groups; glorb-img points to glorb_light.png</done>
</task>

<task type="auto">
  <name>Task 2: Add dark theme CSS and style the toggle button</name>
  <files>renderer.css</files>
  <action>
Append to the END of renderer.css (do not modify existing rules):

1. **Theme toggle button** — mirror the hamburger button style exactly (same position logic, but placed to its left):
```css
#btn-theme {
  position: absolute;
  top: 8px;
  right: 44px; /* 8px gap + 28px hamburger + 8px gap = 44px from right */
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  z-index: 10;
  transition: background 150ms ease;
  padding: 0;
  color: #1a1a1a;
}
#btn-theme:hover {
  background: rgba(0, 0, 0, 0.07);
}
#btn-theme svg {
  width: 16px;
  height: 16px;
}
```

2. **Dark theme overrides** — applied via `body.dark` class:
```css
body.dark,
body.dark #app,
body.dark #settings-panel,
body.dark #quit-overlay {
  background: #171719;
  color: #f0f0f0;
}

body.dark #btn-close,
body.dark #btn-theme,
body.dark .hamburger-bars span {
  color: rgba(255, 255, 255, 0.6);
}

body.dark #btn-close:hover,
body.dark #btn-theme:hover,
body.dark #btn-hamburger:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #f0f0f0;
}

body.dark .hamburger-bars span {
  background: rgba(255, 255, 255, 0.7);
}

body.dark #time-display,
body.dark .time-nums,
body.dark #focus-message,
body.dark .settings-label {
  color: #f0f0f0;
}

body.dark .settings-label {
  color: rgba(255, 255, 255, 0.5);
}

body.dark #ring-progress {
  stroke: #f0f0f0;
}

body.dark circle[stroke="rgba(0, 0, 0, 0.15)"] {
  stroke: rgba(255, 255, 255, 0.15);
}

body.dark #ring-handle {
  stroke: #171719;
}

body.dark #glorb-vignette {
  background: radial-gradient(circle, transparent 40%, #171719 75%);
}

body.dark #btn-start {
  background: #f0f0f0;
  color: #171719;
  border-color: #f0f0f0;
}

body.dark #btn-start:hover {
  background: #d4d4d4;
  border-color: #d4d4d4;
}

body.dark #btn-quit {
  background: #f0f0f0;
  color: #171719;
  border-color: #f0f0f0;
}

body.dark #btn-quit:hover {
  background: #d4d4d4;
  border-color: #d4d4d4;
}

body.dark #btn-keep {
  color: #f0f0f0;
  border-color: rgba(255, 255, 255, 0.25);
}

body.dark #btn-keep:hover {
  background: rgba(255, 255, 255, 0.08);
}

body.dark .strength-btn {
  color: #f0f0f0;
  border-color: rgba(255, 255, 255, 0.2);
}

body.dark .strength-btn:not(.active):hover {
  background: rgba(255, 255, 255, 0.06);
}

body.dark .strength-btn.active {
  background: #f0f0f0;
  color: #171719;
  border-color: #f0f0f0;
}

body.dark #user-name:hover {
  border-bottom-color: #FF6B35;
}

body.dark #name-input {
  color: #f0f0f0;
}

body.dark #glorb-placeholder {
  background: #333336;
}
```
  </action>
  <verify>renderer.css contains #btn-theme rule and body.dark rules at the end</verify>
  <done>All dark overrides present; no existing rules modified</done>
</task>

<task type="auto">
  <name>Task 3: Wire theme toggle JS with persistence</name>
  <files>renderer.html</files>
  <action>
Inside the `<script>` block in renderer.html, append the following section AFTER the existing "Load saved name and focus time on startup" block (near the end of the script, before the closing `</script>`):

```js
// === Theme Toggle ===

const btnTheme = document.getElementById('btn-theme')
const iconSun = document.getElementById('icon-sun')
const iconMoon = document.getElementById('icon-moon')
const glorb = document.getElementById('glorb-img')

let isDark = false

function applyTheme(dark) {
  isDark = dark
  if (dark) {
    document.body.classList.add('dark')
    glorb.src = 'glorb_dark.png'
    iconSun.style.display = 'block'
    iconMoon.style.display = 'none'
  } else {
    document.body.classList.remove('dark')
    glorb.src = 'glorb_light.png'
    iconSun.style.display = 'none'
    iconMoon.style.display = 'block'
  }
}

btnTheme.addEventListener('click', () => {
  applyTheme(!isDark)
  window.glorb.storeSet('theme', isDark ? 'dark' : 'light')
})

// Restore theme on load
window.glorb.storeGet('theme', 'light').then(savedTheme => {
  applyTheme(savedTheme === 'dark')
})
```

Note: The initial `glorb-img` src is `glorb_light.png` (set in Task 1). The `applyTheme` function manages all src swaps so the onerror handler on the img tag only needs to handle the placeholder logic (already present — no change needed there).
  </action>
  <verify>App launches, clicking sun/moon button toggles background between #f0f0f0 and #171719, glorb image swaps, theme survives app restart</verify>
  <done>Theme toggle functional; dark/light state persisted via electron-store key "theme"</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| renderer→main | IPC via window.glorb.storeSet/storeGet (already established) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-msy-01 | Tampering | electron-store theme key | accept | Value is only "light"/"dark"; any unexpected value defaults to light via applyTheme(false) |
</threat_model>

<verification>
1. `npm start` — app window opens, moon icon visible in top right area next to hamburger
2. Click moon icon — background goes dark (#171719), glorb_dark.png loads, sun icon appears
3. Click sun icon — reverts to light (#f0f0f0), glorb_light.png loads, moon icon appears
4. Close and reopen app — theme is preserved
5. Settings panel text, buttons, ring all correctly styled in both themes
</verification>

<success_criteria>
- Sun/moon toggle button renders correctly in both themes with no layout shift to existing controls
- All UI elements (ring, text, buttons, settings panel) are legible in dark mode
- Theme preference survives app restarts via electron-store
- No regressions: hamburger, close button, timer, settings panel continue to function
</success_criteria>

<output>
After completion, create `.planning/quick/260416-msy-add-dark-light-theme-toggle-sun-moon-ico/260416-msy-SUMMARY.md`
</output>
