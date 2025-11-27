from backend.app.utils.recommend_filters import get_valid_recommend_filters
from backend.app.db.procedures import (
    sql_recommend_faculty_by_department,
    sql_recommend_faculty_by_grant_keyword,
    sql_recommend_faculty_by_grants,
    sql_recommend_faculty_by_institution,
    sql_recommend_faculty_by_publication_keyword,
    sql_recommend_faculty_by_shared_keyword,
    sql_get_recommendations,
)


def recommend_faculty(**filters: dict[str, str]):
    """
    Service layer for recommending faculty for a user.

    This function accepts any number of keyword arguments (e.g., user_id=123), which are collected into a dictionary called `filters`.
    Only valid filters, determined by get_valid_recommend_filters(), will be passed to the database procedures.

    Args:
        **filters: Arbitrary keyword arguments representing the filters to use for recommending collaborators.

    Returns:
        list: A list of dictionaries, each containing the recommended faculty information.
    """
    # Call all the recommend procedures to increment the match scores between faculty members in the faculty_recommended_to_faculty table.
    sql_recommend_faculty_by_department()
    sql_recommend_faculty_by_grant_keyword()
    sql_recommend_faculty_by_grants()
    sql_recommend_faculty_by_institution()
    sql_recommend_faculty_by_publication_keyword()
    sql_recommend_faculty_by_shared_keyword()
    valid_filters = {key: filters.get(key) for key in get_valid_recommend_filters()}
    return sql_get_recommendations(**valid_filters)
