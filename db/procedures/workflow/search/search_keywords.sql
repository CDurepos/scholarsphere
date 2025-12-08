DELIMITER $$

/**
 * Search keywords by prefix for autocomplete functionality.
 * 
 * Returns keywords that start with the given search term, ordered by name.
 * Used for autocomplete suggestions when users add research interests.
 * 
 * @param p_search_term  Search prefix (min 2 characters recommended)
 * @param p_limit        Maximum number of results to return (default 10)
 * 
 * @returns Result set containing:
 *   - name: Keyword name (max 64 characters)
 */
DROP PROCEDURE IF EXISTS search_keywords$$
CREATE PROCEDURE search_keywords(
    IN p_search_term VARCHAR(64),
    IN p_limit INT
)
BEGIN
    DECLARE v_limit INT DEFAULT 10;
    
    IF p_limit IS NOT NULL AND p_limit > 0 THEN
        SET v_limit = p_limit;
    END IF;
    
    SELECT DISTINCT name
    FROM keyword
    WHERE LOWER(name) LIKE CONCAT(LOWER(TRIM(p_search_term)), '%')
    ORDER BY name ASC
    LIMIT v_limit;
END $$

DELIMITER ;

