from typing import Optional
from dataclasses import dataclass

@dataclass(slots=True)
class FacultyPhone:
    faculty_id: Optional[str] = None
    phone_num: Optional[str] = None