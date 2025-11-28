from backend.app.services.search import search_faculty_service
from backend.app.utils.search_filters import get_valid_search_filters

from flask import Blueprint, request, jsonify


search_bp = Blueprint("search", __name__)


@search_bp.route("/", methods=["GET"])
@search_bp.route("", methods=["GET"])
def search():
    results = search_faculty_service(**request.args)
    return jsonify(results)
