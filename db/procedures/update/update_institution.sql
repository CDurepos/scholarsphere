DELIMITER $$

/**
 * Updates an existing institution record in the database.
 * 
 * Performs a partial update on an institution record. Only non-NULL parameters
 * will update the corresponding fields; NULL parameters leave existing values
 * unchanged. The institution_id is required to identify which record to update.
 * 
 * @param p_institution_id  Required UUID of the institution record to update
 * @param p_name            Optional new institution name (NULL to keep existing)
 * @param p_street_addr     Optional new street address (NULL to keep existing)
 * @param p_city            Optional new city (NULL to keep existing)
 * @param p_state           Optional new state/province (NULL to keep existing)
 * @param p_country         Optional new country (NULL to keep existing)
 * @param p_zip             Optional new postal code (NULL to keep existing)
 * @param p_website_url     Optional new website URL (NULL to keep existing)
 * @param p_type            Optional new institution type (NULL to keep existing)
 * 
 * @returns Result set containing:
 *   - institution_id: UUID of the updated institution record
 *   - action: Status message ('updated')
 * 
 * @throws SQLSTATE '45000' if institution_id is NULL or if institution_id doesn't exist
 */
CREATE PROCEDURE update_institution (
    IN p_institution_id  CHAR(36),
    IN p_name            VARCHAR(256),
    IN p_street_addr     VARCHAR(255),
    IN p_city            VARCHAR(255),
    IN p_state           VARCHAR(255),
    IN p_country         VARCHAR(255),
    IN p_zip             VARCHAR(16),
    IN p_website_url     VARCHAR(255),
    IN p_type            VARCHAR(64)
)
BEGIN
    DECLARE inst_exists INT;

    IF p_institution_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'institution_id is required for update_institution';
    END IF;

    SELECT COUNT(*) INTO inst_exists
    FROM institution
    WHERE institution_id = p_institution_id;

    IF inst_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'institution_id does not exist';
    END IF;

    -- Update only the fields that are provided (non-NULL)
    -- Use conditional updates to preserve existing values when parameters are NULL
    UPDATE institution
    SET
        name = IF(p_name IS NOT NULL, p_name, name),
        street_addr = IF(p_street_addr IS NOT NULL, p_street_addr, street_addr),
        city = IF(p_city IS NOT NULL, p_city, city),
        state = IF(p_state IS NOT NULL, p_state, state),
        country = IF(p_country IS NOT NULL, p_country, country),
        zip = IF(p_zip IS NOT NULL, p_zip, zip),
        website_url = IF(p_website_url IS NOT NULL, p_website_url, website_url),
        type = IF(p_type IS NOT NULL, p_type, type)
    WHERE institution_id = p_institution_id;

    SELECT p_institution_id AS institution_id, 'updated' AS action;
END $$

DELIMITER ;


DELIMITER ;
