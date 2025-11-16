DELIMITER $$

CREATE FUNCTION user_has_keyword(
    IN p_faculty_id CHAR(36),
    IN p_name VARCHAR(64)
)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM user_keywords
        WHERE faculty_id = p_faculty_id
          AND name = p_name
    );
END $$
