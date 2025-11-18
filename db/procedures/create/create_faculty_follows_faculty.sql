DELIMITER $$

/**
 * Creates a follow relationship between two faculty members.
 * 
 * Inserts a new follow relationship where one faculty member (follower)
 * follows another faculty member (followee). A faculty member cannot
 * follow themselves.
 * 
 * @param p_follower_id  Required UUID of the faculty member who is following
 * @param p_followee_id  Required UUID of the faculty member being followed
 * 
 * @returns Result set containing:
 *   - follower_id: UUID of the faculty member who is following
 *   - followee_id: UUID of the faculty member being followed
 *   - action: Status message ('inserted')
 * 
 * @throws SQLSTATE '45000' if follower_id or followee_id is NULL, if they are the same, or if either faculty doesn't exist
 */
CREATE PROCEDURE create_faculty_follows_faculty (
    IN p_follower_id CHAR(36),
    IN p_followee_id CHAR(36)
)
BEGIN
    DECLARE follower_exists INT;
    DECLARE followee_exists INT;

    -- Validate that both required parameters are provided
    IF p_follower_id IS NULL OR p_followee_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'follower_id and followee_id are required.';
    END IF;

    -- Prevent a faculty member from following themselves
    IF p_follower_id = p_followee_id THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A faculty member cannot follow themselves.';
    END IF;

    -- Verify that the follower exists
    SELECT COUNT(*) INTO follower_exists
    FROM faculty
    WHERE faculty_id = p_follower_id;

    IF follower_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'follower_id does not exist.';
    END IF;

    -- Verify that the followee exists
    SELECT COUNT(*) INTO followee_exists
    FROM faculty
    WHERE faculty_id = p_followee_id;

    IF followee_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'followee_id does not exist.';
    END IF;

    -- Insert the follow relationship
    -- The composite primary key ensures uniqueness (a faculty can only follow another faculty once)
    INSERT INTO faculty_follows_faculty (follower_id, followee_id)
    VALUES (p_follower_id, p_followee_id);

    -- Return confirmation with the inserted values
    SELECT p_follower_id AS follower_id,
           p_followee_id AS followee_id,
           'inserted' AS action;
END $$

DELIMITER ;

