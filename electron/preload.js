const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'electron',
  {
    getAppPaths: () => ipcRenderer.invoke('get-app-paths'),
    selectFolder: () => ipcRenderer.invoke('select-folder'),
    checkOnlineStatus: () => ipcRenderer.invoke('check-online-status')
  }
);
