from flask import Blueprint, request, jsonify
from flask import Flask, send_from_directory
from datetime import datetime
from services.prolog_engine import PrologEngine
from models.session import SessionState
from db import get_db
import uuid

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


    # ---------- Get or create session ----------
    session = sessions.get(user_id)
    if not session:
        session = SessionState(user_id)
        sessions[user_id] = session

    # ---------- CONNECT SA DATABASE ----------
    conn = get_db()
    cursor = conn.cursor()

    # Insert user if not exists
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    # Get latest session from DB or insert new
    cursor.execute(
        "SELECT session_id, current_state FROM sessions WHERE user_id=? ORDER BY started_at DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    if row:
        session_id = row["session_id"]
        db_state = row["current_state"]  # changed: fetch current_state safely
    else:
        cursor.execute(
            "INSERT INTO sessions (user_id, current_state, suspicion_score) VALUES (?, ?, ?)",
            (user_id, session.state, session.score)
        )
        session_id = cursor.lastrowid
        db_state = session.state  # new session, current DB state = initial state
        conn.commit()

    # ---------- Process message timestamp ----------
    sent_time = datetime.utcfromtimestamp(timestamp / 1000) if timestamp else datetime.utcnow()
    
    # Determine message index for interaction rules
    msg_index = len(session.messages) + 1

    # ---------- Context for Prolog assertions ----------
    context = {
        "message": message,
        "message_index": msg_index,
        "sent_hour": sent_time.hour,
        "prev_5min_count": session.prev_5min_count(),  # changed: use actual session metrics
        "curr_5min_count": session.curr_5min_count(),  # changed: use actual session metrics
        "previous_formality": session.get_last_formality(),  # changed: use last message formality
        "current_formality": 0,
        "off_platform_request": int(any(k in message.lower() for k in [
            "telegram","whatsapp","viber","call me","text me","email me","pm me","dm me"
        ]))  # changed: convert to int for SQLite compatibility
    }

    # Analyze message using PrologEngine
    violations = prolog_engine.analyze_message(context)

    # Update session
    if violations:
        for v in violations:
            session.add_violation(WEIGHT_MAP.get(v, 1))
    else:
        session.add_clean_message()

    # ---------- INSERT MESSAGE SA DATABASE ----------
    message_id = f"msg_{uuid.uuid4().hex}"
    cursor.execute("""
        INSERT INTO messages (
            message_id, session_id, message_index, message_text,
            sent_time, sent_hour, prev_5min_count, curr_5min_count,
            previous_formality, current_formality, off_platform_detected
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        message_id, session_id, msg_index, message,
        sent_time, sent_time.hour, context["prev_5min_count"], context["curr_5min_count"],
        context["previous_formality"], context["current_formality"], context["off_platform_request"]
    ))
    conn.commit()

    # Insert violations
    for v in violations:
        cursor.execute("""
            INSERT INTO violations (message_id, violation_type, weight)
            VALUES (?, ?, ?)
        """, (message_id, v, WEIGHT_MAP.get(v, 1)))
    conn.commit()

    # Insert state transition if state changed
    if db_state != session.state:
        cursor.execute("""
            INSERT INTO state_transitions (session_id, from_state, to_state, triggered_by, message_id)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, db_state, session.state, ", ".join(violations) if violations else None, message_id))
        conn.commit()

    # Update session state in DB
    cursor.execute("""
        UPDATE sessions SET current_state=?, suspicion_score=?, last_updated=?
        WHERE session_id=?
    """, (session.state, session.score, datetime.utcnow(), session_id))
    conn.commit()
    conn.close()

    # Store message in memory
    session.add_message(message, formality=0, off_platform=bool(context["off_platform_request"]), sent_time=sent_time)

    # Return response
    return jsonify({
        "status": "ok",
        "session_state": session.state,
        "violations": violations
    })

# ---------- STATE DIAGRAM STUFF SUMTN ----------
@api_blueprint.route("/session/<user_id>/state_diagram", methods=["GET"])
def get_state_diagram(user_id):
    """
    Returns the states and transitions for the user's session in JSON,
    so it can be visualized as a state diagram on the frontend.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Get the latest session for this user
    cursor.execute(
        "SELECT session_id, current_state FROM sessions WHERE user_id=? ORDER BY started_at DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "No session found for this user"}), 404

    session_id = row["session_id"]

    # Get all state transitions for this session
    cursor.execute(
        "SELECT from_state, to_state, triggered_by FROM state_transitions WHERE session_id=? ORDER BY transition_id ASC",
        (session_id,)
    )
    transitions_rows = cursor.fetchall()
    conn.close()

    # Extract unique states
    states = set()
    transitions = []
    for t in transitions_rows:
        states.add(t["from_state"])
        states.add(t["to_state"])
        transitions.append({
            "from": t["from_state"],
            "to": t["to_state"],
            "triggered_by": t["triggered_by"].split(", ") if t["triggered_by"] else []
        })

    return jsonify({
        "states": list(states),
        "transitions": transitions,
        "current_state": row["current_state"]
    })