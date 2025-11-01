from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True)
class Institution:
    name: Optional[str] = None
    website_url: Optional[str] = None
    institution_type: Optional[str] = None
    street_addr: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None