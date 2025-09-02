import os
import random
from flask import Flask, render_template, jsonify, request, session, redirect
import json
from datetime import datetime, timedelta
import tempfile
import requests
import re

app = Flask(__name__)

# Configure session for PythonAnywhere
app.config["SECRET_KEY"] = 'ucla-audio-eval-2024-super-secret-key-psaliba'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = tempfile.gettempdir()

# Simple session management
app.secret_key = app.config["SECRET_KEY"]

# ===== CONFIGURATION  =====
class Config:
    # Google Form Configuration
    GOOGLE_FORM_BASE_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfRvaeYlDVMu2l1ojW0nl51WiMYb729e29cl0X3yZjMQ-io-Q/viewform"
    GOOGLE_FORM_ENTRY_ID = "343010386"  # Entry ID for filename field
    
    # Google Drive Configuration
    GOOGLE_DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1fizob97qYAqEMt2-QFCtLwZzScuEe2cp"
    
    # Cache settings
    CACHE_DURATION_MINUTES = 5  # Refresh file list every 5 minutes
    
    # Local fallback
    LOCAL_AUDIO_FOLDER = 'static'

config = Config()

# ===== GOOGLE DRIVE INTEGRATION =====
class GoogleDriveFolder:
    def __init__(self, folder_url):
        self.folder_url = folder_url
        self.folder_id = self._extract_folder_id(folder_url)
        self.cache = {
            'files': [],
            'timestamp': None
        }
        self.cache_duration = timedelta(minutes=config.CACHE_DURATION_MINUTES)
        
    def _extract_folder_id(self, url):
        """Extract folder ID from Google Drive URL"""
        patterns = [
            r'/folders/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_files(self, force_refresh=False):
        """Get list of audio files from Google Drive folder"""
        now = datetime.now()
        
        # Check cache validity
        if not force_refresh and self.cache['timestamp']:
            if now - self.cache['timestamp'] < self.cache_duration:
                return self.cache['files']
        
        try:
            # Try to fetch file list using Google Drive API v3 (public endpoint)
            api_url = "https://www.googleapis.com/drive/v3/files"
            params = {
                'q': f"'{self.folder_id}' in parents",
                'fields': 'files(id,name,size,modifiedTime)',
                'orderBy': 'name',
                'pageSize': 1000  # Get up to 1000 files
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                files = []
                
                for item in data.get('files', []):
                    # Filter for audio files
                    if item['name'].lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):
                        files.append({
                            'id': item['id'],
                            'name': item['name'],
                            'size': item.get('size', 0),
                            'modified': item.get('modifiedTime', ''),
                            'download_url': f"https://drive.google.com/uc?export=download&id={item['id']}"
                        })
                
                # Sort files by name
                files.sort(key=lambda x: x['name'])
                
                # Update cache
                self.cache = {
                    'files': files,
                    'timestamp': now
                }
                
                print(f"Successfully fetched {len(files)} audio files from Google Drive")
                return files
            else:
                print(f"Google Drive API returned status code: {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching from Google Drive: {e}")
        
        # Return cached files if available, otherwise empty list
        return self.cache.get('files', [])
    
    def get_direct_download_url(self, file_id):
        """Get direct download URL for a file"""
        return f"https://drive.google.com/uc?export=download&id={file_id}"

# Initialize Google Drive folder
drive_folder = GoogleDriveFolder(config.GOOGLE_DRIVE_FOLDER_URL)

def get_audio_files():
    """Get list of audio files from Google Drive"""
    drive_files = drive_folder.get_files()
    
    if drive_files:
        # Return just the filenames for compatibility with existing code
        return [f['name'] for f in drive_files]
    
    # Fallback to local files if Google Drive fails
    try:
        audio_folder = os.path.join(app.static_folder)
        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)
            return []
        
        audio_files = [f for f in os.listdir(audio_folder)
                      if f.endswith(('.wav', '.mp3', '.m4a')) and os.path.isfile(os.path.join(audio_folder, f))]
        return audio_files
    except Exception as e:
        print(f"Error getting local audio files: {e}")
        return []

