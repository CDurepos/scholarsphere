from backend.app.db.connection import get_connection


def sql_search(**filters: dict[str, str]):
    """
    Search for faculty in the database based on search filters.

    Args:
        filters (dict): A dictionary of filters to use for searching. Must contain all the keys
            in get_valid_search_filters(), which should be validated by the service layer.

    Returns:
        list: A list of dictionaries, each containing the faculty information.
    """
    # TODO: Shouldn't get a connection for each call to the procedure. Use connection pooling.
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc("search_faculty", list(filters.values()))
    result = cursor.stored_results().pop().fetchall()
    cursor.close()
    conn.close()
    return result


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
    # TODO: Shouldn't get a connection for each call to the procedure. Use connection pooling.
    # conn = get_connection()
    # cursor = conn.cursor(dictionary=True)
    # cursor.callproc("TODO: create 'read_recommendations' procedure and call it here", list(filters.values()))
    # result = cursor.stored_results().pop().fetchall()
    # cursor.close()
    # conn.close()
    # return result
    return []
