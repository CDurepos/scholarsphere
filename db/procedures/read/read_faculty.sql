DELIMITER $$

-- Get a faculty row provided the faculty_id
CREATE PROCEDURE read_faculty(
    IN p_faculty_id CHAR(36)
)
BEGIN
    SELECT p.*
    FROM publication p
    WHERE p.faculty_id = p_faculty_id;
END $$