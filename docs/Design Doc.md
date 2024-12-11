
## Design Document for Electron App Using Next.js, TypeScript, Shadcn, and Python

### Overview

This document outlines the design and implementation strategy for an Electron application that automates the deployment of a local development environment for Frappe. The application will utilize Next.js with TypeScript, Tailwind CSS, and Shadcn UI components for a modern user interface. Additionally, it will integrate a Python backend to facilitate operations related to Frappe instances.

### Technology Stack

- **Frontend**: Next.js (with TypeScript, Tailwind CSS, App Routed, Route Groutes, Shadcn UI)
- **Backend**: Python (for managing Frappe instances)
- **Containerization**: Docker (to manage Frappe instances)
- **Real-time Communication**: WebSockets (for terminal integration)
- **Language**: Enforce Typescript

### Complete Application Structure

The application will be structured as follows:

```
.
├── README.md                               # Project documentation
├── components.json                         # Configuration for components
├── docs                                    # Documentation folder
│   └── Design Doc.md                       # Detailed design document
├── next-env.d.ts                           # Next.js environment types
├── next.config.ts                          # Next.js configuration file
├── package-lock.json                       # Automatically generated lock file for npm dependencies
├── package.json                            # Project metadata and dependencies
├── postcss.config.mjs                      # PostCSS configuration file
├── public                                  # Static assets
│   ├── file.svg                            # Example SVG asset
│   ├── globe.svg                           # Example SVG asset
│   ├── next.svg                            # Next.js logo SVG
│   ├── vercel.svg                          # Vercel logo SVG
│   └── window.svg                          # Example SVG asset
├── src
│   ├── app                                 # Application routes and components
│   │   ├── favicon.ico                     # Application favicon
│   │   ├── fonts                           # Custom fonts
│   │   │   ├── GeistMonoVF.woff            # Font file
│   │   │   └── GeistVF.woff                # Font file
│   │   ├── globals.css                     # Global CSS styles
│   │   ├── layout.tsx                      # Main layout component
│   │   └── page.tsx                        # Main entry page
│   ├── components                           # Shared components across the app
│   │   └── ui                              # UI components
│   │       ├── button.tsx                   # Button component
│   │       ├── card.tsx                     # Card component
│   │       ├── input.tsx                    # Input component
│   │       └── label.tsx                    # Label component
│   └── lib                                 # Utility functions and libraries
│       └── utils.ts                        # Utility functions
├── tailwind.config.ts                      # Tailwind CSS configuration file
└── tsconfig.json                           # TypeScript configuration file
```

### Application Features & Requirements

#### Dashboard

- **View Existing Frappe Instances**: Display a list of currently running Frappe instances.
- **Create New Instance**: A form to create a new instance that includes:
  - Project Name
  - Site Name
  - Port (auto-detect available ports starting from 8000 checking every 1000)

#### Instance Management

- **Logs Viewer**: Display logs of the selected instance if it is running.
- **Control Buttons**:
  - Start/Stop Bench: Control the Frappe bench process.
  - Open in VSCode: Launch the selected instance in VSCode using a browser window.

#### Integrated Terminal

- **WebSocket Terminal**: A terminal interface similar to VSCode's integrated terminal, allowing users to interact with the backend via WebSockets.

#### Sidebar Navigation

- **Sections**:
  - Dashboard
  - Terminal
  - Settings (to be implemented later)

### Implementation Steps

1. **Initialize Next.js with Required Flags**

   Create a new Next.js application with the specified flags:

   ```bash
   npx create-next-app@latest my-electron-app --typescript --tailwind --eslint --no-turbopack --no-import-alias --app
   ```

2. **Install Shadcn UI**

   Initialize Shadcn UI in your project:

   ```bash
   npx shadcn@latest init -d 
   ```

3. **Setup TypeScript in Electron**

   Create an `electron.ts` file to configure the Electron main process using TypeScript:

```typescript
import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
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
                enableRemoteModule: true,
            }
        });

        // Load Next.js app in development
        this.mainWindow.loadURL('http://localhost:3000');

        // Open DevTools (optional)
        if (process.env.NODE_ENV === 'development') {
            this.mainWindow.webContents.openDevTools();
        }
    }

    private setupIpcHandlers() {
        // IPC handlers for communication between main and renderer processes
        ipcMain.handle('get-available-port', this.findAvailablePort.bind(this));
        ipcMain.handle('create-frappe-instance', this.createFrappeInstance.bind(this));
        ipcMain.handle('list-frappe-instances', this.listFrappeInstances.bind(this));
    }

    private async findAvailablePort(event: any, startPort: number = 8000): Promise<number> {
        // Python script to find available port
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
        // Python script to create Docker container
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
        // Python script to list Docker containers
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

// Initialize the Electron app
new ElectronApp();
```


4. **Python Backend Setup**

Create a `/backend` directory containing Python scripts:

- `port_scanner.py`: Finds available ports.
- `create_instance.py`: Creates Docker containers based on provided configurations.
- `list_instances.py`: Lists currently running Docker containers.

5. **WebSocket Integration**

Use a library like `ws` in Node.js to set up WebSocket communication between the frontend and backend for real-time terminal functionality.

6. **Implement UI Components**

Utilize Shadcn UI components styled with Tailwind CSS to create a responsive and modern user interface.

7. **Testing and Debugging**

Conduct thorough testing of all features, ensuring that the dashboard interacts correctly with the backend and that WebSocket communication is stable.

8. **Build and Package**

Use Electron Forge or a similar tool to package the application for distribution:

```bash
npm run build && npm run make
```

### Conclusion

This design document outlines a comprehensive plan for developing an Electron application that automates the deployment of Frappe environments using modern web technologies while enforcing TypeScript throughout the application. By leveraging Next.js App Router conventions, TypeScript, Tailwind CSS, Shadcn UI components, and Python, this application aims to provide a seamless experience for developers working with Frappe.