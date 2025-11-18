"""
Utility functions for outputting scraped data as JSON.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path


def write_faculty_jsonl(faculty_records: List[Dict[str, Any]], output_path: str):
    """
    Write faculty records to a JSONL file (one JSON object per line).
    
    Args:
        faculty_records: List of faculty dictionaries, each containing:
            - first_name, last_name, biography, orcid, google_scholar_url, 
              research_gate_url, scraped_from
            - emails: List[str] (multi-valued)
            - phones: List[str] (multi-valued)
            - departments: List[str] (multi-valued)
            - titles: List[str] (multi-valued)
            - institution_id: Optional[str]
            - start_date: Optional[str] (YYYY-MM-DD format)
            - end_date: Optional[str] (YYYY-MM-DD format)
        output_path: Path to output JSONL file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in faculty_records:
            # Ensure MV attributes are lists
            record['emails'] = record.get('emails', []) or []
            record['phones'] = record.get('phones', []) or []
            record['departments'] = record.get('departments', []) or []
            record['titles'] = record.get('titles', []) or []
            
            # Convert to JSON and write
            json_line = json.dumps(record, ensure_ascii=False)
            f.write(json_line + '\n')


def write_institution_json(institution: Dict[str, Any], output_path: str):
    """
    Write institution record to a JSON file.
    
    Args:
        institution: Dictionary containing institution data
        output_path: Path to output JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(institution, f, indent=2, ensure_ascii=False)

