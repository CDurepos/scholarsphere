"""
Faculty-related API endpoints

v11.25.2025
"""

from backend.app.services.faculty import (
    create_faculty as create_faculty_service, 
    update_faculty as update_faculty_service,
    get_faculty as get_faculty_service
)

from flask import Blueprint, request, jsonify

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
def update_faculty(faculty_id):
    """
    Update an existing faculty member.
    
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
    
    Note: For multi-valued fields (emails, phones, departments, titles),
    providing a list will replace all existing entries with the new list.
    Omit these fields to leave them unchanged.
    
    Returns:
        JSON response with faculty_id and message
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        if not faculty_id:
            return jsonify({"error": "faculty_id is required"}), 400
        
        result = update_faculty_service(faculty_id, data)
        return jsonify(result), 200
        
    except Exception as e:
        error_msg = str(e).lower()
        if "does not exist" in error_msg or "not found" in error_msg:
            return jsonify({"error": f"Faculty member with id {faculty_id} not found"}), 404
        
        return jsonify({"error": str(e)}), 500
    

# DELETE faculty with faculty_id
@faculty_bp.route("/<string:faculty_id>", methods=["DELETE"])
def delete_faculty(faculty_id):
    return None

# GET recommendations for a faculty by faculty_id
@faculty_bp.route("/<string:faculty_id>/rec", methods=["GET"])
def faculty_rec(faculty_id):
    return None
