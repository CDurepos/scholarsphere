-- For the MV attr table `grants_organization`
-- We utilize the primary key (name, grant_id)
CREATE INDEX idx_grant_id ON grants_organization(grant_id)