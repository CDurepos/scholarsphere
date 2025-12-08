from backend.app.db.transaction_context import TransactionContext

from datetime import datetime, date

#TODO: Do not use a single file for all procedures. Split into multiple files.

# ============================================================================
# SEARCH DB LAYER FUNCTIONS
# ============================================================================
def sql_search_faculty(
    transaction_context: TransactionContext,
    **filters: dict[str, str],
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
    cursor.callproc("search_faculty", tuple(filters.values()))
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []


def sql_search_existing_faculty(
    transaction_context: TransactionContext,
    first_name: str = None,
    last_name: str = None,
    institution: str = None,
) -> list[dict]:
    """
    Search for existing faculty members during signup lookup.
    
    This procedure is specifically designed for the signup flow to find existing
    faculty records. It uses AND logic - all provided parameters must match.
    
    Args:
        transaction_context: Database transaction context.
        first_name: Optional first name to search for (partial match).
        last_name: Optional last name to search for (partial match).
        institution: Optional institution name to search for (partial match).
    
    Returns:
        list[dict]: A list of dictionaries containing faculty information.
    """
    cursor = transaction_context.cursor
    # Pass parameters in order: first_name, last_name, institution
    params = (first_name, last_name, institution)
    cursor.callproc("search_existing_faculty", params)
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []


# ============================================================================
# SEARCH BY KEYWORD DB LAYER FUNCTIONS
# ============================================================================
def sql_search_faculty_by_keyword(
    transaction_context: TransactionContext,
    keywords: str,
) -> list[dict]:
    """
    Search for faculty in the database based on keywords.
    
    Args:
        transaction_context: Database transaction context.
        keywords: Comma-separated string of keywords to search for.
    
    Returns:
        list[dict]: List of faculty records with keyword_overlap score.
    """
    cursor = transaction_context.cursor
    cursor.callproc("search_faculty_by_keyword", (keywords,))
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []


def sql_batch_get_faculty_keywords(
    transaction_context: TransactionContext,
    faculty_ids: list[str],
) -> list[dict]:
    """
    Retrieve all keywords for a batch of faculty members in a single query.
    
    Keywords are combined from two sources:
    1. Direct research keywords (faculty_researches_keyword)
    2. Publication keywords (via publication_authored_by_faculty and 
      publication_explores_keyword)
    
    Args:
        transaction_context: Database transaction context.
        faculty_ids: List of faculty UUIDs to fetch keywords for.
    
    Returns:
        list[dict]: List of dicts with 'faculty_id' and 'keyword' keys.
    """
    if not faculty_ids:
        return []
    
    # Convert list to comma-separated string for the stored procedure
    faculty_ids_str = ",".join(faculty_ids)
    
    cursor = transaction_context.cursor
    cursor.callproc("batch_get_faculty_keywords", (faculty_ids_str,))
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []


def sql_read_publication_authored_by_faculty_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> list[dict]:
    """
    Read the publications that a faculty member has authored.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_publication_authored_by_faculty_by_faculty", (faculty_id,))
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []

def sql_read_faculty_researches_keyword_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> list[dict]:
    """
    Read the keywords that a faculty member researches.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_faculty_researches_keyword_by_faculty", (faculty_id,))
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []


def sql_search_keywords(
    transaction_context: TransactionContext,
    search_term: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search keywords by prefix for autocomplete.
    
    Args:
        transaction_context: Database transaction context.
        search_term: Search prefix string.
        limit: Maximum number of results (default 10).
    
    Returns:
        list[dict]: List of keyword records with 'name' field.
    """
    cursor = transaction_context.cursor
    cursor.callproc("search_keywords", (search_term, limit))
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []


def sql_add_keyword_for_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
    keyword_name: str,
) -> None:
    """
    Add a keyword for a faculty member (creates keyword if needed).
    
    Args:
        transaction_context: Database transaction context.
        faculty_id: UUID of the faculty member.
        keyword_name: Keyword name to add.
    
    Returns:
        None
    """
    cursor = transaction_context.cursor
    cursor.callproc("add_keyword_for_faculty", (faculty_id, keyword_name))
    # Consume result set
    try:
        stored_results = list(cursor.stored_results())
        for result in stored_results:
            result.fetchall()
    except:
        pass


def sql_delete_faculty_researches_keyword(
    transaction_context: TransactionContext,
    faculty_id: str,
    keyword_name: str,
) -> None:
    """
    Remove a keyword from a faculty member's research interests.
    
    Args:
        transaction_context: Database transaction context.
        faculty_id: UUID of the faculty member.
        keyword_name: Keyword name to remove.
    
    Returns:
        None
    """
    cursor = transaction_context.cursor
    cursor.callproc("delete_faculty_researches_keyword", (faculty_id, keyword_name))
    # Consume result set
    try:
        stored_results = list(cursor.stored_results())
        for result in stored_results:
            result.fetchall()
    except:
        pass


def sql_delete_all_faculty_keywords(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> None:
    """
    Delete all keywords for a faculty member.
    
    Args:
        transaction_context: Database transaction context.
        faculty_id: UUID of the faculty member.
    
    Returns:
        None
    """
    cursor = transaction_context.cursor
    cursor.execute(
        "DELETE FROM faculty_researches_keyword WHERE faculty_id = %s",
        (faculty_id,)
    )

def sql_read_publication_explores_keyword_by_publication(
    transaction_context: TransactionContext,
    publication_id: str,
) -> list[dict]:
    """
    Read the keywords that a publication explores.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_publication_explores_keyword_by_publication", (publication_id,))
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0] if results else []


# ============================================================================
# GENERATE KEYWORD DB LAYER FUNCTIONS
# ============================================================================
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
    Create a new keyword generation record for a faculty member. This is used to enforce rate limiting on LLM usage.

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


# ============================================================================
# RECOMMENDATION DB LAYER FUNCTIONS
# ============================================================================

def sql_generate_all_recommendations(
    transaction_context: TransactionContext,
) -> None:
    """
    Generate all faculty recommendations for registered users.
    
    Calls individual recommendation procedures in priority order (low to high)
    so higher-priority matches overwrite lower-priority ones.
    
    Recommendation Types (ENUM values, priority order):
    ===================================================
    0.10 - shared_institution      : Both at the same institution
    0.20 - shared_department       : Both in the same department
    0.30 - shared_grant            : Both have the same grant
    0.33 - publication_to_grant    : A published on X, B has grant for X
    0.34 - grant_to_publication    : A has grant for X, B published on X
    0.41 - grant_to_keyword        : A has grant for X, B researches X
    0.42 - keyword_to_grant        : A researches X, B has grant for X
    0.43 - publication_to_keyword  : A published on X, B researches X
    0.44 - keyword_to_publication  : A researches X, B published on X
    0.50 - shared_keyword          : Both research the same keyword
    
    Args:
        transaction_context (TransactionContext): A transaction context object.
    
    Returns:
        None: Recommendations are stored in faculty_recommended_to_faculty table.
    """
    cursor = transaction_context.cursor
    cursor.callproc("generate_all_recommendations")
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        for result in stored_results:
            result.fetchall()
    except:
        pass


def sql_generate_recommendations_for_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> None:
    """
    Generate recommendations for a single faculty member.
    
    Called immediately after signup to provide instant recommendations
    without waiting for the 12-hour event.
    
    Args:
        transaction_context (TransactionContext): A transaction context object.
        faculty_id (str): UUID of the faculty member to generate recommendations for.
    
    Returns:
        None: Recommendations are stored in faculty_recommended_to_faculty table.
    """
    cursor = transaction_context.cursor
    cursor.callproc("generate_recommendations_for_faculty", (faculty_id,))
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        for result in stored_results:
            result.fetchall()
    except:
        pass


def sql_read_recommendations_for_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> list[dict]:
    """
    Get personalized recommendations for a specific faculty member.
    
    Args:
        transaction_context (TransactionContext): A transaction context object.
        faculty_id (str): UUID of the faculty member to get recommendations for.
    
    Returns:
        list[dict]: List of recommended faculty with match details.
            Each dict contains:
            - faculty_id: UUID of recommended faculty
            - first_name, last_name, biography: Faculty info
            - institution_name: Primary institution
            - department_name: Primary department
            - match_score: Score for ranking (0.0 to 1.0)
            - recommendation_type: ENUM value (e.g., 'shared_keyword')
            - recommendation_text: Human-readable text (e.g., "Similar research interests")
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_recommendations_for_faculty", (faculty_id,))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchall()
    return []


# ============================================================================
# AUTH DB LAYER FUNCTIONS
# ============================================================================

def sql_register_credentials(
    transaction_context: TransactionContext,
    faculty_id: str,
    username: str,
    password: str,
) -> None:
    """
    Register credentials for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        username (str): Username (must be unique).
        password (str): Plain text password (will be hashed by procedure).

    Returns:
        None: No result set. Use read procedures to verify the insert.
    """
    cursor = transaction_context.cursor
    cursor.callproc("register_credentials", (faculty_id, username, password))
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


def sql_validate_login(
    transaction_context: TransactionContext,
    username: str,
    password: str,
) -> tuple[str | None, int]:
    """
    Validate user login credentials.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        username (str): Username to authenticate.
        password (str): Plain text password.

    Returns:
        tuple: (faculty_id, status_code)
            - faculty_id: UUID of the faculty member if successful, None otherwise
            - status_code: 0 = success, 1 = invalid password, 2 = username not found
    """
    cursor = transaction_context.cursor
    result_args = cursor.callproc(
        "validate_login",
        (
            username,
            password,
            '',  # OUT p_faculty_id (filled by procedure)
            0,   # OUT p_status_code (filled by procedure)
        ),
    )
    
    # Consume any result sets first
    try:
        stored_results = list(cursor.stored_results())
        for result in stored_results:
            result.fetchall()
    except:
        pass
    
    # Handle both dict and tuple/list return formats
    if isinstance(result_args, dict):
        faculty_id = result_args.get('validate_login_arg3') or None
        status_code = result_args.get('validate_login_arg4')
        if status_code is None:
            status_code = -1
    elif isinstance(result_args, (tuple, list)) and len(result_args) >= 4:
        faculty_id = result_args[2] if result_args[2] else None
        status_code = result_args[3] if result_args[3] is not None else -1
    else:
        faculty_id = None
        status_code = -1
    
    return faculty_id, status_code


def sql_check_username_exists(
    transaction_context: TransactionContext,
    username: str,
) -> bool:
    """
    Check if a username exists in the database.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        username (str): Username to check.

    Returns:
        bool: True if username exists, False otherwise.
    """
    cursor = transaction_context.cursor
    cursor.execute(
        "SELECT username FROM credentials WHERE username = %s",
        (username,)
    )
    result = cursor.fetchone()
    return result is not None


def sql_check_credentials_exist(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> bool:
    """
    Check if credentials exist for a faculty_id.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member to check.

    Returns:
        bool: True if credentials exist, False otherwise.
    """
    cursor = transaction_context.cursor
    cursor.execute(
        "SELECT faculty_id FROM credentials WHERE faculty_id = %s",
        (faculty_id,)
    )
    result = cursor.fetchone()
    return result is not None


# ============================================================================
# FACULTY DB LAYER FUNCTIONS
# ============================================================================

def sql_create_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
    first_name: str,
    last_name: str | None,
    biography: str | None,
    orcid: str | None,
    google_scholar_url: str | None,
    research_gate_url: str | None,
    scraped_from: str | None,
) -> None:
    """
    Create a new faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        first_name (str): First name (required).
        last_name (str | None): Last name (optional).
        biography (str | None): Biography (optional).
        orcid (str | None): ORCID identifier (optional).
        google_scholar_url (str | None): Google Scholar URL (optional).
        research_gate_url (str | None): ResearchGate URL (optional).
        scraped_from (str | None): Source of scraped data (optional).

    Returns:
        None: No result set. Use read procedures to verify the insert.
    """
    cursor = transaction_context.cursor
    cursor.callproc(
        "create_faculty",
        (
            faculty_id,
            first_name,
            last_name,
            biography,
            orcid,
            google_scholar_url,
            research_gate_url,
            scraped_from,
        ),
    )
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


def sql_read_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> dict | None:
    """
    Read a faculty member by faculty_id.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        dict | None: Faculty record if found, None otherwise.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_faculty", (faculty_id,))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchone()
    return None


def sql_update_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
    first_name: str | None,
    last_name: str | None,
    biography: str | None,
    orcid: str | None,
    google_scholar_url: str | None,
    research_gate_url: str | None,
    scraped_from: str | None,
) -> None:
    """
    Update a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        first_name (str | None): First name (optional).
        last_name (str | None): Last name (optional).
        biography (str | None): Biography (optional).
        orcid (str | None): ORCID identifier (optional).
        google_scholar_url (str | None): Google Scholar URL (optional).
        research_gate_url (str | None): ResearchGate URL (optional).
        scraped_from (str | None): Source of scraped data (optional).

    Returns:
        None: No result set. Use read procedures to verify the update.
    """
    cursor = transaction_context.cursor
    cursor.callproc(
        "update_faculty",
        (
            faculty_id,
            first_name,
            last_name,
            biography,
            orcid,
            google_scholar_url,
            research_gate_url,
            scraped_from,
        ),
    )
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


