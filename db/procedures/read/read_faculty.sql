DELIMITER $$

/**
 * Retrieves a faculty member record by their ID.
 * 
 * Fetches all information for a specific faculty member identified by
 * their unique faculty_id.
 * 
 * @param p_faculty_id  Required UUID of the faculty member to retrieve
 * 
 * @returns Result set containing all columns from the faculty table:
 *   - faculty_id
 *   - first_name
 *   - last_name
 *   - biography
 *   - orcid
 *   - google_scholar_url
 *   - research_gate_url
 *   - scraped_from
 */
CREATE PROCEDURE read_faculty(
    IN p_faculty_id CHAR(36)
)
BEGIN
    -- Simple SELECT query to retrieve all columns for the specified faculty member
    -- Uses table alias 'f' for clarity
    -- Returns all fields from the faculty table for the matching ID
    SELECT f.*
    FROM faculty f
    WHERE f.faculty_id = p_faculty_id;
END $$