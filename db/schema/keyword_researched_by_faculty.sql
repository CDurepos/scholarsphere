CREATE TABLE keyword_researched_by_faculty (
    name VARCHAR(64) NOT NULL,
    user_id CHAR(36) NOT NULL,

    PRIMARY KEY (name, user_id),

    FOREIGN KEY (name)
        REFERENCES keywords(name)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (user_id)
        REFERENCES user(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
