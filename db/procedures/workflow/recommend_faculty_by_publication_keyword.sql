DELIMITER $$

/**
 * Generates faculty recommendations based on publication keywords.
 * 
 * This workflow procedure creates recommendation relationships between faculty
 * members where one faculty member has authored a publication that explores a
 * keyword, and another faculty member researches that same keyword. This helps
 * connect faculty who work in similar research areas through their publications.
 * 
 * The procedure inserts records into faculty_recommended_to_faculty for pairs
 * where:
 * - source_faculty_id: Faculty member who authored a publication with keyword x
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
DROP PROCEDURE IF EXISTS recommend_faculty_by_publication_keyword;
CREATE PROCEDURE recommend_faculty_by_publication_keyword()
BEGIN
    -- INSERT directional recommendations
    -- For each faculty member who has authored a publication with keyword x,
    -- recommend them to all faculty members who research keyword x
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id,
        target_faculty_id,
        match_score,
        created_at
    )
    SELECT DISTINCT
        paf.faculty_id      AS source_faculty_id,
        frk.faculty_id      AS target_faculty_id,
        NULL                AS match_score,
        CURDATE()           AS created_at
    FROM publication_authored_by_faculty AS paf
    JOIN publication_explores_keyword AS pek
        ON paf.publication_id = pek.publication_id
    JOIN faculty_researches_keyword AS frk
        ON pek.name = frk.name
    WHERE paf.faculty_id <> frk.faculty_id
    ON DUPLICATE KEY UPDATE
        match_score = VALUES(match_score),
        created_at = VALUES(created_at);

END $$

DELIMITER ;


DELIMITER ;
