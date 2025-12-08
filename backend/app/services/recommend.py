"""
Author: Clayton Durepos
"""

"""
Recommendation service for faculty collaboration suggestions.
"""
from backend.app.db.procedures import (
    sql_generate_all_recommendations,
    sql_generate_recommendations_for_faculty,
    sql_read_recommendations_for_faculty,
)
from backend.app.db.transaction_context import start_transaction


def generate_recommendations() -> None:
    """
    Generate/refresh all faculty recommendations.
    
    Creates recommendations for all registered users based on:
    - Similar research interests (shared keywords)
    - Published in your research area
    - Holds a relevant grant
    - Same department
    - Shared grant funding
    - Works at the same institution
    
    This is typically run by a scheduled event every 12 hours,
    but can also be triggered manually.
    """
    try:
        with start_transaction() as transaction_context:
            sql_generate_all_recommendations(transaction_context)
    except Exception as e:
        raise Exception(f"Failed to generate recommendations: {str(e)}")


def generate_recommendations_for_user(faculty_id: str) -> None:
    """
    Generate recommendations for a single faculty member.
    
    Called immediately after signup to provide instant recommendations
    without waiting for the 12-hour event.
    
    Args:
        faculty_id: UUID of the faculty member to generate recommendations for.
    """
    try:
        with start_transaction() as transaction_context:
            sql_generate_recommendations_for_faculty(transaction_context, faculty_id)
    except Exception as e:
        # Log the error but don't fail signup if recommendations fail
        print(f"Warning: Failed to generate recommendations for {faculty_id}: {str(e)}")


def get_recommendations_for_faculty(faculty_id: str) -> list[dict]:
    """
    Get personalized recommendations for a specific faculty member.
    
    Args:
        faculty_id: UUID of the faculty member to get recommendations for.
    
    Returns:
        List of recommended faculty with:
        - faculty_id, first_name, last_name, biography
        - institution_name, department_name
        - match_score (0.0 to 1.0)
        - recommendation_type: ENUM value (e.g., 'shared_keyword')
        - recommendation_text: Human-readable text (e.g., "Similar research interests")
    """
    try:
        with start_transaction() as transaction_context:
            recommendations = sql_read_recommendations_for_faculty(
                transaction_context,
                faculty_id,
            )
            
            # Convert to list of dicts
            processed = []
            for rec in recommendations:
                # Convert to dict if needed
                if hasattr(rec, '_asdict'):
                    rec = rec._asdict()
                elif not isinstance(rec, dict):
                    rec = dict(rec)
                
                processed.append(rec)
            
            return processed
    except Exception as e:
        raise Exception(f"Failed to get recommendations: {str(e)}")
