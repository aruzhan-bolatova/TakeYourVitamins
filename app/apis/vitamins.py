from flask import Blueprint, jsonify, request
from app.db.utils import (
    get_all_vitamins, 
    get_vitamin_by_id, 
    insert_vitamin, 
    update_vitamin, 
    delete_vitamin, 
    search_vitamins_by_name,
    import_vitamins_from_json
)

vitamins_blueprint = Blueprint('vitamins', __name__, url_prefix='/api/vitamins')

# API endpoints have been removed as requested 