DELIMITER $$

CREATE PROCEDURE delete_faculty (
    IN p_faculty_id CHAR(36)
)
BEGIN
    DELETE FROM faculty
    WHERE faculty_id = p_faculty_id;

    -- return a simple status message
    SELECT p_faculty_id AS faculty_id, 'deleted' AS action;
END$$

DELIMITER ;