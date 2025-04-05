import React, { useState, useEffect, useRef } from 'react';
import { ChatService } from '../services/ChatService';

const ChatInterface = ({ conversation, isModelLoaded, onNewConversation, onUpdateConversation }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  useEffect(() => {
    if (conversation) {
      setMessages(conversation.messages || []);
    } else {
      setMessages([]);
    }
  }, [conversation]);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleInputChange = (e) => {
    setInput(e.target.value);
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    if (!isModelLoaded) {
      alert('Please download a model first to chat offline');
      return;
    }
    
    // Create a new conversation if none exists
    if (!conversation) {
      await onNewConversation();
      return;
    }
    
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };
    
    // Add user message to UI immediately
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);
    
    try {
      // Get response from model
      const botResponse = await ChatService.sendMessage(input, conversation.id);
      
      const botMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: botResponse,
        timestamp: new Date().toISOString()
      };
      
      // Update messages with bot response
      const finalMessages = [...updatedMessages, botMessage];
      setMessages(finalMessages);
      
      // Save updated conversation to database
      const updatedConversation = {
        ...conversation,
        messages: finalMessages,
        updatedAt: new Date().toISOString()
      };
      
      await ChatService.saveConversation(updatedConversation);
      
      // Refresh conversations list
      if (onUpdateConversation) {
        onUpdateConversation();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to get response from the model. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Render welcome message if no messages yet
  const renderWelcomeMessage = () => {
    if (messages.length === 0) {
      return (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center p-6 max-w-md">
            <h2 className="text-2xl font-bold text-[#8AB795] mb-3">Welcome to PsychPal</h2>
            <p className="text-[#2D3047] mb-4">
              Your privacy-first mental health assistant. All conversations are stored locally on your device.
            </p>
            {!isModelLoaded && (
              <div className="bg-[#F9F8F4] border border-[#A8A4CE] p-3 rounded-md mb-4">
                <p className="text-[#2D3047] text-sm">
                  Please download a model from the Models tab to start chatting offline.
                </p>
              </div>
            )}
            <p className="text-[#2D3047] opacity-70 text-sm italic mt-4">
              Type a message below to begin your conversation.
            </p>
          </div>
        </div>
      );
    }
    return null;
  };
  
  return (
    <div className="flex flex-col h-full bg-[#F9F8F4] font-['Quicksand']">
      {/* Header */}
      <div className="bg-[#8AB795] p-4 shadow-sm">
        <h2 className="text-lg font-semibold text-white">
          {conversation ? conversation.title : 'New Conversation'}
        </h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {renderWelcomeMessage()}

        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] p-4 rounded-2xl ${
              message.role === 'user'
                ? 'bg-[#A8A4CE] text-white rounded-br-none'
                : 'bg-white text-[#2D3047] shadow-md rounded-bl-none'
            }`}>
              <p className="text-[15px] leading-relaxed">{message.content}</p>
              <div className={`text-xs mt-2 ${
                message.role === 'user' ? 'text-white opacity-80' : 'text-[#2D3047] opacity-60'
              }`}>
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white p-4 rounded-2xl shadow-md">
              <div className="flex items-center space-x-2">
                <div className="dot-typing"></div>
                <span className="text-sm text-[#2D3047] opacity-60">Processing...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="bg-[#F9F8F4] border-t border-[#E9E5E3] p-4">
        <div className="flex items-end space-x-3">
          <textarea
            className="flex-1 p-3 rounded-xl border border-[#A8A4CE] focus:outline-none focus:ring-2 focus:ring-[#8AB795] resize-none bg-white"
            placeholder="Share your thoughts..."
            rows="2"
            value={input}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            disabled={isLoading || !isModelLoaded}
          ></textarea>
          <button
            className={`p-3 rounded-xl ${
              isLoading || !input.trim() || !isModelLoaded
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-[#F9A686] hover:bg-[#F8957A] text-white'
            } transition-colors`}
            onClick={handleSendMessage}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>

      <style jsx="true">{`
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600&display=swap');
        
        .dot-typing {
          width: 8px;
          height: 8px;
          background: #8AB795;
          animation: dotTyping 1.4s infinite linear;
        }

        @keyframes dotTyping {
          0%, 100% { opacity: 0.2 }
          50% { opacity: 1 }
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;