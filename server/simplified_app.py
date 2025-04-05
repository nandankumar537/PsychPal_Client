from flask import Flask, request, jsonify
import os
import logging
from flask_cors import CORS
import threading
import uuid
import time
import json

# Import mock services for demo
from mock_services import MockModelService, MockPrivacyService, MockSyncService, MockDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Initialize services with mock implementations
model_service = MockModelService()
privacy_service = MockPrivacyService()
sync_service = MockSyncService(model_service, privacy_service)
database = MockDatabase()

# Store download, training, and sync tasks
download_tasks = {}
training_tasks = {}
sync_tasks = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get conversation history from the database
        conversation = database.get_conversation(conversation_id)
        if not conversation:
            # Create a new conversation if it doesn't exist
            conversation = {
                'id': conversation_id,
                'messages': []
            }
        
        # Add user message to the conversation
        conversation['messages'].append({
            'role': 'user',
            'content': message,
            'timestamp': time.time()
        })
        
        # Get response from the model
        response = model_service.generate_response(message, conversation['messages'])
        
        # Add assistant's response to the conversation
        conversation['messages'].append({
            'role': 'assistant',
            'content': response,
            'timestamp': time.time()
        })
        
        # Save the updated conversation
        database.save_conversation(conversation)
        
        return jsonify({"response": response})
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/model/status', methods=['GET'])
def model_status():
    try:
        status = model_service.get_model_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error in model status endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/model/info', methods=['GET'])
