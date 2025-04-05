import React, { useState, useEffect } from 'react';
import { TrainingService } from '../services/TrainingService';
import { SyncService } from '../services/SyncService';

const Settings = ({ isOnline, isTraining, isSyncing, setIsTraining, setIsSyncing }) => {
  const [trainSettings, setTrainSettings] = useState({
    useLocalData: true,
    numEpochs: 1,
    batchSize: 4,
    learningRate: 0.0001
  });
  
  const [syncSettings, setSyncSettings] = useState({
    privacyEpsilon: 2.0,
    privacyDelta: 1e-5,
    syncFrequency: 'manual' // manual, daily, weekly
  });
  
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [syncProgress, setSyncProgress] = useState(0);
  const [lastSyncTime, setLastSyncTime] = useState(null);
  const [lastTrainingTime, setLastTrainingTime] = useState(null);
  
  useEffect(() => {
    // Load settings from local storage
    const loadSettings = async () => {
      try {
        const savedTrainSettings = localStorage.getItem('trainSettings');
        const savedSyncSettings = localStorage.getItem('syncSettings');
        const savedLastSyncTime = localStorage.getItem('lastSyncTime');
        const savedLastTrainingTime = localStorage.getItem('lastTrainingTime');
        
        if (savedTrainSettings) {
          setTrainSettings(JSON.parse(savedTrainSettings));
        }
        
        if (savedSyncSettings) {
          setSyncSettings(JSON.parse(savedSyncSettings));
        }
        
        if (savedLastSyncTime) {
          setLastSyncTime(savedLastSyncTime);
        }
        
        if (savedLastTrainingTime) {
          setLastTrainingTime(savedLastTrainingTime);
        }
      } catch (error) {
        console.error('Error loading settings:', error);
      }
    };
    
    loadSettings();
  }, []);
  
  // Save settings to local storage when they change
  useEffect(() => {
    localStorage.setItem('trainSettings', JSON.stringify(trainSettings));
  }, [trainSettings]);
  
  useEffect(() => {
    localStorage.setItem('syncSettings', JSON.stringify(syncSettings));
  }, [syncSettings]);
  
  const handleTrainSettingChange = (e) => {
    const { name, value, type, checked } = e.target;
    setTrainSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) : value)
    }));
  };
  
  const handleSyncSettingChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSyncSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) : value)
    }));
  };
  
  const handleStartTraining = async () => {
    if (isTraining) return;
    
    try {
      setIsTraining(true);
      setTrainingProgress(0);
      
      // Start training process
      await TrainingService.startTraining(
        trainSettings, 
        (progress) => {
          setTrainingProgress(progress);
        }
      );
      
      // Update last training time
      const currentTime = new Date().toISOString();
      setLastTrainingTime(currentTime);
      localStorage.setItem('lastTrainingTime', currentTime);
      
      alert('Training completed successfully!');
    } catch (error) {
      console.error('Training error:', error);
      alert('Error during training: ' + error.message);
    } finally {
      setIsTraining(false);
    }
  };
  
  const handleSyncWithServer = async () => {
    if (isSyncing || !isOnline) return;
    
    try {
      setIsSyncing(true);
      setSyncProgress(0);
      
      // Start sync process
      await SyncService.syncWithServer(
        syncSettings,
        (progress) => {
          setSyncProgress(progress);
        }
      );
      
      // Update last sync time
      const currentTime = new Date().toISOString();
      setLastSyncTime(currentTime);
      localStorage.setItem('lastSyncTime', currentTime);
      
      alert('Sync completed successfully!');
    } catch (error) {
      console.error('Sync error:', error);
      alert('Error during sync: ' + error.message);
    } finally {
      setIsSyncing(false);
    }
  };
  
  const formatDateTime = (isoString) => {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    return date.toLocaleString();
  };
  
  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Settings</h1>
      
      {/* Training Settings */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
          Local Model Training
        </h2>
        
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">
            <input
              type="checkbox"
              name="useLocalData"
              checked={trainSettings.useLocalData}
              onChange={handleTrainSettingChange}
              className="mr-2"
            />
            Use local conversation data for training
          </label>
        </div>
        
        <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">
              Number of Epochs
            </label>
            <input
              type="number"
              name="numEpochs"
              min="1"
              max="10"
              value={trainSettings.numEpochs}
              onChange={handleTrainSettingChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">
              Batch Size
            </label>
            <input
              type="number"
              name="batchSize"
              min="1"
              max="16"
              value={trainSettings.batchSize}
              onChange={handleTrainSettingChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">
              Learning Rate
            </label>
            <input
              type="number"
              name="learningRate"
              min="0.00001"
              max="0.01"
              step="0.00001"
              value={trainSettings.learningRate}
              onChange={handleTrainSettingChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
        
        {isTraining && (
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-indigo-600 h-2.5 rounded-full" 
                style={{ width: `${trainingProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-1">Training progress: {trainingProgress}%</p>
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <button
            onClick={handleStartTraining}
            disabled={isTraining}
            className={`px-4 py-2 rounded-md text-white font-medium ${
              isTraining
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700'
            }`}
          >
            {isTraining ? 'Training in Progress...' : 'Start Training'}
          </button>
          
          {lastTrainingTime && (
            <span className="text-sm text-gray-600">
              Last trained: {formatDateTime(lastTrainingTime)}
            </span>
          )}
        </div>
      </div>
      
      {/* Server Sync Settings */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Server Synchronization
        </h2>
        
        <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">
              Privacy Epsilon
            </label>
            <input
              type="number"
              name="privacyEpsilon"
              min="0.1"
              max="10"
              step="0.1"
              value={syncSettings.privacyEpsilon}
              onChange={handleSyncSettingChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-xs text-gray-500 mt-1">Higher values = less privacy, better accuracy</p>
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">
              Privacy Delta
            </label>
            <input
              type="number"
              name="privacyDelta"
              min="1e-10"
              max="1e-2"
              step="1e-6"
              value={syncSettings.privacyDelta}
              onChange={handleSyncSettingChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-xs text-gray-500 mt-1">Failure probability parameter</p>
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">
              Sync Frequency
            </label>
            <select
              name="syncFrequency"
              value={syncSettings.syncFrequency}
              onChange={handleSyncSettingChange}
              className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="manual">Manual Only</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
        </div>
        
        <div className="mb-4">
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>Privacy Note:</strong> When you sync with the server, only the updated model weights with differential privacy are shared, not your conversation data. Your privacy is preserved while helping improve the model for everyone.
            </p>
          </div>
        </div>
        
        {isSyncing && (
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-indigo-600 h-2.5 rounded-full" 
                style={{ width: `${syncProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-1">Sync progress: {syncProgress}%</p>
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <button
            onClick={handleSyncWithServer}
            disabled={isSyncing || !isOnline}
            className={`px-4 py-2 rounded-md text-white font-medium ${
              isSyncing || !isOnline
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700'
            }`}
          >
            {isSyncing 
              ? 'Syncing...' 
              : !isOnline 
                ? 'Offline (Cannot Sync)' 
                : 'Sync with Server'}
          </button>
          
          {lastSyncTime && (
            <span className="text-sm text-gray-600">
              Last synced: {formatDateTime(lastSyncTime)}
            </span>
          )}
        </div>
      </div>
      
      {/* About Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-2">About PsychPal</h2>
        <p className="text-gray-600 mb-2">
          PsychPal is a privacy-focused mental health chatbot that runs locally on your device.
        </p>
        <p className="text-gray-600 mb-2">
          Your conversations are stored only on your device. When you choose to help improve
          the model, only differential privacy protected model updates are shared.
        </p>
        <p className="text-gray-600">
          Version 1.0.0 - Built with Electron, React, and HuggingFace Transformers
        </p>
      </div>
    </div>
  );
};

export default Settings;
