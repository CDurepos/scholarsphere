DELIMITER $$

/**
 * Retrieves all faculty members who follow a given faculty member.
 * 
 * Returns all follow relationships where the specified faculty member
 * is the followee. This shows who is following the faculty member.
 * 
 * @param p_faculty_id  Required UUID of the faculty member (followee)
 * 
 * @returns Result set containing:
 *   - follower_id: UUID of the faculty member who is following
 *   - followee_id: UUID of the faculty member being followed
 *   (Multiple rows if multiple people follow the faculty member)
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 */
DROP PROCEDURE IF EXISTS read_faculty_follows_faculty_by_followee$$
CREATE PROCEDURE read_faculty_follows_faculty_by_followee (
    IN p_faculty_id CHAR(36)
)
BEGIN
    -- Validate that faculty_id is provided
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required.';
    END IF;

    -- Retrieve all follow relationships where the specified faculty member is the followee
    -- Returns multiple rows if multiple people follow the faculty member
    -- Each row represents one follow relationship
    SELECT follower_id, followee_id
    FROM faculty_follows_faculty
    WHERE followee_id = p_faculty_id;
END $$
DELIMITER ;

