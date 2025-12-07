from backend.app.db.procedures import (
    sql_search_faculty,
    sql_search_faculty_by_keyword,
    sql_read_faculty_researches_keyword_by_faculty,
    sql_read_publication_authored_by_faculty_by_faculty,
    sql_read_publication_explores_keyword_by_publication,
)
from backend.app.db.transaction_context import start_transaction
from backend.app.utils.search_filters import get_valid_search_filters


def search_faculty_service(result_limit: int = 50, conn=None, **filters: dict[str, str]):
    """
    Service layer for searching for faculty in the database based on search filters.

    This function accepts any number of keyword arguments (e.g., first_name="Alice", department="CS"), which are collected into a dictionary called `filters`.
    Only valid filters, determined by get_valid_search_filters(), will be passed to the database procedures.

    If a "query" parameter is provided, it will search across all fields (first_name, last_name, department, institution)
    and combine the results.

    Args:
        result_limit: The maximum number of results to include in the response.
        conn: A debug/testing only parameter to pass in a connection to the database. Do not use in production.
        **filters: Arbitrary keyword arguments representing the filters to use for searching.
                   Can include a "query" parameter for general searching across all fields.
                   Can include a "keywords" parameter for searching by keywords / phrases.

    Returns:
        tuple: A tuple containing (results, status_code) where results is a list or error dict.
    """
    try:
        with start_transaction(conn) as transaction_context:
            # Get keywords and ensure empty strings are treated as None
            keywords = filters.get("keywords", "").strip() or None

            # Case 1: Handle generic "query" parameter by searching across all fields
            query = filters.get("query", "").strip()
            if query:
                print("Case 1")
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

                if keywords:
                    #TODO: Just reranking by keywords might not make a lot of sense from a user perspective. Especially if no faculty have the keywords.
                    all_results = rerank_by_keywords(
                        all_results, keywords, transaction_context
                    )
                return all_results[:result_limit], 200

            # Case 2: Normal filtering with specific parameters.
            valid_filters = {
                key: (
                    filters.get(key, "").strip()
                    if filters.get(key, "").strip() != ""
                    else None
                )
                for key in get_valid_search_filters()
            }
            if any(valid_filters.values()):
                print("Case 2")
                results = sql_search_faculty(transaction_context, **valid_filters)
                if keywords:
                    results = rerank_by_keywords(results, keywords, transaction_context)
                return results[:result_limit], 200

            # Case 3: Search purely by keywords
            if keywords:
                print("Case 3")
                # TODO: For any procedure that uses 'TEXT' type parameters, validate the input to ensure it is not too long.
                results = sql_search_faculty_by_keyword(
                    transaction_context, keywords, result_limit
                )
                return results[:result_limit], 200

            # Case 4: No filters or keywords provided
            print("Case 4")
            return [], 200
    except Exception as e:
        # Context manager already handled transaction cleanup
        # Return error dict for route layer to handle
        print(f"Error: {e}")
        error_message = str(e)
        return {"error": f"Error searching for faculty: {error_message}"}, 500


def rerank_by_keywords(results: list[dict], keywords: str, transaction_context):
    """
    Rerank the results by keywords.

    For each faculty, builds a set of all their keywords (from their research keywords
    and from keywords explored in their publications), then scores by how many of the
    search keywords match.
    """
    # Parse search keywords into a lowercase set
    search_keywords = set(k.strip().lower() for k in keywords.split(",") if k.strip())

    if not search_keywords:
        return results

    for result in results:
        faculty_keywords = gather_keywords(result["faculty_id"], transaction_context)
        # Score is the number of matching keywords (set intersection)
        matching_keywords = search_keywords & faculty_keywords
        result["keyword_score"] = len(matching_keywords)

    # Sort by keyword_score descending, keeping original order for ties
    results.sort(key=lambda x: x.get("keyword_score", 0), reverse=True)

    return results


def gather_keywords(faculty_id: str, transaction_context) -> set[str]:
    """
    Gather the keywords for a faculty member.
    """
    faculty_keywords = set()
    # Get keywords from faculty's direct research keywords
    research_keywords = sql_read_faculty_researches_keyword_by_faculty(
        transaction_context, faculty_id
    )
    for kw in research_keywords:
        if kw.get("name"):
            faculty_keywords.add(kw["name"].lower())

    # Get keywords from faculty's publications
    publications = sql_read_publication_authored_by_faculty_by_faculty(
        transaction_context, faculty_id
    )
    for publication in publications:
        pub_keywords = sql_read_publication_explores_keyword_by_publication(
            transaction_context, publication["publication_id"]
        )
        for kw in pub_keywords:
            if kw.get("name"):
                faculty_keywords.add(kw["name"].lower())

    return faculty_keywords
