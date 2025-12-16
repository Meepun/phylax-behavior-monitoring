from flask import Flask, render_template
from flask_cors import CORS
from api.routes import api_blueprint

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(api_blueprint, url_prefix="/api")

    # Route for frontend state diagram
    @app.route("/")
    def index():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)