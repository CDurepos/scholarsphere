from backend.app.utils.jwt import require_auth
from backend.app.services.search import search_faculty_service
from backend.app.utils.search_filters import get_valid_search_filters
from backend.app.db.transaction_context import start_transaction
from backend.app.db.procedures import sql_search_keywords

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
    
    Example:
        GET /api/search/keyword?q=mac&limit=10
        -> ["machine learning", "macroeconomics", "macrobiology"]
    """
    search_term = request.args.get("q", "").strip()
    
    if len(search_term) < 2:
        return jsonify([])
    
    try:
        limit = min(int(request.args.get("limit", 10)), 50)
    except ValueError:
        limit = 10
    
    try:
        with start_transaction() as ctx:
            results = sql_search_keywords(ctx, search_term, limit)
            keywords = [row.get("name") for row in results if row.get("name")]
        return jsonify(keywords)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
