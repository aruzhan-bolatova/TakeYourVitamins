from flask import Blueprint, request, jsonify
from app.models.supplement import Supplement

bp = Blueprint('supplements', __name__, url_prefix='/supplements')

@bp.route('/', methods=['GET'])
def get_supplements():
    search_query = request.args.get('search', '')
    limit = int(request.args.get('limit', 50))
    skip = int(request.args.get('skip', 0))
    
    if search_query:
        # Basic search by name or in aliases
        filter_query = {
            '$or': [
                {'name': {'$regex': search_query, '$options': 'i'}},
                {'aliases': {'$regex': search_query, '$options': 'i'}}
            ]
        }
        supplements = list(Supplement.find_all(filter=filter_query, limit=limit, skip=skip))
    else:
        supplements = list(Supplement.find_all(limit=limit, skip=skip))
    
    # Remove MongoDB _id from response
    for s in supplements:
        if '_id' in s:
            s['_id'] = str(s['_id'])
    
    return jsonify(supplements), 200

@bp.route('/<supplement_id>', methods=['GET'])
def get_supplement(supplement_id):
    supplement = Supplement.find_by_supplement_id(supplement_id)
    if not supplement:
        return jsonify({'error': 'Supplement not found'}), 404
    
    # Convert MongoDB ObjectId to string
    if '_id' in supplement:
        supplement['_id'] = str(supplement['_id'])
    
    return jsonify(supplement), 200