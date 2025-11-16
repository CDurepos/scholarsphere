DELIMITER $$

CREATE PROCEDURE read_faculty_email (
    IN p_faculty_id CHAR(36)
)
BEGIN
    SELECT faculty_id, email
    FROM faculty_email
    WHERE faculty_id = p_faculty_id;
END$$

DELIMITER ;