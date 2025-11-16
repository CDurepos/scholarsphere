CREATE PROCEDURE add_keyword_user(
    IN p_faculty_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    INSERT INTO user_keywords (name, faculty_id)
    VALUES (p_name, p_faculty_id);
END;
