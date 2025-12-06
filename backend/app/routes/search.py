from backend.app.utils.jwt import require_auth
from backend.app.services.search import search_faculty_service
from backend.app.utils.search_filters import get_valid_search_filters

from flask import Blueprint, request, jsonify


search_bp = Blueprint("search", __name__)


@search_bp.route("/faculty", methods=["GET"])
@require_auth
def search_faculty():
    """
    TODO: Enforce query lengths. Throw error if query is too long.
    Search for faculty members based on query parameters.

    Query parameters:
    - query: General search query (searches across all fields)
    - keywords: Comma-separated keywords to filter by
    - first_name: Filter by first name
    - last_name: Filter by last name
    - department: Filter by department
    - institution: Filter by institution

    Returns:
        tuple: A tuple containing (jsonify response, status_code).
    """
    # Check if at least one search parameter has a non-empty value
    has_search_params = any(
        request.args.get(param, "").strip()
        for param in ["query", "keywords", *get_valid_search_filters()]
    )
    
    if not has_search_params:
        return jsonify([]), 200
    
    response = search_faculty_service(result_limit=50, **request.args)
    return response
