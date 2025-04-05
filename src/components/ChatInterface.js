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
            <h2 className="text-2xl font-bold text-indigo-600 mb-3">Welcome to PsychPal</h2>
            <p className="text-gray-600 mb-4">
              Your privacy-first mental health assistant. All conversations are stored locally on your device.
            </p>
            {!isModelLoaded && (
              <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-md mb-4">
                <p className="text-yellow-700 text-sm">
                  Please download a model from the Models tab to start chatting offline.
                </p>
              </div>
            )}
            <p className="text-gray-500 text-sm italic mt-4">
              Type a message below to begin your conversation.
            </p>
          </div>
        </div>
      );
    }
    return null;
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Chat header */}
      <div className="bg-white border-b p-4 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-800">
          {conversation ? conversation.title : 'New Conversation'}
        </h2>
      </div>
      
      {/* Chat messages area */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {renderWelcomeMessage()}
        
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`mb-4 ${message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}`}
          >
            <div 
              className={`max-w-3/4 p-3 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-indigo-600 text-white rounded-br-none' 
                  : 'bg-white text-gray-800 border rounded-bl-none shadow-sm'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              <div 
                className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-indigo-200' : 'text-gray-400'
                }`}
              >
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-white p-3 rounded-lg border rounded-bl-none shadow-sm">
              <div className="flex items-center">
                <div className="dot-typing"></div>
                <span className="ml-2 text-sm text-gray-500">PsychPal is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input area */}
      <div className="bg-white border-t p-4">
        <div className="flex rounded-lg border overflow-hidden">
          <textarea
            className="flex-1 px-4 py-3 focus:outline-none resize-none"
            placeholder="Type your message here..."
            rows="2"
            value={input}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            disabled={isLoading || !isModelLoaded}
          ></textarea>
          <button
            className={`px-4 bg-indigo-600 text-white font-medium ${
              isLoading || !input.trim() || !isModelLoaded
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:bg-indigo-700'
            }`}
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim() || !isModelLoaded}
          >
            Send
          </button>
        </div>
        {!isModelLoaded && (
          <div className="mt-2 text-orange-600 text-sm">
            Please download a model from the Models tab to start chatting
          </div>
        )}
      </div>
      
      {/* CSS for typing animation */}
      <style jsx="true">{`
        .dot-typing {
          position: relative;
          left: -9999px;
          width: 6px;
          height: 6px;
          border-radius: 5px;
          background-color: #6366f1;
          color: #6366f1;
          box-shadow: 9984px 0 0 0 #6366f1, 9999px 0 0 0 #6366f1, 10014px 0 0 0 #6366f1;
          animation: dot-typing 1.5s infinite linear;
        }
        
        @keyframes dot-typing {
          0% {
            box-shadow: 9984px 0 0 0 #6366f1, 9999px 0 0 0 #6366f1, 10014px 0 0 0 #6366f1;
          }
          16.667% {
            box-shadow: 9984px -5px 0 0 #6366f1, 9999px 0 0 0 #6366f1, 10014px 0 0 0 #6366f1;
          }
          33.333% {
            box-shadow: 9984px 0 0 0 #6366f1, 9999px 0 0 0 #6366f1, 10014px 0 0 0 #6366f1;
          }
          50% {
            box-shadow: 9984px 0 0 0 #6366f1, 9999px -5px 0 0 #6366f1, 10014px 0 0 0 #6366f1;
          }
          66.667% {
            box-shadow: 9984px 0 0 0 #6366f1, 9999px 0 0 0 #6366f1, 10014px 0 0 0 #6366f1;
          }
          83.333% {
            box-shadow: 9984px 0 0 0 #6366f1, 9999px 0 0 0 #6366f1, 10014px -5px 0 0 #6366f1;
          }
          100% {
            box-shadow: 9984px 0 0 0 #6366f1, 9999px 0 0 0 #6366f1, 10014px 0 0 0 #6366f1;
          }
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;
