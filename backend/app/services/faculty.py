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
        cursor.callproc(
            "create_faculty",
            (
                faculty_id,
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
        
        # Create emails
        emails = data.get("emails", []) or []
        for email in emails:
            if email and email.strip():
                cursor.callproc("create_faculty_email", (faculty_id, email.strip()))
                # Consume any result set to clear cursor
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
                # Consume any result set to clear cursor
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
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in create_faculty service: {error_trace}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_faculty(faculty_id: str):
    """
    Service layer for fetching complete faculty data by faculty_id.
    
    Fetches all faculty information including emails, phones, departments, titles,
    and institution relationships.
    
    Args:
        faculty_id: UUID of the faculty member to fetch
    
    Returns:
        dict: Complete faculty data including:
            - Basic info (faculty_id, first_name, last_name, biography, etc.)
            - emails (list)
            - phones (list)
            - departments (list)
            - titles (list)
            - institution_name (string, if available)
    
    Raises:
        Exception: If faculty_id doesn't exist
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get basic faculty info
        cursor.callproc("read_faculty", (faculty_id,))
        stored_results = list(cursor.stored_results())
        if not stored_results:
            raise Exception("Failed to retrieve faculty data")
        
        faculty_result = stored_results[0].fetchone()
        if not faculty_result:
            raise Exception("Faculty not found")
        
        # Fetch emails
        cursor.callproc("read_faculty_email", (faculty_id,))
        email_results = list(cursor.stored_results())
        emails = []
        if email_results:
            email_rows = email_results[0].fetchall()
            emails = [row.get('email') for row in email_rows if row.get('email')]
        
        # Fetch phones
        cursor.callproc("read_faculty_phone", (faculty_id,))
        phone_results = list(cursor.stored_results())
        phones = []
        if phone_results:
            phone_rows = phone_results[0].fetchall()
            phones = [row.get('phone_num') for row in phone_rows if row.get('phone_num')]
        
        # Fetch departments
        cursor.callproc("read_faculty_department", (faculty_id,))
        dept_results = list(cursor.stored_results())
        departments = []
        if dept_results:
            dept_rows = dept_results[0].fetchall()
            departments = [row.get('department_name') for row in dept_rows if row.get('department_name')]
        
        # Fetch titles
        cursor.callproc("read_faculty_title", (faculty_id,))
        title_results = list(cursor.stored_results())
        titles = []
        if title_results:
            title_rows = title_results[0].fetchall()
            titles = [row.get('title') for row in title_rows if row.get('title')]
        
        # Fetch institution (get the most recent/current one)
        # First, get the institution_id from the relationship
        cursor.callproc("read_faculty_institution", (faculty_id, None))
        institution_rel_results = list(cursor.stored_results())
        institution_name = None
        if institution_rel_results:
            institution_rel_rows = institution_rel_results[0].fetchall()
            if institution_rel_rows:
                # Get the most recent institution (first row due to ORDER BY start_date DESC)
                most_recent_institution_id = institution_rel_rows[0].get('institution_id')
                if most_recent_institution_id:
                    # Get the institution name
                    cursor.callproc("read_institution", (most_recent_institution_id,))
                    inst_results = list(cursor.stored_results())
                    if inst_results:
                        inst_rows = inst_results[0].fetchall()
                        if inst_rows:
                            institution_name = inst_rows[0].get('name')
        
        # Combine all faculty data
        complete_faculty = {
            **faculty_result,
            "emails": emails,
            "phones": phones,
            "departments": departments,
            "titles": titles,
            "institution_name": institution_name,
        }
        
        return complete_faculty
        
    except Exception as e:
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_faculty(faculty_id: str, data: dict):
    """
    Service layer for updating an existing faculty member.
    
    Updates a faculty record and all associated multi-valued attributes
    (emails, phones, departments, titles). Also handles institution relationship.
    
    Uses a "replace all" strategy for multi-valued attributes:
    - Deletes all existing entries for emails, phones, departments, titles
    - Creates new entries from the provided lists
    
    Args:
        faculty_id: UUID of the faculty member to update
        data: Dictionary containing faculty data to update:
            - first_name (optional)
            - last_name (optional)
            - institution_name (optional)
            - emails (list, optional) - replaces all existing emails
            - phones (list, optional) - replaces all existing phones
            - departments (list, optional) - replaces all existing departments
            - titles (list, optional) - replaces all existing titles
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
        
        # Convert empty strings to None for optional fields
        def empty_to_none(value):
            return None if (value is None or (isinstance(value, str) and value.strip() == "")) else value
        
        # Update basic faculty fields using the update_faculty stored procedure
        cursor.callproc(
            "update_faculty",
            (
                faculty_id,
                empty_to_none(data.get("first_name")),
                empty_to_none(data.get("last_name")),
                empty_to_none(data.get("biography")),
                empty_to_none(data.get("orcid")),
                empty_to_none(data.get("google_scholar_url")),
                empty_to_none(data.get("research_gate_url")),
                None,  # scraped_from - don't update this via API
            ),
        )
        # Consume the result set from the procedure
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
        
        # Handle emails: replace all existing emails
        if "emails" in data:
            # Delete all existing emails for this faculty member
            cursor.execute(
                "DELETE FROM faculty_email WHERE faculty_id = %s",
                (faculty_id,)
            )
            # Create new emails
            emails = data.get("emails", []) or []
            for email in emails:
                if email and email.strip():
                    cursor.callproc("create_faculty_email", (faculty_id, email.strip()))
                    # Consume result set if any
                    try:
                        stored_results = list(cursor.stored_results())
                        if stored_results:
                            stored_results[0].fetchall()
                    except:
                        pass
        
        # Handle phones: replace all existing phones
        if "phones" in data:
            # Delete all existing phones for this faculty member
            cursor.execute(
                "DELETE FROM faculty_phone WHERE faculty_id = %s",
                (faculty_id,)
            )
            # Create new phones
            phones = data.get("phones", []) or []
            for phone in phones:
                if phone and phone.strip():
                    cursor.callproc("create_faculty_phone", (faculty_id, phone.strip()))
                    # Consume result set
                    stored_results = list(cursor.stored_results())
                    if stored_results:
                        stored_results[0].fetchall()
        
        # Handle departments: replace all existing departments
        if "departments" in data:
            # Delete all existing departments for this faculty member
            cursor.execute(
                "DELETE FROM faculty_department WHERE faculty_id = %s",
                (faculty_id,)
            )
            # Create new departments
            departments = data.get("departments", []) or []
            for dept in departments:
                if dept and dept.strip():
                    cursor.callproc("create_faculty_department", (faculty_id, dept.strip()))
                    # Consume result set
                    stored_results = list(cursor.stored_results())
                    if stored_results:
                        stored_results[0].fetchall()
        
        # Handle titles: replace all existing titles
        if "titles" in data:
            # Delete all existing titles for this faculty member
            cursor.execute(
                "DELETE FROM faculty_title WHERE faculty_id = %s",
                (faculty_id,)
            )
            # Create new titles
            titles = data.get("titles", []) or []
            for title in titles:
                if title and title.strip():
                    cursor.callproc("create_faculty_title", (faculty_id, title.strip()))
                    # Consume result set
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
                
                # Check if relationship already exists
                cursor.execute(
                    "SELECT COUNT(*) as count FROM faculty_works_at_institution WHERE faculty_id = %s AND institution_id = %s",
                    (faculty_id, institution_id)
                )
                rel_exists = cursor.fetchone()["count"] > 0
                
                if not rel_exists:
                    # Create new relationship with current date as start_date
                    from datetime import date
                    cursor.callproc(
                        "create_faculty_works_at_institution",
                        (faculty_id, institution_id, date.today(), None)
                    )
                    # Consume result set
                    try:
                        stored_results = list(cursor.stored_results())
                        if stored_results:
                            stored_results[0].fetchall()
                    except:
                        pass
                # If relationship exists, it is not updated
        
        conn.commit()
        
        return {
            "faculty_id": faculty_id,
            "message": "Faculty member updated successfully"
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in update_faculty service: {error_trace}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()