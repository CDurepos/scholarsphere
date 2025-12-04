DELIMITER $$

/**
 * Generates faculty recommendations based on shared institutions.
 * 
 * This workflow procedure creates recommendation relationships between faculty
 * members who work or have worked at the same institution. This helps connect
 * faculty who are or were colleagues at the same institution.
 * 
 * The procedure inserts records into faculty_recommended_to_faculty for pairs
 * where both faculty members have a relationship with the same institution
 * (regardless of whether they currently work there or worked there in the past):
 * - source_faculty_id: One faculty member who works/worked at institution x
 * - target_faculty_id: Another faculty member who also works/worked at institution x
 * 
 * Recommendations are directional (source -> target).
 * 
 * @returns No result set. Use read procedures to view the generated recommendations.
 * 
 * Note: The primary key constraint on faculty_recommended_to_faculty prevents
 * duplicate recommendations. Running this multiple times will update existing
 * records rather than creating duplicates.
 */
DROP PROCEDURE IF EXISTS recommend_faculty_by_institution$$
CREATE PROCEDURE recommend_faculty_by_institution()
BEGIN
    -- INSERT directional recommendations
    -- For each pair of faculty members who work or have worked at the same institution,
    -- create a recommendation from one to the other
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id,
        target_faculty_id,
        match_score,
        created_at
    )
    SELECT DISTINCT
        fwi1.faculty_id     AS source_faculty_id,
        fwi2.faculty_id     AS target_faculty_id,
        NULL                AS match_score,
        CURDATE()           AS created_at
    FROM faculty_works_at_institution AS fwi1
    JOIN faculty_works_at_institution AS fwi2
        ON fwi1.institution_id = fwi2.institution_id
    WHERE fwi1.faculty_id <> fwi2.faculty_id
    ON DUPLICATE KEY UPDATE
        match_score = VALUES(match_score),
        created_at = VALUES(created_at);

END $$

DELIMITER ;


DELIMITER ;
