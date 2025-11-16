DELIMITER $$

CREATE PROCEDURE insert_faculty_email (
    IN p_faculty_id CHAR(36),
    IN p_email      VARCHAR(255)
)
BEGIN
    INSERT INTO faculty_email (faculty_id, email)
    VALUES (p_faculty_id, p_email);
END$$

DELIMITER ;