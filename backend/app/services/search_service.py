from backend.app.db.procedures import sql_search
from backend.app.utils.search_filters import get_valid_search_filters


def search_faculty(**filters: dict[str, str]):
    """
    Service layer for searching for faculty in the database based on search filters.

    This function accepts any number of keyword arguments (e.g., first_name="Alice", department="CS"), which are collected into a dictionary called `filters`.
    Only valid filters, determined by get_valid_search_filters(), will be passed to the database procedures.

    Args:
        **filters: Arbitrary keyword arguments representing the filters to use for searching.

    Returns:
        list: A list of dictionaries, each containing the faculty information.
    """
    valid_filters = {key: filters.get(key) for key in get_valid_search_filters()}
    return sql_search(**valid_filters)
