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
    sql_update_faculty,
    sql_delete_faculty_email_by_faculty,
    sql_delete_faculty_phone_by_faculty,
    sql_delete_faculty_department_by_faculty,
    sql_delete_faculty_title_by_faculty,
    sql_create_faculty_email,
    sql_create_faculty_phone,
    sql_create_faculty_department,
    sql_create_faculty_title,
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
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    if not faculty_id:
        return jsonify({"error": "faculty_id is required"}), 400
    
    try:
        with start_transaction() as tx:
            # Convert empty strings to None for optional fields
            def empty_to_none(value):
                return None if (value is None or (isinstance(value, str) and value.strip() == "")) else value
            
            # 1. Update base faculty information
            sql_update_faculty(
                tx,
                faculty_id,
                empty_to_none(data.get('first_name')),
                empty_to_none(data.get('last_name')),
                empty_to_none(data.get('biography')),
                empty_to_none(data.get('orcid')),
                empty_to_none(data.get('google_scholar_url')),
                empty_to_none(data.get('research_gate_url')),
                None  # scraped_from - don't update this via API
            )
            
            # 2. Delete old related records (only if arrays are provided in request)
            if 'emails' in data:
                sql_delete_faculty_email_by_faculty(tx, faculty_id)
                # 3. Insert new emails
                for email in data.get('emails', []):
                    if email and email.strip():
                        sql_create_faculty_email(tx, faculty_id, email.strip())
            
            if 'phones' in data:
                sql_delete_faculty_phone_by_faculty(tx, faculty_id)
                # 4. Insert new phones
                for phone in data.get('phones', []):
                    if phone and phone.strip():
                        sql_create_faculty_phone(tx, faculty_id, phone.strip())
            
            if 'departments' in data:
                sql_delete_faculty_department_by_faculty(tx, faculty_id)
                # 5. Insert new departments
                for dept in data.get('departments', []):
                    if dept and dept.strip():
                        sql_create_faculty_department(tx, faculty_id, dept.strip())
            
            if 'titles' in data:
                sql_delete_faculty_title_by_faculty(tx, faculty_id)
                # 6. Insert new titles
                for title in data.get('titles', []):
                    if title and title.strip():
                        sql_create_faculty_title(tx, faculty_id, title.strip())
            
            # Transaction commits automatically on success via context manager
            
        return jsonify({
            "message": "Profile updated successfully"
        }), 200
            
    except Exception as e:
        # Transaction already rolled back by context manager on exception
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
