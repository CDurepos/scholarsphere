DELIMITER $$

CREATE PROCEDURE search_faculty(
    IN p_first_name    VARCHAR(128),
    IN p_last_name     VARCHAR(128),
    IN p_department    VARCHAR(128),
    IN p_institution   VARCHAR(255)
)
BEGIN
    SELECT DISTINCT
        f.faculty_id,
        f.first_name,
        f.last_name,
        d.department_name,
        i.name AS institution_name
    FROM faculty AS f
    LEFT JOIN faculty_department AS d
        ON f.faculty_id = d.faculty_id
    LEFT JOIN faculty_works_at_institution AS w
        ON f.faculty_id = w.faculty_id
    LEFT JOIN institution AS i
        ON w.institution_id = i.institution_id
    WHERE
        (p_first_name  IS NULL OR f.first_name      LIKE CONCAT('%', p_first_name, '%'))
        AND (p_last_name IS NULL OR f.last_name      LIKE CONCAT('%', p_last_name, '%'))
        AND (p_department IS NULL OR d.department_name LIKE CONCAT('%', p_department, '%'))
        AND (p_institution IS NULL OR i.name            LIKE CONCAT('%', p_institution, '%'));
END $$