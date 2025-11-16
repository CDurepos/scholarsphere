-- For the MV attr table `grants_organization`
-- We utilize the primary key (name, grant_id)
-- For faster lookup by grants of an organization (`name` is implicitly indexed)

-- We then create an index on the grant_id to further optimize lookup for
-- organizations associated with a given grant
CREATE INDEX idx_grant_id ON grants_organization(grant_id)