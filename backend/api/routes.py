from flask import Blueprint, request, jsonify

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/message", methods=["POST"])
def process_message():
    data = request.json

    user_id = data.get("user_id")
    message = data.get("message")
    timestamp = data.get("timestamp")

    if not message:
        return jsonify({"error": "Message required"}), 400

    # Placeholder response (logic added later)
    return jsonify({
        "status": "ok",
        "flagged": False,
        "warning": None
    })
