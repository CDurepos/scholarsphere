"""
Faculty service layer
Handles business logic for faculty member management
"""
import uuid
from datetime import date
from backend.app.db.transaction_context import start_transaction
from backend.app.db.procedures import (
    sql_create_faculty,
    sql_read_faculty,
    sql_update_faculty,
    sql_create_faculty_email,
    sql_read_faculty_email_by_faculty,
    sql_delete_faculty_email_by_faculty,
    sql_create_faculty_phone,
    sql_read_faculty_phone_by_faculty,
    sql_delete_faculty_phone_by_faculty,
    sql_create_faculty_department,
    sql_read_faculty_department_by_faculty,
    sql_delete_faculty_department_by_faculty,
    sql_create_faculty_title,
    sql_read_faculty_title_by_faculty,
    sql_delete_faculty_title_by_faculty,
    sql_read_faculty_works_at_institution_by_faculty,
    sql_read_institution,
    sql_create_faculty_works_at_institution,
    sql_check_faculty_works_at_institution_exists,
)
from backend.app.services.institution import get_institution_id_by_name


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
    try:
        with start_transaction() as transaction_context:
            # Generate UUID v4 for faculty_id in Python
            faculty_id = str(uuid.uuid4())
            
            # Convert empty strings to None for optional fields
            def empty_to_none(value):
                return None if (value is None or (isinstance(value, str) and value.strip() == "")) else value
            
            # Create faculty record
            sql_create_faculty(
                transaction_context,
                faculty_id,
                data.get("first_name"),
                empty_to_none(data.get("last_name")),
                empty_to_none(data.get("biography")),
                empty_to_none(data.get("orcid")),
                empty_to_none(data.get("google_scholar_url")),
                empty_to_none(data.get("research_gate_url")),
                None,  # scraped_from is always None for user signups
            )
            
            # Create emails
            emails = data.get("emails", []) or []
            for email in emails:
                if email and email.strip():
                    sql_create_faculty_email(transaction_context, faculty_id, email.strip())
            
            # Create phones
            phones = data.get("phones", []) or []
            for phone in phones:
                if phone and phone.strip():
                    sql_create_faculty_phone(transaction_context, faculty_id, phone.strip())
            
            # Create departments
            departments = data.get("departments", []) or []
            for dept in departments:
                if dept and dept.strip():
                    sql_create_faculty_department(transaction_context, faculty_id, dept.strip())
            
            # Create titles
            titles = data.get("titles", []) or []
            for title in titles:
                if title and title.strip():
                    sql_create_faculty_title(transaction_context, faculty_id, title.strip())
            
            # Handle institution relationship if institution_name is provided
            institution_name = data.get("institution_name")
            if institution_name and institution_name.strip():
                # Get or create institution in DB (will create from JSON if needed)
                # Pass the cursor from transaction context so it uses the same transaction
                institution_id = get_institution_id_by_name(institution_name.strip(), transaction_context.cursor)
                
                if institution_id:
                    # Create faculty-institution relationship with current date as start_date
                    sql_create_faculty_works_at_institution(
                        transaction_context,
                        faculty_id,
                        institution_id,
                        date.today(),
                        None
                    )
            
            # Transaction commits automatically on success
        
        return {
            "faculty_id": faculty_id,
            "message": "Faculty member created successfully"
        }
    except Exception as e:
        # Transaction already rolled back by context manager
        raise e


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
    try:
        with start_transaction() as transaction_context:
            # Get basic faculty info
            faculty_result = sql_read_faculty(transaction_context, faculty_id)
            if not faculty_result:
                raise Exception("Faculty not found")
            
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
            
            # Fetch institution (get the most recent/current one)
            institution_rel_rows = sql_read_faculty_works_at_institution_by_faculty(
                transaction_context,
                faculty_id,
                None
            )
            institution_name = None
            if institution_rel_rows:
                # Get the most recent institution (first row due to ORDER BY start_date DESC)
                most_recent_institution_id = institution_rel_rows[0].get('institution_id')
                if most_recent_institution_id:
                    # Get the institution name
                    institution = sql_read_institution(transaction_context, most_recent_institution_id)
                    if institution:
                        institution_name = institution.get('name')
            
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
    try:
        with start_transaction() as transaction_context:
            # Convert empty strings to None for optional fields
            def empty_to_none(value):
                return None if (value is None or (isinstance(value, str) and value.strip() == "")) else value
            
            # Update basic faculty fields
            sql_update_faculty(
                transaction_context,
                faculty_id,
                empty_to_none(data.get("first_name")),
                empty_to_none(data.get("last_name")),
                empty_to_none(data.get("biography")),
                empty_to_none(data.get("orcid")),
                empty_to_none(data.get("google_scholar_url")),
                empty_to_none(data.get("research_gate_url")),
                None,  # scraped_from - don't update this via API
            )
            
            # Handle emails: replace all existing emails
            if "emails" in data:
                # Delete all existing emails for this faculty member
                sql_delete_faculty_email_by_faculty(transaction_context, faculty_id)
                # Create new emails
                emails = data.get("emails", []) or []
                for email in emails:
                    if email and email.strip():
                        sql_create_faculty_email(transaction_context, faculty_id, email.strip())
            
            # Handle phones: replace all existing phones
            if "phones" in data:
                # Delete all existing phones for this faculty member
                sql_delete_faculty_phone_by_faculty(transaction_context, faculty_id)
                # Create new phones
                phones = data.get("phones", []) or []
                for phone in phones:
                    if phone and phone.strip():
                        sql_create_faculty_phone(transaction_context, faculty_id, phone.strip())
            
            # Handle departments: replace all existing departments
            if "departments" in data:
                # Delete all existing departments for this faculty member
                sql_delete_faculty_department_by_faculty(transaction_context, faculty_id)
                # Create new departments
                departments = data.get("departments", []) or []
                for dept in departments:
                    if dept and dept.strip():
                        sql_create_faculty_department(transaction_context, faculty_id, dept.strip())
            
            # Handle titles: replace all existing titles
            if "titles" in data:
                # Delete all existing titles for this faculty member
                sql_delete_faculty_title_by_faculty(transaction_context, faculty_id)
                # Create new titles
                titles = data.get("titles", []) or []
                for title in titles:
                    if title and title.strip():
                        sql_create_faculty_title(transaction_context, faculty_id, title.strip())
            
            # Handle institution relationship if institution_name is provided
            institution_name = data.get("institution_name")
            if institution_name and institution_name.strip():
                # Get or create institution in DB (will create from JSON if needed)
                # Pass the cursor from transaction context so it uses the same transaction
                institution_id = get_institution_id_by_name(institution_name.strip(), transaction_context.cursor)
                
                if institution_id:
                    # Check if relationship already exists
                    rel_exists = sql_check_faculty_works_at_institution_exists(
                        transaction_context,
                        faculty_id,
                        institution_id
                    )
                    
                    if not rel_exists:
                        # Create new relationship with current date as start_date
                        sql_create_faculty_works_at_institution(
                            transaction_context,
                            faculty_id,
                            institution_id,
                            date.today(),
                            None
                        )
                    # If relationship exists, it is not updated
            
            # Transaction commits automatically on success
        
        return {
            "faculty_id": faculty_id,
            "message": "Faculty member updated successfully"
        }
    except Exception as e:
        # Transaction already rolled back by context manager
        raise e
