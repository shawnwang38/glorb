---
phase: quick
plan: 260416-mjb
type: execute
wave: 1
depends_on: []
files_modified:
  - renderer.html
  - renderer.css
  - preload.js
  - main.js
autonomous: true
requirements: []
must_haves:
  truths:
    - "Strength buttons (Auto/Weak/Strong) are clickable and only one is active at a time"
    - "User name in focus summary shows underline on hover and is clickable to edit"
    - "User name persists across app restarts via electron-store or localStorage"
    - "Total focus time persists and accumulates correctly across sessions"
    - "A completed focus session (natural expiry) adds full session duration to focus time"
    - "An early-ended focus session (Unfocus button) adds only the elapsed time to focus time"
  artifacts:
    - path: renderer.html
      provides: "Strength button click handlers, name inline-edit, timer tracking logic"
    - path: renderer.css
      provides: "Strength btn cursor:pointer, name hover underline styles"
    - path: preload.js
      provides: "store IPC bridge (get/set)"
    - path: main.js
      provides: "IPC handlers for store-get and store-set using electron-store"
  key_links:
    - from: renderer.html (strength buttons)
      to: CSS .active class
      via: "JS click handler removes .active from siblings, adds to clicked"
    - from: renderer.html (focus time display)
      to: electron-store
      via: "window.glorb.storeGet('focusTime') on load, storeSet on session end"
    - from: renderer.html (userName span)
      to: electron-store
      via: "window.glorb.storeGet('userName') on load, storeSet on name change"
---

<objective>
Wire up the settings panel's interactive elements and add persistence for user name and accumulated focus time.

Purpose: The settings panel currently renders static UI. This plan makes it fully interactive: strength buttons become a proper radio-group, the user name becomes an editable field, and focus time accumulates durably via electron-store.
Output: renderer.html, renderer.css, preload.js, main.js updated. App persists userName and focusTime across restarts.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add electron-store and wire IPC for persistence</name>
  <files>main.js, preload.js, package.json</files>
  <action>
Install electron-store: run `npm install electron-store` in the project root (cwd: /Users/ouen/slop/glorb).

In main.js:
- Add `const Store = require('electron-store')` and `const store = new Store()` at the top.
- Add two ipcMain.handle calls:
  - `'store-get'` handler: `(event, key, defaultVal) => store.get(key, defaultVal)`
  - `'store-set'` handler: `(event, key, value) => { store.set(key, value) }`

In preload.js, add two methods to the contextBridge glorb object:
  - `storeGet: (key, defaultVal) => ipcRenderer.invoke('store-get', key, defaultVal)`
  - `storeSet: (key, value) => ipcRenderer.invoke('store-set', key, value)`

No other changes to main.js or preload.js.
  </action>
  <verify>npm start — app opens without errors in the console. `window.glorb.storeGet` and `window.glorb.storeSet` are available in DevTools console.</verify>
  <done>electron-store installed, IPC handlers registered, bridge methods exposed.</done>
</task>

<task type="auto">
  <name>Task 2: Strength button radio behavior + name inline edit + CSS polish</name>
  <files>renderer.html, renderer.css</files>
  <action>
### renderer.css changes

1. Change `.strength-btn` `cursor` from `cursor: default` to `cursor: pointer`.
2. Add a hover state for non-active strength buttons:
   ```css
   .strength-btn:not(.active):hover {
     background: rgba(0, 0, 0, 0.06);
   }
   ```
3. Add styles for the editable name span:
   ```css
   #user-name {
     cursor: pointer;
     border-bottom: 1px solid transparent;
     transition: border-color 150ms ease;
   }
   #user-name:hover {
     border-bottom-color: #FF6B35;
   }
   ```
4. Add an inline input style for when the name is being edited:
   ```css
   #name-input {
     display: none;
     background: transparent;
     border: none;
     border-bottom: 1.5px solid #FF6B35;
     font-family: inherit;
     font-size: inherit;
     font-weight: inherit;
     color: inherit;
     outline: none;
     width: 8ch;
     max-width: 120px;
     padding: 0;
     line-height: inherit;
   }
   #name-input.editing {
     display: inline;
   }
   ```

### renderer.html changes

1. In `#focus-message`, replace the static `<span class="orange">Ouen</span>` with:
   ```html
   <span id="user-name" class="orange" title="Click to edit name">Ouen</span><input id="name-input" type="text" maxlength="30" autocomplete="off" spellcheck="false">
   ```

2. In the `<script>` block, after the Phase 3 settings panel toggle section, add a new section `// === Persistence + Settings Interactivity ===` with the following logic:

