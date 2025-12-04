DELIMITER $$

/**
 * Creates a new grant record in the database.
 * 
 * Inserts a new grant record with the provided information. Grants represent
 * funding awards with a specific amount, description, and time period.
 * 
 * @param p_grant_id      Required UUID for the grant record
 * @param p_description   Optional description of the grant (TEXT field)
 * @param p_amount        Required grant amount (DECIMAL with 10 digits, 2 decimal places)
 * @param p_start_date    Required start date of the grant period
 * @param p_end_date      Optional end date of the grant period (NULL if ongoing)
 * 
 * @returns No result set. Use read procedures to verify the insert.
 * 
 * @throws SQLSTATE '23000' if grant_id already exists (primary key constraint)
 */
DROP PROCEDURE IF EXISTS create_grants$$
CREATE PROCEDURE create_grants(
    IN      p_grant_id      CHAR(36),
    IN      p_description   TEXT,
    IN      p_amount        DECIMAL(10,2),
    IN      p_start_date    DATE,
    IN      p_end_date      DATE
)

BEGIN
    INSERT INTO grants(
        grant_id, description, amount, start_date, end_date
    ) VALUES (
        p_grant_id, p_description, p_amount, p_start_date, p_end_date
    );
END $$

DELIMITER ;
