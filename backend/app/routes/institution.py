"""
Institution-related API endpoints
"""

from backend.app.services.institution import get_institutions_from_json
from flask import Blueprint, jsonify


institution_bp = Blueprint("institution", __name__)



@institution_bp.route("/", methods=["GET"])
def institution():
    """
    Get list of available institutions from the JSON file.
    Returns institutions that users can select during signup.
    """
    try:
        institutions = get_institutions_from_json()
        institution_list = [{"name": inst.get("name")} for inst in institutions]
        return jsonify(sorted(institution_list, key=lambda x: x["name"]))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
