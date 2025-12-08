DELIMITER $$

/**
 * Normalize department names for comparison.
 * Handles variations like:
 *   "Department of History" → "history"
 *   "History Department" → "history"
 *   "Dept. of Computer Science" → "computer science"
 *   "School of Business Administration" → "business administration"
 *   "English & Literature" → "english literature"
 *   "Arts and Sciences" → "arts sciences"
 */
DROP FUNCTION IF EXISTS normalize_department_name$$
CREATE FUNCTION normalize_department_name(dept_name VARCHAR(255))
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    DECLARE normalized VARCHAR(255);
    
    SET normalized = LOWER(TRIM(dept_name));
    
    -- Normalize punctuation and connectors
    SET normalized = REPLACE(normalized, '&', ' and ');
    SET normalized = REPLACE(normalized, ',', ' ');
    SET normalized = REPLACE(normalized, '.', ' ');
    SET normalized = REPLACE(normalized, '/', ' ');
    SET normalized = REPLACE(normalized, '-', ' ');
    SET normalized = REPLACE(normalized, '  ', ' ');
    SET normalized = TRIM(normalized);
    
    -- Remove common prefixes
    SET normalized = TRIM(LEADING 'the ' FROM normalized);
    SET normalized = TRIM(LEADING 'department of ' FROM normalized);
    SET normalized = TRIM(LEADING 'dept of ' FROM normalized);
    SET normalized = TRIM(LEADING 'dept ' FROM normalized);
    SET normalized = TRIM(LEADING 'school of ' FROM normalized);
    SET normalized = TRIM(LEADING 'college of ' FROM normalized);
    SET normalized = TRIM(LEADING 'division of ' FROM normalized);
    SET normalized = TRIM(LEADING 'program in ' FROM normalized);
    SET normalized = TRIM(LEADING 'program of ' FROM normalized);
    SET normalized = TRIM(LEADING 'center for ' FROM normalized);
    SET normalized = TRIM(LEADING 'centre for ' FROM normalized);
    SET normalized = TRIM(LEADING 'institute of ' FROM normalized);
    SET normalized = TRIM(LEADING 'institute for ' FROM normalized);
    SET normalized = TRIM(LEADING 'faculty of ' FROM normalized);
    SET normalized = TRIM(LEADING 'office of ' FROM normalized);
    
    -- Remove common suffixes
    SET normalized = TRIM(TRAILING ' department' FROM normalized);
    SET normalized = TRIM(TRAILING ' dept' FROM normalized);
    SET normalized = TRIM(TRAILING ' program' FROM normalized);
    SET normalized = TRIM(TRAILING ' programs' FROM normalized);
    SET normalized = TRIM(TRAILING ' studies' FROM normalized);
    SET normalized = TRIM(TRAILING ' school' FROM normalized);
    SET normalized = TRIM(TRAILING ' division' FROM normalized);
    SET normalized = TRIM(TRAILING ' college' FROM normalized);
    SET normalized = TRIM(TRAILING ' center' FROM normalized);
    SET normalized = TRIM(TRAILING ' centre' FROM normalized);
    SET normalized = TRIM(TRAILING ' institute' FROM normalized);
    SET normalized = TRIM(TRAILING ' faculty' FROM normalized);
    SET normalized = TRIM(TRAILING ' office' FROM normalized);
    
    -- Remove filler words
    SET normalized = REPLACE(normalized, ' and ', ' ');
    SET normalized = REPLACE(normalized, ' of ', ' ');
    SET normalized = REPLACE(normalized, ' the ', ' ');
    SET normalized = REPLACE(normalized, ' in ', ' ');
    SET normalized = REPLACE(normalized, ' for ', ' ');
    
    -- Normalize common abbreviations
    SET normalized = REPLACE(normalized, 'comp sci', 'computer science');
    SET normalized = REPLACE(normalized, 'cs ', 'computer science ');
    SET normalized = REPLACE(normalized, 'bio ', 'biology ');
    SET normalized = REPLACE(normalized, 'chem ', 'chemistry ');
    SET normalized = REPLACE(normalized, 'phys ', 'physics ');
    SET normalized = REPLACE(normalized, 'math ', 'mathematics ');
    SET normalized = REPLACE(normalized, 'maths ', 'mathematics ');
    SET normalized = REPLACE(normalized, 'psych ', 'psychology ');
    SET normalized = REPLACE(normalized, 'poli sci', 'political science');
    SET normalized = REPLACE(normalized, 'polisci', 'political science');
    SET normalized = REPLACE(normalized, 'econ ', 'economics ');
    SET normalized = REPLACE(normalized, 'comm ', 'communication ');
    SET normalized = REPLACE(normalized, 'comms ', 'communication ');
    SET normalized = REPLACE(normalized, 'env ', 'environmental ');
    SET normalized = REPLACE(normalized, 'mgmt', 'management');
    SET normalized = REPLACE(normalized, 'admin', 'administration');
    SET normalized = REPLACE(normalized, 'eng ', 'engineering ');
    SET normalized = REPLACE(normalized, 'engr ', 'engineering ');
    SET normalized = REPLACE(normalized, 'lit ', 'literature ');
    SET normalized = REPLACE(normalized, 'govt ', 'government ');
    SET normalized = REPLACE(normalized, 'govt', 'government');
    
    -- Handle plural/singular variations
    SET normalized = REPLACE(normalized, 'sciences', 'science');
    SET normalized = REPLACE(normalized, 'languages', 'language');
    SET normalized = REPLACE(normalized, 'communications', 'communication');
    SET normalized = REPLACE(normalized, 'arts', 'art');
    
    -- Clean up multiple spaces
    WHILE LOCATE('  ', normalized) > 0 DO
        SET normalized = REPLACE(normalized, '  ', ' ');
    END WHILE;
    
    RETURN TRIM(normalized);
END $$

DELIMITER ;