def model_info():
    try:
        info = model_service.get_model_info()
        return jsonify(info)
    except Exception as e:
        logger.error(f"Error in model info endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/model/available', methods=['GET'])
def available_models():
    try:
        models = model_service.get_available_models()
        return jsonify(models)
    except Exception as e:
        logger.error(f"Error in available models endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/model/download', methods=['POST'])
def download_model():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        model_id = data.get('model_id')
        if not model_id:
            return jsonify({"error": "No model_id provided"}), 400
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Start download in a background thread
        def download_task():
            try:
                download_tasks[task_id]['status'] = 'in_progress'
                download_tasks[task_id]['progress'] = 0
                
                # Simulate download progress
                for i in range(1, 21):
                    if task_id not in download_tasks:  # Task was cancelled
                        return
                    
                    # Update progress (5% increments)
                    progress = i * 5
                    download_tasks[task_id]['progress'] = progress
                    time.sleep(0.2)  # Simulate work faster for demo
                
                # Perform the actual model download
                model_path = model_service.download_model(model_id)
                
                download_tasks[task_id]['status'] = 'completed'
                download_tasks[task_id]['progress'] = 100
                download_tasks[task_id]['model_path'] = model_path
                
                # Update model status in the database
                database.save_model_metadata({
                    'id': model_id,
                    'status': 'loaded',
                    'path': model_path,
                    'download_time': time.time()
                })
                
                # Load the model
                model_service.load_model(model_id, model_path)
                
            except Exception as e:
                logger.error(f"Error in download task: {str(e)}")
                if task_id in download_tasks:
                    download_tasks[task_id]['status'] = 'failed'
                    download_tasks[task_id]['error'] = str(e)
        
        # Store task info
        download_tasks[task_id] = {
            'model_id': model_id,
            'status': 'starting',
            'progress': 0,
            'start_time': time.time()
        }
        
        # Start the download thread
        threading.Thread(target=download_task).start()
        
        return jsonify({
            "message": "Model download started",
            "download_id": task_id
        })
        
    except Exception as e:
        logger.error(f"Error in download model endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/model/download/<task_id>/progress', methods=['GET'])
def download_progress(task_id):
    try:
        if task_id not in download_tasks:
            return jsonify({"error": "Download task not found"}), 404
        
        return jsonify(download_tasks[task_id])
    
    except Exception as e:
        logger.error(f"Error in download progress endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/model/inference', methods=['POST'])
def model_inference():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        messages = data.get('messages', [])
        
        # Generate response using the model
        response = model_service.generate_response_from_messages(messages)
        
        return jsonify({"response": response})
    
    except Exception as e:
        logger.error(f"Error in model inference endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/train', methods=['POST'])
def start_training():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        training_data = data.get('training_data', [])
        settings = data.get('settings', {})
        
        # Ensure model is loaded
        if not model_service.is_model_loaded():
            return jsonify({"error": "No model loaded for training"}), 400
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Start training in a background thread
        def training_task():
            try:
                training_tasks[task_id]['status'] = 'in_progress'
                training_tasks[task_id]['progress'] = 0
                
                # Train the model with LoRA/PEFT
                num_epochs = settings.get('num_epochs', 1)
                batch_size = settings.get('batch_size', 4)
                learning_rate = settings.get('learning_rate', 0.0001)
                use_local_data = settings.get('use_local_data', True)
                
                # If using local data but none provided, load from database
                if use_local_data and not training_data:
                    conversations = database.get_all_conversations()
                    training_data = model_service.prepare_training_data(conversations)
                
                if not training_data:
                    raise ValueError("No training data available")
                
                # Fine-tune the model with LoRA
                for epoch in range(num_epochs):
                    epoch_progress = (epoch / num_epochs) * 100
                    training_tasks[task_id]['progress'] = epoch_progress
                    training_tasks[task_id]['current_epoch'] = epoch + 1
                    training_tasks[task_id]['total_epochs'] = num_epochs
                    
                    # Perform one epoch of training
                    model_service.train_epoch(
                        training_data, 
                        batch_size=batch_size, 
                        learning_rate=learning_rate
                    )
                    
                    # Add a small delay to simulate work
                    time.sleep(0.5)
                
                # Save the trained adapter
                adapter_path = model_service.save_trained_adapter()
                
                training_tasks[task_id]['status'] = 'completed'
                training_tasks[task_id]['progress'] = 100
                training_tasks[task_id]['adapter_path'] = adapter_path
                
                # Save training metadata to the database
                database.save_training_metadata({
                    'id': task_id,
                    'epochs': num_epochs,
                    'batch_size': batch_size,
                    'learning_rate': learning_rate,
                    'num_examples': len(training_data),
                    'adapter_path': adapter_path,
                    'completion_time': time.time()
                })
                
            except Exception as e:
                logger.error(f"Error in training task: {str(e)}")
                if task_id in training_tasks:
                    training_tasks[task_id]['status'] = 'failed'
                    training_tasks[task_id]['error'] = str(e)
        
        # Store task info
        training_tasks[task_id] = {
            'status': 'starting',
            'progress': 0,
            'start_time': time.time(),
            'settings': settings
        }
        
        # Start the training thread
        threading.Thread(target=training_task).start()
        
        return jsonify({
            "message": "Training started",
            "training_id": task_id
        })
        
    except Exception as e:
        logger.error(f"Error in start training endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/train/<task_id>/progress', methods=['GET'])
def training_progress(task_id):
    try:
        if task_id not in training_tasks:
            return jsonify({"error": "Training task not found"}), 404
        
        return jsonify(training_tasks[task_id])
    
    except Exception as e:
        logger.error(f"Error in training progress endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/train/stats', methods=['GET'])
def training_stats():
    try:
        stats = database.get_training_stats()
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error in training stats endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync', methods=['POST'])
def start_sync():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        privacy_settings = data.get('privacy_settings', {})
        sync_frequency = data.get('sync_frequency', 'manual')
        
        # Ensure model is loaded
        if not model_service.is_model_loaded():
            return jsonify({"error": "No model loaded for syncing"}), 400
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Start sync in a background thread
        def sync_task():
            try:
                sync_tasks[task_id]['status'] = 'in_progress'
                sync_tasks[task_id]['progress'] = 0
                
                # Extract privacy parameters
                epsilon = privacy_settings.get('epsilon', 2.0)
                delta = privacy_settings.get('delta', 1e-5)
                
                # Get the most recent trained adapter
                adapter_path = model_service.get_latest_adapter_path()
                if not adapter_path:
                    raise ValueError("No trained adapter found for synchronization")
                
                # Prepare the weights for syncing with differential privacy
                sync_tasks[task_id]['progress'] = 20
                weights = model_service.extract_adapter_weights(adapter_path)
                time.sleep(0.2)
                
                # Apply differential privacy to the weights
                sync_tasks[task_id]['progress'] = 40
                private_weights = privacy_service.add_noise_to_weights(weights, epsilon, delta)
                time.sleep(0.2)
                
                # Send the private weights to the server
                sync_tasks[task_id]['progress'] = 60
                server_response = sync_service.send_weights_to_server(private_weights)
                time.sleep(0.2)
                
                # If server responds with updated weights, merge them
                sync_tasks[task_id]['progress'] = 80
                if 'updated_weights' in server_response:
                    model_service.merge_server_weights(server_response['updated_weights'])
                time.sleep(0.2)
                
                sync_tasks[task_id]['status'] = 'completed'
                sync_tasks[task_id]['progress'] = 100
                sync_tasks[task_id]['server_response'] = server_response
                
                # Save sync metadata to the database
                database.save_sync_metadata({
                    'id': task_id,
                    'privacy_epsilon': epsilon,
                    'privacy_delta': delta,
                    'sync_frequency': sync_frequency,
                    'adapter_path': adapter_path,
                    'completion_time': time.time(),
                    'server_response': server_response
                })
                
            except Exception as e:
                logger.error(f"Error in sync task: {str(e)}")
                if task_id in sync_tasks:
                    sync_tasks[task_id]['status'] = 'failed'
                    sync_tasks[task_id]['error'] = str(e)
        
        # Store task info
        sync_tasks[task_id] = {
            'status': 'starting',
            'progress': 0,
            'start_time': time.time(),
            'privacy_settings': privacy_settings,
            'sync_frequency': sync_frequency
        }
        
        # Start the sync thread
        threading.Thread(target=sync_task).start()
        
        return jsonify({
            "message": "Sync started",
            "sync_id": task_id
        })
        
    except Exception as e:
        logger.error(f"Error in start sync endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync/<task_id>/progress', methods=['GET'])
def sync_progress(task_id):
    try:
        if task_id not in sync_tasks:
            return jsonify({"error": "Sync task not found"}), 404
        
        return jsonify(sync_tasks[task_id])
    
    except Exception as e:
        logger.error(f"Error in sync progress endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync/status', methods=['GET'])
def sync_status():
    try:
        status = database.get_latest_sync_status()
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Error in sync status endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync/schedule', methods=['GET'])
def sync_schedule():
    try:
        schedule = database.get_sync_schedule()
        return jsonify(schedule)
    
    except Exception as e:
        logger.error(f"Error in sync schedule endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "PsychPal API",
        "version": "1.0.0",
        "description": "Privacy-focused mental health chatbot API",
        "endpoints": [
            "/api/chat",
            "/api/model/status",
            "/api/model/info",
            "/api/model/available",
            "/api/model/download",
            "/api/model/inference",
            "/api/train",
            "/api/sync"
        ]
    })

if __name__ == '__main__':
    try:
        # Make sure the application data directories exist
        os.makedirs('data/models', exist_ok=True)
        os.makedirs('data/database', exist_ok=True)
        os.makedirs('data/adapters', exist_ok=True)
        
        # Initialize the database
        database.initialize()
        
        # Start the Flask server
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")