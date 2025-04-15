from flask import Blueprint, jsonify, request
from app.models import Interaction, User, Supplement
from app.db.db import get_database as get_db
from bson.objectid import ObjectId 

# Create the blueprint
bp = Blueprint('interactions', __name__, url_prefix='/api/interactions')



#add interactions
@bp.route('/interactions', methods=['POST'])
@admin_required
def add_interaction():
    """Add a new interaction"""
    try:
        # Validate request has JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        interaction_data = request.json
        
        # Validate interaction data exists
        if not interaction_data:
            return jsonify({"error": "Empty interaction data"}), 400
            
        # Create and validate the interaction object
        interaction = Interaction(interaction_data)
        interaction.validate_data(interaction_data)  # Validate the incoming data
        
        # Insert the interaction into the database
        db = get_db()
        interaction_dict = interaction.to_dict()
        result = db.Interactions.insert_one(interaction_dict)
        
        # Verify insertion was successful
        if not result.inserted_id:
            return jsonify({"error": "Failed to insert interaction"}), 500
            
        # Return the newly created document's _id
        response = {
            "message": "Interaction created successfully", 
            "_id": str(result.inserted_id)
        }
        return jsonify(response), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

#update interaction
@bp.route('/interactions/<string:interaction_id>', methods=['PUT'])
@admin_required
def update_interaction(interaction_id):
    """Update an existing interaction"""
    try:
        _id = ObjectId(interaction_id)  # Convert the string ID to ObjectId
        interaction_data = request.json
        Interaction.update(_id, interaction_data)
        return jsonify({"message": "Interaction updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

#delete interaction
@bp.route('/interactions/<string:interaction_id>', methods=['DELETE'])
@admin_required
def delete_interaction(interaction_id):
    """Delete an interaction (soft delete by default)"""
    try:
        _id = ObjectId(interaction_id)  # Convert the string ID to ObjectId
        soft_delete = request.args.get('soft', 'true').lower() == 'true'  # Default to soft delete
        success = Interaction.delete(_id, soft_delete=soft_delete)
        if not success:
            return jsonify({"error": "Interaction not found"}), 404
        return jsonify({"message": "Interaction deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

#check for interaction between two supplements or one supplement and one food
@bp.route('/interactions/check', methods=['GET'])
def check_interactions(intake_list, food_list):
    interactions=Interaction.check_interactions(intake_list, food_list)

    if(interactions != []):
        return jsonify({
            "message": "Interaction check successful, interactions found",
            "interactions": interactions
            }), 200

    return jsonify({
            "message": "Interaction check successful, no interactions found",
            "interactions": []
            }), 200
    




#get all alerts given a list of supplements and a list of foods
@bp.route('/intake/check-interactions', methods=['POST'])
def generate_alerts_from_list(intake_list, food_list):
    """Check for interactions based on the user's intake list and food items"""
    alerts = Interaction.generate_alerts(intake_list, food_list)

    if(alerts != []):
        return jsonify({
            "message": "Interaction check successful, alerts generated",
            "alerts": alerts
            }), 200

    return jsonify({
        "message": "Interaction check successful, no alerts generated",
        "alerts": []
        }), 200



#get intercations of a supplement by ID
@bp.route('api/supplements/<string:supplement_id>/interactions', methods=['GET'])
def get_interactions_by_supplement_ID(supplement_ID: str):
    """Get a list of interactions"""
    results = Interaction.find_by_supplement(supplement_ID)

    if(results != []):
        return jsonify({
            "message": "Interaction search successful, no interactions found for this supplement",
            "results": results
            }), 200
    
    return jsonify({
        "message": "Interaction search successful, interactions for this supplement found",
        "results": []
        }), 200




