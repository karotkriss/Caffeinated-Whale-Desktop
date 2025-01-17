import { app, BrowserWindow, ipcMain } from 'electron'
import * as path from 'path'
import { spawn } from 'child_process'
if (require('electron-squirrel-startup')) {
  app.quit();
}

class ElectronApp {
  private mainWindow: BrowserWindow | null = null

  constructor() {
    this.initApp()
  }

  private initApp(): void {
    app.on('ready', this.createWindow.bind(this))
    
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit()
      }
    })

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createWindow()
      }
    })

    this.setupIpcHandlers()
  }

  private createWindow(): void {
    this.mainWindow = new BrowserWindow({
      width: 1280,
      height: 720,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      }
    })

    this.mainWindow.loadURL('http://localhost:3000');

    if (process.env.NODE_ENV === 'development') {
      this.mainWindow.webContents.openDevTools()
      
      require('electron-reload')(__dirname, {
        electron: path.join(__dirname, '..', 'node_modules', '.bin', 'electron'),
        hardResetMethod: 'exit'
      });
    }
  }

  private setupIpcHandlers(): void {
    ipcMain.handle('get-available-port', this.findAvailablePort.bind(this))
    ipcMain.handle('create-frappe-instance', this.createFrappeInstance.bind(this))
    ipcMain.handle('list-frappe-instances', this.listFrappeInstances.bind(this))
    ipcMain.handle('delete-frappe-instance', this.deleteFrappeInstance.bind(this))
    ipcMain.handle('run-frappe-command', this.runFrappeCommand.bind(this))
  }

  private async findAvailablePort(event: Electron.IpcMainInvokeEvent, startPort: number = 8000): Promise<number> {
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../../backend/port_scanner.py'), 
      startPort.toString()
    ])

    return new Promise((resolve, reject) => {
      pythonProcess.stdout.on('data', (data: Buffer) => {
        resolve(parseInt(data.toString().trim()))
      })

      pythonProcess.stderr.on('data', (error: Buffer) => {
        reject(error.toString())
      })
    })
  }

  private async createFrappeInstance(event: Electron.IpcMainInvokeEvent, instanceConfig: any): Promise<string> {
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../../backend/create_instance.py'),
      JSON.stringify(instanceConfig)
    ])

    return new Promise((resolve, reject) => {
      pythonProcess.stdout.on('data', (data: Buffer) => {
        resolve(data.toString().trim())
      })

      pythonProcess.stderr.on('data', (error: Buffer) => {
        reject(error.toString())
      })
    })
  }

  private async listFrappeInstances(): Promise<any[]> {
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../../backend/list_instances.py')
    ])

    return new Promise((resolve, reject) => {
      pythonProcess.stdout.on('data', (data: Buffer) => {
        try {
          const instances = JSON.parse(data.toString().trim());
          resolve(instances);
        } catch (error) {
          reject(`Error parsing JSON: ${error}`);
        }
      })

      pythonProcess.stderr.on('data', (error: Buffer) => {
        reject(error.toString())
      })
    })
  }

  private async deleteFrappeInstance(event: Electron.IpcMainInvokeEvent, projectName: string): Promise<void> {
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../../backend/delete_instance.py'),
      projectName
    ])

    return new Promise((resolve, reject) => {
      pythonProcess.stdout.on('data', (data: Buffer) => {
        console.log(`Delete instance output: ${data.toString().trim()}`)
        resolve()
      })

      pythonProcess.stderr.on('data', (error: Buffer) => {
        console.error(`Delete instance error: ${error.toString().trim()}`)
        reject(error.toString())
      })
    })
  }

  private runFrappeCommand(event: Electron.IpcMainInvokeEvent, args: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(__dirname, '..', '..', 'backend', 'frappe_instance_info.py');
      console.log('Executing Python script with args:', args); // For debugging
      const pythonProcess = spawn('python', [scriptPath, ...args]);

      let output = '';
      let errorOutput = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(output);
        } else {
          reject(new Error(`Python script exited with code ${code}. Error: ${errorOutput}`));
        }
      });
    });
  }
}

new ElectronApp()

