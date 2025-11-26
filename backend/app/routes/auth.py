"""
Authentication-related API endpoints
v11.25.2025

Contributions:
    Architecture/boilerplate written by Clayton Durepos
"""
from backend.app.services.search_service import search_faculty
from backend.app.utils.search_filters import get_valid_search_filters

from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)

# Register credentials to faculty_id
@auth_bp.route("/register", methods=["POST"])
def register():
    return None

# Login verification
@auth_bp.route("/login", methods=["POST"])
def login():
    return None