# Aidan - generated_keywords_service


from backend.app.services.faculty import get_faculty
from backend.models.qwen import generate_faculty_keywords_with_qwen
from backend.app.db.transaction_context import start_transaction
from backend.app.db.procedures import sql_create_faculty_generates_keyword
from backend.app.db.procedures import sql_count_faculty_keyword_generations

import uuid
from flask import jsonify
from datetime import datetime, timedelta

# House all rate limited services here.


def generate_keyword_service(faculty_id: str):
    """
    Generate keywords for a faculty member using their biography.

    Args:
        faculty_id (str): The UUID of the faculty member.

    Returns:
        tuple: A tuple containing the JSON response and the HTTP status code.

    Raises:
        ValueError: If the LLM fails to generate keywords.
    """
    REQUESTS_PER_HOUR = 3

    try:
        with start_transaction() as transaction_context:
            # Check rate limit (read-only operation)
            count_faculty_keyword_generations = sql_count_faculty_keyword_generations(
                transaction_context, faculty_id, datetime.now() - timedelta(hours=1)
            )
            if count_faculty_keyword_generations > REQUESTS_PER_HOUR:
                # Early return: no DB changes made, commit is harmless
                return (
                    jsonify(
                        {
                            "error": f"Rate limit exceeded. Maximum of {REQUESTS_PER_HOUR} requests per hour."
                        }
                    ),
                    429,
                )

            # Get faculty data (separate connection, not in transaction)
            faculty = get_faculty(faculty_id)
            biography = faculty["biography"]
            if not biography:
                # Early return: no DB changes made, commit is harmless
                return (
                    jsonify(
                        {"error": "User must have a biography to generate keywords."}
                    ),
                    400,
                )

            # Create generation record BEFORE LLM call
            # If LLM fails, exception will trigger automatic rollback
            generation_id = str(uuid.uuid4())
            sql_create_faculty_generates_keyword(
                transaction_context, generation_id, faculty_id, datetime.now()
            )

            # Call LLM - if this fails, exception triggers rollback via context manager
            # Alternatively, we could wrap this in a try/except and just return an error so the context manager doesn't rollback.
            # This might be preferred if we want to consider the rate limit even if the LLM fails.
            # NOTE: We do not unload the model here because we want to keep it loaded for the next request. If we have multiple 
            # workers, we should carefully consider the memory implications.
            keywords = generate_faculty_keywords_with_qwen(biography)
            if not keywords:
                # Raise exception to trigger rollback of generation record
                raise ValueError("No keywords generated from LLM")

            # Successfully generated keywords, context manager commits the generation record
            return jsonify({"keywords": keywords}), 200

    except Exception as e:
        # Context manager already handled rollback (if needed)
        # Convert exception to JSON error response for API layer
        error_message = str(e)
        return (
            jsonify({"error": f"Error generating keywords: {error_message}"}),
            500,
        )
