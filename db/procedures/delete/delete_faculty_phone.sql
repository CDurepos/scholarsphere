DELIMITER $$

CREATE PROCEDURE delete_faculty_phone (
    IN p_faculty_id CHAR(36),
    IN p_phone_num  VARCHAR(32)
)
BEGIN
    DELETE FROM faculty_phone
    WHERE faculty_id = p_faculty_id
      AND phone_num  = p_phone_num;

    SELECT p_faculty_id AS faculty_id,
           p_phone_num AS phone_num,
           'deleted' AS action;
END$$

DELIMITER ;