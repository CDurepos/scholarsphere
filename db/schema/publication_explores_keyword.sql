CREATE TABLE publication_explores_keyword (
    publication_id  CHAR(36)    NOT NULL,
    name            VARCHAR(64) NOT NULL,

    PRIMARY KEY (publication_id, name),

    FOREIGN KEY (publication_id)
        REFERENCES publication(publication_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    FOREIGN KEY (name)
        REFERENCES keyword(name)
        ON DELETE CASCADE
        ON UPDATE CASCADE

);
