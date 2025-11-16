DELIMITER $$

CREATE PROCEDURE read_faculty_title (
    IN p_faculty_id CHAR(36)
)
BEGIN
    SELECT faculty_id, title
    FROM faculty_title
    WHERE faculty_id = p_faculty_id;
END$$

DELIMITER ;