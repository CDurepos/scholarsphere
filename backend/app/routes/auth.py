"""
Authentication-related API endpoints
v11.25.2025
"""
from backend.app.services.auth import (
    register_credentials as register_credentials_service,
    check_username_available,
    validate_login,
    check_credentials_exist,
)

from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)

# Register credentials to faculty_id
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register credentials for a faculty member.
    
    Expected request body:
    {
        "faculty_id": "uuid",
        "username": "johndoe",
        "password": "plaintextpassword"
    }
    
    Returns:
        JSON response with success message or error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        if not data.get("faculty_id"):
            return jsonify({"error": "faculty_id is required"}), 400
        
        if not data.get("username"):
            return jsonify({"error": "username is required"}), 400
        
        if not data.get("password"):
            return jsonify({"error": "password is required"}), 400
        
        result = register_credentials_service(data)
        return jsonify(result), 201
        
    except Exception as e:
        error_msg = str(e)
        # Check for specific database errors
        if "Username already exists" in error_msg:
            return jsonify({"error": "Username already exists"}), 409
        elif "Credentials already registered" in error_msg:
            return jsonify({"error": "Credentials already registered for this faculty member"}), 409
        elif "faculty_id doesn't exist" in error_msg or "foreign key constraint" in error_msg.lower():
            return jsonify({"error": "Invalid faculty_id"}), 404
        
        import traceback
        error_details = traceback.format_exc()
        print(f"Error registering credentials: {error_details}")
        return jsonify({"error": error_msg}), 500

# Login verification
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login with username and password.
    
    Expected request body:
    {
        "username": "johndoe",
        "password": "plaintextpassword"
    }
    
    Returns:
        JSON response with faculty_id and faculty data, or error message
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        if not data.get("username"):
            return jsonify({"error": "username is required"}), 400
        
        if not data.get("password"):
            return jsonify({"error": "password is required"}), 400
        
        result = validate_login(data)
        
        return jsonify({
            "faculty_id": result["faculty_id"],
            "faculty": result["faculty"]
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        # Check for specific login errors and return appropriate messages
        if "Invalid password" in error_msg:
            return jsonify({"error": "Invalid password"}), 401
        elif "Username not found" in error_msg:
            return jsonify({"error": "Username not found"}), 401
        elif "Login failed" in error_msg:
            return jsonify({"error": "Login failed. Please try again."}), 401
        
        import traceback
        error_details = traceback.format_exc()
        print(f"Error during login: {error_details}")
        return jsonify({"error": error_msg}), 500


# Check username availability
@auth_bp.route("/check-username", methods=["GET"])
def check_username():
    """
    Check if a username is available.
    
    Query parameter:
        ?username=<username>
    
    Returns:
        JSON response with available (bool) and username (str)
    """
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({"error": "username query parameter is required"}), 400
        
        result = check_username_available(username)
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error checking username: {error_details}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/check-credentials/<string:faculty_id>", methods=["GET"])
def check_credentials(faculty_id):
    """
    Check if credentials already exist for a faculty_id.
    
    Returns:
        JSON response with has_credentials (bool) and faculty_id
    """
    try:
        if not faculty_id:
            return jsonify({"error": "faculty_id is required"}), 400
        
        result = check_credentials_exist(faculty_id)
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error checking credentials: {error_details}")
        return jsonify({"error": str(e)}), 500