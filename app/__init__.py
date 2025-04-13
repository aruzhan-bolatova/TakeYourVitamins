# In app/__init__.py
from app.routes import auth, users, supplements, intake_logs, symptom_logs, interactions, alerts
from app.db import close_connection
from app.models import init_db
from flask import Flask
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
    jwt = JWTManager(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(supplements.bp)
    app.register_blueprint(intake_logs.bp)
    app.register_blueprint(symptom_logs.bp)
    app.register_blueprint(interactions.bp)
    app.register_blueprint(alerts.bp)

    with app.app_context():
        init_db()

    @app.teardown_appcontext
    def teardown_db(exception):
        close_connection()

    return app