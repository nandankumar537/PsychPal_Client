import os
import time
import json
import random
import uuid
import math

class MockModelService:
    def __init__(self):
        self.model_loaded = False
        self.current_model = None
        self.available_models = [
            {
                'id': 'minilm-health',
                'name': 'MiniLM Health Assistant',
                'description': 'A small, fast model fine-tuned for mental health assistance',
                'size': 120,  # Size in MB
                'parameters': '125M',
                'context_length': 2048,
                'speed': 'Fast'
            },
            {
                'id': 'distilgpt2-therapy',
                'name': 'DistilGPT2 Therapy',
                'description': 'Medium-sized model for therapeutic conversations',
                'size': 330,  # Size in MB
                'parameters': '355M',
                'context_length': 4096,
                'speed': 'Medium'
            },
            {
                'id': 'llama2-counselor',
                'name': 'Llama2 Counselor',
                'description': 'Large model with advanced counseling capabilities',
                'size': 980,  # Size in MB
                'parameters': '7B',
                'context_length': 8192,
                'speed': 'Slow'
            }
        ]
    
    def is_model_loaded(self):
        return self.model_loaded
    
    def get_model_status(self):
        return {
            'is_loaded': self.model_loaded,
            'model_id': self.current_model['id'] if self.model_loaded else None,
            'last_updated': time.time() if self.model_loaded else None
        }
    
    def get_model_info(self):
        if not self.model_loaded:
            return {
                'error': 'No model loaded'
            }
        
        return {
            'id': self.current_model['id'],
            'name': self.current_model['name'],
            'size': self.current_model['size'],
            'parameters': self.current_model['parameters'],
            'context_length': self.current_model['context_length'],
            'speed': self.current_model['speed'],
            'lastUpdated': time.time() - 3600  # 1 hour ago
        }
    
    def get_available_models(self):
        return self.available_models
    
    def download_model(self, model_id):
        # Find the model in available models
        model = next((m for m in self.available_models if m['id'] == model_id), None)
        if not model:
            raise ValueError(f"Model ID {model_id} not found")
        
        return True
    
    def load_model(self, model_id, model_path):
        # Find the model in available models
        model = next((m for m in self.available_models if m['id'] == model_id), None)
        if not model:
            raise ValueError(f"Model ID {model_id} not found")
        
        self.model_loaded = True
        self.current_model = model
        return True
    
    def generate_response(self, message, conversation_history):
        if not self.model_loaded:
            return "Model not loaded. Please download a model first."
        
        # Very simple response generation based on message content
        message_lower = message.lower()
        
        # Check for greeting
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! How are you feeling today?"
        
        # Check for emotion questions
        if any(emotion in message_lower for emotion in ['sad', 'depressed', 'unhappy', 'down']):
            return "I'm sorry to hear you're feeling that way. Depression and sadness are common emotions that everyone experiences. Would you like to talk more about what's causing these feelings?"
        
        if any(emotion in message_lower for emotion in ['anxious', 'nervous', 'worry', 'stressed']):
            return "Anxiety can be challenging to deal with. Have you tried any relaxation techniques like deep breathing or mindfulness meditation? These can sometimes help manage anxious feelings."
        
        if any(emotion in message_lower for emotion in ['happy', 'good', 'great', 'wonderful']):
            return "I'm glad to hear you're feeling positive! What's contributing to these good feelings today?"
        
        # Check for help-seeking
        if any(phrase in message_lower for phrase in ['help me', 'need help', 'advice', 'suggestion']):
            return "I'm here to help. To provide the most useful support, could you tell me more specifically what you're looking for help with?"
        
        # Check for questions about the app
        if any(phrase in message_lower for phrase in ['how do you work', 'what can you do', 'your capabilities']):
            return "I'm a privacy-focused mental health chatbot that runs locally on your device. I can have conversations about mental health topics, provide basic coping strategies, and offer a space for reflection. All your data stays on your device."
        
        # Default responses
        default_responses = [
            "I'm listening. Can you tell me more about that?",
            "That's interesting. How does that make you feel?",
            "Thank you for sharing. What other thoughts do you have about this?",
            "I understand. Have you considered looking at this from a different perspective?",
            "That sounds challenging. What do you think might help in this situation?"
        ]
        
        return random.choice(default_responses)
    
    def generate_response_from_messages(self, messages):
        if not self.model_loaded:
            return "Model not loaded. Please download a model first."
        
        # Extract the last message content
        if messages and len(messages) > 0:
            last_message = messages[-1].get('content', '')
            return self.generate_response(last_message, messages)
        
        return "I didn't receive any message. How can I help you today?"
    
    def prepare_training_data(self, conversations):
        # Simulate preparing training data from conversations
        training_samples = []
        
        if not conversations:
            # Create some dummy training data if no conversations provided
            return [{"input": "How are you?", "output": "I'm doing well, how about you?"}]
        
        for conversation in conversations:
            messages = conversation.get('messages', [])
            
            # Create input/output pairs from consecutive user/assistant messages
            for i in range(len(messages) - 1):
                if messages[i].get('role') == 'user' and messages[i+1].get('role') == 'assistant':
                    training_samples.append({
                        "input": messages[i].get('content', ''),
                        "output": messages[i+1].get('content', '')
                    })
        
        return training_samples or [{"input": "How are you?", "output": "I'm doing well, how about you?"}]
    
    def train_epoch(self, training_data, batch_size=4, learning_rate=0.0001):
        # Simulate training process
        if not training_data:
            raise ValueError("No training data provided")
        
        # Mock training logic
        time.sleep(1)  # Simulate training time
        
        return {
            "epoch_loss": round(random.uniform(0.1, 0.5), 4),
            "samples_processed": len(training_data)
        }
    
    def save_trained_adapter(self):
        # Simulate saving the adapter
        adapter_dir = os.path.join('data', 'adapters')
        os.makedirs(adapter_dir, exist_ok=True)
        
        adapter_name = f"{self.current_model['id']}_adapter_{int(time.time())}.bin"
        adapter_path = os.path.join(adapter_dir, adapter_name)
        
        # Create an empty file to simulate the adapter
        with open(adapter_path, 'w') as f:
            f.write("")
        
        return adapter_path
    
    def get_latest_adapter_path(self):
        # Simulate getting the latest adapter path
        adapter_dir = os.path.join('data', 'adapters')
        os.makedirs(adapter_dir, exist_ok=True)
        
        # Create a fake adapter path if none exists
        adapter_name = f"{self.current_model['id']}_adapter_{int(time.time())}.bin"
        adapter_path = os.path.join(adapter_dir, adapter_name)
        
        # Create an empty file to simulate the adapter if it doesn't exist
        if not os.path.exists(adapter_path):
            with open(adapter_path, 'w') as f:
                f.write("")
        
        return adapter_path
    
    def extract_adapter_weights(self, adapter_path):
        # Simulate extracting weights
        return {
            "layer.0.weight": [random.uniform(-0.1, 0.1) for _ in range(10)],
            "layer.0.bias": [random.uniform(-0.05, 0.05) for _ in range(10)],
            "layer.1.weight": [random.uniform(-0.1, 0.1) for _ in range(10)],
            "layer.1.bias": [random.uniform(-0.05, 0.05) for _ in range(10)]
        }
    
    def merge_server_weights(self, server_weights):
        # Simulate merging weights
        return True


