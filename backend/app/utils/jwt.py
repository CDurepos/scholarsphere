"""
JWT utility functions for access token generation and verification.
"""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
from backend.app.config import Config


def generate_access_token(faculty_id: str) -> str:
    """
    Generate a JWT access token for a faculty member.
    
    Args:
        faculty_id: UUID of the faculty member
    
    Returns:
        str: JWT access token
    """
    payload = {
        "faculty_id": faculty_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(
            minutes=Config.JWT_ACCESS_TOKEN_EXPIRATION_MINUTES
        ),
        "iat": datetime.datetime.utcnow(),
        "type": "access"
    }
    
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload
    
    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def get_token_from_request() -> str:
    """
    Extract JWT token from Authorization header.
    
    Expected format: "Bearer <token>"
    
    Returns:
        str: JWT token string
    
    Raises:
        ValueError: If token is missing or malformed
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise ValueError("Authorization header is missing")
    
    try:
        scheme, token = auth_header.split(" ", 1)
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authorization scheme")
        return token
    except ValueError:
        raise ValueError("Malformed authorization header")


def require_auth(f=None, *, allow_signup=False):
    """
    Decorator to require authentication for a route.
    
    Extracts and verifies JWT token from Authorization header.
    Sets g.faculty_id and g.token_type for use in route.
    
    Usage:
        @require_auth                    # Only access tokens
        @require_auth(allow_signup=True) # Access or signup tokens
    
    Args:
        allow_signup: If True, accepts both "access" and "signup" tokens.
                     Default is False (only "access" tokens).
    
    Returns 401 if token is missing or invalid.
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            try:
                token = get_token_from_request()
                payload = verify_token(token)
                token_type = payload.get("type")
                
                # Verify token type
                valid_types = ["access", "signup"] if allow_signup else ["access"]
                if token_type not in valid_types:
                    return jsonify({"error": "Invalid token type"}), 401
                
                # Set faculty_id and token_type in Flask's g object
                g.faculty_id = payload.get("faculty_id")
                g.token_type = token_type
                
                return func(*args, **kwargs)
            except ValueError as e:
                return jsonify({"error": str(e)}), 401
            except Exception as e:
                return jsonify({"error": "Authentication failed"}), 401
        
        return decorated_function
    
    # Allow @require_auth (no parentheses) or @require_auth(allow_signup=True)
    if f is not None:
        return decorator(f)
    return decorator


def optional_auth(f):
    """
    Decorator for routes that work with or without authentication.
    
    If a valid token is provided, sets g.faculty_id.
    If no token or invalid token, sets g.faculty_id to None.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.faculty_id = None
        
        try:
            token = get_token_from_request()
            payload = verify_token(token)
            
            if payload.get("type") == "access":
                g.faculty_id = payload.get("faculty_id")
        except:
            # Token missing or invalid - continue without auth
            pass
        
        return f(*args, **kwargs)
    
    return decorated_function


def generate_signup_token(faculty_id: str) -> str:
    """
    Generate a JWT signup token for updating faculty profile during signup.
    
    This token is issued after a user successfully looks up their existing
    faculty record. It allows them to update their profile before creating
    credentials, but only if no credentials exist yet.
    
    Args:
        faculty_id: UUID of the faculty member
    
    Returns:
        str: JWT signup token (expires in 15 minutes)
    """
    payload = {
        "faculty_id": faculty_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        "iat": datetime.datetime.utcnow(),
        "type": "signup"
    }
    
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def verify_signup_token(token: str, expected_faculty_id: str) -> dict:
    """
    Verify and decode a signup token.
    
    Args:
        token: JWT signup token string
        expected_faculty_id: The faculty_id that should be in the token
    
    Returns:
        dict: Decoded token payload
    
    Raises:
        ValueError: If token is invalid, expired, wrong type, or faculty_id mismatch
    """
    try:
        payload = verify_token(token)
        
        # Verify token type
        if payload.get("type") != "signup":
            raise ValueError("Invalid token type: expected signup token")
        
        # Verify faculty_id matches
        token_faculty_id = payload.get("faculty_id")
        if token_faculty_id != expected_faculty_id:
            raise ValueError("Token faculty_id does not match expected faculty_id")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Signup token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid signup token")

