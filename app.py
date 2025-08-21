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

def initialize_session():
    """Initialize or reset session tracking"""
    audio_files = get_audio_files()

    # Initialize session variables
    session['all_files'] = audio_files.copy()
    session['remaining_files'] = audio_files.copy()
    session['played_files'] = []
    session['current_file'] = None
    session['total_files'] = len(audio_files)

    # Shuffle the remaining files for randomness
    if session['remaining_files']:
        random.shuffle(session['remaining_files'])

    print(f"Session initialized with {len(audio_files)} files")

def get_next_file():
    """Get the next file ensuring no repeats until all are played"""
    # Check if we need to initialize or reset
    if 'remaining_files' not in session or not session['remaining_files']:
        initialize_session()

    # If still no files available, return None
    if not session.get('remaining_files'):
        return None

    # Pop the next file from remaining files
    next_file = session['remaining_files'].pop(0)

    # Add current file to played files if it exists
    if session.get('current_file'):
        session['played_files'].append(session['current_file'])

    # Update current file
    session['current_file'] = next_file
    session.modified = True

    print(f"Next file: {next_file}, Remaining: {len(session['remaining_files'])}, Played: {len(session['played_files'])}")

    return next_file

@app.route("/")
def index():
    """Main page with audio player and feedback form"""
    # Initialize session if needed
    if 'all_files' not in session:
        initialize_session()

    # Get the first/current file
    if not session.get('current_file'):
        selected_file = get_next_file()
    else:
        selected_file = session['current_file']

    subfolders = get_subfolders()

    return render_template("index.html",
                         audio_file=selected_file,
                         subfolders=subfolders,
                         google_form_url=config.GOOGLE_FORM_EMBED_URL,
                         samples_evaluated=len(session.get('played_files', [])),
                         total_samples=session.get('total_files', 0),
                         remaining_samples=len(session.get('remaining_files', [])),
                         using_box=config.USE_BOX)

@app.route("/next-audio")
def next_audio():
    """API endpoint to get next random audio file without repeats"""
    # Get the next file
    selected_file = get_next_file()

    if not selected_file:
        # All files have been played, restart the cycle
        print("All files played, restarting cycle")
        initialize_session()
        selected_file = get_next_file()

        if not selected_file:
            return jsonify({'error': 'No audio files found'}), 404

    return jsonify({
        'audio_file': selected_file,
        'samples_evaluated': len(session.get('played_files', [])),
        'total_samples': session.get('total_files', 0),
        'remaining_samples': len(session.get('remaining_files', [])),
        'cycle_complete': len(session.get('remaining_files', [])) == 0,
        'message': 'Starting new cycle - all files have been played!' if len(session.get('remaining_files', [])) == 0 else None
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
        'samples_evaluated': len(session.get('played_files', [])),
        'total_samples': session.get('total_files', 0),
        'remaining_samples': len(session.get('remaining_files', [])),
        'current_file': session.get('current_file', None),
        'played_files': session.get('played_files', [])
    })

@app.route("/reset-session", methods=['POST'])
def reset_session():
    """Reset the evaluation session"""
    initialize_session()
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

    session_info = {
        'played_files': len(session.get('played_files', [])),
        'remaining_files': len(session.get('remaining_files', [])),
        'current_file': session.get('current_file', 'None')
    }

    return jsonify({
        'status': 'running',
        'audio_files_count': len(get_audio_files()),
        'static_folder': app.static_folder,
        'google_form_configured': google_configured,
        'box_configured': box_configured,
        'box_status': box_status,
        'using_box': config.USE_BOX,
        'session_info': session_info
    })

# Don't run with app.run() on PythonAnywhere
if __name__ == "__main__":
    # This will only run locally, not on PythonAnywhere
    app.run(debug=True)
