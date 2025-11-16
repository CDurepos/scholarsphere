DELIMITER $$

CREATE PROCEDURE read_faculty_phone (
    IN p_faculty_id CHAR(36)
)
BEGIN
    SELECT faculty_id, phone_num
    FROM faculty_phone
    WHERE faculty_id = p_faculty_id;
END$$

DELIMITER ;