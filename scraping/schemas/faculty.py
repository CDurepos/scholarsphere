from typing import Optional, List, Union
from dataclasses import dataclass

@dataclass(slots=True)
class Faculty:
    faculty_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[Union[List[str], str]] = None
    department: Optional[Union[List[str], str]] = None
    email: Optional[Union[List[str], str]] = None
    phone_num: Optional[Union[List[str], str]] = None
    biography: Optional[str] = None
    research_interest: Optional[str] = None
    orcid: Optional[str] = None
    google_scholar_url: Optional[str] = None
    research_gate_url: Optional[str] = None
    scraped_from: Optional[str] = None