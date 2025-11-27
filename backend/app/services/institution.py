"""
Institution service layer
Handles institution data from JSON file and database operations
"""

import json
import os
import uuid
from datetime import date
from backend.app.db.connection import get_connection


# Cache for institutions JSON data
_institutions_cache = None


def get_institutions_from_json():
    """
    Load institutions from the JSON file.
    Returns a list of institution dictionaries.
    """
    global _institutions_cache
    
    if _institutions_cache is not None:
        return _institutions_cache
    
    # Get the path to the JSON file
    # The data directory is at backend/data (sibling to app directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up from services -> app -> backend, then into data
    json_path = os.path.join(current_dir, '..', '..', 'data', 'institutions.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            _institutions_cache = json.load(f)
        return _institutions_cache
    except FileNotFoundError:
        print(f"Warning: institutions.json not found at {json_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing institutions.json: {e}")
        return []


def get_institution_id_by_name(institution_name: str, cursor=None):
    """
    Get or create an institution in the database.
    
    First checks if the institution exists in the DB by name.
    If not found, looks it up in the JSON file and creates it in the DB.
    
    Note: If a cursor is provided, the caller is responsible for committing
    the transaction. If no cursor is provided, this function will create its
    own connection and commit the transaction.
    
    Args:
        institution_name: Name of the institution
        cursor: Optional database cursor (if provided, won't close it or commit)
    
    Returns:
        str: institution_id (UUID) if found/created, None otherwise
    """
    if not institution_name or not institution_name.strip():
        return None
    
    institution_name = institution_name.strip()
    should_close_conn = cursor is None
    
    try:
        if cursor is None:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
        else:
            conn = None
        
        # First, check if institution exists in DB
        cursor.execute(
            "SELECT institution_id FROM institution WHERE name = %s",
            (institution_name,)
        )
        result = cursor.fetchone()
        
        if result:
            return result['institution_id']
        
        # Institution not in DB - look it up in JSON and create it
        institutions = get_institutions_from_json()
        institution_data = None
        
        for inst in institutions:
            if inst.get('name') == institution_name:
                institution_data = inst
                break
        
        if not institution_data:
            # Institution not found in JSON either
            print(f"Warning: Institution '{institution_name}' not found in institutions.json")
            return None
        
        # Create the institution in the database
        institution_id = str(uuid.uuid4())
        
        cursor.callproc(
            "create_institution",
            (
                institution_id,
                institution_data.get('name'),
                institution_data.get('street_addr'),
                institution_data.get('city'),
                institution_data.get('state'),
                institution_data.get('country', 'USA'),
                institution_data.get('zip'),
                institution_data.get('website_url'),
                institution_data.get('type'),
            )
        )
        # Consume any result set
        try:
            stored_results = list(cursor.stored_results())
            if stored_results:
                stored_results[0].fetchall()
        except:
            pass
        
        # Only commit if we created our own connection
        if conn:
            conn.commit()
        
        return institution_id
        
    except Exception as e:
        if conn:
            conn.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_institution_id_by_name: {error_trace}")
        raise e
    finally:
        if should_close_conn:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

