DELIMITER $$

CREATE PROCEDURE update_faculty (
    IN p_faculty_id          CHAR(36),
    IN p_first_name          VARCHAR(128),
    IN p_last_name           VARCHAR(128),
    IN p_biography           VARCHAR(2048),
    IN p_orcid               CHAR(19),
    IN p_google_scholar_url  VARCHAR(255),
    IN p_research_gate_url   VARCHAR(255),
    IN p_scraped_from        VARCHAR(255)
)
BEGIN
    DECLARE existing_count INT;

    -- ID is always required for updates
    IF p_faculty_id IS NULL OR TRIM(p_faculty_id) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required for update_faculty';
    END IF;

    -- Check row exists
    SELECT COUNT(*) INTO existing_count
    FROM faculty
    WHERE faculty_id = p_faculty_id;

    IF existing_count = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id does not exist';
    END IF;

    -- Partial safe update
    UPDATE faculty
    SET
        first_name = COALESCE(p_first_name, first_name),
        last_name = COALESCE(p_last_name, last_name),
        biography = COALESCE(p_biography, biography),
        orcid = COALESCE(p_orcid, orcid),
        google_scholar_url = COALESCE(p_google_scholar_url, google_scholar_url),
        research_gate_url = COALESCE(p_research_gate_url, research_gate_url),
        scraped_from = COALESCE(p_scraped_from, scraped_from)
    WHERE faculty_id = p_faculty_id;

    SELECT p_faculty_id AS faculty_id, 'updated' AS action;
END $$

DELIMITER ;