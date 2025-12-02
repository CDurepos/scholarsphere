DELIMITER $$

/**
 * Retrieves all grants associated with a specific organization.
 * 
 * Returns all grant records associated with the specified organization
 * through the grants_organization join table. Includes a derived status
 * field indicating whether each grant is active, expired, or upcoming.
 * 
 * @param p_name  Required organization name (max 256 characters)
 * 
 * @returns Result set containing all columns from the grants table plus:
 *   - grant_id
 *   - description
 *   - amount
 *   - start_date
 *   - end_date
 *   - derived_status: Computed status ('Active', 'Expired', or 'Upcoming')
 * 
 * Results are ordered by start_date (newest first).
 * 
 * @throws SQLSTATE '45000' if organization name is NULL
 */
DROP PROCEDURE IF EXISTS read_grants_by_organization;
CREATE PROCEDURE read_grants_by_organization(
    IN  p_name  VARCHAR(256)
)
BEGIN
    IF p_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'organization name is required';
    END IF;
   
    SELECT  g.*,
            grants_status(g.start_date, g.end_date) AS derived_status
    FROM    grants AS g
    JOIN    grants_organization AS go
            ON g.grant_id = go.grant_id
    WHERE go.name = p_name
    ORDER BY g.start_date DESC;
END $$
DELIMITER ;
