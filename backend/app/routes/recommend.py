from backend.app.services.recommend_service import recommend_collaborators

from flask import Blueprint, request, jsonify


recommend_bp = Blueprint("recommend", __name__)


@recommend_bp.get("/")
def recommend():
    user_id = request.args.get("user_id", type=int)
    results = recommend_collaborators(user_id)
    return jsonify(results)
