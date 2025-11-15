from typing import Optional
from dataclasses import dataclass

@dataclass(slots=True)
class FacultyDepartment:
    faculty_id: Optional[str] = None
    department_name: Optional[str] = None