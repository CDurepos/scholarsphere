from flask import Blueprint, request, jsonify
from backend.app.db.connection import get_connection

equipment_bp = Blueprint("equipment", __name__)

@equipment_bp.route("/search", methods=["GET"])
def search_equipment():
    keywords = request.args.get("keywords", "")
    locations = request.args.getlist("location")
    available_only = request.args.get("available", "false").lower() == "true"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT e.equipment_id, e.name, e.description, e.availability,
               i.name AS institution_name, i.city
        FROM equipment e
        JOIN institution i ON e.institution_id = i.institution_id
        WHERE 1=1
    """
    params = []

    if keywords:
        sql += " AND (e.name LIKE %s OR e.description LIKE %s)"
        kw = f"%{keywords}%"
        params.extend([kw, kw])

    if locations:
        sql += " AND ("
        clauses = []
        for loc in locations:
            clauses.append("(i.city = %s OR i.zip = %s)")
            params.extend([loc, loc])
        sql += " OR ".join(clauses) + ")"

    if available_only:
        sql += " AND e.availability = 'available'"

    cursor.execute(sql, tuple(params))
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(results)
