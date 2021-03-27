# PYTHON PATH GOES HERE
import os
import sys
import logging
from dotenv import load_dotenv
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, os.path.abspath("."))

load_dotenv('.env')

from app import app

app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")

if __name__ == "__main__":
    app.run(
        host=os.environ.get("FLASK_HOST"),
        port=os.environ.get("FLASK_PORT"),
        debug=os.environ.get("DEBUG"))