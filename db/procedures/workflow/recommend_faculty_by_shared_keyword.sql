DELIMITER $$

/**
 * Generates faculty recommendations based on shared research keywords.
 * 
 * This workflow procedure creates recommendation relationships between faculty
 * members who both research the same keyword. This helps connect faculty with
 * overlapping research interests.
 * 
 * The procedure inserts records into faculty_recommended_to_faculty for pairs
 * where both faculty members research the same keyword:
 * - source_faculty_id: One faculty member who researches keyword x
 * - target_faculty_id: Another faculty member who also researches keyword x
 * 
 * Recommendations are directional (source -> target), so each pair will have
 * two recommendations (A->B and B->A) if both directions are desired.
 * 
 * @returns No result set. Use read procedures to view the generated recommendations.
 * 
 * Note: The primary key constraint on faculty_recommended_to_faculty prevents
 * duplicate recommendations. Running this multiple times will update existing
 * records rather than creating duplicates.
 */
DROP PROCEDURE IF EXISTS recommend_faculty_by_shared_keyword;
CREATE PROCEDURE recommend_faculty_by_shared_keyword()
BEGIN
    -- INSERT directional recommendations
    -- For each pair of faculty members who both research the same keyword,
    -- create a recommendation from one to the other
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id,
        target_faculty_id,
        match_score,
        created_at
    )
    SELECT DISTINCT
        frk1.faculty_id     AS source_faculty_id,
        frk2.faculty_id     AS target_faculty_id,
        NULL                AS match_score,
        CURDATE()           AS created_at
    FROM faculty_researches_keyword AS frk1
    JOIN faculty_researches_keyword AS frk2
        ON frk1.name = frk2.name
    WHERE frk1.faculty_id <> frk2.faculty_id
    ON DUPLICATE KEY UPDATE
        match_score = VALUES(match_score),
        created_at = VALUES(created_at);

END $$

DELIMITER ;

