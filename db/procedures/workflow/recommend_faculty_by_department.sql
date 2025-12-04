DELIMITER $$

/**
 * Generates faculty recommendations based on shared departments.
 * 
 * This workflow procedure creates recommendation relationships between faculty
 * members who work in the same department. This helps connect faculty who are
 * colleagues in the same academic department, regardless of which institution
 * they work at.
 * 
 * The procedure inserts records into faculty_recommended_to_faculty for pairs
 * where both faculty members belong to the same department:
 * - source_faculty_id: One faculty member in department x
 * - target_faculty_id: Another faculty member also in department x
 * 
 * Recommendations are directional (source -> target). This connects faculty
 * across different institutions if they share the same department name.
 * 
 * @returns No result set. Use read procedures to view the generated recommendations.
 * 
 * Note: The primary key constraint on faculty_recommended_to_faculty prevents
 * duplicate recommendations. Running this multiple times will update existing
 * records rather than creating duplicates.
 */
DROP PROCEDURE IF EXISTS recommend_faculty_by_department$$
CREATE PROCEDURE recommend_faculty_by_department()
BEGIN
    -- INSERT directional recommendations
    -- For each pair of faculty members who belong to the same department,
    -- create a recommendation from one to the other
    -- Note: This connects faculty across different institutions if they share
    -- the same department name
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id,
        target_faculty_id,
        match_score,
        created_at
    )
    SELECT DISTINCT
        fd1.faculty_id      AS source_faculty_id,
        fd2.faculty_id      AS target_faculty_id,
        NULL                AS match_score,
        CURDATE()           AS created_at
    FROM faculty_department AS fd1
    JOIN faculty_department AS fd2
        ON fd1.department_name = fd2.department_name
    WHERE fd1.faculty_id <> fd2.faculty_id
    ON DUPLICATE KEY UPDATE
        match_score = VALUES(match_score),
        created_at = VALUES(created_at);

END $$

DELIMITER ;
