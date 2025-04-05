import os
import logging
import json
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, LoraConfig, TaskType, PeftModel, PeftConfig
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_id = None
        self.model_path = None
        self.lora_config = None
        self.adapters_dir = os.path.join('data', 'adapters')
        self.models_dir = os.path.join('data', 'models')
        
        # Create necessary directories
        os.makedirs(self.adapters_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
    def is_model_loaded(self):
        """Check if a model is currently loaded."""
        return self.model is not None and self.tokenizer is not None
    
    def get_model_status(self):
        """Get the current status of the model."""
        if self.is_model_loaded():
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
        """Get detailed information about the currently loaded model."""
        if not self.is_model_loaded():
            return {"error": "No model is currently loaded"}
        
        # Get model size in MB
        model_size_mb = 0
        for param in self.model.parameters():
            model_size_mb += param.nelement() * param.element_size()
        model_size_mb = model_size_mb / (1024 * 1024)
        
        return {
            "name": self.model_id,
            "size": round(model_size_mb, 2),
            "path": self.model_path,
            "lastUpdated": time.time(),
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "has_adapters": hasattr(self.model, "peft_config")
        }
    
    def get_available_models(self):
        """Get a list of models available for download."""
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
        """Download a model to local storage."""
        # Create the model directory if it doesn't exist
        model_dir = os.path.join(self.models_dir, model_id)
        os.makedirs(model_dir, exist_ok=True)
        
        try:
            # In a real implementation, we would download the model from a remote server
            # For this implementation, we'll use HuggingFace models
            
            # Map our custom model IDs to actual HuggingFace model IDs
            huggingface_model_map = {
                "gpt2-psychpal-small": "gpt2",
                "distilgpt2-psychpal": "distilgpt2",
                "bert-psychpal-tiny": "prajjwal1/bert-tiny"
            }
            
            hf_model_id = huggingface_model_map.get(model_id, "gpt2")
            
            # Download the model and tokenizer (this will cache them locally)
            tokenizer = AutoTokenizer.from_pretrained(hf_model_id)
            model = AutoModelForCausalLM.from_pretrained(hf_model_id)
            
            # Save the model and tokenizer to the local directory
            model.save_pretrained(model_dir)
            tokenizer.save_pretrained(model_dir)
            
            # Create a model info file
            model_info = {
                "id": model_id,
                "original_model": hf_model_id,
                "download_time": time.time(),
                "path": model_dir
            }
            
            with open(os.path.join(model_dir, "model_info.json"), "w") as f:
                json.dump(model_info, f)
            
            logger.info(f"Downloaded model {model_id} to {model_dir}")
            
            return model_dir
            
        except Exception as e:
            logger.error(f"Error downloading model {model_id}: {str(e)}")
            raise
    
    def load_model(self, model_id, model_path):
        """Load a model from local storage."""
        try:
            # Load the tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # Load the base model
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
            
            # Move model to GPU if available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = self.model.to(device)
            
            # Configure LoRA for fine-tuning
            self.lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=16,  # rank of the update matrices
                lora_alpha=32,  # scaling factor
                lora_dropout=0.05,
                target_modules=["q_proj", "k_proj", "v_proj", "out_proj"],  # Which modules to apply LoRA to
                bias="none"
            )
            
            # Check for existing adapters for this model
            latest_adapter = self.get_latest_adapter_path()
            if latest_adapter:
                # Load the adapter
                logger.info(f"Loading adapter from {latest_adapter}")
                self.model = PeftModel.from_pretrained(self.model, latest_adapter)
            
            self.model_id = model_id
            self.model_path = model_path
            
            logger.info(f"Loaded model {model_id} from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {str(e)}")
            self.model = None
            self.tokenizer = None
            raise
    
    def generate_response(self, message, conversation_history):
        """Generate a response to a message using the loaded model."""
        if not self.is_model_loaded():
            raise ValueError("No model is loaded")
        
        try:
            # Format the conversation history for the model
            formatted_prompt = self._format_conversation(conversation_history)
            
            # Generate a response
            device = "cuda" if torch.cuda.is_available() else "cpu"
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(device)
            
            # Set generation parameters
            gen_kwargs = {
                "max_length": inputs["input_ids"].shape[1] + 100,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "repetition_penalty": 1.2,
                "do_sample": True,
                "pad_token_id": self.tokenizer.eos_token_id
            }
            
            # Generate response
            with torch.no_grad():
                output_sequences = self.model.generate(**inputs, **gen_kwargs)
            
            # Decode the generated response
            response = self.tokenizer.decode(output_sequences[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm having trouble processing your message right now. Could you try again?"
    
    def generate_response_from_messages(self, messages):
        """Generate a response from a list of messages."""
        if not self.is_model_loaded():
            raise ValueError("No model is loaded")
        
        try:
            # Format the messages for the model
            formatted_prompt = ""
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                
                if role == 'user':
                    formatted_prompt += f"User: {content}\n"
                elif role == 'assistant':
                    formatted_prompt += f"Assistant: {content}\n"
            
            formatted_prompt += "Assistant: "
            
            # Generate a response
            device = "cuda" if torch.cuda.is_available() else "cpu"
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(device)
            
            # Set generation parameters
            gen_kwargs = {
                "max_length": inputs["input_ids"].shape[1] + 100,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "repetition_penalty": 1.2,
                "do_sample": True,
                "pad_token_id": self.tokenizer.eos_token_id
            }
            
            # Generate response
            with torch.no_grad():
                output_sequences = self.model.generate(**inputs, **gen_kwargs)
            
            # Decode the generated response
            response = self.tokenizer.decode(output_sequences[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response from messages: {str(e)}")
            return "I'm having trouble processing your message right now. Could you try again?"
    
    def _format_conversation(self, conversation_history):
        """Format conversation history for the model."""
        formatted_prompt = ""
        for message in conversation_history:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'user':
                formatted_prompt += f"User: {content}\n"
            elif role == 'assistant':
                formatted_prompt += f"Assistant: {content}\n"
        
        # Add the assistant prefix for the next response
        formatted_prompt += "Assistant: "
        
        return formatted_prompt
    
    def prepare_training_data(self, conversations):
        """Prepare training data from conversations."""
        training_data = []
        
        for conversation in conversations:
            messages = conversation.get('messages', [])
            
            # Process messages to create training pairs
            for i in range(len(messages) - 1):
                # Only use message pairs where user asks and assistant responds
                if (messages[i].get('role') == 'user' and 
                    messages[i+1].get('role') == 'assistant'):
                    
                    training_data.append({
                        'input': messages[i].get('content', ''),
                        'output': messages[i+1].get('content', '')
                    })
        
        return training_data
    
    def train_epoch(self, training_data, batch_size=4, learning_rate=0.0001):
        """Train the model for one epoch on the provided data."""
        if not self.is_model_loaded():
            raise ValueError("No model is loaded")
        
        try:
            # Check if we're already using a PEFT model
            if not hasattr(self.model, "peft_config"):
                # Apply LoRA to the model
                logger.info("Applying LoRA adapter to the model")
                self.model = get_peft_model(self.model, self.lora_config)
                self.model.print_trainable_parameters()  # Log trainable parameters
            
            # Prepare the optimizer
            optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
            
            # Set the model to training mode
            self.model.train()
            device = next(self.model.parameters()).device
            
            # Process training data in batches
            total_loss = 0
            num_batches = 0
            
            # Simple batching
            for i in range(0, len(training_data), batch_size):
                batch = training_data[i:i+batch_size]
                
                # Prepare inputs and outputs
                batch_inputs = []
                batch_outputs = []
                
                for item in batch:
                    input_text = f"User: {item['input']}\nAssistant: "
                    output_text = item['output']
                    
                    batch_inputs.append(input_text)
                    batch_outputs.append(output_text)
                
                # Tokenize inputs
                inputs = self.tokenizer(batch_inputs, return_tensors="pt", padding=True, truncation=True)
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
                # Tokenize outputs and create labels
                labels = self.tokenizer(batch_outputs, return_tensors="pt", padding=True, truncation=True)
                labels = labels["input_ids"].to(device)
                
                # Forward pass
                outputs = self.model(**inputs, labels=labels)
                loss = outputs.loss
                
                # Backward pass and optimization
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                
                total_loss += loss.item()
                num_batches += 1
            
            # Calculate average loss
            avg_loss = total_loss / num_batches if num_batches > 0 else 0
            logger.info(f"Training epoch completed with average loss: {avg_loss}")
            
            return avg_loss
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise
    
    def save_trained_adapter(self):
        """Save the trained LoRA adapter."""
        if not self.is_model_loaded() or not hasattr(self.model, "peft_config"):
            raise ValueError("No trained adapter to save")
        
        try:
            # Create a timestamp-based directory name
            timestamp = int(time.time())
            adapter_dir = os.path.join(self.adapters_dir, f"{self.model_id}_adapter_{timestamp}")
            
            # Save the adapter
            self.model.save_pretrained(adapter_dir)
            logger.info(f"Saved trained adapter to {adapter_dir}")
            
            return adapter_dir
            
        except Exception as e:
            logger.error(f"Error saving trained adapter: {str(e)}")
            raise
    
    def get_latest_adapter_path(self):
        """Get the path to the most recently created adapter for the current model."""
        if not self.model_id:
            return None
        
        try:
            # List all adapters for this model
            prefix = f"{self.model_id}_adapter_"
            adapter_dirs = [
                d for d in os.listdir(self.adapters_dir) 
                if os.path.isdir(os.path.join(self.adapters_dir, d)) and d.startswith(prefix)
            ]
            
            if not adapter_dirs:
                return None
            
            # Sort by creation time (timestamp in the name)
            adapter_dirs.sort(reverse=True)
            latest_adapter = os.path.join(self.adapters_dir, adapter_dirs[0])
            
            return latest_adapter
            
        except Exception as e:
            logger.error(f"Error getting latest adapter path: {str(e)}")
            return None
    
    def extract_adapter_weights(self, adapter_path):
        """Extract weights from a trained adapter."""
        try:
            # Load the adapter config
            config = PeftConfig.from_pretrained(adapter_path)
            
            # Load the adapter weights
            adapter_weights = {}
            
            # Get the state dict file path
            state_dict_path = os.path.join(adapter_path, "adapter_model.bin")
            if not os.path.exists(state_dict_path):
                raise ValueError(f"Adapter state dict not found at {state_dict_path}")
            
            # Load the state dict
            state_dict = torch.load(state_dict_path, map_location="cpu")
            
            # Convert tensor weights to lists for easier serialization
            for key, tensor in state_dict.items():
                adapter_weights[key] = tensor.cpu().numpy().tolist()
            
            return adapter_weights
            
        except Exception as e:
            logger.error(f"Error extracting adapter weights: {str(e)}")
            raise
    
    def merge_server_weights(self, server_weights):
        """Merge server-provided weights into the current adapter."""
        if not self.is_model_loaded() or not hasattr(self.model, "peft_config"):
            raise ValueError("No adapter loaded to merge weights into")
        
        try:
            # Get the current adapter state dict
            state_dict = self.model.state_dict()
            
            # Convert server weights from lists back to tensors and merge
            for key, weight_list in server_weights.items():
                if key in state_dict:
                    # Convert the weight list back to a tensor
                    weight_tensor = torch.tensor(weight_list, dtype=state_dict[key].dtype)
                    
                    # Ensure the tensor has the same shape
                    if weight_tensor.shape == state_dict[key].shape:
                        # Merge weights (simple average)
                        state_dict[key] = (state_dict[key] + weight_tensor) / 2
                    else:
                        logger.warning(f"Shape mismatch for key {key}: expected {state_dict[key].shape}, got {weight_tensor.shape}")
            
            # Load the merged state dict back into the model
            self.model.load_state_dict(state_dict)
            
            # Save the updated adapter
            adapter_dir = self.save_trained_adapter()
            logger.info(f"Merged server weights and saved updated adapter to {adapter_dir}")
            
            return adapter_dir
            
        except Exception as e:
            logger.error(f"Error merging server weights: {str(e)}")
            raise
