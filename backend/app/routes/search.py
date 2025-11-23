from backend.app.services.search_service import search_users

from flask import Blueprint, request, jsonify


search_bp = Blueprint("search", __name__)


@search_bp.get("/")
def search():
    query = request.args.get("query", "")
    results = search_users(query)
    return jsonify(results)
