"""
Authentication service layer
Handles business logic for user authentication and credential management
"""
from backend.app.db.transaction_context import start_transaction
from backend.app.db.procedures import (
    sql_register_credentials,
    sql_validate_login,
    sql_check_username_exists,
    sql_check_credentials_exist,
    sql_read_faculty,
    sql_read_faculty_email_by_faculty,
    sql_read_faculty_phone_by_faculty,
    sql_read_faculty_department_by_faculty,
    sql_read_faculty_title_by_faculty,
)


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
    try:
        with start_transaction() as transaction_context:
            sql_register_credentials(
                transaction_context,
                data.get("faculty_id"),
                data.get("username"),
                data.get("password"),
            )
            # Transaction commits automatically on success
        
        return {
            "message": "Credentials registered successfully"
        }
    except Exception as e:
        # Transaction already rolled back by context manager
        raise e


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
    try:
        with start_transaction() as transaction_context:
            # Validate login credentials
            faculty_id, status_code = sql_validate_login(
                transaction_context,
                data.get("username"),
                data.get("password"),
            )
            
            # Check status code
            if status_code == 0:
                # Login successful - fetch complete faculty data
                faculty_result = sql_read_faculty(transaction_context, faculty_id)
                if not faculty_result:
                    raise Exception("Faculty data not found after successful login")
                
                # Fetch emails
                email_rows = sql_read_faculty_email_by_faculty(transaction_context, faculty_id)
                emails = [row.get('email') for row in email_rows if row.get('email')]
                
                # Fetch phones
                phone_rows = sql_read_faculty_phone_by_faculty(transaction_context, faculty_id)
                phones = [row.get('phone_num') for row in phone_rows if row.get('phone_num')]
                
                # Fetch departments
                dept_rows = sql_read_faculty_department_by_faculty(transaction_context, faculty_id)
                departments = [row.get('department_name') for row in dept_rows if row.get('department_name')]
                
                # Fetch titles
                title_rows = sql_read_faculty_title_by_faculty(transaction_context, faculty_id)
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


def check_username_available(username: str):
    """
    Check if a username is available (not already taken).
    
    Args:
        username: Username to check
    
    Returns:
        dict: Contains "available" (bool) and "username" (str)
    """
    try:
        with start_transaction() as transaction_context:
            exists = sql_check_username_exists(transaction_context, username)
            return {
                "username": username,
                "available": not exists
            }
    except Exception as e:
        # On error, assume username is not available to be safe
        return {
            "username": username,
            "available": False
        }


def check_credentials_exist(faculty_id: str):
    """
    Check if credentials already exist for a faculty_id.
    
    Args:
        faculty_id: UUID of the faculty member to check
    
    Returns:
        dict: Contains "has_credentials" (bool) and "faculty_id" (str)
    """
    try:
        with start_transaction() as transaction_context:
            exists = sql_check_credentials_exist(transaction_context, faculty_id)
            return {
                "faculty_id": faculty_id,
                "has_credentials": exists
            }
    except Exception as e:
        # On error, assume credentials exist to be safe
        return {
            "faculty_id": faculty_id,
            "has_credentials": True
        }
