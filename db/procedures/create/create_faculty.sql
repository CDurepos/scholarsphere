DELIMITER $$

/**
 * Creates a new faculty member record in the database.
 * 
 * Inserts a new faculty record with the provided information. Automatically
 * generates a new UUID for the faculty_id. Only first_name is required;
 * all other fields are optional.
 * 
 * @param p_first_name          Required first name of the faculty member
 * @param p_last_name           Optional last name
 * @param p_biography           Optional biography text (max 2048 chars)
 * @param p_orcid               Optional ORCID identifier (19 characters)
 * @param p_google_scholar_url  Optional Google Scholar profile URL
 * @param p_research_gate_url   Optional ResearchGate profile URL
 * @param p_scraped_from        Optional source URL if data was scraped
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the newly created faculty member
 * 
 * @throws SQLSTATE '45000' if first_name is NULL
 */
CREATE PROCEDURE create_faculty (
    IN p_first_name          VARCHAR(128),
    IN p_last_name           VARCHAR(128),
    IN p_biography           VARCHAR(2048),
    IN p_orcid               CHAR(19),
    IN p_google_scholar_url  VARCHAR(255),
    IN p_research_gate_url   VARCHAR(255),
    IN p_scraped_from        VARCHAR(255)
)
BEGIN
    -- Variable to hold the generated UUID for the new faculty member
    DECLARE new_id CHAR(36);

    -- Validate that first_name is provided (required field)
    IF p_first_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'first_name is required when creating a faculty record';
    END IF;

    -- Generate a new UUID for this faculty member
    -- UUID() creates a unique 36-character identifier
    SET new_id = UUID();

    -- Insert the new faculty record with all provided information
    -- NULL values are allowed for optional fields (last_name, biography, etc.)
    INSERT INTO faculty (
        faculty_id,
        first_name,
        last_name,
        biography,
        orcid,
        google_scholar_url,
        research_gate_url,
        scraped_from
    )
    VALUES (
        new_id,
        p_first_name,
        p_last_name,
        p_biography,
        p_orcid,
        p_google_scholar_url,
        p_research_gate_url,
        p_scraped_from
    );

    -- Return the generated ID so the caller knows the new faculty member's identifier
    SELECT new_id AS faculty_id;
END $$
