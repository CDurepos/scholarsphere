DELIMITER $$

CREATE PROCEDURE read_faculty_department (
    IN p_faculty_id CHAR(36)
)
BEGIN
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required.';
    END IF;

    SELECT department_name
    FROM faculty_department
    WHERE faculty_id = p_faculty_id;
END $$

DELIMITER ;