const { app, BrowserWindow, Tray, nativeImage, ipcMain, globalShortcut, Notification } = require('electron')
const path = require('path')
const Store = require('electron-store')
const { SerialPort } = require('serialport')
const store = new Store()

let tray = null
let win = null
let onboardingWin = null

// Phase 8 — Intervention state machine (D-09: all state in main process)
let driftCount = 0
const escalationTimers = []  // D-11: store all setTimeout/setInterval refs here
let overlayWin = null        // shared ref for overlay BrowserWindow (Plans 03/04)

function clearAllTimers () {
  while (escalationTimers.length) {
    const ref = escalationTimers.pop()
    if (ref && ref._isInterval) clearInterval(ref)
    else clearTimeout(ref)
  }
  if (overlayWin && !overlayWin.isDestroyed()) {
    overlayWin.close()
    overlayWin = null
  }
}

function trackTimeout (fn, ms) {
  const id = setTimeout(fn, ms)
  escalationTimers.push(id)
  return id
}
function trackInterval (fn, ms) {
  const id = setInterval(fn, ms)
  id._isInterval = true
  escalationTimers.push(id)
  return id
}

// Phase 8 — Path dispatcher (D-10: called from IPC handlers and CLI socket)
// pathId: 'weak-regular' | 'weak-adhd' | 'strong-regular' | 'strong-adhd'
// Implementations filled in by Plans 02 and 03.
function runPath (pathId) {
  switch (pathId) {
    case 'weak-regular':   return runWeakRegular()
    case 'weak-adhd':      return runWeakADHD()
    case 'strong-regular': return runStrongRegular()
    case 'strong-adhd':    return runStrongADHD()
    default:
      console.warn('[intervention] unknown pathId:', pathId)
  }
}

function runWeakRegular ()  { /* Plan 02 */ }
function runWeakADHD ()     { /* Plan 02 */ }
function runStrongRegular () { /* Plan 03 */ }
function runStrongADHD ()   { /* Plan 03 */ }

// Serial connection state (D-10: main process only)
let serialPort = null
let isConnected = false
let reconnectTimer = null

