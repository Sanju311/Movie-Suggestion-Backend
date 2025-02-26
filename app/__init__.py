from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Import and register your blueprint from controller
    from .controller import controller_bp
    app.register_blueprint(controller_bp)
    return app

