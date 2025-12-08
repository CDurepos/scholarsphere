"""
Author(s):Clayton Durepos, Abby Pitcairn, Aidan Bell
"""

"""
Institution-related API endpoints
"""

from flask import Blueprint, jsonify
from backend.app.services.institution import get_institutions_from_json

institution_bp = Blueprint("institution", __name__)

@institution_bp.route("/list", methods=["GET"])
def institution_list():
    try:
        institutions = get_institutions_from_json()
        institutions_sorted = sorted(institutions, key=lambda x: x.get("name",""))
        return jsonify(institutions_sorted)
    except Exception as e:
        print("Institution load error:", e)
        return jsonify({"error": str(e)}), 500

