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
    <div className="w-64 bg-[#e8f4fa] text-[#2b3a4e] flex flex-col h-full font-['Inter']">
      {/* App header */}
      <div className="p-4 border-b border-[#c5ddec]">
        <h1 className="text-xl font-semibold flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-[#3a6b8c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          PsychPal
        </h1>
        <div className="flex items-center mt-2 text-[#4a6572] text-sm">
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isOnline ? 'bg-[#7ec4cf]' : 'bg-[#ff9f8e]'}`}></span>
          {isOnline ? 'Online' : 'Offline'}
          
          <span className="mx-2">•</span>
          
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isModelLoaded ? 'bg-[#7ec4cf]' : 'bg-[#ffd58e]'}`}></span>
          {isModelLoaded ? 'Model Loaded' : 'No Model'}
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="p-2">
        <ul>
          <li>
            <button 
              className={`w-full text-left p-3 rounded-lg flex items-center transition-all ${
                currentView === 'chat' 
                  ? 'bg-[#c5e3f0] text-[#2b3a4e]' 
                  : 'hover:bg-[#d7e8f0] text-[#4a6572]'
              }`}
              onClick={() => setCurrentView('chat')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-[#3a6b8c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Chat
            </button>
          </li>
          {/* Similar updates for other nav buttons */}
        </ul>
      </nav>
      
      {/* Conversations list */}
      {currentView === 'chat' && (
        <div className="flex-1 overflow-y-auto">
          <div className="p-2 border-y border-[#c5ddec] flex justify-between items-center bg-[#e8f4fa]">
            <h2 className="font-medium text-[#3a6b8c]">Conversations</h2>
            <button 
              onClick={onNewConversation}
              className="p-1.5 rounded-lg hover:bg-[#c5e3f0] transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-[#3a6b8c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
                      className={`w-full text-left p-3 rounded-lg mb-1 text-sm transition-colors ${
                        currentConversation?.id === convo.id
                          ? 'bg-[#c5e3f0] text-[#2b3a4e]'
                          : 'hover:bg-[#d7e8f0] text-[#4a6572]'
                      }`}
                      onClick={() => setCurrentConversation(convo)}
                    >
                      <div className="font-medium">{truncateText(convo.title)}</div>
                      <div className="text-xs text-[#6a7b8a]">
                        {formatDate(convo.createdAt)}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-[#6a7b8a] text-sm p-2 text-center">
                No conversations yet
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Footer */}
      <div className="p-3 text-xs text-[#6a7b8a] border-t border-[#c5ddec]">
        <p>PsychPal v1.0.0</p>
        <p>Privacy-Preserving Mental Health Support</p>
      </div>
    </div>
  );
};

export default Sidebar;
