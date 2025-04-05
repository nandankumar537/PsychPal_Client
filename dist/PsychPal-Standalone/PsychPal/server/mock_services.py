import os
import logging
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockModelService:
    def __init__(self):
        self.model_loaded = False
        self.model_id = None
        self.model_path = None
    
    def is_model_loaded(self):
        return self.model_loaded
    
    def get_model_status(self):
        if self.model_loaded:
            return {
                "is_loaded": True,
                "model_info": {
                    "id": self.model_id,
                    "path": self.model_path
                }
            }
        else:
            return {"is_loaded": False}
    
    def get_model_info(self):
        if not self.model_loaded:
            return {"error": "No model is currently loaded"}
        
        return {
            "name": self.model_id,
            "size": 500,
            "path": self.model_path,
            "lastUpdated": time.time(),
            "parameters": 125000000,
            "has_adapters": False
        }
    
    def get_available_models(self):
        return [
            {
                "id": "gpt2-psychpal-small",
                "name": "PsychPal Small (GPT-2)",
                "description": "Lightweight model for mental health conversations",
                "size": "500"
            },
            {
                "id": "distilgpt2-psychpal",
                "name": "PsychPal DistilGPT-2",
                "description": "Balanced model for mental health support",
                "size": "300"
            },
            {
                "id": "bert-psychpal-tiny",
                "name": "PsychPal Tiny (BERT)",
                "description": "Very small model for basic support",
                "size": "100"
            }
        ]
    
    def download_model(self, model_id):
        logger.info(f"Mock downloading model {model_id}")
        model_dir = os.path.join('data', 'models', model_id)
        os.makedirs(model_dir, exist_ok=True)
        return model_dir
    
    def load_model(self, model_id, model_path):
        logger.info(f"Mock loading model {model_id} from {model_path}")
        self.model_loaded = True
        self.model_id = model_id
        self.model_path = model_path
        return True
    
    def generate_response(self, message, conversation_history):
        if not self.model_loaded:
            raise ValueError("No model is loaded")
        
        # Generate a simple response based on the message
        responses = {
            "hello": "Hello! How are you feeling today?",
            "hi": "Hi there! How can I help you today?",
            "how are you": "I'm just a program, but I'm here to help you. How are you feeling?",
            "feeling sad": "I'm sorry to hear that you're feeling sad. Would you like to talk about what's bothering you?",
            "feeling anxious": "Anxiety can be challenging. Can you tell me more about what's making you anxious?",
            "feeling depressed": "I'm sorry you're feeling depressed. Have you been experiencing this for a while?",
            "help": "I'm here to listen and support you. What's on your mind?",
            "thank you": "You're welcome! Is there anything else you'd like to talk about?",
            "bye": "Take care of yourself. Remember that it's okay to reach out whenever you need support."
        }
        
        # Check if the message contains any of the keys
        for key, response in responses.items():
            if key.lower() in message.lower():
                return response
        
        # Default response
        return "I'm here to listen and support you. Please tell me more about what's on your mind."
    
    def generate_response_from_messages(self, messages):
        if not self.model_loaded:
            raise ValueError("No model is loaded")
        
        # Extract the last user message if available
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        # Generate response using the extracted message
        return self.generate_response(user_message, messages)
    
    def prepare_training_data(self, conversations):
        training_data = []
        
        for conversation in conversations:
            messages = conversation.get('messages', [])
            
            for i in range(len(messages) - 1):
                if (messages[i].get('role') == 'user' and 
                    messages[i+1].get('role') == 'assistant'):
                    
                    training_data.append({
                        'input': messages[i].get('content', ''),
                        'output': messages[i+1].get('content', '')
                    })
        
        return training_data
    
    def train_epoch(self, training_data, batch_size=4, learning_rate=0.0001):
        logger.info(f"Mock training with {len(training_data)} examples, batch_size={batch_size}, lr={learning_rate}")
        return 0.5  # Mock loss value
    
    def save_trained_adapter(self):
        adapter_dir = os.path.join('data', 'adapters', f"{self.model_id}_adapter_{int(time.time())}")
        os.makedirs(adapter_dir, exist_ok=True)
        logger.info(f"Mock saving adapter to {adapter_dir}")
        return adapter_dir
    
    def get_latest_adapter_path(self):
        if not self.model_id:
            return None
        
        # Mock path
        return os.path.join('data', 'adapters', f"{self.model_id}_adapter_latest")
    
    def extract_adapter_weights(self, adapter_path):
        logger.info(f"Mock extracting weights from {adapter_path}")
        return {"weight1": [0.1, 0.2, 0.3], "weight2": [0.4, 0.5, 0.6]}
    
    def merge_server_weights(self, server_weights):
        logger.info("Mock merging server weights")
        return True


class MockPrivacyService:
    def __init__(self):
        pass
    
    def add_noise_to_weights(self, weights, epsilon=2.0, delta=1e-5):
        logger.info(f"Mock adding privacy noise with epsilon={epsilon}, delta={delta}")
        # Return the same weights with minimal changes to simulate privacy
        return {k: [v + 0.01 for v in vals] if isinstance(vals, list) else vals 
                for k, vals in weights.items()}
    
    def privatize_gradients(self, gradients, epsilon=2.0, delta=1e-5, clip_norm=1.0):
        logger.info(f"Mock privatizing gradients with epsilon={epsilon}, delta={delta}, clip_norm={clip_norm}")
        # Return the same gradients with minimal changes
        return {k: [v + 0.01 for v in vals] if isinstance(vals, list) else vals 
                for k, vals in gradients.items()}


