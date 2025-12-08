-- Written by Clayton Durepos

DELIMITER $$

/**
 * Retrieve recommendations for a faculty member.
 * Ordered by recommendation_type (ENUM order = priority).
 */
DROP PROCEDURE IF EXISTS read_recommendations_for_faculty$$
CREATE PROCEDURE read_recommendations_for_faculty(IN p_faculty_id CHAR(36))
BEGIN
    SELECT 
        f.faculty_id,
        f.first_name,
        f.last_name,
        f.biography,
        i.name AS institution_name,
        fd.department_name,
        r.recommendation_type,
        CASE r.recommendation_type
            WHEN 'shared_keyword'           THEN 'Similar research interests'
            WHEN 'keyword_to_publication'   THEN 'Published in your research area'
            WHEN 'publication_to_keyword'   THEN 'Researches your publication topics'
            WHEN 'keyword_to_grant'         THEN 'Has funding in your research area'
            WHEN 'grant_to_keyword'         THEN 'Researches your grant topics'
            WHEN 'grant_to_publication'     THEN 'Published on your grant topics'
            WHEN 'publication_to_grant'     THEN 'Has funding for your publication topics'
            WHEN 'shared_grant'             THEN 'Co-funded by same grant'
            WHEN 'shared_department'        THEN 'Same department'
            ELSE 'Potential collaborator'
        END AS recommendation_text
    FROM faculty_recommended_to_faculty r
    JOIN faculty f ON r.target_faculty_id = f.faculty_id
    LEFT JOIN faculty_works_at_institution fwi ON f.faculty_id = fwi.faculty_id AND fwi.end_date IS NULL
    LEFT JOIN institution i ON fwi.institution_id = i.institution_id
    LEFT JOIN (
        SELECT faculty_id, MIN(department_name) AS department_name
        FROM faculty_department
        GROUP BY faculty_id
    ) fd ON f.faculty_id = fd.faculty_id
    WHERE r.source_faculty_id = p_faculty_id
    ORDER BY r.recommendation_type ASC;
END $$

DELIMITER ;
