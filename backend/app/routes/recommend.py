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
    """Manually trigger recommendation generation."""
    try:
        generate_recommendations()
        return jsonify({"message": "Recommendations generated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recommend_bp.route("/<string:faculty_id>", methods=["GET"])
def get_recommendations(faculty_id):
    """
    Get personalized recommendations for a faculty member.
    Returns faculty details with recommendation_type and recommendation_text.
    """
    try:
        recommendations = get_recommendations_for_faculty(faculty_id)
        
        result = []
        for rec in recommendations:
            result.append({
                'faculty_id': rec.get('faculty_id'),
                'first_name': rec.get('first_name'),
                'last_name': rec.get('last_name'),
                'biography': rec.get('biography'),
                'institution_name': rec.get('institution_name'),
                'department_name': rec.get('department_name'),
                'recommendation_type': rec.get('recommendation_type'),
                'recommendation_text': rec.get('recommendation_text'),
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
