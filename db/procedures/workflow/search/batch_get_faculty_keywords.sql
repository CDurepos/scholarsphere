-- Written by Aidan Bell

DELIMITER $$

/**
 * Retrieves all keywords for a batch of faculty members in a single query.
 *
 * Keywords are combined from two sources:
 *   1. Direct research keywords (faculty_researches_keyword)
 *   2. Publication keywords (via publication_authored_by_faculty and 
 *      publication_explores_keyword)
 * 
 * @param p_faculty_ids  Comma-separated list of faculty UUIDs
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - keyword: Lowercase keyword name
 *   (Multiple rows per faculty member if they have multiple keywords)
 */
DROP PROCEDURE IF EXISTS batch_get_faculty_keywords$$
CREATE PROCEDURE batch_get_faculty_keywords(
    IN p_faculty_ids TEXT
)
BEGIN
    -- Create two temporary tables to hold parsed faculty IDs
    -- MySQL doesn't allow referencing the same temp table twice in one query,
    -- so we create two identical copies
    DROP TEMPORARY TABLE IF EXISTS temp_faculty_ids_1;
    DROP TEMPORARY TABLE IF EXISTS temp_faculty_ids_2;
    CREATE TEMPORARY TABLE temp_faculty_ids_1 (
        faculty_id CHAR(36) PRIMARY KEY
    );
    CREATE TEMPORARY TABLE temp_faculty_ids_2 (
        faculty_id CHAR(36) PRIMARY KEY
    );
    
    -- Parse the comma-separated faculty IDs and insert into both temp tables
    SET @ids = p_faculty_ids;
    SET @delimiter = ',';
    
    -- TODO: Make this a function
    WHILE CHAR_LENGTH(@ids) > 0 DO
        SET @id = TRIM(
            IF(
                LOCATE(@delimiter, @ids) > 0,
                SUBSTRING(@ids, 1, LOCATE(@delimiter, @ids) - 1),
                @ids
            )
        );
        
        IF CHAR_LENGTH(@id) > 0 THEN
            INSERT IGNORE INTO temp_faculty_ids_1 (faculty_id) VALUES (@id);
            INSERT IGNORE INTO temp_faculty_ids_2 (faculty_id) VALUES (@id);
        END IF;
        
        SET @ids = IF(
            LOCATE(@delimiter, @ids) > 0,
            SUBSTRING(@ids, LOCATE(@delimiter, @ids) + 1),
            ''
        );
    END WHILE;
    
    -- Retrieve all keywords for all faculty members from both sources
    SELECT faculty_id, keyword FROM (
        -- Keywords from direct research interests (uses temp table 1)
        SELECT 
            frk.faculty_id,
            LOWER(frk.name) AS keyword
        FROM faculty_researches_keyword AS frk
        INNER JOIN temp_faculty_ids_1 AS tfi
            ON frk.faculty_id = tfi.faculty_id
        
        UNION
        
        -- Keywords from publications authored by faculty (uses temp table 2)
        SELECT 
            pabf.faculty_id,
            LOWER(pek.name) AS keyword
        FROM publication_authored_by_faculty AS pabf
        INNER JOIN temp_faculty_ids_2 AS tfi
            ON pabf.faculty_id = tfi.faculty_id
        INNER JOIN publication_explores_keyword AS pek
            ON pabf.publication_id = pek.publication_id
    ) AS all_keywords;
    
    -- Clean up
    DROP TEMPORARY TABLE IF EXISTS temp_faculty_ids_1;
    DROP TEMPORARY TABLE IF EXISTS temp_faculty_ids_2;
END $$
DELIMITER ;
