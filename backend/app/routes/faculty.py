"""
Faculty-related API endpoints

v11.25.2025
"""

from backend.app.services.faculty import (
    create_faculty as create_faculty_service, 
    update_faculty as update_faculty_service,
    get_faculty as get_faculty_service
)
from backend.app.utils.jwt import require_auth
from backend.app.db.transaction_context import start_transaction
from backend.app.db.procedures import (
    sql_read_faculty_researches_keyword_by_faculty,
    sql_add_keyword_for_faculty,
    sql_delete_faculty_researches_keyword,
    sql_delete_all_faculty_keywords,
)

from flask import Blueprint, request, jsonify, g

faculty_bp = Blueprint("faculty", __name__)

# GET by optional filters
@faculty_bp.route("/", methods=["GET"])
def list_faculty():
    return jsonify({"message": "Not implemented"}), 501

@faculty_bp.route("/", methods=["POST"])
def create_faculty():
    """
    Create a new faculty member.
    
    Expected request body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "institution_name": "University of Southern Maine",
        "emails": ["john.doe@example.com"],
        "phones": ["207-555-1234"],
        "departments": ["Computer Science"],
        "titles": ["Professor"],
        "biography": "...",
        "orcid": "...",
        "google_scholar_url": "...",
        "research_gate_url": "..."
    }
    
    Returns:
        JSON response with faculty_id (UUID v4) and message
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        if not data.get("first_name"):
            return jsonify({"error": "first_name is required"}), 400
        
        result = create_faculty_service(data)
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET by faculty_id
@faculty_bp.route("/<string:faculty_id>", methods=["GET"])
def get_faculty(faculty_id):
    """
    Get complete faculty data by faculty_id.
    
    Returns:
        JSON response with complete faculty data including:
        - Basic info (faculty_id, first_name, last_name, biography, etc.)
        - emails (list)
        - phones (list)
        - departments (list)
        - titles (list)
        - institution_name (string)
    """
    try:
        if not faculty_id:
            return jsonify({"error": "faculty_id is required"}), 400
        
        faculty_data = get_faculty_service(faculty_id)
        return jsonify(faculty_data), 200
        
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            return jsonify({"error": f"Faculty member with id {faculty_id} not found"}), 404
        
        return jsonify({"error": str(e)}), 500

# UPDATE by faculty_id
@faculty_bp.route("/<string:faculty_id>", methods=["PUT"])
@require_auth
def update_faculty(faculty_id):
    """
    Update faculty profile with transaction management.
    
    Developer: Owen Leitzell
    
    This endpoint updates faculty base info and all related tables
    (emails, phones, departments, titles) in a single transaction.
    
    Expected request body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "emails": ["john.doe@example.com"],
        "phones": ["207-555-1234"],
        "departments": ["Computer Science"],
        "titles": ["Professor"],
        "biography": "...",
        "orcid": "...",
        "google_scholar_url": "...",
        "research_gate_url": "..."
    }
    
    Note: For multi-valued fields (emails, phones, departments, titles),
    providing a list will replace all existing entries with the new list.
    Omit these fields to leave them unchanged.
    
    Returns:
        JSON response with message
    """
    # Verify the user is updating their own profile
    current_faculty_id = g.faculty_id
    if current_faculty_id != faculty_id:
        return jsonify({"error": "Unauthorized: You can only update your own profile"}), 403
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        if not faculty_id:
            return jsonify({"error": "faculty_id is required"}), 400
        
        # Use service layer function which handles transaction management
        result = update_faculty_service(faculty_id, data)
        return jsonify(result), 200
        
    except Exception as e:
        error_msg = str(e).lower()
        if "does not exist" in error_msg or "not found" in error_msg:
            return jsonify({"error": f"Faculty member with id {faculty_id} not found"}), 404
        
        return jsonify({
            "error": f"Failed to update profile: {str(e)}"
        }), 500
    

# DELETE faculty with faculty_id
@faculty_bp.route("/<string:faculty_id>", methods=["DELETE"])
def delete_faculty(faculty_id):
    return None

# GET recommendations for a faculty by faculty_id
@faculty_bp.route("/<string:faculty_id>/rec", methods=["GET"])
def faculty_rec(faculty_id):
    return None


# Keyword endpoints
@faculty_bp.route("/<string:faculty_id>/keyword", methods=["GET"])
def get_faculty_keywords(faculty_id):
    """
    Get all keywords (research interests) for a faculty member.
    
    Path Parameters:
        faculty_id (str): UUID of the faculty member
    
    Returns:
        JSON array of keyword names
    
    Example:
        GET /api/faculty/uuid-here/keyword
        -> ["machine learning", "artificial intelligence", "data science"]
    """
    if not faculty_id:
        return jsonify({"error": "faculty_id is required"}), 400
    
    try:
        with start_transaction() as ctx:
            results = sql_read_faculty_researches_keyword_by_faculty(ctx, faculty_id)
            keywords = [row.get("name") for row in results if row.get("name")]
        return jsonify(keywords)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@faculty_bp.route("/<string:faculty_id>/keyword", methods=["PUT"])
@require_auth
def update_faculty_keywords(faculty_id):
    """
    Replace all keywords for a faculty member with a new list.
    
    Requires authentication and can only be done by the faculty member themselves.
    
    Path Parameters:
        faculty_id (str): UUID of the faculty member
    
    Request Body:
        { "keywords": ["machine learning", "AI", "data science"] }
    
    Returns:
        { "message": "Keywords updated successfully" }
    """
    # Verify the user is updating their own profile
    current_faculty_id = g.faculty_id
    if current_faculty_id != faculty_id:
        return jsonify({"error": "Unauthorized: You can only update your own profile"}), 403
    
    data = request.get_json()
    if not data or "keywords" not in data:
        return jsonify({"error": "keywords array is required"}), 400
    
    keywords = data.get("keywords", [])
    if not isinstance(keywords, list):
        return jsonify({"error": "keywords must be an array"}), 400
    
    # Validate and normalize each keyword (lowercase for consistency)
    validated_keywords = []
    seen_keywords = set()  # Track normalized keywords to avoid duplicates
    for kw in keywords:
        if isinstance(kw, str):
            kw = kw.strip()
            if 2 <= len(kw) <= 64:
                normalized = kw.lower()
                # Only add if we haven't seen this normalized keyword already
                if normalized not in seen_keywords:
                    validated_keywords.append(kw)  # Keep original casing for display
                    seen_keywords.add(normalized)
    
    try:
        with start_transaction() as ctx:
            # Delete all existing keywords
            sql_delete_all_faculty_keywords(ctx, faculty_id)
            # Add new keywords
            for keyword in validated_keywords:
                sql_add_keyword_for_faculty(ctx, faculty_id, keyword)
        
        # Generate recommendations after keyword update
        # This ensures new connections appear immediately when keywords are added
        try:
            from backend.app.db.procedures import sql_generate_recommendations_for_faculty
            with start_transaction() as rec_ctx:
                sql_generate_recommendations_for_faculty(rec_ctx, faculty_id)
        except Exception as rec_err:
            # Log but don't fail the update if recommendation generation fails
            print(f"Warning: Failed to generate recommendations after keyword update: {rec_err}")
        
        return jsonify({"message": "Keywords updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
