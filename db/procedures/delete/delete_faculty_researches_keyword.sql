CREATE PROCEDURE delete_faculty_researches_keyword(
    IN p_faculty_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    DELETE FROM faculty_researches_keyword
    WHERE faculty_id = p_faculty_id
      AND name = p_name;
END;
