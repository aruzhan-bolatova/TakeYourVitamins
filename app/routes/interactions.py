from flask import Blueprint, jsonify

# Create the blueprint
bp = Blueprint('interactions', __name__, url_prefix='/api/interactions')

@bp.route('/', methods=['GET'])
def get_interactions():
    """Get a list of interactions"""
    # Placeholder implementation
    return jsonify({"message": "Interactions endpoint coming soon"}), 501
