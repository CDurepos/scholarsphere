-- Written by Clayton Durepos, Aidan Bell

DELIMITER $$

/**
 * Retrieves all faculty members that a given faculty member follows.
 * 
 * Returns all follow relationships where the specified faculty member
 * is the follower. This shows who the faculty member is following.
 * 
 * @param p_faculty_id  Required UUID of the faculty member (follower)
 * 
 * @returns Result set containing:
 *   - follower_id: UUID of the faculty member who is following
 *   - followee_id: UUID of the faculty member being followed
 *   (Multiple rows if the faculty member follows multiple people)
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 */
DROP PROCEDURE IF EXISTS read_faculty_follows_faculty_by_follower$$
CREATE PROCEDURE read_faculty_follows_faculty_by_follower (
    IN p_faculty_id CHAR(36)
)
BEGIN
    -- Validate that faculty_id is provided
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required.';
    END IF;

    -- Retrieve all follow relationships where the specified faculty member is the follower
    -- Returns multiple rows if the faculty member follows multiple people
    -- Each row represents one follow relationship
    SELECT follower_id, followee_id
    FROM faculty_follows_faculty
    WHERE follower_id = p_faculty_id;
END $$

DELIMITER ;
