from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import threading
import uuid
import json
import sys

# Add the parent directory to the Python path to allow importing the mock services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the mock services for simulation
from server.mock_services import MockModelService, MockPrivacyService, MockSyncService, MockDatabase

# Create the Flask app
app = Flask(__name__, static_folder='../build', static_url_path='')
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize services
database = MockDatabase(db_path=os.path.join('data', 'database', 'psychpal.db'))
model_service = MockModelService()
privacy_service = MockPrivacyService()
sync_service = MockSyncService(model_service, privacy_service)

# Task tracking
tasks = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    conversation_id = data.get('conversation_id', str(uuid.uuid4()))
    
    # Get conversation history
    conversation = database.get_conversation(conversation_id) or {
        'id': conversation_id,
        'title': message[:30] + '...' if len(message) > 30 else message,
        'messages': []
    }
    
    # Add user message
    conversation['messages'].append({
        'role': 'user',
        'content': message,
        'timestamp': time.time()
    })
    
    # Generate response
    if model_service.is_model_loaded():
        response = model_service.generate_response(message, conversation['messages'])
    else:
        response = "I'm sorry, but no model is currently loaded. Please go to the Models tab and download a model before chatting."
    
    # Add assistant response
    conversation['messages'].append({
        'role': 'assistant',
        'content': response,
        'timestamp': time.time()
    })
    
    # Save conversation
    database.save_conversation(conversation)
    
    return jsonify({
        'response': response,
        'conversation_id': conversation_id
    })

@app.route('/api/model/status', methods=['GET'])
def model_status():
    return jsonify(model_service.get_model_status())

@app.route('/api/model/info', methods=['GET'])
def model_info():
    return jsonify(model_service.get_model_info())

@app.route('/api/model/available', methods=['GET'])
def available_models():
    return jsonify(model_service.get_available_models())

@app.route('/api/model/download', methods=['POST'])
def download_model():
    data = request.json
    model_id = data.get('model_id')
    
    if not model_id:
        return jsonify({'error': 'No model ID provided'}), 400
    
    download_id = str(uuid.uuid4())
    tasks[download_id] = {
        'type': 'download',
        'progress': 0,
        'status': 'started',
        'model_id': model_id
    }
    
    def download_task():
        try:
            # Simulate download progress
            for i in range(1, 11):
                tasks[download_id]['progress'] = i * 10
                time.sleep(0.5)  # Simulate download time
            
            # Load the model after download
            model_service.load_model(model_id, os.path.join('data', 'models', f'{model_id}.bin'))
            
            # Save metadata
            database.save_model_metadata({
                'id': model_id,
                'name': f"Model {model_id}",
                'size': 250,  # Size in MB
                'download_date': time.time(),
                'is_loaded': True
            })
            
            tasks[download_id]['status'] = 'completed'
        except Exception as e:
            tasks[download_id]['status'] = 'failed'
            tasks[download_id]['error'] = str(e)
    
    thread = threading.Thread(target=download_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'download_id': download_id,
        'status': 'started'
    })

@app.route('/api/model/download/<task_id>/progress', methods=['GET'])
def download_progress(task_id):
    if task_id not in tasks or tasks[task_id]['type'] != 'download':
        return jsonify({'error': 'Invalid download ID'}), 404
    
    return jsonify({
        'progress': tasks[task_id]['progress'],
        'status': tasks[task_id]['status'],
        'error': tasks[task_id].get('error')
    })

@app.route('/api/inference', methods=['POST'])
def model_inference():
    data = request.json
    messages = data.get('messages', [])
    
    if not model_service.is_model_loaded():
        return jsonify({'error': 'No model loaded'}), 400
    
    response = model_service.generate_response_from_messages(messages)
    
    return jsonify({
        'response': response
    })