def sql_create_faculty_email(
    transaction_context: TransactionContext,
    faculty_id: str,
    email: str,
) -> None:
    """
    Create a faculty email record.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        email (str): Email address.

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.callproc("create_faculty_email", (faculty_id, email))
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


def sql_read_faculty_email_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> list[dict]:
    """
    Read all email records for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        list[dict]: List of email records.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_faculty_email_by_faculty", (faculty_id,))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchall()
    return []


def sql_delete_faculty_email_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> None:
    """
    Delete all email records for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.execute(
        "DELETE FROM faculty_email WHERE faculty_id = %s",
        (faculty_id,)
    )


def sql_create_faculty_phone(
    transaction_context: TransactionContext,
    faculty_id: str,
    phone_num: str,
) -> None:
    """
    Create a faculty phone record.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        phone_num (str): Phone number.

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.callproc("create_faculty_phone", (faculty_id, phone_num))
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


def sql_read_faculty_phone_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> list[dict]:
    """
    Read all phone records for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        list[dict]: List of phone records.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_faculty_phone_by_faculty", (faculty_id,))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchall()
    return []


def sql_delete_faculty_phone_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> None:
    """
    Delete all phone records for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.execute(
        "DELETE FROM faculty_phone WHERE faculty_id = %s",
        (faculty_id,)
    )


