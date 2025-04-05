export class DatabaseService {
  static db = null;
  static DB_NAME = 'psychpal_db';
  static DB_VERSION = 1;
  
  // Initialize the database
  static async initialize() {
    if (this.db) {
      return this.db;
    }
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);
      
      request.onerror = (event) => {
        console.error('Database error:', event.target.error);
        reject('Could not open database');
      };
      
      request.onsuccess = (event) => {
        this.db = event.target.result;
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create conversations store
        if (!db.objectStoreNames.contains('conversations')) {
          const conversationsStore = db.createObjectStore('conversations', { keyPath: 'id' });
          conversationsStore.createIndex('createdAt', 'createdAt', { unique: false });
        }
        
        // Create settings store
        if (!db.objectStoreNames.contains('settings')) {
          db.createObjectStore('settings', { keyPath: 'id' });
        }
        
        // Create model store
        if (!db.objectStoreNames.contains('models')) {
          db.createObjectStore('models', { keyPath: 'id' });
        }
      };
    });
  }
  
  // Save a conversation to the database
  static async saveConversation(conversation) {
    await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['conversations'], 'readwrite');
      const store = transaction.objectStore('conversations');
      
      // Ensure conversation has createdAt
      if (!conversation.createdAt) {
        conversation.createdAt = new Date().toISOString();
      }
      
      // Add updatedAt
      conversation.updatedAt = new Date().toISOString();
      
      const request = store.put(conversation);
      
      request.onsuccess = () => {
        resolve(conversation);
      };
      
      request.onerror = (event) => {
        console.error('Error saving conversation:', event.target.error);
        reject('Failed to save conversation');
      };
    });
  }
  
  // Get all conversations
  static async getConversations() {
    await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['conversations'], 'readonly');
      const store = transaction.objectStore('conversations');
      const index = store.index('createdAt');
      
      const request = index.openCursor(null, 'prev'); // Get in reverse chronological order
      const conversations = [];
      
      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor) {
          conversations.push(cursor.value);
          cursor.continue();
        } else {
          resolve(conversations);
        }
      };
      
      request.onerror = (event) => {
        console.error('Error getting conversations:', event.target.error);
        reject('Failed to get conversations');
      };
    });
  }
  
  // Get a specific conversation by ID
  static async getConversation(id) {
    await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['conversations'], 'readonly');
      const store = transaction.objectStore('conversations');
      const request = store.get(id);
      
      request.onsuccess = (event) => {
        resolve(request.result);
      };
      
      request.onerror = (event) => {
        console.error('Error getting conversation:', event.target.error);
        reject('Failed to get conversation');
      };
    });
  }
  
  // Delete a conversation
  static async deleteConversation(id) {
    await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['conversations'], 'readwrite');
      const store = transaction.objectStore('conversations');
      const request = store.delete(id);
      
      request.onsuccess = () => {
        resolve(true);
      };
      
      request.onerror = (event) => {
        console.error('Error deleting conversation:', event.target.error);
        reject('Failed to delete conversation');
      };
    });
  }
  
  // Save a setting
  static async saveSetting(key, value) {
    await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['settings'], 'readwrite');
      const store = transaction.objectStore('settings');
      
      const request = store.put({
        id: key,
        value,
        updatedAt: new Date().toISOString()
      });
      
      request.onsuccess = () => {
        resolve(true);
      };
      
      request.onerror = (event) => {
        console.error('Error saving setting:', event.target.error);
        reject('Failed to save setting');
      };
    });
  }
  
  // Get a setting
  static async getSetting(key) {
    await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['settings'], 'readonly');
      const store = transaction.objectStore('settings');
      const request = store.get(key);
      
      request.onsuccess = (event) => {
        resolve(request.result ? request.result.value : null);
      };
      
      request.onerror = (event) => {
        console.error('Error getting setting:', event.target.error);
        reject('Failed to get setting');
      };
    });
  }
  
  // Save model metadata
  static async saveModelMetadata(modelInfo) {
    await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['models'], 'readwrite');
      const store = transaction.objectStore('models');
      
      // Ensure model has updatedAt
      modelInfo.updatedAt = new Date().toISOString();
      
      const request = store.put(modelInfo);
      
      request.onsuccess = () => {
        resolve(true);
      };
      
      request.onerror = (event) => {
        console.error('Error saving model metadata:', event.target.error);
        reject('Failed to save model metadata');
      };
    });
  }
  
  // Get model metadata
  static async getModelMetadata(modelId) {
    await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['models'], 'readonly');
      const store = transaction.objectStore('models');
      const request = store.get(modelId);
      
      request.onsuccess = (event) => {
        resolve(request.result);
      };
      
      request.onerror = (event) => {
        console.error('Error getting model metadata:', event.target.error);
        reject('Failed to get model metadata');
      };
    });
  }
}
