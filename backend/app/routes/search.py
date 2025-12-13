"""
Author(s): Aidan Bell, Clayton Durepos
"""

from backend.app.utils.jwt import require_auth
from backend.app.services.search import (
    search_faculty_service,
    search_keywords_service,
)
from backend.app.utils.search_filters import get_valid_search_filters
from flask import Blueprint, request, jsonify


search_bp = Blueprint("search", __name__)


@search_bp.route("/faculty", methods=["GET"])
@require_auth
def search_faculty():
    """
    Search for faculty members based on query parameters.

    Query parameters:
    - query: General search query (searches across all fields)
    - keywords: Comma-separated keywords to filter by
    - first_name: Filter by first name
    - last_name: Filter by last name
    - department: Filter by department
    - institution: Filter by institution

    Returns:
        JSON array of matching faculty members
    """
    has_search_params = any(
        request.args.get(param, "").strip()
        for param in ["query", "keywords", *get_valid_search_filters()]
    )
    
    if not has_search_params:
        return jsonify([]), 200
    
    results, status_code = search_faculty_service(result_limit=50, **request.args)
    return jsonify(results), status_code


@search_bp.route("/keyword", methods=["GET"])
def search_keywords():
    """
    Search keywords by prefix for autocomplete.
    
    Query Parameters:
        q (str): Search term (required, min 2 characters)
        limit (int): Max results (optional, default 10, max 50)
    
    Returns:
        JSON array of keyword names
    """
    search_term = request.args.get("q", "").strip()
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        limit = 10
    
    return search_keywords_service(search_term, limit)
