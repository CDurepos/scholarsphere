DELIMITER $$

DROP PROCEDURE IF EXISTS insert_grants_granted_to_faculty
CREATE PROCEDURE insert_grants_granted_to_faculty(
    p_faculty_id    CHAR(36),
    p_grant_id      CHAR(36)
)
BEGIN
    INSERT INTO grants_granted_to_faculty(faculty_id, grant_id)
    VALUES(p_faculty_id, p_grant_id);
END $$

DELIMITER ;