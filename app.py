# REPLACE LATER WITH GRAPHS ETC

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

# Example automaton state
current_state = "S0"

@app.route("/")
def admin():
    return render_template("admin.html")

@socketio.on("user_action")
def handle_action(data):
    global current_state

    action = data.get("action")

    # Simple automaton logic example
    if current_state == "S0" and action == "start":
        current_state = "S1"
    elif current_state == "S1" and action == "stop":
        current_state = "S0"

    emit("behavior_update", {
        "state": current_state,
        "action": action
    }, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