class MockPrivacyService:
    def __init__(self):
        pass
    
    def add_noise_to_weights(self, weights, epsilon=2.0, delta=1e-5):
        # Simulate adding differential privacy noise to weights
        noisy_weights = {}
        
        for key, value in weights.items():
            if isinstance(value, list):
                # Determine noise scale based on epsilon and delta
                noise_scale = self._calculate_noise_scale(epsilon, delta, 1.0)
                
                # Add Gaussian noise to each weight
                noisy_weights[key] = [
                    w + random.gauss(0, noise_scale) for w in value
                ]
            else:
                noisy_weights[key] = value
        
        return noisy_weights
    
    def _calculate_noise_scale(self, epsilon, delta, sensitivity):
        # Simple approximation of Gaussian mechanism noise scale
        # In a real implementation, this would use the advanced composition theorem
        return sensitivity * math.sqrt(2 * math.log(1.25 / delta)) / epsilon
    
    def privatize_gradients(self, gradients, epsilon=2.0, delta=1e-5, clip_norm=1.0):
        # Simulate gradient clipping and noise addition
        clipped_gradients = self._clip_gradients(gradients, clip_norm)
        
        # Apply noise
        privatized_gradients = self.add_noise_to_weights(clipped_gradients, epsilon, delta)
        
        return privatized_gradients
    
    def _clip_gradients(self, gradients, clip_norm):
        # Simulate gradient clipping
        clipped = {}
        
        for key, value in gradients.items():
            if isinstance(value, list):
                # Calculate L2 norm
                norm = math.sqrt(sum(w**2 for w in value))
                
                # Clip if necessary
                if norm > clip_norm:
                    scale = clip_norm / norm
                    clipped[key] = [w * scale for w in value]
                else:
                    clipped[key] = value
            else:
                clipped[key] = value
        
        return clipped


