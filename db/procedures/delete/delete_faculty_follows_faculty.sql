DELIMITER $$

/**
 * Removes a follow relationship between two faculty members.
 * 
 * Deletes a specific follow relationship where one faculty member
 * (follower) follows another faculty member (followee). Both IDs
 * must be provided to uniquely identify which relationship to remove.
 * 
 * @param p_follower_id  Required UUID of the faculty member who is following
 * @param p_followee_id  Required UUID of the faculty member being followed
 * 
 * @returns Result set containing:
 *   - follower_id: UUID of the faculty member who was following
 *   - followee_id: UUID of the faculty member who was being followed
 *   - action: Status message ('deleted')
 * 
 * @throws SQLSTATE '45000' if follower_id or followee_id is NULL, or if no matching relationship exists
 */
CREATE PROCEDURE delete_faculty_follows_faculty (
    IN p_follower_id CHAR(36),
    IN p_followee_id CHAR(36)
)
BEGIN
    -- Validate that both required parameters are provided
    IF p_follower_id IS NULL OR p_followee_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'follower_id and followee_id are required.';
    END IF;

    -- Delete the specific follow relationship
    -- Both follower_id AND followee_id are required in WHERE clause to uniquely
    -- identify which relationship to remove
    DELETE FROM faculty_follows_faculty
    WHERE follower_id = p_follower_id
      AND followee_id = p_followee_id;

    -- Check if any rows were actually deleted
    -- ROW_COUNT() returns 0 if no matching record was found
    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No matching follow relationship to delete.';
    END IF;

    -- Return confirmation of what was deleted
    SELECT p_follower_id AS follower_id,
           p_followee_id AS followee_id,
           'deleted' AS action;
END $$

DELIMITER ;

