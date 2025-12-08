-- Written by Clayton Durepos

DELIMITER $$

/**
 * Searches for existingfaculty members based on search criteria.
 * Used specifically for looking up faculty during signup.
 * 
 * This procedure performs a flexible search across faculty records, matching
 * against first name, last name, and institution. All parameters
 * are optional - if NULL, that criterion is ignored. Uses LIKE pattern matching
 * with wildcards for partial matches.
 * 
 * @param p_first_name    Optional first name to search for (partial match)
 * @param p_last_name     Optional last name to search for (partial match)
 * @param p_institution   Optional institution name to search for (partial match)
 * 
 * @returns Result set containing:
 *   - faculty_id: Unique identifier for the faculty member
 *   - first_name: Faculty member's first name
 *   - last_name: Faculty member's last name
 *   - institution_name: Institution name (if associated)
 */
CREATE PROCEDURE search_existing_faculty(
    IN p_first_name    VARCHAR(128),
    IN p_last_name     VARCHAR(128),
    IN p_institution   VARCHAR(255)
)
BEGIN
    -- Use DISTINCT to handle cases where a faculty member has multiple departments or institutions
    SELECT DISTINCT
        f.faculty_id,
        f.first_name,
        f.last_name,
        i.name AS institution_name
    FROM faculty AS f
    -- LEFT JOIN to get institution information through the works_at relationship
    LEFT JOIN faculty_works_at_institution AS w
        ON f.faculty_id = w.faculty_id
    LEFT JOIN institution AS i
        ON w.institution_id = i.institution_id
    WHERE
        -- Each condition checks if the parameter is NULL (ignore) or matches with LIKE
        -- CONCAT(value, '%') creates a pattern for partial matching (starts with)
        -- Use AND logic: all provided (non-NULL) parameters must match
        (p_first_name  IS NULL OR f.first_name      LIKE CONCAT(p_first_name, '%'))
        AND (p_last_name IS NULL OR f.last_name      LIKE CONCAT(p_last_name, '%'))
        AND (p_institution IS NULL OR i.name            LIKE CONCAT(p_institution, '%'))
    LIMIT 5;
END $$
DELIMITER ;

