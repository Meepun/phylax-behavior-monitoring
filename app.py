from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from api.routes import api_blueprint

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

app.register_blueprint(api_blueprint, url_prefix="/api")

@socketio.on("send_message")
def handle_message(data):
    socketio.emit("receive_message", data, include_self=False)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)