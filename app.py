from flask import Flask, render_template
from flask_cors import CORS
from api.routes import api_blueprint
from flask import Blueprint

frontend = Blueprint("frontend", __name__) 

@frontend.route("/")
def index():
    return render_template("index.html")

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(frontend)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)