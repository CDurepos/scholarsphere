DELIMITER $$

--Use a procedure because we want to return a table
CREATE PROCEDURE read_user_publications(
    IN p_faculty_id CHAR(36)
)
BEGIN
    SELECT p.*
    FROM publication p
    JOIN publication_authors pa
        ON p.publication_id = pa.publication_id
    WHERE pa.faculty_id = p_faculty_id;
END $$

DELIMITER ;