class MockSyncService:
    def __init__(self, model_service, privacy_service):
        self.model_service = model_service
        self.privacy_service = privacy_service
    
    def send_weights_to_server(self, weights):
        logger.info("Mock sending weights to server")
        
        time.sleep(1)  # Simulate network delay
        
        return {
            "status": "success",
            "message": "Weights received and processed successfully",
            "timestamp": time.time(),
            "updates_applied": True,
            "client_contribution_id": f"contrib_{int(time.time())}",
            "updated_weights": weights  # Just return the same weights
        }
    
    def schedule_sync(self, frequency="manual"):
        logger.info(f"Mock scheduling sync with frequency: {frequency}")
        
        next_sync_time = None
        if frequency == "daily":
            next_sync_time = time.time() + (24 * 60 * 60)
        elif frequency == "weekly":
            next_sync_time = time.time() + (7 * 24 * 60 * 60)
        
        return {
            "frequency": frequency,
            "next_sync_time": next_sync_time,
            "enabled": frequency != "manual"
        }
    
    def check_server_connection(self):
        return True
    
    def get_server_status(self):
        return {
            "status": "online",
            "message": "Server is operational",
            "timestamp": time.time(),
            "maintenance_scheduled": False,
            "client_version_supported": True,
            "total_clients": 1500,
            "active_clients_24h": 750
        }


class MockDatabase:
    def __init__(self, db_path=None):
        self.conversations = {}
        self.model_metadata = {}
        self.training_metadata = []
        self.sync_metadata = []
        self.settings = {}
    
    def initialize(self):
        logger.info("Mock database initialized")
        return True
    
    def save_conversation(self, conversation):
        conversation_id = conversation.get('id')
        if not conversation_id:
            raise ValueError("Conversation must have an 'id' field")
        
        self.conversations[conversation_id] = conversation
        logger.info(f"Mock saved conversation {conversation_id}")
        return True
    
    def get_conversation(self, conversation_id):
        if not conversation_id or conversation_id not in self.conversations:
            return None
        
        return self.conversations.get(conversation_id)
    
    def delete_conversation(self, conversation_id):
        if not conversation_id or conversation_id not in self.conversations:
            return False
        
        del self.conversations[conversation_id]
        logger.info(f"Mock deleted conversation {conversation_id}")
        return True
    
    def get_all_conversations(self):
        return list(self.conversations.values())
    
    def save_model_metadata(self, metadata):
        model_id = metadata.get('id')
        if not model_id:
            raise ValueError("Model metadata must have an 'id' field")
        
        self.model_metadata[model_id] = metadata
        logger.info(f"Mock saved model metadata for {model_id}")
        return True
    
    def get_latest_model_metadata(self):
        if not self.model_metadata:
            return None
        
        # Just return the last one added
        last_key = list(self.model_metadata.keys())[-1]
        return self.model_metadata[last_key]
    
    def save_training_metadata(self, metadata):
        training_id = metadata.get('id')
        if not training_id:
            raise ValueError("Training metadata must have an 'id' field")
        
        self.training_metadata.append(metadata)
        logger.info(f"Mock saved training metadata for {training_id}")
        return True
    
    def get_training_stats(self):
        stats = {
            'total_training_sessions': len(self.training_metadata),
            'last_training_time': self.training_metadata[-1]['completion_time'] if self.training_metadata else None,
            'model_performance': {
                'perplexity': None,
                'loss': 0.5 if self.training_metadata else None
            }
        }
        return stats
    
    def save_sync_metadata(self, metadata):
        sync_id = metadata.get('id')
        if not sync_id:
            raise ValueError("Sync metadata must have an 'id' field")
        
        self.sync_metadata.append(metadata)
        logger.info(f"Mock saved sync metadata for {sync_id}")
        return True
    
    def get_latest_sync_status(self):
        if not self.sync_metadata:
            return {
                'last_sync_time': None,
                'sync_successful': False,
                'gradient_updates_sent': 0,
                'server_updates_received': 0
            }
        
        latest_sync = self.sync_metadata[-1]
        return {
            'last_sync_time': latest_sync['completion_time'],
            'sync_successful': True,
            'gradient_updates_sent': 100,
            'server_updates_received': 50
        }
    
    def get_sync_schedule(self):
        freq = self.settings.get('sync_frequency', 'manual')
        next_time = None
        
        if freq == 'daily':
            next_time = time.time() + (24 * 60 * 60)
        elif freq == 'weekly':
            next_time = time.time() + (7 * 24 * 60 * 60)
        
        return {
            'frequency': freq,
            'next_sync_time': next_time,
            'enabled': freq != 'manual'
        }
    
    def save_setting(self, key, value):
        self.settings[key] = value
        logger.info(f"Mock saved setting {key}")
        return True
    
    def get_setting(self, key, default=None):
        return self.settings.get(key, default)