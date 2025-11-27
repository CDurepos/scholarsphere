from backend.app.db.connection import get_connection


def register_credentials(data: dict):
    """
    Service layer for registering credentials for a faculty member.
    
    Creates a credentials record with hashed password. The password hashing
    is handled by the database procedure using SHA-256.
    
    Args:
        data: Dictionary containing:
            - faculty_id (required): UUID of the faculty member
            - username (required): Username (must be unique)
            - password (required): Plain text password (will be hashed by procedure)
    
    Returns:
        dict: Contains success message
    
    Raises:
        Exception: If username already exists, credentials already exist for faculty,
                  or faculty_id doesn't exist
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Call the register_credentials stored procedure
        # The procedure handles password hashing internally
        cursor.callproc(
            "register_credentials",
            (
                data.get("faculty_id"),
                data.get("username"),
                data.get("password"),
            ),
        )
        
        # register_credentials doesn't return a result set, but consume anyways to clear cursor
        try:
            stored_results = list(cursor.stored_results())
            if stored_results:
                stored_results[0].fetchall()
        except:
            pass
        
        conn.commit()
        
        return {
            "message": "Credentials registered successfully"
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in register_credentials service: {error_trace}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def validate_login(data: dict):
    """
    Service layer for validating user login credentials.
    
    Validates username and password using the validate_login stored procedure.
    If successful, returns faculty_id and fetches faculty data.
    
    Args:
        data: Dictionary containing:
            - username (required): Username to authenticate
            - password (required): Plain text password
    
    Returns:
        dict: Contains faculty_id and faculty data if successful
    
    Raises:
        Exception: If username or password is invalid
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        username = data.get("username")
        password = data.get("password")
        
        # Call validate_login procedure with OUT parameters
        result_args = cursor.callproc(
            "validate_login",
            (
                username,
                password,
                '',  # OUT p_faculty_id (placeholder - will be filled by procedure)
                0,   # OUT p_status_code (placeholder - will be filled by procedure)
            ),
        )
        
        # Consume any result sets first (procedure doesn't return result sets, but be safe)
        try:
            stored_results = list(cursor.stored_results())
            for result in stored_results:
                result.fetchall()
        except:
            pass
        
        # When using dictionary=True cursor, callproc returns a dict with keys like 'procedure_name_argN'
        # For validate_login: arg1=username, arg2=password, arg3=faculty_id (OUT), arg4=status_code (OUT)
        if isinstance(result_args, dict):
            faculty_id = result_args.get('validate_login_arg3') or None
            status_code = result_args.get('validate_login_arg4')
            if status_code is None:
                status_code = -1
        elif isinstance(result_args, (tuple, list)) and len(result_args) >= 4:
            # Fallback for tuple/list return (if dictionary=False)
            faculty_id = result_args[2] if result_args[2] else None
            status_code = result_args[3] if result_args[3] is not None else -1
        else:
            faculty_id = None
            status_code = -1
        
        # Check status code
        if status_code == 0:
            # Login successful - fetch complete faculty data
            # Get basic faculty info
            cursor.callproc("read_faculty", (faculty_id,))
            stored_results = list(cursor.stored_results())
            if not stored_results:
                raise Exception("Failed to retrieve faculty data")
            
            faculty_result = stored_results[0].fetchone()
            if not faculty_result:
                raise Exception("Faculty data not found after successful login")
            
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
            
            # Combine all faculty data
            complete_faculty = {
                **faculty_result,
                "emails": emails,
                "phones": phones,
                "departments": departments,
                "titles": titles,
            }
            
            return {
                "faculty_id": faculty_id,
                "faculty": complete_faculty
            }
        elif status_code == 1:
            raise Exception("Invalid password")
        elif status_code == 2:
            raise Exception("Username not found")
        else:
            raise Exception("Login failed")
        
    except Exception as e:
        # Re-raise with original message
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def check_username_available(username: str):
    """
    Check if a username is available (not already taken).
    
    Args:
        username: Username to check
    
    Returns:
        dict: Contains "available" (bool) and "username" (str)
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if username exists
        cursor.execute(
            "SELECT username FROM credentials WHERE username = %s",
            (username,)
        )
        result = cursor.fetchone()
        
        return {
            "username": username,
            "available": result is None
        }
        
    except Exception as e:
        # On error, assume username is not available to be safe
        return {
            "username": username,
            "available": False
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
