from backend.app.utils.jwt import require_auth
from backend.app.services.rate_limit import generate_keyword_service

from flask import Blueprint, request, jsonify

rate_limit_bp = Blueprint("rate_limit", __name__)

# House all rate limited endpoints here.


@rate_limit_bp.route("/<string:faculty_id>/generate-keyword", methods=["GET"])
@require_auth
def generate_keyword(faculty_id):
    """
    Generate keywords for a faculty member using their biography.

    Args:
        faculty_id (str): The UUID of the faculty member.

    Returns:
        tuple: A tuple containing (jsonify response, status_code).
    """
    response = generate_keyword_service(faculty_id)
    return response
