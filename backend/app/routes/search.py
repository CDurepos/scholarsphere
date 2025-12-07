from backend.app.utils.jwt import require_auth
from backend.app.services.search import (
    search_faculty_service,
    search_keywords_service,
)
from backend.app.utils.search_filters import get_valid_search_filters
from backend.app.db.connection import get_connection

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
    limit = request.args.get("limit", 10)
    
    try:
        limit = int(limit)
    except ValueError:
        limit = 10
    
    return search_keywords_service(search_term, limit)

@search_bp.route("/equipment", methods=["GET"])
def search_equipment():
    """
    Search equipment by keywords, location, and availability.
    
    Query Parameters:
        keywords (str): Optional search keywords (searches name and description)
        location (list): Optional list of locations (city or zip codes), can be specified multiple times
        available (str): Optional "true" to filter by availability = 'available'
    
    Returns:
        JSON array of equipment records with institution information
    
    Example:
        GET /api/search/equipment?keywords=microscope&location=Portland&available=true
    """
    keywords = request.args.get("keywords", "")
    locations = request.args.getlist("location")
    available_only = request.args.get("available", "false").lower() == "true"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        sql = """
            SELECT e.equipment_id, e.name, e.description, e.availability,
                   i.name AS institution_name, i.city
            FROM equipment e
            JOIN institution i ON e.institution_id = i.institution_id
            WHERE 1=1
        """
        params = []

        if keywords:
            sql += " AND (e.name LIKE %s OR e.description LIKE %s)"
            kw = f"%{keywords}%"
            params.extend([kw, kw])

        if locations:
            sql += " AND ("
            clauses = []
            for loc in locations:
                clauses.append("(i.city = %s OR i.zip = %s)")
                params.extend([loc, loc])
            sql += " OR ".join(clauses) + ")"

        if available_only:
            sql += " AND e.availability = 'available'"

        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()

        return jsonify(results)
    finally:
        cursor.close()
        conn.close()
