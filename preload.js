const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('glorb', {
  quit: () => ipcRenderer.invoke('quit-app'),
  resize: (width, height) => ipcRenderer.invoke('resize-window', { width, height })
})
