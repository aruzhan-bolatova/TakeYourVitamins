from flask import Blueprint, request, jsonify
from app.models.interaction import Interaction
from flask_jwt_extended import jwt_required

bp = Blueprint('alerts', __name__, url_prefix='/alerts')

@bp.route('/check', methods=['POST'])
@jwt_required()
def check_alerts():
    data = request.get_json()
    intake_list = data.get('intakeList', [])
    food_items = data.get('foodItems', [])
    alerts = Interaction.check_interactions(intake_list, food_items)
    return jsonify({'alerts': alerts}), 200