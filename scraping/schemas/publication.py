"""
Author: Aidan Bell
"""

from typing import Optional
from dataclasses import dataclass

@dataclass(slots=True)
class Publication:
    publication_id: Optional[str] = None
    doi: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    year: Optional[str] = None
    citation_count: Optional[str] = None
    publisher: Optional[str] = None