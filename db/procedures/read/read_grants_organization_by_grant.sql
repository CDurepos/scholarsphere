DELIMITER $$

/**
 * Retrieves all organization names associated with a specific grant.
 * 
 * Returns all organization names that provided or are associated with
 * the specified grant. Grants can be associated with multiple organizations.
 * 
 * @param p_grant_id  Required UUID of the grant
 * 
 * @returns Result set containing:
 *   - name: Organization name (max 256 characters)
 *   (Multiple rows if the grant is associated with multiple organizations)
 * 
 * @throws SQLSTATE '45000' if grant_id is NULL
 */
DROP PROCEDURE IF EXISTS read_grants_organization_by_grant$$
CREATE PROCEDURE read_grants_organization_by_grant(
    IN p_grant_id   CHAR(36)
)
BEGIN
    IF p_grant_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'grant_id is required';
    END IF;

    SELECT name
    FROM grants_organization
    WHERE grant_id = p_grant_id;
END $$
DELIMITER ;
