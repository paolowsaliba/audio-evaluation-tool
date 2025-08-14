import os
import random
from flask import Flask, render_template, jsonify, request, session
from flask_session import Session
import json
from datetime import datetime

app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configuration for future Box.com integration
class Config:
    # Box.com settings (to be configured with actual credentials)
    BOX_CLIENT_ID = os.environ.get('BOX_CLIENT_ID', '')
    BOX_CLIENT_SECRET = os.environ.get('BOX_CLIENT_SECRET', '')
    BOX_ACCESS_TOKEN = os.environ.get('BOX_ACCESS_TOKEN', '')
    
    # Local folder for development
    LOCAL_AUDIO_FOLDER = 'static'
    USE_BOX = False  # Set to True when Box.com is configured
    
    # Google Form embed URL (replace with your actual form)
    GOOGLE_FORM_EMBED_URL = "YOUR_GOOGLE_FORM_EMBED_URL_HERE"

config = Config()

def get_audio_files(folder_path=None):
    """Get list of audio files from local folder or Box.com"""
    if config.USE_BOX:
        # TODO: Implement Box.com file listing
        # from boxsdk import Client, OAuth2
        # oauth2 = OAuth2(client_id=config.BOX_CLIENT_ID, 
        #                 client_secret=config.BOX_CLIENT_SECRET,
        #                 access_token=config.BOX_ACCESS_TOKEN)
        # client = Client(oauth2)
        # folder = client.folder(folder_id)
        # items = folder.get_items()
        # audio_files = [item.name for item in items if item.name.endswith('.wav')]
        pass
    else:
        # Local file system
        audio_folder = os.path.join(app.static_folder)
        audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.wav')]
        return audio_files

def get_subfolders():
    """Get available subfolders for audio categorization"""
    if config.USE_BOX:
        # TODO: Implement Box.com subfolder listing
        return []
    else:
        audio_folder = os.path.join(app.static_folder)
        subfolders = [d for d in os.listdir(audio_folder) 
                     if os.path.isdir(os.path.join(audio_folder, d))]
        return subfolders if subfolders else ['default']

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
        selected_file = random.choice(audio_files)
        session['current_file'] = selected_file
    else:
        selected_file = None
    
    return render_template("index.html", 
                         audio_file=selected_file,
                         subfolders=subfolders,
                         google_form_url=config.GOOGLE_FORM_EMBED_URL,
                         samples_evaluated=len(session.get('samples_evaluated', [])))

@app.route("/next-audio")
def next_audio():
    """API endpoint to get next random audio file"""
    folder = request.args.get('folder', 'default')
    audio_files = get_audio_files(folder)
    
    if not audio_files:
        return jsonify({'error': 'No audio files found'}), 404
    
    # Track evaluated samples
    if 'current_file' in session and session['current_file'] not in session.get('samples_evaluated', []):
        if 'samples_evaluated' not in session:
            session['samples_evaluated'] = []
        session['samples_evaluated'].append(session['current_file'])
    
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
    
    return jsonify({
        'audio_file': selected_file,
        'samples_evaluated': len(session.get('samples_evaluated', [])),
        'total_samples': len(audio_files)
    })

@app.route("/get-metadata/<filename>")
def get_metadata(filename):
    """Get metadata for a specific audio file"""
    # This could be expanded to read actual metadata from files
    # or from a database/CSV file
    metadata = {
        'filename': filename,
        'duration': 'Unknown',  # Could use librosa or similar to get actual duration
        'language': 'Unknown',  # Could be parsed from filename or metadata
        'speaker_id': 'Unknown',
        'generation_model': 'Unknown'
    }
    return jsonify(metadata)

@app.route("/save-feedback", methods=['POST'])
def save_feedback():
    """Save feedback locally (backup for Google Forms)"""
    feedback = request.json
    feedback['timestamp'] = datetime.now().isoformat()
    feedback['filename'] = session.get('current_file', 'unknown')
    
    # Save to JSON file (you could also use CSV or database)
    feedback_file = 'feedback_data.json'
    
    try:
        with open(feedback_file, 'r') as f:
            all_feedback = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_feedback = []
    
    all_feedback.append(feedback)
    
    with open(feedback_file, 'w') as f:
        json.dump(all_feedback, f, indent=2)
    
    return jsonify({'status': 'success', 'message': 'Feedback saved'})

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

if __name__ == "__main__":
    app.run(debug=True)