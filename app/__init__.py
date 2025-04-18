# In app/__init__.py
from app.routes import auth, users, supplements, intake_logs, symptom_logs, interactions, alerts, reports
from app.db.db import register_shutdown_handler  # Update import for new function
from app.models import init_db, TokenBlacklist
from app.utils.error_handlers import register_error_handlers, APIError, handle_api_error
from flask import Flask, jsonify, redirect
from flask_jwt_extended import JWTManager
from app.swagger import swagger_template, swagger_ui_blueprint
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')
    jwt = JWTManager(app)
    
    # JWT configuration to check for blacklisted tokens
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return TokenBlacklist.is_blacklisted(jti)
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has been revoked',
            'code': 'token_revoked'
        }), 401

    # Register route blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(supplements.bp)
    app.register_blueprint(intake_logs.bp)
    app.register_blueprint(symptom_logs.bp)
    app.register_blueprint(interactions.bp)
    app.register_blueprint(alerts.bp)
    app.register_blueprint(reports.bp)
    
    # Register Swagger UI blueprint
    app.register_blueprint(swagger_ui_blueprint)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register custom error handler for APIError
    app.errorhandler(APIError)(handle_api_error)
    
    # Create a route for the Swagger JSON
    @app.route('/static/swagger.json')
    def swagger():
        return jsonify(swagger_template)

    with app.app_context():
        init_db()

    # Register the improved MongoDB connection shutdown handler
    register_shutdown_handler(app)
    
    # Add a basic route for the root path that redirects to the Swagger UI
    @app.route('/')
    def index():
        return redirect('/api/docs')

    # Add a health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': 'API is up and running'
        })

    return app