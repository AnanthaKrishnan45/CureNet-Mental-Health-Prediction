# CureNet Mental Health Chatbot

CureNet is a full-stack educational mental-wellness chatbot based on the original repository concept. The original project had a Flask endpoint with placeholder OpenVINO paths and a frontend that called `localhost:5000`; this version replaces those placeholders with a working Flask backend and a responsive frontend.

## What works

- Responsive mental-wellness chat UI
- Flask REST API
- Same-origin frontend/backend integration
- Session-based conversation history
- SQLite storage for conversations
- Topic-aware responses for anxiety, stress, depression, sleep, panic, loneliness and sadness
- Crisis-language detection and safety escalation
- Simple non-diagnostic wellness screener API
- Health-check endpoint
- No external AI API key required

## Important

This is an educational support chatbot. It does **not** diagnose mental-health conditions, prescribe treatment, or replace a qualified clinician.

If someone may be in immediate danger or may act on thoughts of suicide/self-harm, use local emergency services or go to the nearest emergency department. In India, the Government of India's Tele-MANAS service can be reached 24x7 at **14416** or **1800-89-14416**.

## Run locally

### 1. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the backend

```bash
python app.py
```

### 4. Open the frontend

Visit:

```text
http://127.0.0.1:5000
```

The Flask server serves both the frontend and API, so there is no CORS setup or separate frontend server required.

## API

### Health

```http
GET /api/health
```

### Chat

```http
POST /api/chat
Content-Type: application/json

{
  "message": "I feel very stressed",
  "session_id": "demo-session"
}
```

### Wellness screener

```http
POST /api/screen
Content-Type: application/json

{
  "answers": {
    "mood": 2,
    "sleep": 3,
    "energy": 2,
    "worry": 2
  }
}
```

The screener is intentionally labelled non-diagnostic and should not be presented as a clinical diagnosis.

### History

```http
GET /api/history/<session_id>
```

## Project structure

```text
CureNet-Mental-Health-Chatbot/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── .gitkeep
└── static/
    ├── index.html
    ├── style.css
    └── script.js
```

## Deployment

For production, run Flask behind a production WSGI server such as Gunicorn or Waitress and add authentication, HTTPS, rate limiting, secure database controls, privacy/retention policies, structured clinical governance, and professional review before handling real patient information.
