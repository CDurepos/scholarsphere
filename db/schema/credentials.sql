-- USER CREDENTIALS SCHEMA
CREATE TABLE IF NOT EXISTS credentials (
    -- ASSOCIATED USER ID
    faculty_id        CHAR(36)      NOT NULL UNIQUE,

    username          VARCHAR(255)  NOT NULL UNIQUE,

    -- HASH OF PW
    password_hash     VARCHAR(255)  NOT NULL,

    -- PW SALT FOR SECURITY
    password_salt     VARCHAR(255)  NOT NULL,

    -- TRACK LAST LOGIN
    last_login        DATETIME      NULL,

    PRIMARY KEY (faculty_id),

    FOREIGN KEY (faculty_id)
        REFERENCES faculty (faculty_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
