import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { spawn } from 'child_process';

class ElectronApp {
  private mainWindow: BrowserWindow | null = null;

  constructor() {
    this.initApp();
  }

  private initApp() {
    app.on('ready', this.createWindow.bind(this));
    
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createWindow();
      }
    });

    this.setupIpcHandlers();
  }

  private createWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1280,
      height: 720,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false,
        preload: path.join(__dirname, 'preload.js'),
      }
    });

    this.mainWindow.loadURL('http://localhost:3000');

    if (process.env.NODE_ENV === 'development') {
      this.mainWindow.webContents.openDevTools();
    }
  }

  private setupIpcHandlers() {
    ipcMain.handle('get-available-port', this.findAvailablePort.bind(this));
    ipcMain.handle('create-frappe-instance', this.createFrappeInstance.bind(this));
    ipcMain.handle('list-frappe-instances', this.listFrappeInstances.bind(this));
  }

  private async findAvailablePort(event: any, startPort: number = 8000): Promise<number> {
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../backend/port_scanner.py'), 
      startPort.toString()
    ]);

    return new Promise((resolve, reject) => {
      pythonProcess.stdout.on('data', (data) => {
        resolve(parseInt(data.toString().trim()));
      });

      pythonProcess.stderr.on('data', (error) => {
        reject(error.toString());
      });
    });
  }

  private async createFrappeInstance(event: any, instanceConfig: any): Promise<string> {
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../backend/create_instance.py'),
      JSON.stringify(instanceConfig)
    ]);

    return new Promise((resolve, reject) => {
      pythonProcess.stdout.on('data', (data) => {
        resolve(data.toString().trim());
      });

      pythonProcess.stderr.on('data', (error) => {
        reject(error.toString());
      });
    });
  }

  private async listFrappeInstances(): Promise<any[]> {
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../backend/list_instances.py')
    ]);

    return new Promise((resolve, reject) => {
      pythonProcess.stdout.on('data', (data) => {
        resolve(JSON.parse(data.toString().trim()));
      });

      pythonProcess.stderr.on('data', (error) => {
        reject(error.toString());
      });
    });
  }
}

new ElectronApp();