def sql_create_faculty_department(
    transaction_context: TransactionContext,
    faculty_id: str,
    department_name: str,
) -> None:
    """
    Create a faculty department record.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        department_name (str): Department name.

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.callproc("create_faculty_department", (faculty_id, department_name))
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


def sql_read_faculty_department_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> list[dict]:
    """
    Read all department records for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        list[dict]: List of department records.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_faculty_department_by_faculty", (faculty_id,))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchall()
    return []


def sql_delete_faculty_department_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> None:
    """
    Delete all department records for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.execute(
        "DELETE FROM faculty_department WHERE faculty_id = %s",
        (faculty_id,)
    )


def sql_create_faculty_title(
    transaction_context: TransactionContext,
    faculty_id: str,
    title: str,
) -> None:
    """
    Create a faculty title record.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        title (str): Title.

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.callproc("create_faculty_title", (faculty_id, title))
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


def sql_read_faculty_title_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> list[dict]:
    """
    Read all title records for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        list[dict]: List of title records.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_faculty_title_by_faculty", (faculty_id,))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchall()
    return []


def sql_delete_faculty_title_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> None:
    """
    Delete all title records for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.execute(
        "DELETE FROM faculty_title WHERE faculty_id = %s",
        (faculty_id,)
    )


def sql_read_faculty_works_at_institution_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
    institution_id: str | None,
) -> list[dict]:
    """
    Read faculty-institution relationships for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        institution_id (str | None): Optional institution ID to filter by.

    Returns:
        list[dict]: List of relationship records.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_faculty_works_at_institution_by_faculty", (faculty_id, institution_id))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchall()
    return []


def sql_read_institution(
    transaction_context: TransactionContext,
    institution_id: str,
) -> dict | None:
    """
    Read an institution by institution_id.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        institution_id (str): UUID of the institution.

    Returns:
        dict | None: Institution record if found, None otherwise.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_institution", (institution_id,))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchone()
    return None


