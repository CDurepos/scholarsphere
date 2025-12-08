DELIMITER $$

/**
 * Searches for faculty members based on keyword overlap.
 * 
 * This procedure finds faculty whose research keywords (from faculty_researches_keyword)
 * or publication keywords (from publication_explores_keyword via publication_authored_by_faculty)
 * match the provided comma-separated list of keywords.
 * 
 * Faculty are ranked by the number of matching keywords and only those with
 * more than 1 keyword overlap are returned.
 * 
 * @param p_keywords  Comma-separated list of keywords to search for (case-insensitive)
 * 
 * @returns Result set containing:
 *   - faculty_id: Unique identifier for the faculty member
 *   - first_name: Faculty member's first name
 *   - last_name: Faculty member's last name
 *   - department_name: Department name (if associated)
 *   - institution_name: Institution name (if associated)
 *   - keyword_overlap: Number of matching keywords
 *   Ordered by keyword_overlap descending
 */
DROP PROCEDURE IF EXISTS search_faculty_by_keyword$$
CREATE PROCEDURE search_faculty_by_keyword(
    IN p_keywords TEXT
)
BEGIN
    -- Create temporary tables to hold the parsed keywords
    -- MySQL doesn't allow referencing the same temp table twice in one query,
    -- so we create two identical copies
    DROP TEMPORARY TABLE IF EXISTS temp_search_keywords_1;
    DROP TEMPORARY TABLE IF EXISTS temp_search_keywords_2;
    CREATE TEMPORARY TABLE temp_search_keywords_1 (
        keyword VARCHAR(64) PRIMARY KEY
    );
    CREATE TEMPORARY TABLE temp_search_keywords_2 (
        keyword VARCHAR(64) PRIMARY KEY
    );
    
    -- Parse the comma-separated keywords and insert into temp table
    -- Using a loop to split the string
    SET @keywords = p_keywords;
    SET @delimiter = ',';
    
    WHILE CHAR_LENGTH(@keywords) > 0 DO
        SET @keyword = TRIM(LOWER(
            IF(
                LOCATE(@delimiter, @keywords) > 0,
                SUBSTRING(@keywords, 1, LOCATE(@delimiter, @keywords) - 1),
                @keywords
            )
        ));
        
        IF CHAR_LENGTH(@keyword) > 0 THEN
            INSERT IGNORE INTO temp_search_keywords_1 (keyword) VALUES (@keyword);
            INSERT IGNORE INTO temp_search_keywords_2 (keyword) VALUES (@keyword);
        END IF;
        
        SET @keywords = IF(
            LOCATE(@delimiter, @keywords) > 0,
            SUBSTRING(@keywords, LOCATE(@delimiter, @keywords) + 1),
            ''
        );
    END WHILE;
    
    -- Find faculty with keyword overlap from both sources
    SELECT 
        f.faculty_id,
        f.first_name,
        f.last_name,
        d.department_name,
        i.name AS institution_name,
        COUNT(DISTINCT matched_keywords.keyword) AS keyword_overlap
    FROM faculty AS f
    -- Join to get all keywords associated with this faculty (from both sources)
    INNER JOIN (
        -- Keywords from faculty_researches_keyword (uses temp table 1)
        SELECT 
            frk.faculty_id,
            LOWER(frk.name) AS keyword
        FROM faculty_researches_keyword AS frk
        INNER JOIN temp_search_keywords_1 AS tsk
            ON LOWER(frk.name) = tsk.keyword
        
        UNION
        
        -- Keywords from publications authored by faculty (uses temp table 2)
        SELECT 
            pabf.faculty_id,
            LOWER(pek.name) AS keyword
        FROM publication_authored_by_faculty AS pabf
        INNER JOIN publication_explores_keyword AS pek
            ON pabf.publication_id = pek.publication_id
        INNER JOIN temp_search_keywords_2 AS tsk
            ON LOWER(pek.name) = tsk.keyword
    ) AS matched_keywords
        ON f.faculty_id = matched_keywords.faculty_id
    -- LEFT JOIN for department info
    LEFT JOIN faculty_department AS d
        ON f.faculty_id = d.faculty_id
    -- LEFT JOIN for institution info
    LEFT JOIN faculty_works_at_institution AS w
        ON f.faculty_id = w.faculty_id
    LEFT JOIN institution AS i
        ON w.institution_id = i.institution_id
    GROUP BY 
        f.faculty_id,
        f.first_name,
        f.last_name,
        d.department_name,
        i.name
    HAVING COUNT(DISTINCT matched_keywords.keyword) > 0
    ORDER BY keyword_overlap DESC;
    
    -- Clean up
    DROP TEMPORARY TABLE IF EXISTS temp_search_keywords_1;
    DROP TEMPORARY TABLE IF EXISTS temp_search_keywords_2;
END $$
DELIMITER ;

