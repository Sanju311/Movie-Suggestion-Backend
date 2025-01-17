from flask import Flask

app = Flask(__name__)

# Import the controller to register routes
from app import controller