-- Written by Clayton Durepos

-- SESSION SCHEMA
-- Stores hashed refresh tokens for long-term authentication sessions
CREATE TABLE IF NOT EXISTS session (
    -- Primary key
    session_id              CHAR(36)        PRIMARY KEY,
    
    -- Associated faculty member
    faculty_id           CHAR(36)         NOT NULL,
    
    -- Hash of the refresh token (SHA-256)
    -- Never store the raw token, only the hash
    token_hash           VARCHAR(64)      NOT NULL UNIQUE,
    
    -- When this session was created
    created_at           DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- When this token expires (typically 7-30 days)
    expires_at           DATETIME         NOT NULL,

    -- Whether this session has been revoked
    revoked              BOOLEAN          NOT NULL DEFAULT FALSE,
    
    -- Foreign key constraint
    FOREIGN KEY (faculty_id)
        REFERENCES faculty (faculty_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Index for lookups by faculty_id
    INDEX idx_faculty_id (faculty_id),
    
    -- Index for lookups by token_hash
    INDEX idx_token_hash (token_hash),
    
    -- Index for cleanup of expired tokens
    INDEX idx_expires_at (expires_at)
);

