DELIMITER $$

/**
 * Optimized procedure to retrieve complete faculty profile with all related data in a single query.
 * 
 * This procedure uses JOINs and GROUP_CONCAT to fetch all faculty information
 * (emails, phones, departments, titles, institution) in one optimized query,
 * significantly reducing database round trips compared to multiple separate queries.
 * 
 * Performance optimization:
 * - Single query instead of 6-7 separate queries
 * - Uses LEFT JOINs to avoid missing data
 * - GROUP_CONCAT aggregates multi-valued fields efficiently
 * - Subquery gets most recent institution relationship
 * 
 * @param p_faculty_id  Required UUID of the faculty member to retrieve
 * 
 * @returns Single row containing:
 *   - All faculty base fields (faculty_id, first_name, last_name, biography, etc.)
 *   - emails: Comma-separated list of email addresses (or NULL)
 *   - phones: Comma-separated list of phone numbers (or NULL)
 *   - departments: Comma-separated list of department names (or NULL)
 *   - titles: Comma-separated list of titles (or NULL)
 *   - institution_name: Name of the most recent institution (or NULL)
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 * 
 * Developer: Owen Leitzell
 * Created for query optimization assignment
 */
DROP PROCEDURE IF EXISTS read_faculty_complete_optimized$$
CREATE PROCEDURE read_faculty_complete_optimized (
    IN p_faculty_id CHAR(36)
)
BEGIN
    -- Validate that faculty_id is provided
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required';
    END IF;

    -- Single optimized query using JOINs and GROUP_CONCAT
    SELECT 
        -- Base faculty fields
        f.faculty_id,
        f.first_name,
        f.last_name,
        f.biography,
        f.orcid,
        f.google_scholar_url,
        f.research_gate_url,
        f.scraped_from,
        
        -- Aggregated multi-valued fields using GROUP_CONCAT
        -- DISTINCT removes duplicates, ORDER BY ensures consistent ordering
        GROUP_CONCAT(DISTINCT fe.email ORDER BY fe.email SEPARATOR ',') AS emails,
        GROUP_CONCAT(DISTINCT fp.phone_num ORDER BY fp.phone_num SEPARATOR ',') AS phones,
        GROUP_CONCAT(DISTINCT fd.department_name ORDER BY fd.department_name SEPARATOR ',') AS departments,
        GROUP_CONCAT(DISTINCT ft.title ORDER BY ft.title SEPARATOR ',') AS titles,
        
        -- Most recent institution name using subquery
        -- Gets the institution name for the most recent start_date
        (
            SELECT i.name
            FROM faculty_works_at_institution fwi
            INNER JOIN institution i ON fwi.institution_id = i.institution_id
            WHERE fwi.faculty_id = f.faculty_id
            ORDER BY fwi.start_date DESC, fwi.end_date IS NULL DESC
            LIMIT 1
        ) AS institution_name
        
    FROM faculty f
    
    -- LEFT JOINs ensure we get faculty even if they have no related records
    LEFT JOIN faculty_email fe ON f.faculty_id = fe.faculty_id
    LEFT JOIN faculty_phone fp ON f.faculty_id = fp.faculty_id
    LEFT JOIN faculty_department fd ON f.faculty_id = fd.faculty_id
    LEFT JOIN faculty_title ft ON f.faculty_id = ft.faculty_id
    
    WHERE f.faculty_id = p_faculty_id
    
    -- GROUP BY is required when using aggregate functions
    GROUP BY 
        f.faculty_id,
        f.first_name,
        f.last_name,
        f.biography,
        f.orcid,
        f.google_scholar_url,
        f.research_gate_url,
        f.scraped_from;
END $$

DELIMITER ;

