# routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo

from services.prolog_engine import PrologEngine
from services.analyzer import MessageAnalyzer

from config import DEBUG_CONTEXT_ENDPOINT

from models.session import SessionState
from models.automata import SessionAutomata

# In-memory session storage
sessions = {}

# Violation weights
WEIGHT_MAP = {
    "abrupt_formality_change": 2,
    "odd_hour_messaging": 1,
    "early_off_platform_contact": 3,
    "authority_impersonation": 5
}

api_blueprint = Blueprint("api", __name__)
prolog_engine = PrologEngine()  # Load knowledge base once


# ======================================================
# MAIN MESSAGE PROCESSING ENDPOINT
# ======================================================
@api_blueprint.route("/message", methods=["POST"])
def process_message():
    data = request.json or {}

    user_id = data.get("user_id")
    message = data.get("message")
    timestamp = data.get("timestamp")
    sent_hour_override = data.get("sent_hour")

    if not user_id or not message:
        return jsonify({"error": "user_id and message required"}), 400

    # ----------------------------
    # Get or create session
    # ----------------------------
    session = sessions.get(user_id)
    if not session:
        session = SessionState(user_id)
        session.automata = SessionAutomata()
        sessions[user_id] = session

    # ----------------------------
    # Determine message time & hour
    # ----------------------------
    tz = ZoneInfo("Asia/Manila")

    if sent_hour_override is not None:
        sent_hour = int(sent_hour_override)
        sent_time = datetime.now(tz)
    elif timestamp:
        sent_time = datetime.fromtimestamp(timestamp / 1000, tz=tz)
        sent_hour = sent_time.hour
    else:
        sent_time = datetime.now(tz)
        sent_hour = sent_time.hour

    # ----------------------------
    # Build analyzer context
    # ----------------------------
    context = MessageAnalyzer.build_context(
        message_text=message,
        session=session,
        sent_time=sent_time,
        sent_hour=sent_hour
    )

    # ----------------------------
    # Prolog analysis
    # ----------------------------
    violations = prolog_engine.analyze_message(context)
    violations = list(set(violations))

    # ----------------------------
    # Update session automata
    # ----------------------------
    if violations:
        violations = [str(v) for v in violations]
        non_supporting = [v for v in violations if v != "odd_hour_messaging"]

        if non_supporting:
            # At least one real violation exists
            for v in violations:
                if v == "odd_hour_messaging":
                    if non_supporting:
                        session.automata.add_violation(
                            WEIGHT_MAP.get(v, 1),
                            message_time=sent_time  # Pass timestamp here
                        )
                else:
                    session.automata.add_violation(
                        WEIGHT_MAP.get(v, 1),
                        message_time=sent_time  # Pass timestamp here
                    )
        else:
            # Only odd-hour → count as clean for decay but still list in violations
            session.automata.add_clean_message(message_time=sent_time)
    else:
        # No violations → normal clean message
        session.automata.add_clean_message(message_time=sent_time)

    # ----------------------------
    # Store message history
    # ----------------------------
    session.add_message(
        message_text=message,
        formality=context["current_formality"],
        off_platform=context["off_platform_request"],
        sent_time=sent_time
    )

    return jsonify({
        "status": "ok",
        "session_state": session.automata.state,
        "score": session.automata.score,
        "sent_hour": sent_hour,
        "violations": violations
    })


# ======================================================
# DEBUG CONTEXT ENDPOINT (NO PROLOG, NO AUTOMATA)
# ======================================================
@api_blueprint.route("/debug/context", methods=["POST"])
def debug_context():
    if not DEBUG_CONTEXT_ENDPOINT:
        return jsonify({"error": "Debug endpoint disabled"}), 403

    data = request.json or {}

    user_id = data.get("user_id")
    message = data.get("message")
    timestamp = data.get("timestamp")
    sent_hour_override = data.get("sent_hour")

    if not user_id or not message:
        return jsonify({"error": "user_id and message required"}), 400

    # ----------------------------
    # Get or create session
    # ----------------------------
    session = sessions.get(user_id)
    if not session:
        session = SessionState(user_id)
        session.automata = SessionAutomata()
        sessions[user_id] = session

    # ----------------------------
    # Determine message time & hour
    # ----------------------------
    tz = ZoneInfo("Asia/Manila")

    if sent_hour_override is not None:
        sent_hour = int(sent_hour_override)
        sent_time = datetime.now(tz)
    elif timestamp:
        sent_time = datetime.fromtimestamp(timestamp / 1000, tz=tz)
        sent_hour = sent_time.hour
    else:
        sent_time = datetime.now(tz)
        sent_hour = sent_time.hour

    # ----------------------------
    # Build context ONLY
    # ----------------------------
    context = MessageAnalyzer.build_context(
        message_text=message,
        session=session,
        sent_time=sent_time,
        sent_hour=sent_hour
    )

    return jsonify({
        "status": "debug",
        "context": context
    })