@app.route('/api/train', methods=['POST'])
def start_training():
    data = request.json
    settings = data.get('settings', {})
    
    if not model_service.is_model_loaded():
        return jsonify({'error': 'No model loaded'}), 400
    
    training_id = str(uuid.uuid4())
    tasks[training_id] = {
        'type': 'training',
        'progress': 0,
        'status': 'started',
        'settings': settings
    }
    
    def training_task():
        try:
            # Get all conversations
            conversations = database.get_all_conversations() if settings.get('use_local_data', True) else []
            
            # Prepare training data
            training_data = model_service.prepare_training_data(conversations)
            
            # Simulate training progress
            num_epochs = settings.get('num_epochs', 1)
            batch_size = settings.get('batch_size', 4)
            learning_rate = settings.get('learning_rate', 0.0001)
            
            for epoch in range(num_epochs):
                # Simulate epoch training
                model_service.train_epoch(training_data, batch_size, learning_rate)
                
                # Update progress (evenly distribute across epochs)
                progress = int(((epoch + 1) / num_epochs) * 100)
                tasks[training_id]['progress'] = progress
                
                time.sleep(1)  # Simulate training time
            
            # Save the trained adapter
            adapter_path = model_service.save_trained_adapter()
            
            # Save training metadata
            database.save_training_metadata({
                'id': training_id,
                'date': time.time(),
                'epochs': num_epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate,
                'adapter_path': adapter_path,
                'training_samples': len(training_data)
            })
            
            tasks[training_id]['status'] = 'completed'
        except Exception as e:
            tasks[training_id]['status'] = 'failed'
            tasks[training_id]['error'] = str(e)
    
    thread = threading.Thread(target=training_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'training_id': training_id,
        'status': 'started'
    })

@app.route('/api/train/<task_id>/progress', methods=['GET'])
def training_progress(task_id):
    if task_id not in tasks or tasks[task_id]['type'] != 'training':
        return jsonify({'error': 'Invalid training ID'}), 404
    
    return jsonify({
        'progress': tasks[task_id]['progress'],
        'status': tasks[task_id]['status'],
        'error': tasks[task_id].get('error')
    })

@app.route('/api/train/stats', methods=['GET'])
def training_stats():
    return jsonify(database.get_training_stats())

@app.route('/api/sync', methods=['POST'])
def start_sync():
    data = request.json
    privacy_settings = data.get('privacy_settings', {})
    sync_frequency = data.get('sync_frequency', 'manual')
    
    if not model_service.is_model_loaded():
        return jsonify({'error': 'No model loaded'}), 400
    
    sync_id = str(uuid.uuid4())
    tasks[sync_id] = {
        'type': 'sync',
        'progress': 0,
        'status': 'started',
        'settings': privacy_settings
    }
    
    def sync_task():
        try:
            # Get adapter weights
            adapter_path = model_service.get_latest_adapter_path()
            weights = model_service.extract_adapter_weights(adapter_path)
            
            # Apply differential privacy
            epsilon = privacy_settings.get('epsilon', 2.0)
            delta = privacy_settings.get('delta', 1e-5)
            privatized_weights = privacy_service.add_noise_to_weights(weights, epsilon, delta)
            
            # Simulate syncing with server
            tasks[sync_id]['progress'] = 50
            time.sleep(1)  # Simulate network latency
            
            # Send to server and get back aggregated weights
            server_response = sync_service.send_weights_to_server(privatized_weights)
            server_weights = server_response.get('aggregated_weights', {})
            
            # Update local model with merged weights
            model_service.merge_server_weights(server_weights)
            
            # Update sync schedule
            sync_service.schedule_sync(sync_frequency)
            
            # Save sync metadata
            database.save_sync_metadata({
                'id': sync_id,
                'date': time.time(),
                'epsilon': epsilon,
                'delta': delta,
                'frequency': sync_frequency,
                'status': 'success'
            })
            
            tasks[sync_id]['progress'] = 100
            tasks[sync_id]['status'] = 'completed'
        except Exception as e:
            tasks[sync_id]['status'] = 'failed'
            tasks[sync_id]['error'] = str(e)
    
    thread = threading.Thread(target=sync_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'sync_id': sync_id,
        'status': 'started'
    })

@app.route('/api/sync/<task_id>/progress', methods=['GET'])
def sync_progress(task_id):
    if task_id not in tasks or tasks[task_id]['type'] != 'sync':
        return jsonify({'error': 'Invalid sync ID'}), 404
    
    return jsonify({
        'progress': tasks[task_id]['progress'],
        'status': tasks[task_id]['status'],
        'error': tasks[task_id].get('error')
    })

@app.route('/api/sync/status', methods=['GET'])
def sync_status():
    return jsonify(database.get_latest_sync_status())

@app.route('/api/sync/schedule', methods=['GET'])
def sync_schedule():
    return jsonify(database.get_sync_schedule())

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'app_name': 'PsychPal API',
        'description': 'Backend API for PsychPal mental health chatbot'
    })

if __name__ == '__main__':
    # Create data directories if they don't exist
    os.makedirs(os.path.join('data', 'models'), exist_ok=True)
    os.makedirs(os.path.join('data', 'database'), exist_ok=True)
    os.makedirs(os.path.join('data', 'adapters'), exist_ok=True)
    
    # Initialize the database
    database.initialize()
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)