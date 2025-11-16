DELIMITER $$

/**
 * Creates an association between a faculty member and a publication.
 * 
 * Inserts a record into the publication_authored_by_faculty join table,
 * establishing that a specific faculty member authored a specific publication.
 * This allows many-to-many relationships between faculty and publications.
 * 
 * @param p_faculty_id      Required UUID of the faculty member
 * @param p_publication_id  Required UUID of the publication
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - publication_id: UUID of the publication
 *   - action: Status message ('inserted')
 * 
 * @throws SQLSTATE '45000' if faculty_id or publication_id is NULL
 */
CREATE PROCEDURE insert_publication_authored_by_faculty (
    IN p_faculty_id CHAR(36),
    IN p_publication_id CHAR(36)
)
BEGIN
    -- Validate that both IDs are provided (neither can be NULL)
    IF p_faculty_id IS NULL OR p_publication_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and publication_id are required.';
    END IF;

    -- Insert the relationship into the join table
    -- This creates a link between a faculty member and a publication
    -- Note: If this relationship already exists, this will fail due to unique constraint
    INSERT INTO publication_authored_by_faculty (faculty_id, publication_id)
    VALUES (p_faculty_id, p_publication_id);

    -- Return confirmation with both IDs to verify the relationship was created
    SELECT p_faculty_id AS faculty_id,
           p_publication_id AS publication_id,
           'inserted' AS action;
END $$