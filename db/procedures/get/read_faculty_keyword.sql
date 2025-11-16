DELIMITER $$

CREATE PROCEDURE read_keyword_user(
    IN p_faculty_id CHAR(36)
)
BEGIN
    SELECT name
    FROM user_keywords
    WHERE faculty_id = p_faculty_id;
END $$