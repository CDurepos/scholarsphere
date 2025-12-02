# ScholarSphere Procedures

This directory contains all `*.sql` scripts for procedures of the ScholarSphere application.

## Naming Conventions

### Script Styling

In each script, we utilize variable prefixes to clarify their role and to avoid naming collisions within the DB.

`v_` is used to signify a local variable.

`p_` is used to signify a parameter.

### File Names

The majority of procedures follow the naming convention...

`{create | read | update | delete}_{table_name}.sql`

Read operations follow the naming convention...

`read_{table-name}_by_{filter}.sql`

For example, `read_faculty-institution_by_faculty.sql` returns a table containing the `institution_id`s corresponding to the `institution` entities that a `faculty` entity works at. In contrast, `read_faculty-institution_by_institution.sql` returns a table containing the `faculty_id`s of the `faculty` entities that work at an institution.

## Contributions
Each ScholarSphere team member has written the scripts for the associated procedures below...

Aidan: search_faculty.sql, add_publication_for_faculty.sql, create_publication_authored_by_faculty.sql, create_faculty.sql, update_faculty.sql, read_faculty.sql, delete_faculty.sql, create_faculty_title.sql, update_faculty_title.sql, read_faculty_title.sql, delete_faculty_title.sql, create_faculty_phone.sql, update_faculty_phone.sql, read_faculty_phone.sql, delete_faculty_phone.sql, create_faculty_email.sql, update_faculty_email.sql, read_faculty_email.sql, delete_faculty_email.sql, create_faculty_department.sql, update_faculty_department.sql, read_faculty_department.sql, delete_faculty_department.sql

Clayton:

Abby:

Owen: