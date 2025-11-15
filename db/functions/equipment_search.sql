-- Search the equipment directory using keywords, availability and optional location filter

----------------------------
-- Parameters / Input
-- ----------------------------
SET @p_search1 = 'microscope';
SET @p_search2 = '';

SET @p_location = 'Portland';

-- ----------------------------
-- Execute search
-- ----------------------------
SELECT e.eq_id,
       e.name,
       e.description,
       e.availability,
       e.institution_id,
       i.name AS institution_name,
       i.city,
       i.zip
FROM equipment e
JOIN Institution i ON e.institution_id = i.institution_id
WHERE
    -- Availability filter
    e.availability LIKE '%available%'
    AND e.availability NOT LIKE '%not%'
    AND e.availability NOT LIKE '%un%'

    -- Keyword search: each word must appear in either name OR description
    AND (
        (e.name LIKE CONCAT('%', @p_search1, '%') OR e.description LIKE CONCAT('%', @p_search1, '%'))
    )
    AND (
        (e.name LIKE CONCAT('%', @p_search2, '%') OR e.description LIKE CONCAT('%', @p_search2, '%'))
    )

    -- Location filter: match city or zip
    AND (i.city LIKE CONCAT('%', @p_location, '%') OR i.zip LIKE CONCAT('%', @p_location, '%'));
