--add relationship row--

CREATE PROCEDURE add_author_publication(
    IN p_faculty_id CHAR(36),
    IN p_publication_id CHAR(36)
)
BEGIN
    INSERT INTO publication_authors (faculty_id, publication_id)
    VALUES (p_faculty_id, p_publication_id);
END;
