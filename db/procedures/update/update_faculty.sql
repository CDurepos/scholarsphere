DELIMITER $$

/**
 * Updates an existing faculty member record.
 * 
 * Performs a partial update on a faculty record. Only non-NULL parameters
 * will update the corresponding fields; NULL parameters leave existing values
 * unchanged. The faculty_id is required to identify which record to update.
 * 
 * @param p_faculty_id          Required UUID of the faculty member to update
 * @param p_first_name          Optional new first name (NULL to keep existing)
 * @param p_last_name           Optional new last name (NULL to keep existing)
 * @param p_biography           Optional new biography (NULL to keep existing)
 * @param p_orcid               Optional new ORCID (NULL to keep existing)
 * @param p_google_scholar_url  Optional new Google Scholar URL (NULL to keep existing)
 * @param p_research_gate_url   Optional new ResearchGate URL (NULL to keep existing)
 * @param p_scraped_from        Optional new scraped_from value (NULL to keep existing)
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the updated faculty member
 *   - action: Status message ('updated')
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL or empty, or if faculty_id doesn't exist
 */
CREATE PROCEDURE update_faculty (
    IN p_faculty_id          CHAR(36),
    IN p_first_name          VARCHAR(128),
    IN p_last_name           VARCHAR(128),
    IN p_biography           VARCHAR(2048),
    IN p_orcid               CHAR(19),
    IN p_google_scholar_url  VARCHAR(255),
    IN p_research_gate_url   VARCHAR(255),
    IN p_scraped_from        VARCHAR(255)
)
BEGIN
    -- Variable to check if the faculty record exists
    DECLARE existing_count INT;

    -- Validate that faculty_id is provided and not empty
    IF p_faculty_id IS NULL OR TRIM(p_faculty_id) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required for update_faculty';
    END IF;

    -- Verify that the faculty member exists before attempting update
    -- This prevents silent failures if an invalid ID is provided
    SELECT COUNT(*) INTO existing_count
    FROM faculty
    WHERE faculty_id = p_faculty_id;

    IF existing_count = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id does not exist';
    END IF;

    -- Perform partial update using COALESCE
    -- COALESCE returns the first non-NULL value:
    --   - If parameter is NULL, keep existing value (first_name)
    --   - If parameter has a value, use the new value (p_first_name)
    -- This allows updating only specific fields without affecting others
    UPDATE faculty
    SET
        first_name = COALESCE(p_first_name, first_name),
        last_name = COALESCE(p_last_name, last_name),
        biography = COALESCE(p_biography, biography),
        orcid = COALESCE(p_orcid, orcid),
        google_scholar_url = COALESCE(p_google_scholar_url, google_scholar_url),
        research_gate_url = COALESCE(p_research_gate_url, research_gate_url),
        scraped_from = COALESCE(p_scraped_from, scraped_from)
    WHERE faculty_id = p_faculty_id;

    -- Return confirmation of the update
    SELECT p_faculty_id AS faculty_id, 'updated' AS action;
END $$