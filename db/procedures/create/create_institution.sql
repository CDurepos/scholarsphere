-- Written by Clayton Durepos

DELIMITER $$

/**
 * Creates a new institution record in the database.
 * 
 * Inserts a new institution record with the provided information. The institution_id
 * and name are required, along with country. All other location and contact fields
 * are optional. The zip code must be exactly 5 digits if provided.
 * 
 * @param p_institution_id  Required UUID for the institution record
 * @param p_name            Required institution name (max 256 characters)
 * @param p_street_addr     Optional street address (max 255 characters)
 * @param p_city            Optional city name (max 255 characters)
 * @param p_state           Optional state or province (max 255 characters)
 * @param p_country         Required country name (max 255 characters)
 * @param p_zip             Optional postal code (must be exactly 5 digits if provided)
 * @param p_website_url     Optional website URL (max 255 characters)
 * @param p_type            Optional institution type (ENUM: 'Public University', 'Private University', 'Community College')
 * 
 * @returns No result set. Use read_institution to verify the insert.
 * 
 * @throws SQLSTATE '23000' if institution_id already exists (primary key constraint)
 * @throws SQLSTATE 'HY000' if zip code format is invalid (must be 5 digits)
 */
DROP PROCEDURE IF EXISTS create_institution$$
CREATE PROCEDURE create_institution(
    IN p_institution_id CHAR(36),
    IN p_name VARCHAR(256),
    IN p_street_addr VARCHAR(255),
    IN p_city VARCHAR(255),
    IN p_state VARCHAR(255),
    IN p_country VARCHAR(255),
    IN p_zip VARCHAR(16),
    IN p_website_url VARCHAR(255),
    IN p_type VARCHAR(64)
)
BEGIN
    INSERT INTO institution (
        institution_id,
        name,
        street_addr,
        city,
        state,
        country,
        zip,
        website_url,
        type
    ) VALUES (
        p_institution_id,
        p_name,
        p_street_addr,
        p_city,
        p_state,
        p_country,
        p_zip,
        p_website_url,
        p_type
    );
END $$

DELIMITER ;
