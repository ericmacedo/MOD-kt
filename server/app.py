# Flask
from flask import Flask
from flask_cors import CORS
from flask_compress import Compress

# Application
from api import api

FRONTEND_ROUTES = [
    "", "corpus", "dashboard", "sessions"]

app = Flask(__name__, static_url_path="")
Compress(app)
CORS(app)

app.register_blueprint(api, url_prefix='/api/')


@app.route("/", defaults={"path": ""})
@app.route("/<path>")
def index(path):
    if path in FRONTEND_ROUTES:
        return app.send_static_file("index.html")
    else:
        return app.send_static_file(path)
