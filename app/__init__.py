from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register your blueprint from controller
    from .controller import controller_bp
    app.register_blueprint(controller_bp)
    return app