def sql_create_faculty_works_at_institution(
    transaction_context: TransactionContext,
    faculty_id: str,
    institution_id: str,
    start_date: date,
    end_date: date | None,
) -> None:
    """
    Create a faculty-institution relationship.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        institution_id (str): UUID of the institution.
        start_date (date): Start date of the relationship.
        end_date (date | None): End date of the relationship (optional).

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.callproc(
        "create_faculty_works_at_institution",
        (faculty_id, institution_id, start_date, end_date)
    )
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


def sql_check_faculty_works_at_institution_exists(
    transaction_context: TransactionContext,
    faculty_id: str,
    institution_id: str,
) -> bool:
    """
    Check if a faculty-institution relationship exists.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.
        institution_id (str): UUID of the institution.

    Returns:
        bool: True if relationship exists, False otherwise.
    """
    cursor = transaction_context.cursor
    cursor.execute(
        "SELECT COUNT(*) as count FROM faculty_works_at_institution WHERE faculty_id = %s AND institution_id = %s",
        (faculty_id, institution_id)
    )
    result = cursor.fetchone()
    return result["count"] > 0 if result else False


def sql_delete_faculty_works_at_institution_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> None:
    """
    Delete all institution relationships for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        None: No result set.
    """
    cursor = transaction_context.cursor
    cursor.callproc("delete_faculty_works_at_institution_by_faculty", (faculty_id,))
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


# ============================================================================
# SESSION DB LAYER FUNCTIONS
# ============================================================================

def sql_create_session(
    transaction_context: TransactionContext,
    session_id: str,
    faculty_id: str,
    token_hash: str,
    expires_at: datetime,
) -> None:
    """
    Create a new session record.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        session_id (str): UUID of the session.
        faculty_id (str): UUID of the faculty member.
        token_hash (str): SHA-256 hash of the refresh token (64 characters).
        expires_at (datetime): Expiration datetime for the session.

    Returns:
        None: No result set. Use read procedures to verify the insert.
    """
    cursor = transaction_context.cursor
    cursor.callproc(
        "create_session",
        (session_id, faculty_id, token_hash, expires_at)
    )
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass


def sql_read_session_by_token_hash(
    transaction_context: TransactionContext,
    token_hash: str,
) -> dict | None:
    """
    Read a session by its token hash.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        token_hash (str): SHA-256 hash of the refresh token (64 characters).

    Returns:
        dict | None: Session record if found and active, None otherwise.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_session_by_token_hash", (token_hash,))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchone()
    return None


