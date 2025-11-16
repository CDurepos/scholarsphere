DELIMITER $$

CREATE PROCEDURE insert_into_faculty (
    IN p_first_name          VARCHAR(128),
    IN p_last_name           VARCHAR(128),
    IN p_biography           VARCHAR(2048),
    IN p_orcid               CHAR(19),
    IN p_google_scholar_url  VARCHAR(255),
    IN p_research_gate_url   VARCHAR(255),
    IN p_scraped_from        VARCHAR(255)
)
BEGIN
    DECLARE new_id CHAR(36);

    -- Required field check
    IF p_first_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'first_name is required when creating a faculty record';
    END IF;

    SET new_id = UUID();

    INSERT INTO faculty (
        faculty_id,
        first_name,
        last_name,
        biography,
        orcid,
        google_scholar_url,
        research_gate_url,
        scraped_from
    )
    VALUES (
        new_id,
        p_first_name,
        p_last_name,
        p_biography,
        p_orcid,
        p_google_scholar_url,
        p_research_gate_url,
        p_scraped_from
    );

    SELECT new_id AS faculty_id;
END $$

DELIMITER ;
