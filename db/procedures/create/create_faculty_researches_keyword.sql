DELIMITER $$

CREATE PROCEDURE insert_into_faculty_researches_keyword(
    IN p_faculty_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    INSERT INTO faculty_researches_keyword (name, faculty_id)
    VALUES (p_name, p_faculty_id);
END $$

DELIMITER ;