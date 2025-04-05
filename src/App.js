import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import Settings from './components/Settings';
import ModelManager from './components/ModelManager';
import { DatabaseService } from './services/DatabaseService';
import { ModelService } from './services/ModelService';

function App() {
  const [currentView, setCurrentView] = useState('chat');
  const [isOnline, setIsOnline] = useState(false);
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [isModelDownloading, setIsModelDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [isTraining, setIsTraining] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  
  // Initialize services
  useEffect(() => {
    const initializeApp = async () => {
      // Initialize database
      await DatabaseService.initialize();
      
      // Check if model is already downloaded
      const modelStatus = await ModelService.checkModelStatus();
      setIsModelLoaded(modelStatus.isLoaded);
      
      // Load conversations
      loadConversations();
      
      // Check online status
      checkOnlineStatus();
      
      // Set up regular online status checking
      const intervalId = setInterval(checkOnlineStatus, 30000);
      return () => clearInterval(intervalId);
    };
    
    initializeApp();
  }, []);
  
  const checkOnlineStatus = async () => {
    try {
      if (window.electron) {
        const status = await window.electron.checkOnlineStatus();
        setIsOnline(status.online);
      } else {
        // Fallback method when not in Electron
        setIsOnline(navigator.onLine);
      }
    } catch (error) {
      console.error('Failed to check online status:', error);
      setIsOnline(false);
    }
  };
  
  const loadConversations = async () => {
    try {
      const convos = await DatabaseService.getConversations();
      setConversations(convos);
      
      // If there are conversations and none is selected, select the most recent one
      if (convos.length > 0 && !currentConversation) {
        setCurrentConversation(convos[0]);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };
  
  const createNewConversation = async () => {
    try {
      const newConvo = {
        id: Date.now().toString(),
        title: 'New Conversation',
        createdAt: new Date().toISOString(),
        messages: []
      };
      
      await DatabaseService.saveConversation(newConvo);
      setCurrentConversation(newConvo);
      await loadConversations();
    } catch (error) {
      console.error('Failed to create new conversation:', error);
    }
  };
  
  const downloadModel = async () => {
    try {
      setIsModelDownloading(true);
      setDownloadProgress(0);
      
      await ModelService.downloadModel(
        (progress) => setDownloadProgress(progress)
      );
      
      setIsModelLoaded(true);
    } catch (error) {
      console.error('Failed to download model:', error);
    } finally {
      setIsModelDownloading(false);
    }
  };
  
  // Render appropriate view based on currentView state
  const renderView = () => {
    switch (currentView) {
      case 'chat':
        return (
          <ChatInterface 
            conversation={currentConversation}
            isModelLoaded={isModelLoaded}
            onNewConversation={createNewConversation}
            onUpdateConversation={loadConversations}
          />
        );
      case 'models':
        return (
          <ModelManager 
            isModelLoaded={isModelLoaded}
            isModelDownloading={isModelDownloading}
            downloadProgress={downloadProgress}
            onDownloadModel={downloadModel}
            isOnline={isOnline}
          />
        );
      case 'settings':
        return (
          <Settings 
            isOnline={isOnline}
            isTraining={isTraining}
            isSyncing={isSyncing}
            setIsTraining={setIsTraining}
            setIsSyncing={setIsSyncing}
          />
        );
      default:
        return <ChatInterface />;
    }
  };
  
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar 
        currentView={currentView}
        setCurrentView={setCurrentView}
        conversations={conversations}
        currentConversation={currentConversation}
        setCurrentConversation={setCurrentConversation}
        onNewConversation={createNewConversation}
        isOnline={isOnline}
        isModelLoaded={isModelLoaded}
      />
      <main className="flex-1 flex flex-col overflow-hidden">
        {renderView()}
      </main>
    </div>
  );
}

export default App;
