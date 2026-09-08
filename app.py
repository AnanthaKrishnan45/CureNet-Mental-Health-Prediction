from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
import re
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "curenet.db"

app = Flask(__name__, static_folder="static", static_url_path="/static")


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def save_message(session_id, role, message):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO conversations(session_id, role, message, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, message, datetime.utcnow().isoformat(timespec="seconds") + "Z"),
        )
        conn.commit()


CRISIS_PATTERNS = [
    r"\bsuicid(e|al)\b",
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\btake my life\b",
    r"\bdon'?t want to live\b",
    r"\bwant to die\b",
    r"\bhurt myself\b",
    r"\bself[- ]?harm\b",
]

TOPIC_RESPONSES = {
    "anxiety": (
        "It sounds like anxiety may be making things feel overwhelming. "
        "Try slowing your breathing for a minute: inhale gently for 4 seconds, "
        "exhale for 6 seconds, and repeat a few times. If this keeps affecting "
        "your daily life, consider speaking with a qualified mental-health professional."
    ),
    "stress": (
        "Stress can build up when your mind and body do not get enough recovery time. "
        "Try choosing one small task, taking a short screen-free break, drinking some water, "
        "and returning to the task afterward. If stress is persistent or severe, professional support can help."
    ),
    "depression": (
        "I'm sorry you're dealing with this. Low mood can make ordinary tasks feel difficult. "
        "A small next step could be contacting someone you trust, getting some daylight, or taking a short walk. "
        "If low mood persists, worsens, or affects functioning, please consider a qualified clinician."
    ),
    "sleep": (
        "For sleep problems, try keeping a consistent wake time, reducing caffeine late in the day, "
        "and giving yourself a quiet wind-down period before bed. Persistent insomnia is worth discussing with a clinician."
    ),
    "panic": (
        "During a panic-like episode, try grounding yourself: name 5 things you can see, "
        "4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste. "
        "If symptoms are new, severe, or feel medically dangerous, seek urgent medical care."
    ),
    "lonely": (
        "Feeling lonely can be painful. If possible, send a simple message to someone you trust, "
        "even if you do not feel ready for a long conversation. Regular social contact can also help over time."
    ),
    "sad": (
        "I'm sorry you're feeling sad. You do not have to solve everything at once. "
        "Try one manageable action and consider talking with someone you trust. "
        "If sadness is persistent or interfering with your life, professional support is appropriate."
    ),
}

KEYWORDS = {
    "anxiety": ["anxiety", "anxious", "worry", "worried", "nervous", "overthinking"],
    "stress": ["stress", "stressed", "pressure", "burnout", "overwhelmed"],
    "depression": ["depression", "depressed", "hopeless", "empty", "worthless"],
    "sleep": ["sleep", "insomnia", "can't sleep", "cannot sleep", "awake at night"],
    "panic": ["panic", "panic attack", "heart racing", "breathing fast"],
    "lonely": ["lonely", "alone", "isolated"],
    "sad": ["sad", "crying", "unhappy", "down"],
}


def crisis_response():
    return (
        "I'm really sorry you're going through this. I can't provide emergency care, "
        "but I can help you take a safer next step. If you may act on thoughts of suicide "
        "or self-harm, please contact emergency services or go to the nearest emergency department now. "
        "In India, Tele-MANAS provides 24x7 mental-health support at 14416 or 1800-89-14416. "
        "If possible, stay with someone you trust and move away from anything you could use to hurt yourself."
    )


def choose_response(message):
    text = message.lower().strip()

    if any(re.search(pattern, text) for pattern in CRISIS_PATTERNS):
        return crisis_response(), "crisis"

    if any(x in text for x in ["hello", "hi", "hey", "good morning", "good evening"]):
        return (
            "Hi. I'm CureNet, a mental-wellness support chatbot. "
            "You can tell me what you're feeling, ask about stress, anxiety, sleep, or coping strategies. "
            "I don't diagnose medical conditions.",
            "general",
        )

    if "what can you do" in text or "help me" in text:
        return (
            "I can provide general mental-wellness information, simple coping ideas, "
            "and help you reflect on symptoms. I cannot diagnose a condition or replace a doctor, "
            "psychologist, or counsellor.",
            "general",
        )

    for topic, words in KEYWORDS.items():
        if any(word in text for word in words):
            return TOPIC_RESPONSES[topic], topic

    if any(x in text for x in ["thank", "thanks"]):
        return "You're welcome. Take things one step at a time, and reach out to a trusted person if you need support.", "general"

    return (
        "Thank you for sharing that. Can you tell me a little more about what has been bothering you "
        "and how long you've been feeling this way? I can offer general coping information, but I can't diagnose you.",
        "general",
    )


@app.get("/")
def index():
    return send_from_directory(BASE_DIR / "static", "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "CureNet Mental Health Chatbot"})


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    session_id = str(data.get("session_id", "anonymous")).strip()[:100]

    if not message:
        return jsonify({"error": "Message is required."}), 400
    if len(message) > 2000:
        return jsonify({"error": "Message is too long. Please keep it under 2000 characters."}), 400

    response, intent = choose_response(message)
    save_message(session_id, "user", message)
    save_message(session_id, "assistant", response)

    return jsonify({
        "response": response,
        "intent": intent,
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    })


@app.post("/api/screen")
def screen():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", {})
    if not isinstance(answers, dict):
        return jsonify({"error": "answers must be an object"}), 400

    # This is a non-diagnostic wellness screener, not a clinical instrument.
    score = 0
    for value in answers.values():
        try:
            score += max(0, min(3, int(value)))
        except (TypeError, ValueError):
            continue

    if score <= 4:
        level = "lower"
        message = "Your responses do not suggest a high level of distress in this simple screener. Keep monitoring your wellbeing."
    elif score <= 9:
        level = "moderate"
        message = "Your responses suggest some distress. Consider talking with someone you trust and, if it persists, a qualified professional."
    else:
        level = "higher"
        message = "Your responses suggest significant distress. Consider seeking support from a qualified mental-health professional soon."

    return jsonify({"score": score, "level": level, "message": message})


@app.get("/api/history/<session_id>")
def history(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT role, message, created_at FROM conversations WHERE session_id = ? ORDER BY id DESC LIMIT 50",
            (session_id[:100],),
        ).fetchall()
    rows.reverse()
    return jsonify([
        {"role": role, "message": message, "created_at": created_at}
        for role, message, created_at in rows
    ])


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
