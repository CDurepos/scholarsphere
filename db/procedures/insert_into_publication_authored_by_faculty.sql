DELIMITER $$

CREATE PROCEDURE insert_into_publication_authored_by_faculty (
    IN p_faculty_id CHAR(36),
    IN p_publication_id CHAR(36)
)
BEGIN
    -- Argument validation
    IF p_faculty_id IS NULL OR p_publication_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and publication_id are required.';
    END IF;

    -- Insert into join table
    INSERT INTO publication_authors (faculty_id, publication_id)
    VALUES (p_faculty_id, p_publication_id);

    -- Return confirmation (optional)
    SELECT p_faculty_id AS faculty_id,
           p_publication_id AS publication_id,
           'inserted' AS action;
END $$

DELIMITER ;