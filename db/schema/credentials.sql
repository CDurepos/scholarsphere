CREATE TABLE credentials (
    faculty_id  CHAR(36) NOT NULL,
    username    VARCHAR(255) NOT NULL UNIQUE,
    pw_hash     VARCHAR(255) NOT NULL,
    pw_salt     VARCHAR(255) NOT NULL,
    last_login  DATETIME NULL,

    PRIMARY KEY (faculty_id),

    FOREIGN KEY (faculty_id)
        REFERENCES faculty (faculty_id)
);
