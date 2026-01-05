# 🚀 TUBIFY - YouTube Traffic Generator

Enterprise-grade YouTube traffic generation platform with automated video/shorts views using authenticated sessions, proxy support, and intelligent cookie rotation.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-purple)

---

## ✨ Features

### 🎯 Core Functionality
- **Automated View Generation**: Generate views for YouTube videos and shorts
- **Smart Cookie Management**: Rotate through multiple cookie files for different sessions
- **Concurrent Processing**: Process up to 10 videos simultaneously with intelligent queue management
- **Proxy Support**: Built-in proxy configuration for enhanced privacy

### 🤖 Automation Capabilities
- **Video Handling**:
  - Auto-like (if not already liked)
  - Auto-subscribe (if not already subscribed)
  - Random seeking during playback (3 times per session)
  - 90-second watch duration
  
- **Shorts Handling**:
  - Auto-like (if not already liked)
  - 90-second watch duration

### 💼 Enterprise Features
- **Secure Authentication**: Login-protected dashboard
- **Real-time Monitoring**: Live session status and progress tracking
- **Advanced Controls**: Activate, pause, stop, or delete videos
- **Clean Logging**: Step-by-step execution logs
- **Professional UI**: Clean, modern, enterprise-grade interface

---

## 📋 Requirements

- Python 3.9 or higher
- Windows/Linux/macOS
- Internet connection
- Valid YouTube cookies (Netscape format)
- Proxy server (optional but recommended)

---

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd youtube-traffic-generator
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
```bash
playwright install chromium
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and update with your credentials:

```env
# Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

# Proxy Configuration (optional)
PROXY_SERVER=http://your-proxy-server:port
PROXY_USERNAME=your_proxy_username
PROXY_PASSWORD=your_proxy_password

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_change_this

# Automation Settings
MAX_CONCURRENT_SESSIONS=10
WATCH_DURATION=90
```

### 6. Add Cookie Files
Place your YouTube cookie files (Netscape format) in the `cookies_store/` directory:

```
cookies_store/
├── cookies_1.txt
├── cookies_2.txt
├── cookies_3.txt
└── ...
```

**How to export cookies:**
1. Install browser extension: "Get cookies.txt LOCALLY"
2. Visit YouTube while logged in
3. Export cookies in Netscape format
4. Save to `cookies_store/` directory

---

## 🚀 Usage

### Start the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Access Dashboard
1. Open browser and navigate to `http://localhost:5000`
2. Login with credentials from `.env` file
3. Start adding videos!

### Adding Videos
1. Navigate to **"Add Videos"** tab
2. Paste YouTube URL
3. Select type (Video or Shorts)
4. Choose number of views
5. Click **"Add Video"**

### Managing Videos
1. Navigate to **"Management"** tab
2. View all videos with real-time progress
3. Control actions:
   - **Activate**: Start processing views
   - **Pause**: Temporarily pause processing
   - **Stop**: Stop all processing for this video
   - **Delete**: Remove video and all sessions

---

## 📁 Project Structure

```
tubify/
├── app.py                    # Main Flask application
├── config.py                 # Configuration loader
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
│
├── database/                 # Database models & connection
│   ├── models.py
│   └── db.py
│
├── automation/               # Automation engine
│   ├── browser.py           # Browser session manager
│   ├── cookie_parser.py     # Cookie file parser
│   ├── video_handler.py     # Video automation logic
│   ├── shorts_handler.py    # Shorts automation logic
│   └── queue_manager.py     # Queue & concurrency manager
│
├── routes/                   # Flask routes
│   ├── auth.py              # Authentication
│   ├── views.py             # Page rendering
│   └── api.py               # REST API endpoints
│
├── static/                   # Frontend assets
│   ├── css/style.css
│   └── js/
│       ├── auth.js
│       ├── input.js
│       └── management.js
│
├── templates/                # HTML templates
│   ├── login.html
│   └── dashboard.html
│
├── cookies_store/            # Cookie files
└── logs/                     # Application logs
```

---

## 🔌 API Endpoints

### Videos
- `GET /api/videos` - Get all videos
- `POST /api/videos` - Add new video
- `PATCH /api/videos/:id/status` - Update video status
- `DELETE /api/videos/:id` - Delete video
- `GET /api/videos/:id/sessions` - Get video sessions

### Stats
- `GET /api/stats` - Get dashboard statistics
- `GET /health` - Health check

---

## ⚙️ Configuration

### Concurrent Sessions
By default, Tubify processes 10 videos simultaneously. Adjust in `.env`:

```env
MAX_CONCURRENT_SESSIONS=10
```

### Watch Duration
Default watch time is 90 seconds. Adjust in `.env`:

```env
WATCH_DURATION=90
```

### Proxy Configuration
Configure proxy in `.env` for enhanced privacy:

```env
PROXY_SERVER=http://proxy-server:port
PROXY_USERNAME=username
PROXY_PASSWORD=password
```

---

## 🐛 Troubleshooting

### Cookies Not Working
- Ensure cookies are in Netscape format
- Export fresh cookies from logged-in YouTube session
- Check cookie expiration dates

### Automation Fails
- Verify proxy is working (if configured)
- Check YouTube access from your network
- Ensure Playwright browsers are installed

### Database Issues
- Delete `tubify.db` file and restart application
- Database will be recreated automatically

---

## 📊 Queue System

Tubify intelligently manages video processing:

1. **10 Concurrent Sessions Max**: Only 10 videos process simultaneously
2. **Automatic Queue**: Pending videos wait in queue
3. **Auto-Start**: When a session completes, next pending video starts automatically
4. **Cookie Rotation**: Each session uses a different cookie file

**Example:**
- Submit 20 videos
- First 10 start immediately (if status = "active")
- Remaining 10 wait in queue
- As each of the first 10 completes, one from queue starts
- Process continues until all 20 are completed

---

## 🎨 Design Philosophy

Tubify features a clean, professional, enterprise-grade UI:

- **Dark Theme**: Reduces eye strain for long sessions
- **Sharp Design**: No bubbly elements, professional appearance
- **Real-time Updates**: Live progress tracking
- **Intuitive Controls**: Clear action buttons and status indicators

---

## 🔒 Security

- **Encrypted Passwords**: Use strong passwords in `.env`
- **Session Management**: Secure Flask sessions
- **Cookie Protection**: Store cookies securely
- **Proxy Support**: Enhanced privacy with proxy
- **No Data Leakage**: All data stored locally

---

## 📝 Notes

- Use responsibly and comply with YouTube's Terms of Service
- Recommended to use residential proxies
- Cookie files should be from real, active accounts
- Monitor session success rate and adjust if needed

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Flask - Web framework
- Playwright - Browser automation
- SQLAlchemy - Database ORM

---

## 📧 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ for enterprise-level YouTube traffic generation**