**Strength buttons — radio group:**
```js
const strengthBtns = document.querySelectorAll('.strength-btn[data-strength]')
strengthBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    strengthBtns.forEach(b => b.classList.remove('active'))
    btn.classList.add('active')
    const val = btn.dataset.strength
    window.glorb.storeSet('strength', val)
  })
})
// Restore saved strength on load
window.glorb.storeGet('strength', 'auto').then(savedStrength => {
  strengthBtns.forEach(b => b.classList.remove('active'))
  const target = document.querySelector(`.strength-btn[data-strength="${savedStrength}"]`)
  if (target) target.classList.add('active')
})
```

**User name inline edit:**
```js
const userNameEl = document.getElementById('user-name')
const nameInput = document.getElementById('name-input')

function commitName() {
  const newName = nameInput.value.trim() || userNameEl.textContent
  userNameEl.textContent = newName || 'You'
  nameInput.classList.remove('editing')
  nameInput.style.display = 'none'
  userNameEl.style.display = ''
  window.glorb.storeSet('userName', userNameEl.textContent)
  // Refresh greeting
  updateFocusMessage()
}

userNameEl.addEventListener('click', () => {
  nameInput.value = userNameEl.textContent
  nameInput.style.display = 'inline'
  nameInput.classList.add('editing')
  userNameEl.style.display = 'none'
  nameInput.focus()
  nameInput.select()
})

nameInput.addEventListener('blur', commitName)
nameInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') { e.preventDefault(); nameInput.blur() }
  if (e.key === 'Escape') {
    nameInput.value = userNameEl.textContent
    nameInput.blur()
  }
})

// Load saved name
window.glorb.storeGet('userName', 'Ouen').then(name => {
  userNameEl.textContent = name
  updateFocusMessage()
})
```

**Focus time accumulation:**

Add a variable `let sessionStartTime = null` near the top of the script (alongside `let timerState`).

In `btnStart.addEventListener('click', ...)`:
- When `timerState === 'idle'` (about to start): set `sessionStartTime = Date.now()`
- When `timerState === 'running'` (Unfocus / early end): compute elapsed seconds = `Math.round((Date.now() - sessionStartTime) / 1000)`, then call `addFocusTime(elapsed)`. Then call `resetTimer()`.

In the `tick()` function, when `remaining <= 0` (natural completion): compute elapsed = `getTotalSeconds()` (the full session). Call `addFocusTime(elapsed)` before `resetTimer()`.

Add these helpers:
```js
function addFocusTime(seconds) {
  window.glorb.storeGet('focusTime', 0).then(current => {
    const updated = (current || 0) + seconds
    window.glorb.storeSet('focusTime', updated)
    updateFocusMessage()
  })
}

function updateFocusMessage() {
  window.glorb.storeGet('focusTime', 0).then(secs => {
    document.getElementById('focus-time').textContent = formatFocusTime(secs || 0)
  })
  window.glorb.storeGet('userName', 'Ouen').then(name => {
    userNameEl.textContent = name
  })
}
```

On page load, call `updateFocusMessage()` to populate from store.

Remove the hardcoded `04h 16m` from the `#focus-time` span — change it to `00h 00m` as a placeholder until the store loads.
  </action>
  <verify>
1. Open app. Settings panel opens via hamburger.
2. Click Weak — Weak becomes dark/active, Auto deactivates.
3. Click Glorb name — name becomes an input. Type a new name, press Enter — name updates.
4. Close and reopen app — new name still shows.
5. Start a 1-minute timer, wait a few seconds, click Unfocus — focus time increments by elapsed seconds (not 0, not full duration).
6. Start timer, let it expire — focus time increments by full session duration.
  </verify>
  <done>
- Strength buttons clickable with single-selection enforced; selection persists.
- Name is hover-underlined, click-to-edit with Enter/Escape/blur commit; persists across restarts.
- Focus time accumulates: elapsed-only for early exit, full duration for natural completion.
- Focus time and name survive app restart.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| renderer → main (IPC) | Renderer sends store keys/values; main writes to disk |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-mjb-01 | Tampering | store-set IPC handler | accept | App is local-only, single-user; no network exposure; data is non-sensitive (name, focus time) |
| T-mjb-02 | Information Disclosure | electron-store file on disk | accept | Stores only non-sensitive preferences; no passwords or PII beyond first name |
</threat_model>

<verification>
- `npm start` launches without errors
- Settings panel strength buttons respond to clicks with correct active-state toggling
- Name edit flow: click → input appears → type → Enter → span updates → persists on restart
- Focus time increments correctly for both early-end and natural-completion paths
- `window.glorb.storeGet` and `window.glorb.storeSet` available in DevTools
</verification>

<success_criteria>
- Strength selector is a functional radio group (pick-one) with persistence
- User name supports hover-underline + click-to-edit + Enter/Escape/blur commit + persistence
- Focus time accumulates elapsed time on Unfocus and full duration on natural timer completion
- All three data points (strength, userName, focusTime) survive app restart
</success_criteria>

<output>
After completion, create `.planning/quick/260416-mjb-make-the-settings-buttons-clickable-the-/260416-mjb-SUMMARY.md`
</output>
