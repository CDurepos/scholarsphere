from typing import Optional
from dataclasses import dataclass

@dataclass(slots=True)
class Institution:
    institution_id: Optional[str] = None
    name: Optional[str] = None
    website_url: Optional[str] = None
    institution_type: Optional[str] = None
    street_addr: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None