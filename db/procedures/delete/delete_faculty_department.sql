DELIMITER $$

CREATE PROCEDURE delete_faculty_department (
    IN p_faculty_id CHAR(36),
    IN p_department_name VARCHAR(128)
)
BEGIN
    IF p_faculty_id IS NULL OR p_department_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and department_name are required.';
    END IF;

    DELETE FROM faculty_department
    WHERE faculty_id = p_faculty_id
      AND department_name = p_department_name;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No matching faculty/department entry to delete.';
    END IF;

    SELECT p_faculty_id AS faculty_id,
           p_department_name AS department_name,
           'deleted' AS action;
END $$

DELIMITER ;