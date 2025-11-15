from typing import Optional
from dataclasses import dataclass

@dataclass(slots=True)
class FacultyEmail:
    faculty_id: Optional[str] = None
    email: Optional[str] = None