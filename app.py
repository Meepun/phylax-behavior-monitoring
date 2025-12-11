from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from automata import apply_action, get_automaton_json
from prolog_engine import add_action, classify_behavior

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("send_action")
def handle_action(data):
    action = data["action"]

    # Apply action in automaton
    new_state = apply_action(action)

    # Classify behavior with Prolog
    add_action(action)  # optional: store action history
    behavior = classify_behavior(action)

    # Get full FSM JSON for frontend
    automaton_json = get_automaton_json()

    emit("behavior_update", {
        "action": action,
        "state": new_state,
        "behavior": behavior,
        "states": automaton_json["states"],
        "transitions": automaton_json["transitions"]
    })

    emit("chat", {"text": f"System: processed action '{action}'"}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
