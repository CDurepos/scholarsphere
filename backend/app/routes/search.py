from backend.app.services.search_service import search_faculty
from backend.app.utils.search_filters import get_valid_search_filters

from flask import Blueprint, request, jsonify


search_bp = Blueprint("search", __name__)


@search_bp.get("/")
def search():
    results = search_faculty(**request.args)
    return jsonify(results)
