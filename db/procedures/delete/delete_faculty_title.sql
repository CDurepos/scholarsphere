-- Written by Aidan Bell

DELIMITER $$

/**
 * Removes a specific title from a faculty member.
 * 
 * Deletes a title association for the specified faculty member. Both
 * faculty_id and title must be provided to uniquely identify which
 * title record to remove, since faculty members can have multiple titles.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_title       Required title to remove
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - title: The title that was deleted
 *   - action: Status message ('deleted')
 */
CREATE PROCEDURE delete_faculty_title (
    IN p_faculty_id CHAR(36),
    IN p_title      VARCHAR(255)
)
BEGIN
    -- Delete the specific title association
    -- Both faculty_id AND title are required in WHERE clause to uniquely
    -- identify which title to remove (since faculty can have multiple titles)
    DELETE FROM faculty_title
    WHERE faculty_id = p_faculty_id
      AND title = p_title;

    -- Return confirmation of what was deleted
    SELECT p_faculty_id AS faculty_id,
           p_title AS title,
           'deleted' AS action;
END$$

DELIMITER ;