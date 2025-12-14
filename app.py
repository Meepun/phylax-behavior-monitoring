from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

socketio = SocketIO(
    app,
    cors_allowed_origins="http://localhost:5173"
)

@socketio.on("user_action")
def handle_action(data):
    emit("behavior_update", {
        "state": "S1",
        "action": data["action"]
    }, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, port=5000)
