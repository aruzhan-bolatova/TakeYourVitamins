# In app/__init__.py
from app.routes import auth, users, supplements, intake_logs, symptom_logs, interactions, alerts
from app.db import close_connection
from app.models import init_db
from flask import Flask, jsonify, redirect
from flask_jwt_extended import JWTManager
from app.swagger import swagger_template, swagger_ui_blueprint
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')
    jwt = JWTManager(app)

    # Register route blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(supplements.bp)
    app.register_blueprint(intake_logs.bp)
    app.register_blueprint(symptom_logs.bp)
    app.register_blueprint(interactions.bp)
    app.register_blueprint(alerts.bp)
    
    # Register Swagger UI blueprint
    app.register_blueprint(swagger_ui_blueprint)
    
    # Create a route for the Swagger JSON
    @app.route('/static/swagger.json')
    def swagger():
        return jsonify(swagger_template)

    with app.app_context():
        init_db()

    @app.teardown_appcontext
    def teardown_db(exception):
        close_connection()
        
    # Add a basic route for the root path that redirects to the Swagger UI
    @app.route('/')
    def index():
        return redirect('/api/docs')

    return app