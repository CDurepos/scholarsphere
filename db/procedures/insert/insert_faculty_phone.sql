DELIMITER $$

CREATE PROCEDURE insert_faculty_phone (
    IN p_faculty_id CHAR(36),
    IN p_phone_num  VARCHAR(32)
)
BEGIN
    INSERT INTO faculty_phone (faculty_id, phone_num)
    VALUES (p_faculty_id, p_phone_num);

    SELECT p_faculty_id AS faculty_id,
           p_phone_num AS phone_num,
           'inserted' AS action;
END$$

DELIMITER ;