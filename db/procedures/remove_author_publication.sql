CREATE PROCEDURE remove_author_publication(
    IN p_faculty_id CHAR(36)
    IN p_publication_id CHAR(36)
)
BEGIN
    DELETE FROM publication_authors
    WHERE faculty_id = p_faculty_id AND publication_id = p_publication_id;
END;

