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

    # Automaton transition
    new_state = apply_action(action)

    # Prolog reasoning
    add_action(action)
    behavior = classify_behavior()

    # Broadcast real-time logs
    emit("log", {
        "text": f"Action: {action}\nState: {new_state}\nBehavior: {behavior}"
    }, broadcast=True)

    # Update diagram
    emit("diagram", get_automaton_json(), broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)

