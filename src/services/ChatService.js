import { DatabaseService } from './DatabaseService';
import { ModelService } from './ModelService';

export class ChatService {
  // Send a message to the local LLM model and get a response
  static async sendMessage(message, conversationId) {
    try {
      // Check if model is loaded
      const modelStatus = await ModelService.checkModelStatus();
      if (!modelStatus.isLoaded) {
        throw new Error('No model loaded. Please download a model first.');
      }
      
      // Call the local model inference endpoint
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get response from model');
      }
      
      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error in ChatService.sendMessage:', error);
      // If there's a network error (e.g., Flask server is down), fall back to direct inference
      return this.fallbackLocalInference(message, conversationId);
    }
  }
  
  // Fallback to direct model inference when the Flask server is unreachable
  static async fallbackLocalInference(message, conversationId) {
    try {
      // Load conversation history from database
      const conversation = await DatabaseService.getConversation(conversationId);
      if (!conversation) {
        throw new Error('Conversation not found');
      }
      
      // Format messages for the model
      const messages = conversation.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      // Add the new user message
      messages.push({
        role: 'user',
        content: message
      });
      
      // Use ModelService to perform local inference
      return await ModelService.localInference(messages);
    } catch (error) {
      console.error('Error in fallbackLocalInference:', error);
      throw error;
    }
  }
  
  // Save a conversation to the database
  static async saveConversation(conversation) {
    try {
      return await DatabaseService.saveConversation(conversation);
    } catch (error) {
      console.error('Error saving conversation:', error);
      throw error;
    }
  }
  
  // Delete a conversation from the database
  static async deleteConversation(conversationId) {
    try {
      return await DatabaseService.deleteConversation(conversationId);
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  }
  
  // Update the title of a conversation
  static async updateConversationTitle(conversationId, newTitle) {
    try {
      const conversation = await DatabaseService.getConversation(conversationId);
      if (!conversation) {
        throw new Error('Conversation not found');
      }
      
      conversation.title = newTitle;
      return await DatabaseService.saveConversation(conversation);
    } catch (error) {
      console.error('Error updating conversation title:', error);
      throw error;
    }
  }
}
