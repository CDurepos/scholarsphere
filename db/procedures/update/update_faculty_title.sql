DELIMITER $$

/**
 * Updates a specific title for a faculty member.
 * 
 * Changes an existing title to a new value. Both the old title and new title
 * must be specified to uniquely identify which title record to update, since
 * faculty members can have multiple titles.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_old_title   Required current title value to be changed
 * @param p_new_title   Required new title value
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - old_title: The previous title value
 *   - new_title: The new title value
 *   - action: Status message ('updated')
 */
CREATE PROCEDURE update_faculty_title (
    IN p_faculty_id   CHAR(36),
    IN p_old_title    VARCHAR(255),
    IN p_new_title    VARCHAR(255)
)
BEGIN
    -- Validate that all required parameters are provided
    IF p_faculty_id IS NULL OR p_old_title IS NULL OR p_new_title IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id, old_title, and new_title are required for update_faculty_title';
    END IF;

    -- Update the specific title record
    -- Both faculty_id AND old_title are needed in WHERE clause because
    -- a faculty member can have multiple titles, so we need to identify which one to change
    UPDATE faculty_title
    SET title = p_new_title
    WHERE faculty_id = p_faculty_id
      AND title      = p_old_title;

    -- Check if any rows were actually updated
    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No matching faculty/title entry to update';
    END IF;

    -- Return confirmation showing both old and new values
    SELECT p_faculty_id AS faculty_id,
           p_old_title AS old_title,
           p_new_title AS new_title,
           'updated' AS action;
END$$

DELIMITER ;