-- Written by Clayton Durepos

DELIMITER $$

/**
 * Updates an existing grant record in the database.
 * 
 * Updates all fields of a grant record. All parameters except description
 * and end_date are required. This performs a full update, replacing all
 * values rather than a partial update.
 * 
 * @param p_grant_id      Required UUID of the grant record to update
 * @param p_description   Optional new description (NULL allowed)
 * @param p_amount        Required new grant amount (DECIMAL with 10 digits, 2 decimal places)
 * @param p_start_date    Required new start date of the grant period
 * @param p_end_date      Optional new end date of the grant period (NULL allowed)
 * 
 * @returns No result set. Use read procedures to verify the update.
 * 
 * @throws SQLSTATE '45000' if grant_id, amount, or start_date is NULL
 * @throws SQLSTATE '45000' if grant_id doesn't exist
 */
DROP PROCEDURE IF EXISTS update_grants$$
CREATE PROCEDURE update_grants(
    IN p_grant_id       CHAR(36),
    IN p_description    VARCHAR(2048),
    IN p_amount         DECIMAL(10,2),
    IN p_start_date     DATE,
    IN p_end_date       DATE
)
BEGIN
    IF p_grant_id IS NULL OR p_amount IS NULL OR p_start_date IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'grant_id, amount, and start_date are required for update_grants';
    END IF;

    UPDATE grants
    SET 
        description = p_description, 
        amount = p_amount, 
        start_date = p_start_date, 
        end_date = p_end_date
    WHERE grant_id = p_grant_id;
END $$
DELIMITER ;
