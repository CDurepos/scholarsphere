-- Written by Aidan Bell

CREATE TABLE IF NOT EXISTS faculty_phone (
    faculty_id  CHAR(36)        NOT NULL,

    -- (Estimated) Max phone number length is 15 digits
    -- 32 Char max for extra space
    phone_num   VARCHAR(32),

    PRIMARY KEY (faculty_id, phone_num),

    FOREIGN KEY (faculty_id) 
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE
);