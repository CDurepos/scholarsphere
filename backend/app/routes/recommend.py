from backend.app.services.recommend_service import recommend_faculty

from flask import Blueprint, request, jsonify


recommend_bp = Blueprint("recommend", __name__)


@recommend_bp.route("", methods=["GET"])
@recommend_bp.route("/", methods=["GET"])
def recommend():
    results = recommend_faculty(**request.args)
    return jsonify(results)
