# PYTHON PATH GOES HERE
import os, sys, logging, faulthandler
from dotenv import load_dotenv
from nltk import download as NLTK_Downloader

sys.path.insert(0, os.path.abspath("."))

logging.basicConfig(filename="./log/flask.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")

faulthandler.enable()

NLTK_Downloader([
    "stopwords", "wordnet", "punkt",
    "averaged_perceptron_tagger"
], quiet=True)

load_dotenv('.env')

from app import app

app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")

if __name__ == "__main__":
    app.run(
        host=os.environ.get("FLASK_HOST"),
        port=os.environ.get("FLASK_PORT"),
        debug=os.environ.get("DEBUG"),
        threaded=True)
