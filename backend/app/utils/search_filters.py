# List of all valid filters that can be used for searching.
def get_valid_search_filters() -> list[str]:
    return ["first_name", "last_name", "department", "institution"]


# The order in which the filters should be passed to the procedure.
def get_expected_search_filter_order() -> list[str]:
    return ["first_name", "last_name", "department", "institution"]
