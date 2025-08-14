# Audio Evaluation Tool

A web-based tool for evaluating synthetic audio quality, developed for the UCLA Trustworthy AI Lab.

## 🎯 Project Overview

This tool enables linguists and researchers to:
- Listen to synthetic (AI-generated) audio samples
- Evaluate audio quality through structured feedback forms
- Track evaluation progress across sessions
- Export feedback data for analysis

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Collection**: Google Forms integration
- **Deployment**: PythonAnywhere
- **Future Integration**: Box.com for centralized file storage

## 📁 Project Structure

```
audio-evaluation-tool/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main UI template
├── static/               # Audio files and static assets
│   └── *.wav            # Audio samples for evaluation
└── feedback_data.json   # Local feedback storage (backup)
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/audio-evaluation-tool.git
   cd audio-evaluation-tool
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add audio files**
   - Place `.wav` files in the `static/` directory

5. **Configure Google Form (optional)**
   - Update `GOOGLE_FORM_EMBED_URL` in `app.py`

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the tool**
   - Open browser to `http://localhost:5000`

## 📊 Features

### Current Features
- ✅ Random audio sample selection
- ✅ Audio playback controls (play, pause, replay)
- ✅ Session-based progress tracking
- ✅ Google Forms integration for feedback
- ✅ Local feedback storage backup
- ✅ Metadata display for audio files
- ✅ Responsive UI design

### Planned Features
- 🔄 Box.com integration for centralized file storage
- 🔄 AI-powered feedback analysis and summarization
- 🔄 Multi-folder audio organization
- 🔄 Batch evaluation processing
- 🔄 Export functionality for feedback data
- 🔄 Advanced analytics dashboard

## 🌐 Deployment

### PythonAnywhere Deployment

The application is designed for easy deployment on PythonAnywhere's free tier:

1. Create account at [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Upload project files
3. Configure web app with Flask
4. Set environment variables
5. Map static files directory

See [Deployment Guide](docs/deployment.md) for detailed instructions.

## 🔧 Configuration

### Environment Variables

Create a `.env` file (not tracked in git) with:

```env
SECRET_KEY=your-secret-key-here
GOOGLE_FORM_EMBED_URL=your-google-form-url
BOX_CLIENT_ID=your-box-client-id
BOX_CLIENT_SECRET=your-box-client-secret
BOX_ACCESS_TOKEN=your-box-token
```

### Google Forms Setup

1. Create a Google Form with evaluation fields
2. Get embed URL: Send → Embed → Copy src URL
3. Update `GOOGLE_FORM_EMBED_URL` in configuration

## 👥 Team

- **Developer**: [Your Name] - Computer Engineering, Seattle University
- **Advisor**: Professor Guang Cheng - UCLA Statistics Department
- **Collaborator**: Wesley - UCLA Statistics Department
- **UI/UX Designer**: Meihan Hu

## 📝 License

This project is part of research at UCLA Trustworthy AI Lab.

## 🤝 Contributing

This is a research project. For contributions or questions, please contact the development team.

## 📧 Contact

For questions or support, please reach out to the project team at UCLA Trustworthy AI Lab.

---

*This project is part of summer research at the UCLA Trustworthy AI Lab, focusing on improving speech recognition models through data augmentation and quality assessment.*
