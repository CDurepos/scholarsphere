from backend.app.services.search import search_faculty_service
from backend.app.utils.search_filters import get_valid_search_filters

from flask import Blueprint, request, jsonify


search_bp = Blueprint("search", __name__)


@search_bp.route("/faculty", methods=["GET"])
def search_faculty():
    """
    Search for faculty members based on query parameters.

    Query parameters:
    - query: General search query (searches across all fields)
    - first_name: Filter by first name
    - last_name: Filter by last name
    - department: Filter by department
    - institution: Filter by institution

    Returns:
        tuple: A tuple containing (jsonify response, status_code).
    """
    response = search_faculty_service(**request.args)
    return response
