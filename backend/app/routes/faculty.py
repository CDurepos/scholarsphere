"""
Faculty-related API endpoints

v11.25.2025
"""

from backend.app.services.faculty import create_faculty

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
        
        result = create_faculty(data)
        return jsonify(result), 201
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating faculty: {error_details}")  # Log to console for debugging
        return jsonify({"error": str(e), "details": error_details}), 500

# GET by faculty_id
@faculty_bp.route("/<string:faculty_id>", methods=["GET"])
def get_faculty(faculty_id):
    return None

# UPDATE by faculty_id
@faculty_bp.route("/<string:faculty_id>", methods=["PUT"])
def update_faculty(faculty_id):
    return None

# DELETE faculty with faculty_id
@faculty_bp.route("/<string:faculty_id>", methods=["DELETE"])
def delete_faculty(faculty_id):
    return None

# GET recommendations for a faculty by faculty_id
@faculty_bp.route("/<string:faculty_id>/rec", methods=["GET"])
def faculty_rec(faculty_id):
    return None
