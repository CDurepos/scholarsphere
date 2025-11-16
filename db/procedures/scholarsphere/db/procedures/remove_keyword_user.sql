CREATE PROCEDURE remove_keyword_user(
    IN p_faculty_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    DELETE FROM user_keywords
    WHERE faculty_id = p_faculty_id
      AND name = p_name;
END;
