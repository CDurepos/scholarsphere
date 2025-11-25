"""
Institution-related API endpoints
v11.25.2025

Contributions:
    Architecture/boilerplate by Clayton Durepos
"""

from backend.app.services.search_service import search_faculty
from backend.app.utils.search_filters import get_valid_search_filters

from flask import Blueprint, request, jsonify


institution_bp = Blueprint("institution", __name__)

sample = [
        {
            "institution_id": "107",
            "name": "Central Maine Community College",
        },
        {   
            "institution_id": "108",
            "name": "Kennebec Valley Community College",
        },
        {
            "institution_id": "456",
            "name": "University of Maine",
        },
        {
            "institution_id": "789",
            "name": "University of Maine at Augusta",
        },
        {
            "institution_id": "102",
            "name": "University of Maine at Fort Kent",
        },
        {
            "institution_id": "103",
            "name": "University of Maine at Machias",
        },
        {
            "institution_id": "101",
            "name": "University of Maine at Presque Isle",
        },
        {   
            "institution_id": "123",
            "name": "University of Southern Maine",
        },
        {
            "institution_id": "104",
            "name": "Southern Maine Community College",
        },
        {
            "institution_id": "105",
            "name": "York County Community College",
        }
    ]


@institution_bp.route("", methods=["GET"])
@institution_bp.route("/", methods=["GET"])
def institution():

    # For pre-db connection testing
    return jsonify(sample)
