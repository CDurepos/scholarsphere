-- Written by Aidan Bell

DELIMITER $$

/**
 * Retrieves all follow relationships from the database.
 * 
 * Returns all records from the faculty_follows_faculty table, showing
 * all follow relationships between faculty members.
 * 
 * @returns Result set containing:
 *   - follower_id: UUID of the faculty member who is following
 *   - followee_id: UUID of the faculty member being followed
 * 
 * Results are ordered by follower_id, then followee_id.
 */
DROP PROCEDURE IF EXISTS read_faculty_follows_faculty$$
CREATE PROCEDURE read_faculty_follows_faculty()
BEGIN
    SELECT 
        follower_id,
        followee_id
    FROM faculty_follows_faculty
    ORDER BY follower_id, followee_id;
END $$

DELIMITER ;

