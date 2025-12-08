-- Written by Abby Pitcairn

-- Represents the many-to-many relation between Faculty and Institution
CREATE TABLE faculty_works_at_institution (
    faculty_id      CHAR(36)    NOT NULL,
    institution_id  CHAR(36)    NOT NULL,

    start_date      DATE        NOT NULL,

    -- Nullable end date
    -- Users may currently work at an institution
    end_date        DATE,

    PRIMARY KEY (faculty_id, institution_id),

    FOREIGN KEY (faculty_id)
        REFERENCES faculty(faculty_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (institution_id)
        REFERENCES institution(institution_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    -- Index on institution_id for joins from institution side
    INDEX idx_fwai_institution_id (institution_id)
);