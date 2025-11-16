DELIMITER $$

CREATE PROCEDURE update_faculty_email (
    IN p_faculty_id   CHAR(36),
    IN p_old_email    VARCHAR(255),
    IN p_new_email    VARCHAR(255)
)
BEGIN
    UPDATE faculty_email
    SET email = p_new_email
    WHERE faculty_id = p_faculty_id
      AND email = p_old_email;
END$$

DELIMITER ;