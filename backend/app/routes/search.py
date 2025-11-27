from backend.app.services.search import search_faculty
from backend.app.utils.search_filters import get_valid_search_filters

from flask import Blueprint, request, jsonify


search_bp = Blueprint("search", __name__)

sample = [
    {
        "faculty_id": "123",
        "first_name": "Jane",
        "last_name": "Doe",
        "institution_name": "University of Southern Maine",
        "emails": ["bmansouri@usm.edu"],
        "phones": ["123-456-7890"],
        "departments": ["Computer Science"],
        "titles": ["Professor"],
        "biography": "Behrooz is a professor of computer science at University of Southern Maine.",
    }
]


@search_bp.route("/", methods=["GET"])
def search():
    # results = search_faculty(**request.args)

    # For pre-db connection testing
    return jsonify(sample)
    # return jsonify(results)
