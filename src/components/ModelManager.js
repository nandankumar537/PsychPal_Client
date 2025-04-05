import React, { useState, useEffect } from 'react';
import { ModelService } from '../services/ModelService';

const ModelManager = ({ 
  isModelLoaded, 
  isModelDownloading, 
  downloadProgress, 
  onDownloadModel,
  isOnline 
}) => {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [downloadFolder, setDownloadFolder] = useState('');
  
  useEffect(() => {
    const loadModels = async () => {
      try {
        const availableModels = await ModelService.getAvailableModels();
        setModels(availableModels);
        
        if (availableModels.length > 0) {
          setSelectedModel(availableModels[0].id);
        }
        
        // Get download location
        const appPaths = await window.electron.getAppPaths();
        setDownloadFolder(appPaths.modelsPath);
        
        // Get info about currently loaded model
        if (isModelLoaded) {
          const info = await ModelService.getCurrentModelInfo();
          setModelInfo(info);
        }
      } catch (error) {
        console.error('Failed to load models:', error);
      }
    };
    
    loadModels();
  }, [isModelLoaded]);
  
  const handleModelSelect = (e) => {
    setSelectedModel(e.target.value);
  };
  
  const handleSelectFolder = async () => {
    try {
      const folder = await window.electron.selectFolder();
      if (folder) {
        setDownloadFolder(folder);
      }
    } catch (error) {
      console.error('Failed to select folder:', error);
    }
  };
  
  const handleDownload = () => {
    if (!selectedModel || isModelDownloading) return;
    onDownloadModel();
  };
  
  // Calculate estimated download size based on model
  const getEstimatedSize = (modelId) => {
    const model = models.find(m => m.id === modelId);
    return model ? model.size : '0';
  };
  
  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Model Management</h1>
      
      {/* Current Model Status */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Current Model Status</h2>
        
        {isModelLoaded ? (
          <div>
            <div className="flex items-center mb-2">
              <span className="inline-block w-3 h-3 rounded-full bg-green-500 mr-2"></span>
              <span className="font-medium">Model loaded and ready</span>
            </div>
            
            {modelInfo && (
              <div className="mt-3 bg-gray-50 p-4 rounded-md">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="text-gray-600">Name:</div>
                  <div className="font-medium">{modelInfo.name}</div>
                  
                  <div className="text-gray-600">Size:</div>
                  <div className="font-medium">{modelInfo.size} MB</div>
                  
                  <div className="text-gray-600">Location:</div>
                  <div className="font-medium text-gray-800 truncate">{modelInfo.path}</div>
                  
                  <div className="text-gray-600">Last Updated:</div>
                  <div className="font-medium">{new Date(modelInfo.lastUpdated).toLocaleString()}</div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>
            <div className="flex items-center mb-4">
              <span className="inline-block w-3 h-3 rounded-full bg-yellow-500 mr-2"></span>
              <span className="font-medium">No model loaded</span>
            </div>
            <p className="text-gray-600 text-sm">
              You need to download a model before you can chat offline. Please select a model below.
            </p>
          </div>
        )}
      </div>
      
      {/* Download New Model */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Download Model</h2>
        
        {!isOnline ? (
          <div className="bg-red-50 text-red-700 p-4 rounded-md mb-4">
            <div className="flex items-center mb-1">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">You are offline</span>
            </div>
            <p className="text-sm">
              You need an internet connection to download new models. Please connect to the internet and try again.
            </p>
          </div>
        ) : (
          <>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-medium mb-2">
                Select Model
              </label>
              <select
                value={selectedModel || ''}
                onChange={handleModelSelect}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={isModelDownloading}
              >
                {models.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name} ({model.size} MB) - {model.description}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-medium mb-2">
                Download Location
              </label>
              <div className="flex">
                <input
                  type="text"
                  value={downloadFolder}
                  readOnly
                  className="flex-1 p-2 border rounded-l focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50"
                />
                <button
                  onClick={handleSelectFolder}
                  className="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-r border-t border-r border-b"
                  disabled={isModelDownloading}
                >
                  Browse
                </button>
              </div>
            </div>
            
            {selectedModel && (
              <div className="bg-blue-50 p-3 rounded-md mb-4 text-sm">
                <p className="text-blue-800">
                  <strong>Note:</strong> The selected model requires approximately {getEstimatedSize(selectedModel)} MB of disk space. 
                  The download might take some time depending on your internet connection.
                </p>
              </div>
            )}
            
            {isModelDownloading && (
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Downloading model...</span>
                  <span>{downloadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-indigo-600 h-2.5 rounded-full" 
                    style={{ width: `${downloadProgress}%` }}
                  ></div>
                </div>
              </div>
            )}
            
            <button
              onClick={handleDownload}
              disabled={!selectedModel || isModelDownloading}
              className={`w-full py-2 rounded-md text-white font-medium ${
                !selectedModel || isModelDownloading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700'
              }`}
            >
              {isModelDownloading ? 'Downloading...' : 'Download Selected Model'}
            </button>
          </>
        )}
      </div>
      
      {/* Model Management Tips */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Usage Tips</h2>
        
        <div className="space-y-3 text-sm text-gray-700">
          <div className="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-indigo-500 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>
              <strong>Offline Usage:</strong> Once a model is downloaded, you can chat with PsychPal 
              even without an internet connection.
            </p>
          </div>
          
          <div className="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-indigo-500 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>
              <strong>Storage Space:</strong> Models can take up significant disk space. Ensure 
              you have enough free space before downloading.
            </p>
          </div>
          
          <div className="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-indigo-500 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>
              <strong>Model Training:</strong> After downloading a model, you can fine-tune it with your 
              conversation data in the Settings tab to improve responses for your specific needs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelManager;
