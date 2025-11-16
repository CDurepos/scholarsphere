DELIMITER $$

CREATE PROCEDURE delete_faculty_email (
    IN p_faculty_id CHAR(36),
    IN p_email      VARCHAR(255)
)
BEGIN
    DELETE FROM faculty_email
    WHERE faculty_id = p_faculty_id
      AND email = p_email;
END$$

DELIMITER ;