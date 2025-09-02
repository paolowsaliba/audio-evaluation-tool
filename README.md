# 🎧 Audio Evaluation Tool

A web-based platform for evaluating synthetic audio quality, developed by the UCLA Trustworthy AI Lab. This tool streamlines the process of listening to and evaluating audio samples through an intuitive interface with Google Forms integration.

## ✨ Features

- **Google Drive Integration**: Automatically syncs with a Google Drive folder to fetch audio files
- **Auto-refresh**: Checks for new files every 5 minutes without manual intervention
- **Form Auto-fill**: Automatically pre-fills the current audio filename in the evaluation form
- **Session Management**: Tracks evaluated samples and prevents repeats until all files are played
- **Progress Tracking**: Visual progress bar showing evaluation completion
- **Keyboard Shortcuts**: Quick navigation with keyboard commands
- **Responsive Design**: Clean, modern interface that works on all devices

## 🚀 Live Demo

The application is hosted on PythonAnywhere: [https://uclatrustworthyailab.pythonanywhere.com/](https://uclatrustworthyailab.pythonanywhere.com/)

## 📋 Prerequisites

- Python 3.7+
- Flask
- Google Drive folder (public access)
- Google Form for evaluation

## 🛠️ Installation

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/audio-evaluation-tool.git
   cd audio-evaluation-tool
   ```

2. **Install dependencies**:
   ```bash
   pip install flask requests
   ```

3. **Configure the application**:
   Edit `app.py` and update the following configuration:
   ```python
   # Google Form Configuration
   GOOGLE_FORM_BASE_URL = "your-google-form-url"
   GOOGLE_FORM_ENTRY_ID = "your-entry-id"  # For filename field
   
   # Google Drive Configuration
   GOOGLE_DRIVE_FOLDER_URL = "your-google-drive-folder-url"
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

### Deployment on PythonAnywhere

1. **Create a PythonAnywhere account** (free tier works)

2. **Upload files**:
   - `app.py` - Main Flask application
   - `templates/index.html` - HTML template

3. **Configure the web app**:
   - Set Python version to 3.7+
   - Set source code directory
   - Configure WSGI file to import your app

4. **Reload the web app**

## ⚙️ Configuration

### Setting up Google Drive

1. **Create a Google Drive folder** for your audio files
2. **Make it publicly accessible**:
   - Right-click the folder → "Share"
   - Change to "Anyone with the link can view"
3. **Copy the folder URL** (format: `https://drive.google.com/drive/folders/FOLDER_ID`)
4. **Add audio files** (.wav, .mp3, .m4a supported)

### Setting up Google Form

1. **Create a Google Form** for audio evaluation
2. **Add a text field** for the filename
3. **Get the entry ID**:
   - Go to Form → More → "Get pre-filled link"
   - Fill in the filename field with test data
   - Get the link and find `entry.XXXXXXXXX`
   - The numbers are your entry ID
4. **Get the form URL** for embedding

### Audio File Naming

The system supports various naming patterns:
- `output-17-07-2025-zul-part-1-augmentation-1.wav`
- `audio_001.wav`
- Any `.wav`, `.mp3`, or `.m4a` files

## 🎮 Usage

### Basic Workflow

1. **Load the application** - First audio file loads automatically
2. **Listen to the audio** using the built-in player
3. **Fill out the evaluation form** (filename is auto-filled)
4. **Click "Next Sample"** or press 'N' to load the next file
5. **Continue until all files are evaluated**

### Keyboard Shortcuts

- **N** - Load next sample
- **R** - Replay current audio
- **F** - Force refresh file list

### Features in Action

- **Auto-refresh**: Files are checked every 5 minutes for updates
- **No Repeats**: Each file plays once per cycle
- **Progress Tracking**: See how many files you've evaluated
- **Cycle Complete**: Notification when all files have been played

## 📁 Project Structure

```
audio-evaluation-tool/
│
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # HTML template
├── static/               # Static files (optional local audio)
│   └── *.wav            # Local audio files (fallback)
├── requirements.txt      # Python dependencies
└── README.md            # Documentation
```

## 🔄 Auto-Update Mechanism

The application automatically:
- Checks Google Drive every 5 minutes for new files
- Updates the file list without page reload
- Notifies users when new files are detected
- Maintains evaluation progress across updates

## 🐛 Troubleshooting

### Files not loading from Google Drive
- Ensure the folder is publicly accessible
- Check that files are in supported formats (.wav, .mp3, .m4a)
- Verify the folder URL is correct in configuration

### Form not pre-filling
- Verify the entry ID is correct
- Check that the form is set to accept pre-filled values
- Ensure the form URL includes the embedded parameter

### Session issues
- Clear browser cookies
- Use the "Reset Session" button
- Check that session secret key is set

## 📊 API Endpoints

- `GET /` - Main application page
- `GET /next-audio` - Get next audio file in queue
- `GET /api/files` - List all available files
- `POST /api/refresh` - Force refresh file list
- `GET /progress` - Get current evaluation progress
- `POST /reset-session` - Reset evaluation session
- `GET /test` - System status and configuration check

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **UCLA Trustworthy AI Lab** - Research and Development
- **Paolo** - Implementation and Deployment

## 🙏 Acknowledgments

- UCLA Trustworthy AI Lab for the research initiative
- PythonAnywhere for hosting services
- Google Drive API for file storage solution
- Flask framework for web development

## 📧 Contact

For questions or support, please contact the UCLA Trustworthy AI Lab.

---

**Last Updated**: Septemeber 2025
