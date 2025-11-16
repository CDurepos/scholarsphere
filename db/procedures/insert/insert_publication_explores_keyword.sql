DELIMITER $$

CREATE PROCEDURE insert_into_publication_explores_keyword(
    IN p_publication_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    INSERT INTO publication_explores_keyword(publication_id, name)
    VALUES (p_publication_id, p_name);
END $$
