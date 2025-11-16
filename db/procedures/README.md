# ScholarSphere Procedures

This directory contains all `*.sql` scripts for procedures of the ScholarSphere application.

## Naming Conventions

### Script Styling

In each script, we utilize variable prefixes to clarify their role and to avoid naming collisions within the DB.

`v_` is used to signify a local variable.

`p_` is used to signify a parameter.

### File Names

The majority of procedures follow the naming convention...

`{operation}_{returned_or_affected_entity}_{property}.sql`

There are exceptions.

## Contributions
Each ScholarSphere team member has written the scripts for the associated procedures below...

Aidan: search_faculty.sql, update_faculty.sql, insert_into_faculty.sql, add_publication_for_faculty.sql, insert_into_publication_authored_by_faculty.sql

Clayton:

Abby:

Owen: