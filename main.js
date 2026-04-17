const { app, BrowserWindow, Tray, nativeImage, ipcMain, globalShortcut, Notification } = require('electron')
const path = require('path')
const Store = require('electron-store')
const { SerialPort } = require('serialport')
const store = new Store()

let tray = null
let win = null

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
    if (isConnected) {
      clearInterval(reconnectTimer)
      reconnectTimer = null
      return
    }
    const portPath = await findArduinoPort()
    if (portPath) {
      openPort(portPath)
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
  if (portPath) {
    openPort(portPath)
  } else {
    // D-12: no port found — proceed silently, start polling for later plug-in
    startReconnectLoop()
  }
}

app.dock.hide()
app.setActivationPolicy('accessory')

app.whenReady().then(() => {
  createWindow()
  createTray()
  initSerial()

  globalShortcut.register('Command+Q', () => {
    app.quit()
  })
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
