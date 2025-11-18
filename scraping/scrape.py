#!/usr/bin/env python3
"""
Scraper orchestration script.

Runs all institution scrapers (UMA, UMF, UMO, USM) and collects their JSON output
into the scraping/out directory. Each scraper produces two files:
- {institution}_faculty.jsonl: Newline-delimited JSON with faculty records
- {institution}_institution.json: Single JSON object with institution data

Usage:
    python scraping/scrape.py
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_umf_scraper(output_dir: str) -> Tuple[str, str]:
    """Run UMF scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running UMF Scraper")
    print("="*60)
    from scraping.umf.scraper import main as umf_main
    return umf_main(output_dir)


def run_uma_scraper(output_dir: str) -> Tuple[str, str]:
    """Run UMA scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running UMA Scraper")
    print("="*60)
    from scraping.uma.scraper import main as uma_main
    return uma_main(output_dir)


def run_umo_scraper(output_dir: str) -> Tuple[str, str]:
    """Run UMO scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running UMO Scraper")
    print("="*60)
    from scraping.umo.pipeline import main as umo_main
    return umo_main(output_dir)


def run_usm_scraper(output_dir: str) -> Tuple[str, str]:
    """Run USM scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running USM Scraper")
    print("="*60)
    from scraping.usm.scraper import main as usm_main
    return usm_main(output_dir)


def count_jsonl_records(file_path: str) -> int:
    """Count the number of records in a JSONL file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def main():
    """Orchestrate all scrapers and collect output."""
    output_dir = "scraping/out"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("ScholarSphere Scraper Orchestration")
    print("="*60)
    
    scrapers = [
        ("UMF", run_umf_scraper),
        ("UMA", run_uma_scraper),
        ("UMO", run_umo_scraper),
        ("USM", run_usm_scraper),
    ]
    
    all_faculty_files: List[str] = []
    all_institution_files: List[str] = []
    
    for name, scraper_func in scrapers:
        try:
            print(f"\n[INFO] Running {name} scraper...")
            faculty_file, institution_file = scraper_func(output_dir)
            
            if faculty_file and os.path.exists(faculty_file):
                all_faculty_files.append(faculty_file)
                print(f"[OK] {name} faculty data: {faculty_file}")
            
            if institution_file and os.path.exists(institution_file):
                all_institution_files.append(institution_file)
                print(f"[OK] {name} institution data: {institution_file}")
        except Exception as e:
            print(f"[ERROR] {name} scraper failed: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*60)
    print("Scraping Summary")
    print("="*60)
    
    print(f"Institution files: {len(all_institution_files)}")
    for inst_file in all_institution_files:
        size = os.path.getsize(inst_file)
        print(f"  - {inst_file} ({size} bytes)")
    
    print(f"\nFaculty files: {len(all_faculty_files)}")
    for faculty_file in all_faculty_files:
        size = os.path.getsize(faculty_file)
        record_count = count_jsonl_records(faculty_file)
        print(f"  - {faculty_file} ({record_count} records, {size} bytes)")
    
    print(f"\n[INFO] All scrapers completed! Output saved to: {output_dir}")
    print("[INFO] Ready for data insertion (run scraping/insert.py)")


if __name__ == "__main__":
    main()
