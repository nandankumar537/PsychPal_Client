import React from 'react';

const Sidebar = ({ 
  currentView, 
  setCurrentView, 
  conversations, 
  currentConversation, 
  setCurrentConversation, 
  onNewConversation,
  isOnline,
  isModelLoaded
}) => {
  // Format the timestamp for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  // Truncate conversation title/content if too long
  const truncateText = (text, maxLength = 30) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };
  
  return (
    <div className="w-64 bg-indigo-800 text-white flex flex-col h-full">
      {/* App header */}
      <div className="p-4 border-b border-indigo-700">
        <h1 className="text-xl font-bold flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          PsychPal
        </h1>
        <div className="flex items-center mt-2 text-indigo-200 text-sm">
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isOnline ? 'bg-green-400' : 'bg-red-400'}`}></span>
          {isOnline ? 'Online' : 'Offline'}
          
          <span className="mx-2">•</span>
          
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isModelLoaded ? 'bg-green-400' : 'bg-yellow-400'}`}></span>
          {isModelLoaded ? 'Model Loaded' : 'No Model'}
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="p-2">
        <ul>
          <li>
            <button 
              className={`w-full text-left p-2 rounded flex items-center ${currentView === 'chat' ? 'bg-indigo-700' : 'hover:bg-indigo-700/50'}`}
              onClick={() => setCurrentView('chat')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Chat
            </button>
          </li>
          <li>
            <button 
              className={`w-full text-left p-2 rounded flex items-center ${currentView === 'models' ? 'bg-indigo-700' : 'hover:bg-indigo-700/50'}`}
              onClick={() => setCurrentView('models')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
              Models
            </button>
          </li>
          <li>
            <button 
              className={`w-full text-left p-2 rounded flex items-center ${currentView === 'settings' ? 'bg-indigo-700' : 'hover:bg-indigo-700/50'}`}
              onClick={() => setCurrentView('settings')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Settings
            </button>
          </li>
        </ul>
      </nav>
      
      {/* Conversations list - only show if in chat view */}
      {currentView === 'chat' && (
        <div className="flex-1 overflow-y-auto">
          <div className="p-2 border-b border-t border-indigo-700 flex justify-between items-center">
            <h2 className="font-medium">Conversations</h2>
            <button 
              onClick={onNewConversation}
              className="p-1 rounded-full hover:bg-indigo-700"
              title="New Conversation"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>
          </div>
          
          <div className="px-2 py-1">
            {conversations.length > 0 ? (
              <ul>
                {conversations.map((convo) => (
                  <li key={convo.id}>
                    <button
                      className={`w-full text-left p-2 rounded mb-1 text-sm ${
                        currentConversation && currentConversation.id === convo.id
                          ? 'bg-indigo-700'
                          : 'hover:bg-indigo-700/50'
                      }`}
                      onClick={() => setCurrentConversation(convo)}
                    >
                      <div className="font-medium">{truncateText(convo.title)}</div>
                      <div className="text-xs text-indigo-300">
                        {formatDate(convo.createdAt)}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-indigo-300 text-sm p-2 text-center">
                No conversations yet
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* App info footer */}
      <div className="p-3 text-xs text-indigo-300 border-t border-indigo-700">
        <p>PsychPal v1.0.0</p>
        <p>Privacy-Preserving Mental Health Support</p>
      </div>
    </div>
  );
};

export default Sidebar;
