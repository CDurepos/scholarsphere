DELIMITER $$

CREATE PROCEDURE add_publication_for_faculty (
    IN p_faculty_id CHAR(36),
    IN p_title VARCHAR(64),
    IN p_publisher VARCHAR(255),
    IN p_year INT,
    IN p_doi VARCHAR(64),
    IN p_abstract TEXT
)
BEGIN
    DECLARE v_publication_id CHAR(36);

    -- Validate input
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required.';
    END IF;

    -- 1. Insert the publication (calls the existing procedure)
    CALL insert_into_publication(
        v_publication_id,
        p_title,
        p_publisher,
        p_year,
        p_doi,
        p_abstract
    );

    -- 2. Insert into join table (calls the existing procedure)
    CALL insert_into_publication_authored_by_faculty(
        p_faculty_id,
        v_publication_id
    );

    -- 3. Return the resulting IDs
    SELECT v_publication_id AS publication_id,
           p_faculty_id AS faculty_id,
           'inserted' AS action;

END $$