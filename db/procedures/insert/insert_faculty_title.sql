DELIMITER $$

/**
 * Adds a title to a faculty member.
 * 
 * Inserts a new title record for the specified faculty member. Faculty members
 * can have multiple titles, so this creates an additional title association
 * rather than replacing existing ones.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_title       Required title to associate with the faculty member
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - title: The title that was inserted
 *   - action: Status message ('inserted')
 */
CREATE PROCEDURE create_faculty_title (
    IN p_faculty_id CHAR(36),
    IN p_title      VARCHAR(255)
)
BEGIN
    -- Insert a new title association for the faculty member
    -- This allows faculty to have multiple titles (e.g., "Professor", "Department Chair")
    -- The combination of faculty_id and title should be unique
    INSERT INTO faculty_title (faculty_id, title)
    VALUES (p_faculty_id, p_title);

    -- Return confirmation with the inserted values
    SELECT p_faculty_id AS faculty_id,
           p_title AS title,
           'inserted' AS action;
END$$

DELIMITER ;