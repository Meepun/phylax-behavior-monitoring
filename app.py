from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from automata import apply_action, get_automaton_json

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("index.html")

# wag nyo seryosohin part na toh 
@socketio.on("send_action")
def handle_action(data):
    action = data["action"]

    # Update FSM using automata.py
    new_state = apply_action(action)
    automaton_json = get_automaton_json()

    # TEMP: simple behavior logic
    if action.lower() in ["hi", "hello"]:
        behavior = "normal"
    elif len(action) > 10:
        behavior = "suspicious"
    else:
        behavior = "normal"

    # Emit to frontend
    emit("behavior_update", {
        "action": action,
        "state": new_state,
        "behavior": behavior,
        "states": automaton_json["states"],
        "transitions": automaton_json["transitions"]
    })

if __name__ == "__main__":
    socketio.run(app, debug=True)
