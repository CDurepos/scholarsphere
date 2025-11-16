DELIMITER $$

CREATE PROCEDURE create_faculty_title (
    IN p_faculty_id CHAR(36),
    IN p_title      VARCHAR(255)
)
BEGIN
    INSERT INTO faculty_title (faculty_id, title)
    VALUES (p_faculty_id, p_title);

    SELECT p_faculty_id AS faculty_id,
           p_title AS title,
           'inserted' AS action;
END$$

DELIMITER ;