import { contextBridge, ipcRenderer } from 'electron'

interface ElectronAPI {
  getAvailablePort: (startPort: number) => Promise<number>
  createFrappeInstance: (instanceConfig: any) => Promise<string>
  listFrappeInstances: () => Promise<any[]>
}

const electronAPI: ElectronAPI = {
  getAvailablePort: (startPort: number) => ipcRenderer.invoke('get-available-port', startPort),
  createFrappeInstance: (instanceConfig: any) => ipcRenderer.invoke('create-frappe-instance', instanceConfig),
  listFrappeInstances: () => ipcRenderer.invoke('list-frappe-instances'),
}

contextBridge.exposeInMainWorld('electronAPI', electronAPI)

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}

