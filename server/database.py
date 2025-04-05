import os
import json
import time
import logging
import sqlite3
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path=None):
        """
        Initialize the database service.
        
        Args:
            db_path (str, optional): The path to the SQLite database file.
                                    If None, defaults to 'data/database/psychpal.db'.
        """
        self.db_path = db_path or os.path.join('data', 'database', 'psychpal.db')
        self.connection = None
        self.lock = Lock()  # Thread safety lock
        
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def initialize(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create conversations table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at REAL,
                    updated_at REAL,
                    data TEXT
                )
                ''')
                
                # Create model_metadata table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_metadata (
                    id TEXT PRIMARY KEY,
                    status TEXT,
                    path TEXT,
                    download_time REAL,
                    data TEXT
                )
                ''')
                
                # Create training_metadata table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_metadata (
                    id TEXT PRIMARY KEY,
                    epochs INTEGER,
                    batch_size INTEGER,
                    learning_rate REAL,
                    num_examples INTEGER,
                    adapter_path TEXT,
                    completion_time REAL,
                    data TEXT
                )
                ''')
                
                # Create sync_metadata table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_metadata (
                    id TEXT PRIMARY KEY,
                    privacy_epsilon REAL,
                    privacy_delta REAL,
                    sync_frequency TEXT,
                    adapter_path TEXT,
                    completion_time REAL,
                    data TEXT
                )
                ''')
                
                # Create settings table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at REAL
                )
                ''')
                
                conn.commit()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def get_connection(self):
        """Get a connection to the SQLite database."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Set row factory to return rows as dictionaries
            self.connection.row_factory = self._dict_factory
        
        return self.connection
    
    def _dict_factory(self, cursor, row):
        """Convert SQLite row objects to dictionaries."""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def save_conversation(self, conversation):
        """
        Save a conversation to the database.
        
        Args:
            conversation (dict): The conversation to save.
            
        Returns:
            bool: True if successful.
        """
        try:
            conversation_id = conversation.get('id')
            if not conversation_id:
                raise ValueError("Conversation must have an 'id' field")
            
            # Prepare the data to save
            title = conversation.get('title', 'Conversation')
            created_at = conversation.get('createdAt', time.time())
            updated_at = time.time()
            
            # Serialize the entire conversation object
            conversation_json = json.dumps(conversation)
            
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert or update the conversation
                cursor.execute('''
                INSERT OR REPLACE INTO conversations (id, title, created_at, updated_at, data)
                VALUES (?, ?, ?, ?, ?)
                ''', (conversation_id, title, created_at, updated_at, conversation_json))
                
                conn.commit()
            
            logger.info(f"Saved conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            raise
    
    def get_conversation(self, conversation_id):
        """
        Get a conversation by ID.
        
        Args:
            conversation_id (str): The ID of the conversation.
            
        Returns:
            dict: The conversation, or None if not found.
        """
        try:
            if not conversation_id:
                return None
            
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT data FROM conversations WHERE id = ?
                ''', (conversation_id,))
                
                result = cursor.fetchone()
            
            if result and 'data' in result:
                conversation = json.loads(result['data'])
                return conversation
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {str(e)}")
            return None
    
    def delete_conversation(self, conversation_id):
        """
        Delete a conversation by ID.
        
        Args:
            conversation_id (str): The ID of the conversation.
            
        Returns:
            bool: True if successful.
        """
        try:
            if not conversation_id:
                return False
            
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                DELETE FROM conversations WHERE id = ?
                ''', (conversation_id,))
                
                conn.commit()
            
            logger.info(f"Deleted conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
            return False
    
    def get_all_conversations(self):
        """
        Get all conversations.
        
        Returns:
            list: A list of all conversations.
        """
        try:
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT data FROM conversations ORDER BY updated_at DESC
                ''')
                
                results = cursor.fetchall()
            
            conversations = []
            for result in results:
                if 'data' in result:
                    conversation = json.loads(result['data'])
                    conversations.append(conversation)
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting all conversations: {str(e)}")
            return []
    
    def save_model_metadata(self, metadata):
        """
        Save model metadata to the database.
        
        Args:
            metadata (dict): The model metadata to save.
            
        Returns:
            bool: True if successful.
        """
        try:
            model_id = metadata.get('id')
            if not model_id:
                raise ValueError("Model metadata must have an 'id' field")
            
            status = metadata.get('status', 'unknown')
            path = metadata.get('path', '')
            download_time = metadata.get('download_time', time.time())
            
            # Serialize the entire metadata object
            metadata_json = json.dumps(metadata)
            
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT OR REPLACE INTO model_metadata (id, status, path, download_time, data)
                VALUES (?, ?, ?, ?, ?)
                ''', (model_id, status, path, download_time, metadata_json))
                
                conn.commit()
            
            logger.info(f"Saved model metadata for {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model metadata: {str(e)}")
            raise
    
    def get_latest_model_metadata(self):
        """
        Get the most recently downloaded model's metadata.
        
        Returns:
            dict: The model metadata, or None if not found.
        """
        try:
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT data FROM model_metadata 
                ORDER BY download_time DESC 
                LIMIT 1
                ''')
                
                result = cursor.fetchone()
            
            if result and 'data' in result:
                metadata = json.loads(result['data'])
                return metadata
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest model metadata: {str(e)}")
            return None
    
    def save_training_metadata(self, metadata):
        """
        Save training metadata to the database.
        
        Args:
            metadata (dict): The training metadata to save.
            
        Returns:
            bool: True if successful.
        """
        try:
            training_id = metadata.get('id')
            if not training_id:
                raise ValueError("Training metadata must have an 'id' field")
            
            epochs = metadata.get('epochs', 0)
            batch_size = metadata.get('batch_size', 0)
            learning_rate = metadata.get('learning_rate', 0)
            num_examples = metadata.get('num_examples', 0)
            adapter_path = metadata.get('adapter_path', '')
            completion_time = metadata.get('completion_time', time.time())
            
            # Serialize the entire metadata object
            metadata_json = json.dumps(metadata)
            
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT OR REPLACE INTO training_metadata 
                (id, epochs, batch_size, learning_rate, num_examples, adapter_path, completion_time, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (training_id, epochs, batch_size, learning_rate, num_examples, adapter_path, completion_time, metadata_json))
                
                conn.commit()
            
            logger.info(f"Saved training metadata for {training_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving training metadata: {str(e)}")
            raise
    
    def get_training_stats(self):
        """
        Get training statistics from the database.
        
        Returns:
            dict: Training statistics.
        """
        try:
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get total number of training sessions
                cursor.execute('SELECT COUNT(*) as count FROM training_metadata')
                count_result = cursor.fetchone()
                total_sessions = count_result['count'] if count_result else 0
                
                # Get most recent training session
                cursor.execute('''
                SELECT data FROM training_metadata 
                ORDER BY completion_time DESC 
                LIMIT 1
                ''')
                latest_result = cursor.fetchone()
                
                # Get model performance statistics
                # In a real implementation, this would be calculated or stored separately
                # Here we'll use placeholder values
                model_perplexity = None
                model_loss = None
                
                if latest_result and 'data' in latest_result:
                    latest_metadata = json.loads(latest_result['data'])
                    # If this metadata included performance metrics, we would extract them here
                
                stats = {
                    'total_training_sessions': total_sessions,
                    'last_training_time': latest_metadata['completion_time'] if latest_result else None,
                    'model_performance': {
                        'perplexity': model_perplexity,
                        'loss': model_loss
                    }
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting training stats: {str(e)}")
            return {
                'total_training_sessions': 0,
                'last_training_time': None,
                'model_performance': {
                    'perplexity': None,
                    'loss': None
                }
            }
    
    def save_sync_metadata(self, metadata):
        """
        Save synchronization metadata to the database.
        
        Args:
            metadata (dict): The sync metadata to save.
            
        Returns:
            bool: True if successful.
        """
        try:
            sync_id = metadata.get('id')
            if not sync_id:
                raise ValueError("Sync metadata must have an 'id' field")
            
            privacy_epsilon = metadata.get('privacy_epsilon', 0)
            privacy_delta = metadata.get('privacy_delta', 0)
            sync_frequency = metadata.get('sync_frequency', 'manual')
            adapter_path = metadata.get('adapter_path', '')
            completion_time = metadata.get('completion_time', time.time())
            
            # Serialize the entire metadata object
            metadata_json = json.dumps(metadata)
            
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT OR REPLACE INTO sync_metadata 
                (id, privacy_epsilon, privacy_delta, sync_frequency, adapter_path, completion_time, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (sync_id, privacy_epsilon, privacy_delta, sync_frequency, adapter_path, completion_time, metadata_json))
                
                conn.commit()
            
            logger.info(f"Saved sync metadata for {sync_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving sync metadata: {str(e)}")
            raise
    
    def get_latest_sync_status(self):
        """
        Get the latest synchronization status.
        
        Returns:
            dict: The sync status.
        """
        try:
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT data FROM sync_metadata 
                ORDER BY completion_time DESC 
                LIMIT 1
                ''')
                
                result = cursor.fetchone()
            
            if result and 'data' in result:
                sync_metadata = json.loads(result['data'])
                
                # Extract the server response from the metadata
                server_response = sync_metadata.get('server_response', {})
                
                return {
                    'last_sync_time': sync_metadata.get('completion_time'),
                    'sync_successful': server_response.get('status') == 'success',
                    'gradient_updates_sent': 1,  # In a real implementation, this would be tracked
                    'server_updates_received': 1 if 'updated_weights' in server_response else 0
                }
            
            return {
                'last_sync_time': None,
                'sync_successful': False,
                'gradient_updates_sent': 0,
                'server_updates_received': 0
            }
            
        except Exception as e:
            logger.error(f"Error getting latest sync status: {str(e)}")
            return {
                'last_sync_time': None,
                'sync_successful': False,
                'gradient_updates_sent': 0,
                'server_updates_received': 0
            }
    
    def get_sync_schedule(self):
        """
        Get the current synchronization schedule.
        
        Returns:
            dict: The sync schedule.
        """
        try:
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get the most recent sync metadata to determine the schedule
                cursor.execute('''
                SELECT data FROM sync_metadata 
                ORDER BY completion_time DESC 
                LIMIT 1
                ''')
                
                result = cursor.fetchone()
            
            if result and 'data' in result:
                sync_metadata = json.loads(result['data'])
                frequency = sync_metadata.get('sync_frequency', 'manual')
                
                # Calculate next sync time based on frequency
                last_sync_time = sync_metadata.get('completion_time')
                next_sync_time = None
                
                if last_sync_time:
                    if frequency == 'daily':
                        next_sync_time = last_sync_time + (24 * 60 * 60)  # 24 hours
                    elif frequency == 'weekly':
                        next_sync_time = last_sync_time + (7 * 24 * 60 * 60)  # 7 days
                
                return {
                    'frequency': frequency,
                    'next_sync_time': next_sync_time,
                    'enabled': frequency != 'manual'
                }
            
            # Default schedule if none found
            return {
                'frequency': 'manual',
                'next_sync_time': None,
                'enabled': False
            }
            
        except Exception as e:
            logger.error(f"Error getting sync schedule: {str(e)}")
            return {
                'frequency': 'manual',
                'next_sync_time': None,
                'enabled': False
            }
    
    def save_setting(self, key, value):
        """
        Save a setting to the database.
        
        Args:
            key (str): The setting key.
            value: The setting value (will be JSON serialized).
            
        Returns:
            bool: True if successful.
        """
        try:
            # Serialize the value to JSON if it's not a string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            updated_at = time.time()
            
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ''', (key, value, updated_at))
                
                conn.commit()
            
            logger.info(f"Saved setting {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving setting {key}: {str(e)}")
            raise
    
    def get_setting(self, key, default=None):
        """
        Get a setting from the database.
        
        Args:
            key (str): The setting key.
            default: The default value to return if the setting doesn't exist.
            
        Returns:
            The setting value.
        """
        try:
            with self.lock, self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT value FROM settings WHERE key = ?
                ''', (key,))
                
                result = cursor.fetchone()
            
            if result and 'value' in result:
                value = result['value']
                
                # Try to parse as JSON, return as-is if not valid JSON
                try:
                    return json.loads(value)
                except:
                    return value
            
            return default
            
        except Exception as e:
            logger.error(f"Error getting setting {key}: {str(e)}")
            return default
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
