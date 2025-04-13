from flask import Blueprint, jsonify

# Create the blueprint
bp = Blueprint('supplements', __name__, url_prefix='/api/supplements')

@bp.route('/', methods=['GET'])
def get_supplements():
    """Get a list of supplements"""
    # Placeholder implementation
    return jsonify({"message": "Supplements endpoint coming soon"}), 501
