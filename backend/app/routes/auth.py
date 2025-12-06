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
from backend.app.services.session import (
    create_session,
    get_session_by_token_hash,
    hash_token,
    revoke_session,
    revoke_all_sessions,
)
from backend.app.utils.jwt import generate_access_token
from flask import Blueprint, request, jsonify, make_response

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
        
        return jsonify({"error": error_msg}), 500

# Login verification
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login with username and password.
    
    Expected request body:
    {
        "username": "johndoe",
        "password": "plaintextpassword",
        "remember_me": false  // Optional: extends session to 30 days if true
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
        faculty_id = result["faculty_id"]
        
        # Check for remember_me flag (defaults to False)
        remember_me = bool(data.get("remember_me", False))
        
        # Generate access token (JWT)
        access_token = generate_access_token(faculty_id)
        
        # Create session and generate refresh token
        refresh_token, session_id, expiration_days = create_session(faculty_id, remember_me)
        
        # Create response with access token in JSON body
        response = make_response(jsonify({
            "access_token": access_token,
            "faculty_id": faculty_id,
            "faculty": result["faculty"]
        }), 200)
        
        # Set cookie with expiration matching the session
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=expiration_days * 24 * 60 * 60,
            path="/"
        )
        
        return response
        
    except Exception as e:
        error_msg = str(e)
        
        if "Invalid password" in error_msg:
            return jsonify({"error": "Invalid password"}), 401
        elif "Username not found" in error_msg:
            return jsonify({"error": "Username not found"}), 401
        elif "Login failed" in error_msg:
            return jsonify({"error": "Login failed. Please try again."}), 401
        elif "hash_password" in error_msg or "function" in error_msg.lower():
            return jsonify({"error": "Database configuration error. Please contact support."}), 500
        
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
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    """
    Refresh access token using refresh token from cookie.
    
    Returns:
        JSON response with new access_token, or error message
    """
    try:
        refresh_token = request.cookies.get("refresh_token")
        
        if not refresh_token:
            return jsonify({"error": "Refresh token not found"}), 401
        
        token_hash = hash_token(refresh_token)
        session = get_session_by_token_hash(token_hash)
        
        if not session:
            return jsonify({"error": "Invalid or expired refresh token"}), 401
        
        faculty_id = session["faculty_id"]
        access_token = generate_access_token(faculty_id)
        
        return jsonify({
            "access_token": access_token
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to refresh token"}), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logout by revoking the current session.
    
    Revokes the session associated with the refresh token in the cookie.
    
    Returns:
        JSON response with success message
    """
    try:
        # Get refresh token from cookie
        refresh_token = request.cookies.get("refresh_token")
        
        if refresh_token:
            # Hash and revoke the session
            token_hash = hash_token(refresh_token)
            revoke_session(token_hash)
        
        # Create response that clears the cookie
        response = make_response(jsonify({
            "message": "Logged out successfully"
        }), 200)
        
        # Clear the refresh token cookie
        response.set_cookie(
            "refresh_token",
            "",
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=0  # Expire immediately
        )
        
        return response
        
    except Exception as e:
        return jsonify({"error": "Failed to logout"}), 500