function createWindow () {
  win = new BrowserWindow({
    width: 286,
    height: 468,
    show: false,
    frame: false,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  win.loadFile('renderer.html')

  win.on('blur', () => {
    win.hide()
  })
}

function createTray () {
  const trayIcon = nativeImage
    .createFromPath(path.join(__dirname, 'glorb_icon.png'))
    .resize({ width: 18, height: 18 })
  trayIcon.setTemplateImage(true)

  tray = new Tray(trayIcon)

  tray.on('click', () => {
    if (win.isVisible()) {
      win.hide()
    } else {
      const bounds = tray.getBounds()
      win.setPosition(
        Math.round(bounds.x + bounds.width / 2 - 143),
        Math.round(bounds.y + bounds.height)
      )
      win.show()
      win.focus()
    }
  })
}

function createOnboardingWindow () {
  onboardingWin = new BrowserWindow({
    width: 800,
    height: 620,
    show: true,
    frame: true,
    resizable: false,
    center: true,
    alwaysOnTop: false,
    skipTaskbar: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  onboardingWin.loadFile('onboarding.html')

  onboardingWin.on('closed', () => {
    onboardingWin = null
  })
}

// D-11: Arduino VID/PIDs — genuine (0x2341), CH340 clone (0x1A86), Arduino.org (0x2A03)
const ARDUINO_VIDS = new Set(['2341', '1a86', '2a03'])

async function findArduinoPort() {
  const ports = await SerialPort.list()
  // Primary: match by vendorId
  let match = ports.find(p =>
    p.vendorId && ARDUINO_VIDS.has(p.vendorId.toLowerCase())
  )
  // Fallback: match by manufacturer/description string
  if (!match) {
    match = ports.find(p => {
      const desc = ((p.manufacturer || '') + (p.friendlyName || '')).toLowerCase()
      return desc.includes('arduino') || desc.includes('ch340')
    })
  }
  return match ? match.path : null
}

function notifyConnectionState() {
  // Push state to renderer if window exists
  if (win && !win.isDestroyed()) {
    win.webContents.send('serial-status-changed', { connected: isConnected })
  }
}

function startReconnectLoop() {
  if (reconnectTimer) return  // already polling
  reconnectTimer = setInterval(async () => {
    const portPath = await findArduinoPort()
    if (isConnected) {
      // Detect unplug: port no longer listed
      if (!portPath) {
        isConnected = false
        if (serialPort) { serialPort.destroy(); serialPort = null }
        notifyConnectionState()
      }
    } else {
      if (portPath) openPort(portPath)
    }
  }, 3000)  // D-14: poll every 3 seconds
}

function openPort(portPath) {
  if (serialPort && serialPort.isOpen) return

  serialPort = new SerialPort({ path: portPath, baudRate: 115200 }, (err) => {
    if (err) {
      // D-12/D-16: silent failure — no dialogs
      isConnected = false
      notifyConnectionState()
      startReconnectLoop()
      return
    }
    isConnected = true
    notifyConnectionState()
    serialPort.write('DEFAULT\n')  // initialize displays to open eyes on connect
  })

  serialPort.on('close', () => {
    // D-15: unexpected close → start polling
    isConnected = false
    serialPort = null
    notifyConnectionState()
    startReconnectLoop()
  })

  serialPort.on('error', (err) => {
    // D-15/D-16: silent error — start polling
    isConnected = false
    serialPort = null
    notifyConnectionState()
    startReconnectLoop()
  })
}

async function initSerial() {
  // D-13: attempt auto-detect on startup
  const portPath = await findArduinoPort()
  if (portPath) openPort(portPath)
  startReconnectLoop()  // D-14/D-15: always poll for connect and disconnect
}

app.dock.hide()
app.setActivationPolicy('accessory')

app.whenReady().then(async () => {
  createWindow()
  createTray()
  initSerial()

  globalShortcut.register('Command+Q', () => {
    app.quit()
  })

  // ONBOARD-01: show onboarding on first launch if no profile yet
  const onboardingComplete = store.get('onboardingComplete', false)
  if (!onboardingComplete) {
    createOnboardingWindow()
  }
})

app.on('window-all-closed', (e) => {
  e.preventDefault()
})

ipcMain.handle('quit-app', () => {
  app.quit()
})

ipcMain.handle('resize-window', (event, { width, height }) => {
  win.setSize(Math.round(width), Math.round(height))
  const bounds = tray.getBounds()
  win.setPosition(
    Math.round(bounds.x + bounds.width / 2 - width / 2),
    Math.round(bounds.y + bounds.height)
  )
})

ipcMain.handle('store-get', (event, key, defaultVal) => store.get(key, defaultVal))
ipcMain.handle('store-set', (event, key, value) => { store.set(key, value) })

ipcMain.handle('notify', (event, { title, body }) => {
  new Notification({ title, body }).show()
})

// D-18: serial status IPC
ipcMain.handle('serial-status', () => ({ connected: isConnected }))

// Phase 6 — BEH-01/02/03: send serial command from renderer
// D-03: silent no-op when disconnected — no throw, no log
// D-04: cmd must include newline, e.g. 'SMILE\n' or 'DEFAULT\n'
ipcMain.handle('send-serial', (event, cmd) => {
  if (serialPort && serialPort.isOpen) {
    serialPort.write(cmd)
  }
})

// Phase 7 — ONBOARD-01/06: onboarding window lifecycle
ipcMain.handle('open-onboarding', () => {
  // Reset flag so onboarding runs from the beginning
  store.set('onboardingComplete', false)
  if (onboardingWin && !onboardingWin.isDestroyed()) {
    onboardingWin.focus()
    return
  }
  createOnboardingWindow()
})

ipcMain.handle('close-onboarding', () => {
  if (onboardingWin && !onboardingWin.isDestroyed()) {
    onboardingWin.close()
  }
  // Notify main window to refresh name/profile after onboarding completes
  if (win && !win.isDestroyed()) {
    win.webContents.send('onboarding-complete')
  }
})

// Phase 8 — INTERV-01/02: drift and refocus IPC handlers
ipcMain.handle('drift-detected', () => {
  driftCount++
  runPath('weak-regular')  // Phase 9 will replace with dynamic path selection
})

ipcMain.handle('refocus-detected', () => {
  if (driftCount > 0) {
    new Notification({ title: 'Glorb', body: 'Focus regained.' }).show()
  }
  driftCount = 0
  clearAllTimers()
})
