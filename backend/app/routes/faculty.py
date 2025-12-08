"""
Faculty-related API endpoints

v11.25.2025
"""

from backend.app.services.faculty import (
    create_faculty as create_faculty_service, 
    update_faculty as update_faculty_service,
    get_faculty as get_faculty_service,
    get_faculty_keywords as get_faculty_keywords_service,
    update_faculty_keywords as update_faculty_keywords_service,
)
from backend.app.services.auth import check_credentials_exist
from backend.app.utils.jwt import require_auth

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
@require_auth(allow_signup=True)
def update_faculty(faculty_id):
    """
    Update faculty profile with transaction management.
    
    Accepts access tokens (authenticated users) or signup tokens (during signup).
    
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
    
    Returns:
        JSON response with message
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Verify user can update this profile
        if g.faculty_id != faculty_id:
            return jsonify({"error": "Unauthorized: You can only update your own profile"}), 403
        
        # For signup tokens, verify no credentials exist yet
        if g.token_type == "signup":
            if check_credentials_exist(faculty_id).get("has_credentials"):
                return jsonify({"error": "Account already exists. Please log in."}), 403
        
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
    """
    try:
        keywords = get_faculty_keywords_service(faculty_id)
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
    if g.faculty_id != faculty_id:
        return jsonify({"error": "Unauthorized: You can only update your own profile"}), 403
    
    data = request.get_json()
    if not data or "keywords" not in data:
        return jsonify({"error": "keywords array is required"}), 400
    
    keywords = data.get("keywords", [])
    if not isinstance(keywords, list):
        return jsonify({"error": "keywords must be an array"}), 400
    
    try:
        result = update_faculty_keywords_service(faculty_id, keywords)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
