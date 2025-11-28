DELIMITER $$

/**
 * Generates faculty recommendations based on grant keywords.
 * 
 * This workflow procedure creates recommendation relationships between faculty
 * members where one faculty member has received a grant associated with a
 * keyword, and another faculty member researches that same keyword. This helps
 * connect faculty who work in similar research areas through their funding.
 * 
 * The procedure inserts records into faculty_recommended_to_faculty for pairs
 * where:
 * - source_faculty_id: Faculty member who received a grant with keyword x
 * - target_faculty_id: Faculty member who researches keyword x
 * 
 * Recommendations are directional (source -> target).
 * 
 * @returns No result set. Use read procedures to view the generated recommendations.
 * 
 * Note: The primary key constraint on faculty_recommended_to_faculty prevents
 * duplicate recommendations. Running this multiple times will update existing
 * records rather than creating duplicates.
 */
DROP PROCEDURE IF EXISTS recommend_faculty_by_grant_keyword;
CREATE PROCEDURE recommend_faculty_by_grant_keyword()
BEGIN
    -- INSERT directional recommendations
    -- For each faculty member who has received a grant with keyword x,
    -- recommend them to all faculty members who research keyword x
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id,
        target_faculty_id,
        match_score,
        created_at
    )
    SELECT DISTINCT
        ggf.faculty_id      AS source_faculty_id,
        frk.faculty_id      AS target_faculty_id,
        NULL                AS match_score,
        CURDATE()           AS created_at
    FROM grants_granted_to_faculty AS ggf
    JOIN grants_for_keyword AS gfk
        ON ggf.grant_id = gfk.grant_id
    JOIN faculty_researches_keyword AS frk
        ON gfk.name = frk.name
    WHERE ggf.faculty_id <> frk.faculty_id
    ON DUPLICATE KEY UPDATE
        match_score = VALUES(match_score),
        created_at = VALUES(created_at);

END $$

DELIMITER ;
