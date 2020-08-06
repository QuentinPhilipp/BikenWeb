from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

app = Flask(__name__)

from biken import routes
