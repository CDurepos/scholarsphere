DELIMITER $$

DROP FUNCTION IF EXISTS keyword_exists;
CREATE FUNCTION keyword_exists(p_name VARCHAR(64))
RETURNS BOOLEAN
READS SQL DATA
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM keyword
        WHERE name = p_name
    );
END $$

DELIMITER ;
