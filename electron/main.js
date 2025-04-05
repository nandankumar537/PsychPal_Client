const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const isDev = process.env.NODE_ENV === 'development';
const os = require('os');
const { spawn } = require('child_process');

// Declare mainWindow in a broader scope
let mainWindow;
let flaskProcess = null;

// Start Flask server
function startFlaskServer() {
  if (isDev) {
    // In development - assume Flask is running independently
    console.log('Development mode: Flask server should be started manually');
    return;
  }

  const flaskPath = path.join(process.resourcesPath, 'server', 'app.py');
  const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
  
  console.log(`Starting Flask server from: ${flaskPath}`);
  
  flaskProcess = spawn(pythonExecutable, [flaskPath]);
  
  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask stdout: ${data}`);
  });
  
  flaskProcess.stderr.on('data', (data) => {
    console.log(`Flask stderr: ${data}`);
  });
  
  flaskProcess.on('close', (code) => {
    console.log(`Flask process exited with code ${code}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../public/icon.svg')
  });

  // Load React App
  const startUrl = isDev 
    ? 'http://localhost:5000' 
    : `file://${path.join(__dirname, '../build/index.html')}`;
  
  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

// Create data directory for the app
function createAppDataDirectory() {
  const appDataPath = path.join(os.homedir(), '.psychpal');
  const modelsPath = path.join(appDataPath, 'models');
  const databasePath = path.join(appDataPath, 'database');
  
  if (!fs.existsSync(appDataPath)) {
    fs.mkdirSync(appDataPath);
  }
  
  if (!fs.existsSync(modelsPath)) {
    fs.mkdirSync(modelsPath);
  }
  
  if (!fs.existsSync(databasePath)) {
    fs.mkdirSync(databasePath);
  }
  
  return { appDataPath, modelsPath, databasePath };
}

app.whenReady().then(() => {
  const { appDataPath, modelsPath, databasePath } = createAppDataDirectory();
  
  // Set global app data paths
  global.appData = {
    appDataPath,
    modelsPath,
    databasePath
  };
  
  // Start the Flask server
  startFlaskServer();
  
  // Create the main window
  createWindow();
  
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  if (flaskProcess) {
    console.log('Terminating Flask server...');
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', flaskProcess.pid, '/f', '/t']);
    } else {
      flaskProcess.kill();
    }
  }
});

// IPC Handlers
ipcMain.handle('get-app-paths', () => {
  return global.appData;
});

ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  
  if (result.canceled) {
    return null;
  } else {
    return result.filePaths[0];
  }
});

ipcMain.handle('check-online-status', () => {
  return { online: require('electron').net.online };
});
