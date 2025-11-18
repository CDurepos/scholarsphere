DELIMITER $$

/**
 * Retrieves institution records from the database.
 * 
 * Returns institution information for a specific institution or all institutions
 * in the database. Results are ordered alphabetically by institution name.
 * 
 * @param p_institution_id  Optional UUID of a specific institution to retrieve.
 *                          When provided, only that institution record is returned.
 *                          When NULL, all institutions in the database are returned.
 * 
 * @returns Result set containing all columns from the institution table:
 *   - institution_id
 *   - name
 *   - street_addr
 *   - city
 *   - state
 *   - country
 *   - zip
 *   - website_url
 *   - type
 */
CREATE PROCEDURE read_institution (
    IN p_institution_id CHAR(36)
)
BEGIN
    SELECT i.*
    FROM institution i
    WHERE (p_institution_id IS NULL OR i.institution_id = p_institution_id)
    ORDER BY i.name;
END $$

DELIMITER ;


DELIMITER ;
