from collections import defaultdict

from backend.app.db.procedures import (
    sql_search_faculty,
    sql_search_faculty_by_keyword,
    sql_batch_get_faculty_keywords,
)
from backend.app.db.transaction_context import start_transaction
from backend.app.utils.search_filters import get_valid_search_filters


def search_faculty_service(result_limit: int = 50, conn=None, **filters: dict[str, str]):
    """
    Service layer for searching for faculty in the database based on search filters.

    This function accepts any number of keyword arguments (e.g., first_name="Alice", department="CS"), 
    which are collected into a dictionary called `filters`.
    Only valid filters, determined by get_valid_search_filters(), will be passed to the database procedures.

    If a "query" parameter is provided, it is treated as comma-separated search terms.
    Each term is searched across all fields (first_name, last_name, department, institution).
    Only faculty matching ALL terms (in any field) are returned (intersection logic).

    Args:
        result_limit: The maximum number of results to include in the response.
        conn: A debug/testing only parameter to pass in a connection to the database. Do not use in production.
        **filters: Arbitrary keyword arguments representing the filters to use for searching.
                   Can include a "query" parameter for general searching across all fields (comma-separated terms).
                   Can include a "keywords" parameter for searching by research keywords / phrases.

    Returns:
        tuple: A tuple containing (results, status_code) where results is a list or error dict.
    """
    try:
        with start_transaction(conn) as transaction_context:
            # Get keywords and ensure empty strings are treated as None
            keywords = filters.get("keywords", "").strip() or None

            # Case 1: Handle generic "query" parameter by searching across all fields
            # Query is comma-separated terms; faculty must match ALL terms (in any field) to be returned
            query = filters.get("query", "").strip()
            if query:
                # Parse query into individual search terms
                search_terms = [term.strip() for term in query.split(",") if term.strip()][:len(get_valid_search_filters())] # Crucial that this is sliced.
                
                if not search_terms:
                    return [], 200
                
                # For each term, search with that term in ALL filter fields
                # The SQL procedure uses OR, so it finds faculty matching the term in ANY field
                # We then intersect results across all terms
                result_sets = []
                for term in search_terms:
                    # Pass the same term as all 4 arguments
                    term_filters = {key: term for key in get_valid_search_filters()}
                    results = sql_search_faculty(transaction_context, **term_filters)
                    # Store as dict keyed by faculty_id for easy lookup
                    result_sets.append({r["faculty_id"]: r for r in results})
                
                # Find faculty_ids that appear in ALL result sets (intersection)
                if result_sets:
                    common_ids = set(result_sets[0].keys())
                    for result_dict in result_sets[1:]:
                        common_ids &= set(result_dict.keys())
                    
                    # Build final results from the first result set (preserves full record)
                    all_results = [result_sets[0][fid] for fid in common_ids]
                else:
                    all_results = []

                if keywords:
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
                results = sql_search_faculty(transaction_context, **valid_filters)
                if keywords:
                    results = rerank_by_keywords(results, keywords, transaction_context)
                return results[:result_limit], 200

            # Case 3: Search purely by keywords
            if keywords:
                # TODO: For any procedure that uses 'TEXT' type parameters, validate the input to ensure it is not too long.
                results = sql_search_faculty_by_keyword(
                    transaction_context, keywords, result_limit
                )
                return results[:result_limit], 200

            # Case 4: No filters or keywords provided
            return [], 200
    except Exception as e:
        # Context manager already handled transaction cleanup
        # Return error dict for route layer to handle
        # print(f"Error: {e}")
        error_message = str(e)
        return {"error": f"Error searching for faculty: {error_message}"}, 500


def rerank_by_keywords(results: list[dict], keywords: str, transaction_context):
    """
    Rerank the results by keywords.

    For each faculty, this function builds a set of all their keywords, then scores by how many of the
    search keywords match.
    """
    if not results:
        return results
    
    # Parse search keywords into a lowercase set
    search_keywords = set(k.strip().lower() for k in keywords.split(",") if k.strip())

    if not search_keywords:
        return results

    # Extract all faculty IDs from results
    faculty_ids = [r["faculty_id"] for r in results if r.get("faculty_id")]
    
    if not faculty_ids:
        return results

    # Single batch query to get all keywords for all faculty members
    all_keywords = sql_batch_get_faculty_keywords(transaction_context, faculty_ids)
    # Build a mapping: faculty_id -> set of keywords
    faculty_keyword_map = defaultdict(set)
    for row in all_keywords:
        faculty_id = row.get("faculty_id")
        keyword = row.get("keyword")
        if faculty_id and keyword:
            faculty_keyword_map[faculty_id].add(keyword)

    # Score each faculty by keyword overlap
    for result in results:
        faculty_keywords = faculty_keyword_map[result["faculty_id"]] # defaultdict returns empty set if key not found
        # Score is the number of matching keywords (set intersection)
        matching_keywords = search_keywords & faculty_keywords
        result["keyword_score"] = len(matching_keywords)

    # Sort by keyword_score descending, keeping original order for ties
    results.sort(key=lambda x: x.get("keyword_score", 0), reverse=True)

    return results
