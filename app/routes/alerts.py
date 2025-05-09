from flask import Blueprint, jsonify

# Create the blueprint
bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

@bp.route('/', methods=['GET'])
def get_alerts():
    """Get a list of alerts"""
    # Placeholder implementation
    return jsonify({"message": "Alerts endpoint coming soon"}), 501
