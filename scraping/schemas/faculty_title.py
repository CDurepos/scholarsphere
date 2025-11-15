from typing import Optional
from dataclasses import dataclass

@dataclass(slots=True)
class FacultyTitle:
    faculty_id: Optional[str] = None
    title: Optional[str] = None