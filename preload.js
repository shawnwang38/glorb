const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('glorb', {
  quit: () => ipcRenderer.invoke('quit-app'),
  resize: (width, height) => ipcRenderer.invoke('resize-window', { width, height }),
  storeGet: (key, defaultVal) => ipcRenderer.invoke('store-get', key, defaultVal),
  storeSet: (key, value) => ipcRenderer.invoke('store-set', key, value),
  notify: (title, body) => ipcRenderer.invoke('notify', { title, body }),
  serialStatus: () => ipcRenderer.invoke('serial-status'),
  onSerialStatus: (callback) => ipcRenderer.on('serial-status-changed', (_event, data) => callback(data)),
  sendSerial: (cmd) => ipcRenderer.invoke('send-serial', cmd),
  closeOnboarding: () => ipcRenderer.invoke('close-onboarding'),
  openOnboarding: () => ipcRenderer.invoke('open-onboarding'),
  onOnboardingComplete: (cb) => ipcRenderer.on('onboarding-complete', () => cb())
})
