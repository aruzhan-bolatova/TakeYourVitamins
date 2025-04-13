from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint
import os

def create_app():
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config.from_pyfile('../app/config.py')
    
    # Register API blueprints
    from app.apis.vitamins import vitamins_blueprint
    app.register_blueprint(vitamins_blueprint)
    
    # Register Swagger UI blueprint
    from app.swagger import swagger_template
    
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/swagger.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Take Your Vitamins API"
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Add route for swagger.json
    @app.route(API_URL)
    def swagger_json():
        return jsonify(swagger_template)
    
    return app
