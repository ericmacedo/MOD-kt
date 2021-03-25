# PYTHON PATH GOES HERE
import os
import sys
import logging
from dotenv import load_dotenv
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, os.path.abspath("."))

load_dotenv('.env')

from __init__ import app