from backend.app.db.procedures import sql_search_faculty
from backend.app.db.transaction_context import start_transaction
from backend.app.utils.search_filters import get_valid_search_filters

from flask import jsonify


def search_faculty_service(**filters: dict[str, str]):
    """
    Service layer for searching for faculty in the database based on search filters.

    This function accepts any number of keyword arguments (e.g., first_name="Alice", department="CS"), which are collected into a dictionary called `filters`.
    Only valid filters, determined by get_valid_search_filters(), will be passed to the database procedures.

    If a "query" parameter is provided, it will search across all fields (first_name, last_name, department, institution)
    and combine the results.

    Args:
        **filters: Arbitrary keyword arguments representing the filters to use for searching.
                   Can include a "query" parameter for general searching across all fields.

    Returns:
        tuple: A tuple containing (jsonify response, status_code).
    """
    try:
        with start_transaction() as transaction_context:
            # Handle generic "query" parameter by searching across all fields
            if "query" in filters and filters["query"]:
                query = filters["query"]
                # Search across all fields and combine unique results
                all_results = []
                seen_ids = set()

                # Try searching in each field
                for field in get_valid_search_filters():
                    # Create a filter dict with the query in the current field and None for others
                    field_filters = {key: None for key in get_valid_search_filters()}
                    field_filters[field] = query
                    results = sql_search_faculty(transaction_context, **field_filters)
                    for result in results:
                        faculty_id = result.get("faculty_id")
                        if faculty_id and faculty_id not in seen_ids:
                            seen_ids.add(faculty_id)
                            all_results.append(result)

                return jsonify(all_results), 200

            # Normal filtering with specific parameters
            valid_filters = {
                key: filters.get(key) for key in get_valid_search_filters()
            }
            results = sql_search_faculty(transaction_context, **valid_filters)
            return jsonify(results), 200
    except Exception as e:
        # Context manager already handled transaction cleanup
        # Convert exception to JSON error response for API layer
        error_message = str(e)
        return (
            jsonify({"error": f"Error searching for faculty: {error_message}"}),
            500,
        )
