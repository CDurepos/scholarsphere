-- Entities
SOURCE schema/faculty.sql
SOURCE schema/credentials.sql
SOURCE schema/institution.sql 
SOURCE schema/equipment.sql
SOURCE schema/grants.sql
SOURCE schema/publication.sql

-- Faculty MV Attr
SOURCE schema/faculty_email.sql
SOURCE schema/faculty_phone.sql
SOURCE schema/faculty_department.sql
SOURCE schema/faculty_title.sql

-- Grant MV Attr
SOURCE schema/grants_organization.sql

-- Faculty Relationship Tables
SOURCE schema/faculty_follows_faculty.sql
SOURCE schema/faculty_recommended_to_faculty.sql
SOURCE schema/faculty_works_at_institution.sql
SOURCE schema/faculty_researches_keyword.sql

-- Grant Relationship Tables
SOURCE schema/grants_for_keyword.sql
SOURCE schema/grants_granted_to_faculty.sql
SOURCE schema/grants_provided_by_organization.sql

-- Publication Relationship Tables
SOURCE schema/publication_authored_by_faculty.sql
SOURCE schema/publication_explores_keyword.sql
