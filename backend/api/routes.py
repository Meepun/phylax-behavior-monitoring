from flask import Blueprint, request, jsonify
from services.session_store import get_session

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/message", methods=["POST"])
def process_message():
    data = request.json

    user_id = data.get("user_id")
    message = data.get("message")
    timestamp = data.get("timestamp")

    if not user_id or not message:
        return jsonify({"error": "user_id and message required"}), 400

    # 🔹 Get or create session state
    session = get_session(user_id)

    # 🔹 Check if user is already locked
    if session.is_locked():
        return jsonify({
            "status": "blocked",
            "reason": "Session locked. Revalidation required."
        }), 403

    # 🔹 TEMPORARY logic (simulate suspicious detection)
    # We'll replace this with Prolog later
    suspicious = "bank" in message.lower()

    if suspicious:
        session.register_flag()

    response = {
        "status": "ok",
        "flagged": suspicious,
        "flag_count": session.flag_count,
        "state": session.state
    }

    if session.is_locked():
        response["warning"] = "Session locked. Please revalidate identity."
    elif suspicious:
        response["warning"] = "Suspicious behavior detected."

    return jsonify(response)
