DELIMITER $$

CREATE PROCEDURE delete_publication_authored_by_faculty(
    IN p_faculty_id CHAR(36)
    IN p_publication_id CHAR(36)
)
BEGIN
    DELETE FROM publication_authored_by_faculty
    WHERE faculty_id = p_faculty_id AND publication_id = p_publication_id;
END $$