class MockSyncService:
    def __init__(self, model_service, privacy_service):
        self.model_service = model_service
        self.privacy_service = privacy_service
        self.sync_schedule = "manual"
        self.last_sync = None
    
    def send_weights_to_server(self, weights):
        # Simulate server communication
        aggregated_weights = self._simulate_server_aggregation(weights)
        
        self.last_sync = time.time()
        
        return {
            "status": "success",
            "aggregated_weights": aggregated_weights,
            "participants": random.randint(5, 100),
            "server_round": random.randint(1, 50)
        }
    
    def _simulate_server_aggregation(self, client_weights):
        # Simulate the server aggregating weights from multiple clients
        aggregated = {}
        
        for key, value in client_weights.items():
            if isinstance(value, list):
                # Simulate averaging with other clients by adding small random changes
                aggregated[key] = [
                    w + random.uniform(-0.01, 0.01) for w in value
                ]
            else:
                aggregated[key] = value
        
        return aggregated
    
    def schedule_sync(self, frequency="manual"):
        valid_frequencies = ["manual", "daily", "weekly"]
        if frequency not in valid_frequencies:
            frequency = "manual"
        
        self.sync_schedule = frequency
        
        return {
            "status": "success",
            "frequency": frequency,
            "next_sync": self._calculate_next_sync(frequency)
        }
    
    def _calculate_next_sync(self, frequency):
        if frequency == "manual":
            return None
        
        now = time.time()
        if frequency == "daily":
            return now + 86400  # 24 hours
        elif frequency == "weekly":
            return now + 604800  # 7 days
        
        return None
    
    def check_server_connection(self):
        # Simulate connection check
        return True
    
    def get_server_status(self):
        return {
            "online": True,
            "version": "1.0.0",
            "participants": random.randint(50, 1000),
            "current_round": random.randint(1, 100),
            "last_update": time.time() - random.randint(0, 86400)
        }


class MockDatabase:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join('data', 'database', 'psychpal.db')
        self.conversations = {}
        self.model_metadata = {}
        self.training_metadata = []
        self.sync_metadata = []
        self.settings = {}
    
    def initialize(self):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Load existing data if available
        self._load_data()
        
        return True
    
    def _load_data(self):
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.conversations = data.get('conversations', {})
                    self.model_metadata = data.get('model_metadata', {})
                    self.training_metadata = data.get('training_metadata', [])
                    self.sync_metadata = data.get('sync_metadata', [])
                    self.settings = data.get('settings', {})
        except Exception:
            # If loading fails, use empty data
            pass
    
    def _save_data(self):
        data = {
            'conversations': self.conversations,
            'model_metadata': self.model_metadata,
            'training_metadata': self.training_metadata,
            'sync_metadata': self.sync_metadata,
            'settings': self.settings
        }
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with open(self.db_path, 'w') as f:
            json.dump(data, f)
    
    def save_conversation(self, conversation):
        if not conversation.get('id'):
            conversation['id'] = str(uuid.uuid4())
        
        self.conversations[conversation['id']] = conversation
        self._save_data()
        return True
    
    def get_conversation(self, conversation_id):
        return self.conversations.get(conversation_id)
    
    def delete_conversation(self, conversation_id):
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            self._save_data()
            return True
        return False
    
    def get_all_conversations(self):
        return list(self.conversations.values())
    
    def save_model_metadata(self, metadata):
        if not metadata.get('id'):
            metadata['id'] = str(uuid.uuid4())
        
        self.model_metadata = metadata
        self._save_data()
        return True
    
    def get_latest_model_metadata(self):
        return self.model_metadata
    
    def save_training_metadata(self, metadata):
        if not metadata.get('id'):
            metadata['id'] = str(uuid.uuid4())
        
        self.training_metadata.append(metadata)
        self._save_data()
        return True
    
    def get_training_stats(self):
        if not self.training_metadata:
            return {
                'total_sessions': 0,
                'last_training': None,
                'average_loss': 0,
                'total_samples': 0
            }
        
        total_sessions = len(self.training_metadata)
        last_training = max(meta.get('date', 0) for meta in self.training_metadata)
        total_samples = sum(meta.get('training_samples', 0) for meta in self.training_metadata)
        
        # Calculate a fake average loss
        average_loss = round(random.uniform(0.1, 0.5), 4)
        
        return {
            'total_sessions': total_sessions,
            'last_training': last_training,
            'average_loss': average_loss,
            'total_samples': total_samples
        }
    
    def save_sync_metadata(self, metadata):
        if not metadata.get('id'):
            metadata['id'] = str(uuid.uuid4())
        
        self.sync_metadata.append(metadata)
        self._save_data()
        return True
    
    def get_latest_sync_status(self):
        if not self.sync_metadata:
            return {
                'last_sync': None,
                'status': 'never',
                'total_syncs': 0
            }
        
        last_sync = max(meta.get('date', 0) for meta in self.sync_metadata)
        total_syncs = len(self.sync_metadata)
        
        return {
            'last_sync': last_sync,
            'status': 'success',
            'total_syncs': total_syncs
        }
    
    def get_sync_schedule(self):
        frequency = self.settings.get('sync_frequency', 'manual')
        
        next_sync = None
        if frequency == 'daily':
            next_sync = time.time() + 86400
        elif frequency == 'weekly':
            next_sync = time.time() + 604800
        
        return {
            'frequency': frequency,
            'next_sync': next_sync
        }
    
    def save_setting(self, key, value):
        self.settings[key] = value
        self._save_data()
        return True
    
    def get_setting(self, key, default=None):
        return self.settings.get(key, default)