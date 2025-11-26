"""
Faculty-related API endpoints

v11.25.2025
Contributions:
    Architecture/Boilerplate written by Clayton Durepos
"""

from backend.app.services.search_service import search_faculty
from backend.app.utils.search_filters import get_valid_search_filters

from flask import Blueprint, request, jsonify

faculty_bp = Blueprint("faculty", __name__)

# GET by optional filters
@faculty_bp.route("", methods=["GET"])
def list_faculty():
    return None

@faculty_bp.route("", methods=["POST"])
def create_faculty():
    return None

# GET by faculty_id
@faculty_bp.route("/<string:faculty_id>", methods=["GET"])
def get_faculty():
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
