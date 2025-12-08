-- Written by Owen Leitzell

DELIMITER $$

/**
 * Adds a new publication and associates it with a faculty member.
 * 
 * This workflow procedure combines two operations:
 * 1. Creates a new publication record
 * 2. Links the publication to the specified faculty member via the join table
 * 
 * This is a convenience procedure that handles the complete workflow of
 * adding a publication for a faculty member in a single call.
 * 
 * @param p_faculty_id     Required UUID of the faculty member
 * @param p_publication_id Required UUID of the publication
 * @param p_title          Publication title
 * @param p_publisher      Publisher name
 * @param p_year           Publication year
 * @param p_doi            Digital Object Identifier (DOI)
 * @param p_abstract       Publication abstract text
 * @param p_citation_count Citation count
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the associated faculty member
 *   - publication_id: UUID of the newly created publication
 *   - action: Status message ('inserted')
 * 
 * @throws SQLSTATE '45000' if faculty_id or publication_id is NULL
 */
CREATE PROCEDURE add_publication_for_faculty (
    IN p_faculty_id CHAR(36),
    IN p_publication_id CHAR(36),
    IN p_title VARCHAR(128),
    IN p_publisher VARCHAR(255),
    IN p_year INT,
    IN p_doi VARCHAR(64),
    IN p_abstract TEXT,
    IN p_citation_count INT
)
BEGIN
    -- Validate input: faculty_id and publication_id must be provided
    IF p_faculty_id IS NULL OR p_publication_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and publication_id are required.';
    END IF;

    -- Step 1: Create the publication record
    CALL create_publication(
        p_publication_id,
        p_title,
        p_publisher,
        p_year,
        p_doi,
        p_abstract,
        p_citation_count
    );

    -- Step 2: Link the publication to the faculty member
    -- This creates the many-to-many relationship in the join table
    CALL create_publication_authored_by_faculty(
        p_faculty_id,
        p_publication_id
    );

    -- Step 3: Return confirmation with both IDs for reference
    SELECT p_faculty_id AS faculty_id,
           p_publication_id AS publication_id,
           'inserted' AS action;

END $$
DELIMITER ;
