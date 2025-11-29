from backend.app.db.transaction_context import TransactionContext

from datetime import datetime


def sql_search_faculty(
    transaction_context: TransactionContext, **filters: dict[str, str]
) -> list[dict]:
    """
    Search for faculty in the database based on search filters.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        filters (dict): A dictionary of filters to use for searching. Must contain all the keys
            in get_valid_search_filters(), which should be validated by the service layer.

    Returns:
        list[dict]: A list of dictionaries, each containing the faculty information.
    """
    cursor = transaction_context.cursor
    cursor.callproc("search_faculty", list(filters.values()))
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []


def sql_count_faculty_keyword_generations(
    transaction_context: TransactionContext,
    faculty_id: str,
    since_datetime: datetime,
) -> int:
    """
    Count the number of keyword generation requests for a faculty member since a given datetime.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): The UUID of the faculty member.
        since_datetime (datetime): The datetime since which to count the keyword generation requests.

    Returns:
        int: The number of keyword generation requests for the faculty member since the given datetime.
    """
    cursor = transaction_context.cursor

    result_args = cursor.callproc(
        "count_faculty_keyword_generations",
        (
            faculty_id,
            since_datetime,
            0,  # OUT p_generation_count (filled by procedure)
        ),
    )

    # Handle both dict and tuple/list return formats (mysql.connector behavior varies)
    if isinstance(result_args, dict):
        generation_count = result_args.get("count_faculty_keyword_generations_arg3", 0)
        return generation_count if generation_count is not None else 0
    elif isinstance(result_args, (tuple, list)) and len(result_args) >= 3:
        generation_count = result_args[2]
        return generation_count if generation_count is not None else 0
    else:
        return 0


def sql_create_faculty_generates_keyword(
    transaction_context: TransactionContext,
    generation_id: str,
    faculty_id: str,
    generated_at: datetime,
) -> list[dict]:
    """
    Create a new keyword generation record for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        generation_id (str): The UUID of the generation record.
        faculty_id (str): The UUID of the faculty member.
        generated_at (datetime): The datetime when the keyword generation request was made.

    Returns:
        list[dict]: A list of dictionaries, each containing the generation record information.
    """
    cursor = transaction_context.cursor
    cursor.callproc(
        "create_faculty_generates_keyword", [generation_id, faculty_id, generated_at]
    )
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []


# The following procedures starting with "sql_recommend_" increment the match scores between faculty members in the faculty_recommended_to_faculty table.
def sql_recommend_faculty_by_department():
    return []


def sql_recommend_faculty_by_grant_keyword():
    return []


def sql_recommend_faculty_by_grants():
    return []


def sql_recommend_faculty_by_institution():
    return []


def sql_recommend_faculty_by_publication_keyword():
    return []


def sql_recommend_faculty_by_shared_keyword():
    return []


def sql_get_recommendations(**filters: dict[str, str]):
    """
    Get recommendations for a user based on the faculty_recommended_to_faculty table.

    Args:
        filters (dict): A dictionary of filters to use for getting recommendations. Must contain all the keys
            in get_valid_recommend_filters(), which should be validated by the service layer.

    Returns:
        list: A list of dictionaries, each containing the recommended faculty information.
    """
    return []
