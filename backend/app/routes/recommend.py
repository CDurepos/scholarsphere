"""
Recommendation API endpoints
"""
from backend.app.services.recommend import (
    generate_recommendations,
    get_recommendations_for_faculty,
)
from flask import Blueprint, jsonify


recommend_bp = Blueprint("recommend", __name__)


@recommend_bp.route("/generate", methods=["POST"])
def generate():
    """
    Manually trigger recommendation generation.
    
    This is normally run by a scheduled event every 12 hours,
    but can be triggered manually if needed (e.g., after bulk data import).
    
    Returns:
        JSON response with success message or error
    """
    try:
        generate_recommendations()
        return jsonify({
            "message": "Recommendations generated successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@recommend_bp.route("/<string:faculty_id>", methods=["GET"])
def get_recommendations(faculty_id):
    """
    Get personalized recommendations for a specific faculty member.
    
    URL Parameters:
        faculty_id: UUID of the faculty member
    
    Returns:
        JSON array of recommended faculty with match details:
        - faculty_id, first_name, last_name, biography
        - institution_name, department_name
        - match_score (0.0 to 1.0)
        - recommendation_type: ENUM value (e.g., "shared_keyword")
        - recommendation_text: Human-readable text (e.g., "Similar research interests")
    """
    try:
        recommendations = get_recommendations_for_faculty(faculty_id)
        
        # Serialize recommendations for JSON response
        result = []
        for rec in recommendations:
            result.append({
                'faculty_id': rec.get('faculty_id'),
                'first_name': rec.get('first_name'),
                'last_name': rec.get('last_name'),
                'biography': rec.get('biography'),
                'institution_name': rec.get('institution_name'),
                'department_name': rec.get('department_name'),
                'match_score': float(rec.get('match_score', 0)),
                'recommendation_type': rec.get('recommendation_type'),
                'recommendation_text': rec.get('recommendation_text'),
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
