DELIMITER $$

CREATE FUNCTION get_publication_title(p_publication_id CHAR(36))
RETURNS VARCHAR(64)
BEGIN
    DECLARE v_title VARCHAR(64);

    SELECT title INTO v_title
    FROM publications
    WHERE publication_id = p_publication_id;

    RETURN v_title;
END $$
