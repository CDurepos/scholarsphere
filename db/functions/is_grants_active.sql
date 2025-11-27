DELIMITER $$

DROP FUNCTION IF EXISTS is_grant_active;

CREATE FUNCTION is_grant_active(
    p_start_date DATE,
    p_end_date   DATE
) RETURNS BOOLEAN
READS SQL DATA
BEGIN
    RETURN grant_status(p_start_date, p_end_date) = 'ACTIVE';
END $$
DELIMITER ;
