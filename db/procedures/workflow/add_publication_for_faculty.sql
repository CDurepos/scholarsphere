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
 * @param p_faculty_id    Required UUID of the faculty member
 * @param p_title         Publication title
 * @param p_publisher     Publisher name
 * @param p_year          Publication year
 * @param p_doi           Digital Object Identifier (DOI)
 * @param p_abstract      Publication abstract text
 * 
 * @returns Result set containing:
 *   - publication_id: UUID of the newly created publication
 *   - faculty_id: UUID of the associated faculty member
 *   - action: Status message ('inserted')
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 */
CREATE PROCEDURE add_publication_for_faculty (
    IN p_faculty_id CHAR(36),
    IN p_title VARCHAR(64),
    IN p_publisher VARCHAR(255),
    IN p_year INT,
    IN p_doi VARCHAR(64),
    IN p_abstract TEXT
)
BEGIN
    -- Variable to store the generated publication ID
    DECLARE v_publication_id CHAR(36);
    DECLARE v_generated_id CHAR(36);

    -- Validate input: faculty_id must be provided
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required.';
    END IF;

    -- Step 1: Generate a UUID for the new publication
    SET v_publication_id = UUID();

    -- Step 2: Create the publication record
    CALL create_publication(
        v_publication_id,
        p_title,
        p_publisher,
        p_year,
        p_doi,
        p_abstract,
        v_generated_id
    );

    -- Step 3: Link the publication to the faculty member
    -- This creates the many-to-many relationship in the join table
    CALL create_publication_authored_by_faculty(
        p_faculty_id,
        v_publication_id
    );

    -- Step 4: Return confirmation with both IDs for reference
    SELECT v_publication_id AS publication_id,
           p_faculty_id AS faculty_id,
           'inserted' AS action;

END $$

DELIMITER ;