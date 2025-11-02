from typing import Optional
from dataclasses import dataclass

@dataclass(slots=True)
class Faculty:
    faculty_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone_num: Optional[str] = None
    biography: Optional[str] = None
    collab_interest: Optional[str] = None
    orcid: Optional[str] = None
    google_scholar_url: Optional[str] = None
    research_gate_url: Optional[str] = None
    scraped_from: Optional[str] = None