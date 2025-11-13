-- Represents the many-to-many relation between Faculty and Institution
CREATE TABLE Works_at (
    faculty_id UUID NOT NULL,
    institution_id UUID NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,

    PRIMARY KEY (faculty_id, institution_id, start_date),

    FOREIGN KEY (faculty_id)
        REFERENCES Faculty(faculty_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (institution_id)
        REFERENCES Institution(institution_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);