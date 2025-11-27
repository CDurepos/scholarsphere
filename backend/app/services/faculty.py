import uuid
from datetime import date
from backend.app.db.connection import get_connection


def create_faculty(data: dict):
    """
    Service layer for creating a new faculty member.
    
    Creates a faculty record and all associated multi-valued attributes
    (emails, phones, departments, titles). Also handles institution relationship.
    
    Generates a UUID v4 for the faculty_id in Python before inserting into the database.
    
    Args:
        data: Dictionary containing faculty data:
            - first_name (required)
            - last_name (optional)
            - institution_name (optional)
            - emails (list, optional)
            - phones (list, optional)
            - departments (list, optional)
            - titles (list, optional)
            - biography (optional)
            - orcid (optional)
            - google_scholar_url (optional)
            - research_gate_url (optional)
    
    Returns:
        dict: Contains faculty_id and success message
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Generate UUID v4 for faculty_id in Python
        faculty_id = str(uuid.uuid4())
        
        # Convert empty strings to None for optional fields
        def empty_to_none(value):
            return None if (value is None or (isinstance(value, str) and value.strip() == "")) else value
        
        # Use the create_faculty stored procedure, passing the generated UUID
        # Try with new signature first (8 params including faculty_id)
        try:
            cursor.callproc(
                "create_faculty",
                (
                    faculty_id,  # Pass the Python-generated UUID v4
                    data.get("first_name"),
                    empty_to_none(data.get("last_name")),
                    empty_to_none(data.get("biography")),
                    empty_to_none(data.get("orcid")),
                    empty_to_none(data.get("google_scholar_url")),
                    empty_to_none(data.get("research_gate_url")),
                    None,  # scraped_from is always None for user signups
                ),
            )
            # Consume the result set from the procedure (returns faculty_id)
            stored_results = list(cursor.stored_results())
            if stored_results:
                stored_results[0].fetchall()
        except Exception as proc_error:
            # If procedure call fails, it might be the old signature
            # Try with old signature (7 params, no faculty_id)
            error_msg = str(proc_error).lower()
            if "wrong number of arguments" in error_msg or "parameter" in error_msg or "incorrect parameter count" in error_msg:
                print(f"Warning: Procedure may have old signature. Error: {proc_error}")
                print("Attempting with old signature (procedure will generate UUID)...")
                # Try old signature - procedure will generate UUID
                cursor.callproc(
                    "create_faculty",
                    (
                        data.get("first_name"),
                        empty_to_none(data.get("last_name")),
                        empty_to_none(data.get("biography")),
                        empty_to_none(data.get("orcid")),
                        empty_to_none(data.get("google_scholar_url")),
                        empty_to_none(data.get("research_gate_url")),
                        None,  # scraped_from is always None for user signups
                    ),
                )
                # Get the generated faculty_id from the procedure result
                stored_results = list(cursor.stored_results())
                if stored_results:
                    result = stored_results[0].fetchone()
                    if result and "faculty_id" in result:
                        faculty_id = result["faculty_id"]
            else:
                raise proc_error
        
        # Create emails
        emails = data.get("emails", []) or []
        for email in emails:
            if email and email.strip():
                cursor.callproc("create_faculty_email", (faculty_id, email.strip()))
                # create_faculty_email doesn't return a result set, but consume anyways to clear cursor
                try:
                    stored_results = list(cursor.stored_results())
                    if stored_results:
                        stored_results[0].fetchall()
                except:
                    pass
        
        # Create phones
        phones = data.get("phones", []) or []
        for phone in phones:
            if phone and phone.strip():
                cursor.callproc("create_faculty_phone", (faculty_id, phone.strip()))
                # Consume result set from the procedure
                stored_results = list(cursor.stored_results())
                if stored_results:
                    stored_results[0].fetchall()
        
        # Create departments
        departments = data.get("departments", []) or []
        for dept in departments:
            if dept and dept.strip():
                cursor.callproc("create_faculty_department", (faculty_id, dept.strip()))
                # Consume result set from the procedure
                stored_results = list(cursor.stored_results())
                if stored_results:
                    stored_results[0].fetchall()
        
        # Create titles
        titles = data.get("titles", []) or []
        for title in titles:
            if title and title.strip():
                cursor.callproc("create_faculty_title", (faculty_id, title.strip()))
                # Consume result set from the procedure
                stored_results = list(cursor.stored_results())
                if stored_results:
                    stored_results[0].fetchall()
        
        # Handle institution relationship if institution_name is provided
        institution_name = data.get("institution_name")
        if institution_name and institution_name.strip():
            # Look up institution_id by name
            cursor.execute(
                "SELECT institution_id FROM institution WHERE name = %s",
                (institution_name.strip(),)
            )
            institution_result = cursor.fetchone()
            
            if institution_result:
                institution_id = institution_result["institution_id"]
                # Create faculty-institution relationship with current date as start_date
                cursor.callproc(
                    "create_faculty_works_at_institution",
                    (faculty_id, institution_id, date.today(), None)
                )
                # create_faculty_works_at_institution doesn't return a result set, but consume anyways to clear cursor
                try:
                    stored_results = list(cursor.stored_results())
                    if stored_results:
                        stored_results[0].fetchall()
                except:
                    pass
        
        conn.commit()
        
        return {
            "faculty_id": faculty_id,
            "message": "Faculty member created successfully"
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in create_faculty service: {error_trace}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
