const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('glorb', {
  quit: () => ipcRenderer.invoke('quit-app')
})
