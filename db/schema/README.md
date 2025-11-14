# ScholarSphere Schema

This directory contains the blueprint for each table required by and utilized in the ScholarSphere application.

## Naming Convention

All entity table schema are stored in a file corresponding to the name of the entity they outline.

Join table, or relationship, schema are stored in files that follow the following naming convention: 
`{entity1}_{relationship}_{entity2}.sql`

Tables for multivalued attributes of an entity are stored in files that follow the following naming convention:
`{entity}_{property}.sql`

Relationship names themselves follow snake casing, i.e. all lowercase letters with underscores substituted for spaces.

## Team Contributions

1. Clayton: [
    `grants.sql`, `grants_organization.sql`, `grants_granted_to_faculty.sql`, `grants_provided_by_instutition.sql`, `credentials.sql`
    ]

2. Owen:    [
    `publications.sql`, `publication_authored_by_faculty.sql`, `publication_explores_keyword.sql`, `keywords.sql`, `keyword_researched_by_faculty.sql`
    ]

3. Abby:    [
    `institution.sql`, `faculty_works_at_institution.sql`, `equipment.sql`
]

4. Aidan:   [
    `faculty.sql`, `faculty_phone.sql`, `faculty_email.sql`, `faculty_title.sql`, `faculty_follows_faculty.sql`, `faculty_recommended_to_faculty.sql`,
    `faculty_department.sql`
]