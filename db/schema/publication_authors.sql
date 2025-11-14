CREATE TABLE publication_authors (
    user_id CHAR(36) NOT NULL,
    publication_id CHAR(36) NOT NULL,

    PRIMARY KEY (user_id, publication_id),

    FOREIGN KEY (user_id)
        REFERENCES user(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    FOREIGN KEY (publication_id)
        REFERENCES Publication(publication_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE

);