def sql_read_session_by_faculty(
    transaction_context: TransactionContext,
    faculty_id: str,
) -> list[dict]:
    """
    Read all active sessions for a faculty member.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        faculty_id (str): UUID of the faculty member.

    Returns:
        list[dict]: List of active session records.
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_session_by_faculty", (faculty_id,))
    stored_results = list(cursor.stored_results())
    if stored_results:
        return stored_results[0].fetchall()
    return []


def sql_update_session(
    transaction_context: TransactionContext,
    session_id: str | None = None,
    token_hash: str | None = None,
    faculty_id: str | None = None,
    revoked: bool | None = None,
    expires_at: datetime | None = None,
) -> int:
    """
    Update session records based on identifier and optional fields.

    Args:
        transaction_context (TransactionContext): A transaction context object to use for the database connection.
        session_id (str | None): Optional UUID of the specific session to update.
        token_hash (str | None): Optional SHA-256 hash of the refresh token (64 characters).
        faculty_id (str | None): Optional UUID of the faculty member (updates all their sessions).
        revoked (bool | None): Optional boolean value for the revoked flag.
        expires_at (datetime | None): Optional datetime value for the expiration time.

    Returns:
        int: Number of rows affected.

    Raises:
        Exception: If no identifier is provided or no fields to update are provided.
    """
    cursor = transaction_context.cursor
    cursor.callproc(
        "update_session",
        (session_id, token_hash, faculty_id, revoked, expires_at)
    )
    # Consume any result set
    try:
        stored_results = list(cursor.stored_results())
        if stored_results:
            stored_results[0].fetchall()
    except:
        pass
    return cursor.rowcount
