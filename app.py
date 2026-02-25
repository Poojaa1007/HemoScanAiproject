"""
HemoVision AI – Main Application
==================================
Flask application entry point.
Registers all blueprints and loads the ML model at startup.
"""

import os
import sys

# Add app directory to path for clean imports
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template
from routes.prediction import prediction_bp
from routes.diet import diet_bp
from routes.admin import admin_bp
from services.model_service import load_model


def create_app():
    """Application factory."""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    app.secret_key = 'hemovision-ai-secret-key-2024'

    # Register blueprints
    app.register_blueprint(prediction_bp)
    app.register_blueprint(diet_bp)
    app.register_blueprint(admin_bp)

    # Load ML model at startup
    with app.app_context():
        try:
            load_model()
            print("✅ ML Model loaded successfully")
        except Exception as e:
            print(f"⚠️  Model not found. Run train_model.py first. Error: {e}")

    # Main page route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('index.html', error='Page not found'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('index.html', error='Internal server error'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
