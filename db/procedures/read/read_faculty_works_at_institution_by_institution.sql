-- Written by Clayton Durepos

DELIMITER $$

/**
 * Retrieves all faculty members who work at a given institution.
 * 
 * Returns all faculty records associated with the specified institution.
 * This includes faculty members who currently work at the institution or
 * have worked there in the past (based on the faculty_works_at_institution
 * relationship table).
 * 
 * @param p_institution_id  Required UUID of the institution
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
 * 
 * @throws SQLSTATE '45000' if institution_id is NULL
 */
DROP PROCEDURE IF EXISTS read_faculty_works_at_institution_by_institution$$
CREATE PROCEDURE read_faculty_works_at_institution_by_institution (
    IN p_institution_id CHAR(36)
)
BEGIN
    -- Validate that institution_id is provided
    IF p_institution_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'institution_id is required';
    END IF;

    -- Retrieve all faculty members associated with the specified institution
    -- Joins faculty_works_at_institution to find all faculty at this institution
    -- Returns all faculty information for those who work or have worked at the institution
    SELECT f.*
    FROM faculty f
    INNER JOIN faculty_works_at_institution fwi
        ON f.faculty_id = fwi.faculty_id
    WHERE fwi.institution_id = p_institution_id
    ORDER BY f.last_name, f.first_name;
END $$

DELIMITER ;
