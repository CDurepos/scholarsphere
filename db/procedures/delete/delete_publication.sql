DELIMITER $$

CREATE PROCEDURE delete_author_publication(
    IN p_id CHAR(36)
)
BEGIN
    DELETE FROM publication
    WHERE publication_id = p_id;
END $$
