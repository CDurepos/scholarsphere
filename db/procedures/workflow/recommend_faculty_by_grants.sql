DELIMITER $$

/**
 * Generates faculty recommendations based on shared grants.
 * 
 * This workflow procedure creates recommendation relationships between faculty
 * members who have received the same grants. For each pair of faculty members
 * who share at least one grant, a recommendation is created from one faculty
 * member to the other. This helps identify faculty with similar funding
 * interests and research areas.
 * 
 * The procedure inserts records into faculty_recommended_to_faculty for all
 * pairs of faculty members who have grants in common. Recommendations are
 * directional (source_faculty_id -> target_faculty_id).
 * 
 * @returns No result set. Use read procedures to view the generated recommendations.
 * 
 * Note: This procedure may create duplicate recommendations if run multiple times.
 * Consider clearing existing recommendations before running, or use a unique
 * constraint to prevent duplicates.
 */
DROP PROCEDURE IF EXISTS recommend_faculty_by_grants;
CREATE PROCEDURE recommend_faculty_by_grants()
BEGIN
    -- INSERT directional recommendations
    -- For each pair of faculty members who share a grant, create a recommendation
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id,
        target_faculty_id,
        match_score,
        created_at
    )
    SELECT DISTINCT
        g1.faculty_id      AS source_faculty_id,
        g2.faculty_id      AS target_faculty_id,
        NULL               AS match_score,
        CURDATE()          AS created_at
    FROM grants_granted_to_faculty AS g1
    JOIN grants_granted_to_faculty AS g2
         ON g1.grant_id = g2.grant_id
    WHERE g1.faculty_id <> g2.faculty_id
    ON DUPLICATE KEY UPDATE
        match_score = VALUES(match_score),
        created_at = VALUES(created_at);

END $$

DELIMITER ;