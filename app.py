import os
import random
from flask import Flask, render_template, jsonify, request, session
import json
from datetime import datetime
import tempfile

# Import Box SDK if you're using Box
try:
    from boxsdk import OAuth2, Client
    BOX_AVAILABLE = True
except ImportError:
    BOX_AVAILABLE = False
    print("Box SDK not installed. Run: pip install boxsdk")

app = Flask(__name__)

# Configure session for PythonAnywhere
app.config["SECRET_KEY"] = 'ucla-audio-eval-2024-secret-key-psaliba'  # Changed to actual key
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = tempfile.gettempdir()

# Simple session management
app.secret_key = app.config["SECRET_KEY"]

# ===== CONFIGURATION - UPDATE THESE WITH YOUR ACTUAL VALUES =====
class Config:
    # Google Form embed URL - REPLACE WITH YOUR ACTUAL FORM URL
    GOOGLE_FORM_EMBED_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfRvaeYlDVMu2l1ojW0nl51WiMYb729e29cl0X3yZjMQ-io-Q/viewform?embedded=true"
    # Example: "https://docs.google.com/forms/d/e/1FAIpQLSeABCDEFG/viewform?embedded=true"
    
    # Box.com settings - REPLACE WITH YOUR ACTUAL CREDENTIALS
    BOX_CLIENT_ID = ''  # Add your Box client ID here
    BOX_CLIENT_SECRET = ''  # Add your Box client secret here
    BOX_ACCESS_TOKEN = ''  # Add your Box developer token here (expires in 60 min)
    BOX_FOLDER_ID = ''  # Add your Box folder ID here
    
    # Set to True ONLY after adding Box credentials above
    USE_BOX = False  # Change to True when Box credentials are added
    LOCAL_AUDIO_FOLDER = 'static'

config = Config()

# Box.com integration functions
def get_box_client():
    """Initialize Box client"""
    if not BOX_AVAILABLE:
        print("Box SDK not available")
        return None
    
    if not config.USE_BOX or not config.BOX_CLIENT_ID:
        return None
    
    try:
        oauth2 = OAuth2(
            client_id=config.BOX_CLIENT_ID,
            client_secret=config.BOX_CLIENT_SECRET,
            access_token=config.BOX_ACCESS_TOKEN
        )
        return Client(oauth2)
    except Exception as e:
        print(f"Box client error: {e}")
        return None

def get_audio_files_from_box():
    """Get audio files from Box folder"""
    client = get_box_client()
    if not client:
        return []
    
    try:
        folder = client.folder(folder_id=config.BOX_FOLDER_ID)
        items = folder.get_items()
        
        audio_files = []
        for item in items:
            if item.type == 'file' and item.name.endswith('.wav'):
                audio_files.append(item.name)
        
        print(f"Found {len(audio_files)} audio files in Box")
        return audio_files
    except Exception as e:
        print(f"Box error: {e}")
        return []

def get_audio_files(folder_path=None):
    """Get list of audio files from Box or local folder"""
    # Try Box first if enabled
    if config.USE_BOX and config.BOX_CLIENT_ID:
        box_files = get_audio_files_from_box()
        if box_files:
            return box_files
    
    # Fall back to local files
    try:
        audio_folder = os.path.join(app.static_folder)
        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)
            return []
        
        audio_files = [f for f in os.listdir(audio_folder) 
                      if f.endswith('.wav') and os.path.isfile(os.path.join(audio_folder, f))]
        return audio_files
    except Exception as e:
        print(f"Error getting audio files: {e}")
        return []

def get_subfolders():
    """Get available subfolders for audio categorization"""
    try:
        audio_folder = os.path.join(app.static_folder)
        if not os.path.exists(audio_folder):
            return ['default']
        
        subfolders = [d for d in os.listdir(audio_folder) 
                     if os.path.isdir(os.path.join(audio_folder, d))]
        return subfolders if subfolders else ['default']
    except Exception as e:
        print(f"Error getting subfolders: {e}")
        return ['default']

