-- GRANT ORG SCHEMA
-- Not all organizations that fund a grant may be an educational or research institution
-- We store the names of funding org's as a MV attribute of grants 
-- Rather than creating an instance of institution for every funding agency
CREATE TABLE grants_organization (
    grant_id       CHAR(36)     NOT NULL,
    name           VARCHAR(255) NOT NULL,

    PRIMARY KEY (grant_id, name),

    FOREIGN KEY (grant_id)
        REFERENCES grants (grant_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
