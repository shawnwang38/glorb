const { app, BrowserWindow, Tray, nativeImage, ipcMain, globalShortcut, Notification } = require('electron')
const path = require('path')
const Store = require('electron-store')
const store = new Store()

let tray = null
let win = null

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

app.dock.hide()
app.setActivationPolicy('accessory')

app.whenReady().then(() => {
  createWindow()
  createTray()

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
