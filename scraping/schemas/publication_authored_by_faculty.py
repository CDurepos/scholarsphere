from typing import Optional
from dataclasses import dataclass

# For the join table

@dataclass(slots=True)
class PublicationAuthoredByFaculty:
    faculty_id: Optional[str] = None
    publication_id: Optional[str] = None