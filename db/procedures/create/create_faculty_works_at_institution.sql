DELIMITER $$

/**
 * Creates a new faculty-institution relationship record in the database.
 * 
 * Inserts a new faculty_works_at_institution record establishing a relationship
 * between a faculty member and an institution. This represents an employment
 * period, with a start date (required) and optional end date. The composite
 * primary key (faculty_id, institution_id, start_date) must be unique.
 * 
 * @param p_faculty_id      Required UUID of the faculty member
 *                          Must reference an existing faculty record
 * @param p_institution_id  Required UUID of the institution
 *                          Must reference an existing institution record
 * @param p_start_date      Required start date of the employment relationship
 *                          Part of the composite primary key
 * @param p_end_date        Optional end date of the employment relationship
 *                          NULL indicates the faculty member currently works at the institution
 * 
 * @returns No result set. Use read_faculty_works_at_institution to verify the insert.
 * 
 * @throws SQLSTATE '23000' if faculty_id doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if institution_id doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if a record with the same (faculty_id, institution_id, start_date) already exists
 */
DROP PROCEDURE IF EXISTS create_faculty_works_at_institution$$
CREATE PROCEDURE create_faculty_works_at_institution(
    IN p_faculty_id CHAR(36),
    IN p_institution_id CHAR(36),
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    INSERT INTO faculty_works_at_institution(
        faculty_id, 
        institution_id, 
        start_date, 
        end_date
    ) VALUES (
        p_faculty_id, 
        p_institution_id, 
        p_start_date, 
        p_end_date
    );
END $$

DELIMITER ;