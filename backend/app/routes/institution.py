"""
Institution-related API endpoints
"""

from backend.app.db.connection import get_connection
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


@institution_bp.route("/", methods=["GET"])
@institution_bp.route("", methods=["GET"])
def institution():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT institution_id, name FROM institution ORDER BY name")
        institutions = cursor.fetchall()
        return jsonify(institutions)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error fetching institutions: {error_details}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
