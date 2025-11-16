DELIMITER $$

CREATE PROCEDURE insert_faculty_department (
    IN p_faculty_id CHAR(36),
    IN p_department_name VARCHAR(128)
)
BEGIN
    -- Validation
    IF p_faculty_id IS NULL OR p_department_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and department_name are required.';
    END IF;

    INSERT INTO faculty_department (faculty_id, department_name)
    VALUES (p_faculty_id, p_department_name);

    SELECT p_faculty_id AS faculty_id,
           p_department_name AS department_name,
           'inserted' AS action;
END $$

DELIMITER ;