@app.route("/")
def index():
    """Main page with audio player and feedback form"""
    # Initialize session tracking
    if 'samples_evaluated' not in session:
        session['samples_evaluated'] = []
        session['current_index'] = 0
    
    audio_files = get_audio_files()
    subfolders = get_subfolders()
    
    if audio_files:
        # Get a random file that hasn't been evaluated yet if possible
        evaluated = session.get('samples_evaluated', [])
        unevaluated = [f for f in audio_files if f not in evaluated]
        
        if unevaluated:
            selected_file = random.choice(unevaluated)
        else:
            selected_file = random.choice(audio_files)
        
        session['current_file'] = selected_file
    else:
        selected_file = None
    
    return render_template("index.html", 
                         audio_file=selected_file,
                         subfolders=subfolders,
                         google_form_url=config.GOOGLE_FORM_EMBED_URL,
                         samples_evaluated=len(session.get('samples_evaluated', [])),
                         using_box=config.USE_BOX)

@app.route("/next-audio")
def next_audio():
    """API endpoint to get next random audio file"""
    folder = request.args.get('folder', 'default')
    audio_files = get_audio_files(folder)
    
    if not audio_files:
        return jsonify({'error': 'No audio files found'}), 404
    
    # Track evaluated samples
    if 'current_file' in session:
        current = session['current_file']
        if 'samples_evaluated' not in session:
            session['samples_evaluated'] = []
        if current not in session['samples_evaluated']:
            session['samples_evaluated'].append(current)
    
    # Get next random file, avoiding recently played ones if possible
    evaluated = session.get('samples_evaluated', [])
    unevaluated = [f for f in audio_files if f not in evaluated]
    
    if unevaluated:
        selected_file = random.choice(unevaluated)
    else:
        # All files evaluated, start over
        selected_file = random.choice(audio_files)
        session['samples_evaluated'] = []
    
    session['current_file'] = selected_file
    session.modified = True  # Ensure session is saved
    
    return jsonify({
        'audio_file': selected_file,
        'samples_evaluated': len(session.get('samples_evaluated', [])),
        'total_samples': len(audio_files)
    })

@app.route("/get-metadata/<filename>")
def get_metadata(filename):
    """Get metadata for a specific audio file"""
    metadata = {
        'filename': filename,
        'duration': 'Unknown',
        'language': 'Unknown',
        'speaker_id': 'Unknown',
        'generation_model': 'Unknown'
    }
    return jsonify(metadata)

@app.route("/save-feedback", methods=['POST'])
def save_feedback():
    """Save feedback locally (backup for Google Forms)"""
    try:
        feedback = request.json
        feedback['timestamp'] = datetime.now().isoformat()
        feedback['filename'] = session.get('current_file', 'unknown')
        
        # Define feedback file path
        feedback_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feedback_data.json')
        
        # Load existing feedback
        try:
            with open(feedback_file, 'r') as f:
                all_feedback = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_feedback = []
        
        # Append new feedback
        all_feedback.append(feedback)
        
        # Save updated feedback
        with open(feedback_file, 'w') as f:
            json.dump(all_feedback, f, indent=2)
        
        return jsonify({'status': 'success', 'message': 'Feedback saved'})
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/progress")
def progress():
    """Get evaluation progress for current session"""
    return jsonify({
        'samples_evaluated': len(session.get('samples_evaluated', [])),
        'current_file': session.get('current_file', None)
    })

@app.route("/reset-session", methods=['POST'])
def reset_session():
    """Reset the evaluation session"""
    session.clear()
    return jsonify({'status': 'success', 'message': 'Session reset'})

@app.route("/test")
def test():
    """Test endpoint to verify app is running"""
    google_configured = bool(config.GOOGLE_FORM_EMBED_URL and 'YOUR-ACTUAL-FORM-ID' not in config.GOOGLE_FORM_EMBED_URL)
    box_configured = bool(config.USE_BOX and config.BOX_CLIENT_ID)
    
    box_status = "Not configured"
    if box_configured and BOX_AVAILABLE:
        client = get_box_client()
        if client:
            try:
                folder = client.folder(folder_id=config.BOX_FOLDER_ID)
                items = list(folder.get_items())
                box_status = f"Connected! Found {len(items)} items"
            except Exception as e:
                box_status = f"Error: {str(e)}"
    
    return jsonify({
        'status': 'running',
        'audio_files_count': len(get_audio_files()),
        'static_folder': app.static_folder,
        'google_form_configured': google_configured,
        'box_configured': box_configured,
        'box_status': box_status,
        'using_box': config.USE_BOX
    })

# Don't run with app.run() on PythonAnywhere
if __name__ == "__main__":
    # This will only run locally, not on PythonAnywhere
    app.run(debug=True)
