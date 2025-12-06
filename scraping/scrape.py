#!/usr/bin/env python3
"""
Scraper orchestration script.

Runs all institution scrapers (UMA, UMF, UMO, USM) and collects their JSON output
into the scraping/out directory. Each scraper produces:
- {institution}_faculty.jsonl: Newline-delimited JSON with faculty records
- {institution}_publications.jsonl: Newline-delimited JSON with publication records (UMO only)

Institution data is sourced from data/institutions.json.

Usage:
    python scraping/scrape.py
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List, Optional, Union

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_umf_scraper(output_dir: str) -> str:
    """Run UMF scraper and return output file path."""
    print("\n" + "="*60)
    print("Running UMF Scraper")
    print("="*60)
    from scraping.umf.scraper import main as umf_main
    return umf_main(output_dir)


def run_uma_scraper(output_dir: str) -> str:
    """Run UMA scraper and return output file path."""
    print("\n" + "="*60)
    print("Running UMA Scraper")
    print("="*60)
    from scraping.uma.scraper import main as uma_main
    return uma_main(output_dir)


def run_umo_scraper(output_dir: str) -> Tuple[str, str]:
    """Run UMO scraper and return output file paths (faculty, publications)."""
    print("\n" + "="*60)
    print("Running UMO Scraper")
    print("="*60)
    from scraping.umo.pipeline import main as umo_main
    return umo_main(output_dir)


def run_usm_scraper(output_dir: str) -> str:
    """Run USM scraper and return output file path."""
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
    print("[INFO] Institution data sourced from data/institutions.json")
    
    # Scrapers: (name, function, faculty_filename, publications_filename or None)
    scrapers = [
        ("UMF", run_umf_scraper, "umf_faculty.jsonl", None),
        ("UMA", run_uma_scraper, "uma_faculty.jsonl", None),
        ("UMO", run_umo_scraper, "umo_faculty.jsonl", "umo_publications.jsonl"),
        ("USM", run_usm_scraper, "usm_faculty.jsonl", None),
    ]
    
    all_faculty_files: List[str] = []
    all_publications_files: List[str] = []
    
    for name, scraper_func, faculty_filename, publications_filename in scrapers:
        faculty_file = os.path.join(output_dir, faculty_filename)
        publications_file = os.path.join(output_dir, publications_filename) if publications_filename else None
        
        # Check if output already exists
        if os.path.exists(faculty_file) and (not publications_file or os.path.exists(publications_file)):
            print(f"\n[SKIP] {name} scraper - output files already exist")
            all_faculty_files.append(faculty_file)
            print(f"[OK] {name} faculty data: {faculty_file}")
            if publications_file:
                all_publications_files.append(publications_file)
                print(f"[OK] {name} publications data: {publications_file}")
            continue
        
        try:
            print(f"\n[INFO] Running {name} scraper...")
            result = scraper_func(output_dir)
            
            # Handle scrapers that return 1 value (faculty) or 2 values (faculty, publications)
            if isinstance(result, tuple):
                faculty_file, publications_file = result
            else:
                faculty_file = result
                publications_file = None
            
            if faculty_file and os.path.exists(faculty_file):
                all_faculty_files.append(faculty_file)
                print(f"[OK] {name} faculty data: {faculty_file}")

            if publications_file and os.path.exists(publications_file):
                all_publications_files.append(publications_file)
                print(f"[OK] {name} publications data: {publications_file}")
        except Exception as e:
            print(f"[ERROR] {name} scraper failed: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*60)
    print("Scraping Summary")
    print("="*60)
    
    print(f"Faculty files: {len(all_faculty_files)}")
    for faculty_file in all_faculty_files:
        size = os.path.getsize(faculty_file)
        record_count = count_jsonl_records(faculty_file)
        print(f"  - {faculty_file} ({record_count} records, {size} bytes)")

    print(f"\nPublications files: {len(all_publications_files)}")
    for publications_file in all_publications_files:
        size = os.path.getsize(publications_file)
        record_count = count_jsonl_records(publications_file)
        print(f"  - {publications_file} ({record_count} records, {size} bytes)")
    
    print(f"\n[INFO] All scrapers completed! Output saved to: {output_dir}")
    print("[INFO] Ready for data insertion (run scraping/insert.py)")


if __name__ == "__main__":
    main()
