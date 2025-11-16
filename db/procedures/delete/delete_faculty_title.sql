DELIMITER $$

CREATE PROCEDURE delete_faculty_title (
    IN p_faculty_id CHAR(36),
    IN p_title      VARCHAR(255)
)
BEGIN
    DELETE FROM faculty_title
    WHERE faculty_id = p_faculty_id
      AND title = p_title;

    SELECT p_faculty_id AS faculty_id,
           p_title AS title,
           'deleted' AS action;
END$$

DELIMITER ;