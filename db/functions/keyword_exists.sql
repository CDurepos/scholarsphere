DELIMITER $$

CREATE FUNCTION keyword_exists(p_name VARCHAR(64))
RETURNS BOOLEAN
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM keyword
        WHERE name = p_name
    );
END $$
