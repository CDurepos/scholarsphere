DELIMITER $$

/**
 * Updates or creates an organization association for a grant.
 * 
 * Inserts a new grants_organization record, or updates an existing one if
 * a record with the same grant_id already exists. This uses MySQL's
 * ON DUPLICATE KEY UPDATE to handle both insert and update in one operation.
 * 
 * @param p_grant_id  Required UUID of the grant
 * @param p_name      Required organization name (max 255 characters)
 * 
 * @returns No result set. Use read procedures to verify the update/insert.
 * 
 * @throws SQLSTATE '23000' if grant_id doesn't exist (foreign key constraint)
 */
DROP PROCEDURE IF EXISTS update_grants_organization;
CREATE PROCEDURE update_grants_organization(
    IN  p_grant_id  CHAR(36),
    IN  p_name      VARCHAR(255)
)
BEGIN
    IF p_grant_id IS NULL OR p_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'grant_id and name are required for update_grants_organization';
    END IF;

    INSERT INTO grants_organization (grant_id, name)
    VALUES  (p_grant_id, p_name)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name);
END $$
DELIMITER ;
