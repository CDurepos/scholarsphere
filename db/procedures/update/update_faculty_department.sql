DELIMITER $$

CREATE PROCEDURE update_faculty_department (
    IN p_faculty_id CHAR(36),
    IN p_old_department_name VARCHAR(128),
    IN p_new_department_name VARCHAR(128)
)
BEGIN
    IF p_faculty_id IS NULL
       OR p_old_department_name IS NULL
       OR p_new_department_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id, old department, and new department are required.';
    END IF;

    UPDATE faculty_department
    SET department_name = p_new_department_name
    WHERE faculty_id = p_faculty_id
      AND department_name = p_old_department_name;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No matching faculty/department entry to update.';
    END IF;

    SELECT p_faculty_id AS faculty_id,
           p_old_department_name AS old_department,
           p_new_department_name AS new_department,
           'updated' AS action;
END $$

DELIMITER ;