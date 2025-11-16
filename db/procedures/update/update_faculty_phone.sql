DELIMITER $$

CREATE PROCEDURE update_faculty_phone (
    IN p_faculty_id   CHAR(36),
    IN p_old_phone    VARCHAR(32),
    IN p_new_phone    VARCHAR(32)
)
BEGIN
    UPDATE faculty_phone
    SET phone_num = p_new_phone
    WHERE faculty_id = p_faculty_id
      AND phone_num  = p_old_phone;

    SELECT p_faculty_id AS faculty_id,
           p_old_phone AS old_phone,
           p_new_phone AS new_phone,
           'updated' AS action;
END$$

DELIMITER ;