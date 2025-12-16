from flask import Blueprint, request, jsonify
from datetime import datetime
from services.prolog_engine import PrologEngine
from models.session import SessionState

# Store sessions in memory (example)
sessions = {}

# Violation weights
WEIGHT_MAP = {
    "sudden_message_frequency": 3,
    "abrupt_formality_change": 2,
    "odd_hour_messaging": 1,
    "early_off_platform_contact": 4,
    "authority_impersonation": 5
}

api_blueprint = Blueprint("api", __name__)
prolog_engine = PrologEngine()  # KB loaded here

@api_blueprint.route("/message", methods=["POST"])
def process_message():
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message")
    timestamp = data.get("timestamp")

    if not user_id or not message:
        return jsonify({"error": "user_id and message required"}), 400

    # Get or create session
    session = sessions.get(user_id)
    if not session:
        session = SessionState(user_id)
        sessions[user_id] = session

    # Process message timestamp
    sent_time = datetime.utcfromtimestamp(timestamp / 1000) if timestamp else datetime.utcnow()
    
    # Determine message index for interaction rules
    msg_index = len(session.messages) + 1 if hasattr(session, "messages") else 1

    # Context for Prolog assertions
    context = {
        "message": message,
        "message_index": msg_index,
        "sent_hour": sent_time.hour,
        "prev_5min_count": 0,  # Placeholder, update if you have real metrics
        "curr_5min_count": 1,  # Placeholder, update if you have real metrics
        "previous_formality": 0,
        "current_formality": 0,
        "off_platform_request": any(k in message.lower() for k in [
            "telegram","whatsapp","viber","call me","text me","email me","pm me","dm me"
        ])
    }

    # Analyze message using PrologEngine
    violations = prolog_engine.analyze_message(context)

    # Update session
    if violations:
        for v in violations:
            session.add_violation(WEIGHT_MAP.get(v, 1))
    else:
        session.add_clean_message()

    # Store message (optional, for session tracking)
    if not hasattr(session, "messages"):
        session.messages = []
    session.messages.append({
        "message": message,
        "timestamp": sent_time,
        "violations": violations
    })

    # Return response
    return jsonify({
        "status": "ok",
        "session_state": session.state,
        "violations": violations
    })
