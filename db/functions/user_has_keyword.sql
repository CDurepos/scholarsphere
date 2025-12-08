-- Written by Owen Leitzell

DELIMITER $$

DROP FUNCTION IF EXISTS user_has_keyword$$
CREATE FUNCTION user_has_keyword(
    p_faculty_id CHAR(36),
    p_name VARCHAR(64)
)
RETURNS BOOLEAN
READS SQL DATA
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM user_keywords
        WHERE faculty_id = p_faculty_id
          AND name = p_name
    );
END $$

DELIMITER ;