def get_audio_file_info(filename):
    """Get full info for a specific audio file"""
    drive_files = drive_folder.get_files()
    for file in drive_files:
        if file['name'] == filename:
            return file
    return None

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

def create_prefilled_form_url(filename):
    """Create Google Form URL with pre-filled filename"""
    if not filename:
        return config.GOOGLE_FORM_BASE_URL + "?embedded=true"
    
    # Build URL with pre-filled entry
    params = {
        'embedded': 'true',
        f'entry.{config.GOOGLE_FORM_ENTRY_ID}': filename
    }
    
    # Create query string
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{config.GOOGLE_FORM_BASE_URL}?{query_string}"

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
    
    # Get file info for download URL
    file_info = get_audio_file_info(selected_file) if selected_file else None
    
    # Create pre-filled form URL
    form_url = create_prefilled_form_url(selected_file)
    
    # Get last cache update time
    cache_time = drive_folder.cache.get('timestamp')
    last_update = cache_time.strftime("%I:%M %p") if cache_time else "Never"
    
    return render_template("index.html",
                         audio_file=selected_file,
                         audio_file_info=file_info,
                         google_form_url=form_url,
                         samples_evaluated=len(session.get('played_files', [])),
                         total_samples=session.get('total_files', 0),
                         remaining_samples=len(session.get('remaining_files', [])),
                         using_google_drive=True,
                         last_update=last_update,
                         cache_duration=config.CACHE_DURATION_MINUTES)

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
    
    # Get file info for download URL
    file_info = get_audio_file_info(selected_file)
    
    # Create pre-filled form URL
    form_url = create_prefilled_form_url(selected_file)
    
    return jsonify({
        'audio_file': selected_file,
        'audio_url': file_info['download_url'] if file_info else f"/static/{selected_file}",
        'form_url': form_url,
        'samples_evaluated': len(session.get('played_files', [])),
        'total_samples': session.get('total_files', 0),
        'remaining_samples': len(session.get('remaining_files', [])),
        'cycle_complete': len(session.get('remaining_files', [])) == 0,
        'message': 'Starting new cycle - all files have been played!' if len(session.get('remaining_files', [])) == 0 else None
    })

@app.route("/api/files")
def api_files():
    """API endpoint to get current file list"""
    files = drive_folder.get_files()
    return jsonify({
        'success': True,
        'files': files,
        'count': len(files),
        'cached_at': drive_folder.cache['timestamp'].isoformat() if drive_folder.cache['timestamp'] else None
    })

@app.route("/api/refresh", methods=['POST'])
def api_refresh():
    """Force refresh file list from Google Drive"""
    files = drive_folder.get_files(force_refresh=True)
    
    # Reinitialize session with new files
    initialize_session()
    
    return jsonify({
        'success': True,
        'message': 'Files refreshed from Google Drive',
        'count': len(files),
        'files': [f['name'] for f in files]
    })

@app.route("/api/audio/<file_id>")
def serve_audio(file_id):
    """Redirect to Google Drive download URL"""
    download_url = drive_folder.get_direct_download_url(file_id)
    return redirect(download_url)

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
    drive_files = drive_folder.get_files()
    
    session_info = {
        'played_files': len(session.get('played_files', [])),
        'remaining_files': len(session.get('remaining_files', [])),
        'current_file': session.get('current_file', 'None')
    }
    
    return jsonify({
        'status': 'running',
        'google_drive_configured': bool(config.GOOGLE_DRIVE_FOLDER_URL),
        'google_drive_folder_id': drive_folder.folder_id,
        'google_form_configured': bool(config.GOOGLE_FORM_BASE_URL),
        'google_form_entry_id': config.GOOGLE_FORM_ENTRY_ID,
        'audio_files_count': len(drive_files),
        'cache_duration_minutes': config.CACHE_DURATION_MINUTES,
        'last_cache_update': drive_folder.cache['timestamp'].isoformat() if drive_folder.cache['timestamp'] else None,
        'session_info': session_info
    })

# Don't run with app.run() on PythonAnywhere
if __name__ == "__main__":
    # This will only run locally, not on PythonAnywhere
    app.run(debug=True)
