DELIMITER $$

CREATE PROCEDURE update_faculty_title (
    IN p_faculty_id   CHAR(36),
    IN p_old_title    VARCHAR(255),
    IN p_new_title    VARCHAR(255)
)
BEGIN
    UPDATE faculty_title
    SET title = p_new_title
    WHERE faculty_id = p_faculty_id
      AND title      = p_old_title;

    SELECT p_faculty_id AS faculty_id,
           p_old_title AS old_title,
           p_new_title AS new_title,
           'updated' AS action;
END$$

DELIMITER ;