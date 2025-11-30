#!/usr/bin/env python3
"""
Scraper orchestration script.

Runs all institution scrapers (UMA, UMF, UMO, USM) and collects their JSON output
into the scraping/out directory. Each scraper produces two files and an optional third file:
- {institution}_faculty.jsonl: Newline-delimited JSON with faculty records
- {institution}_institution.json: Single JSON object with institution data
- {institution}_publications.jsonl: Newline-delimited JSON with publication records

Usage:
    python scraping/scrape.py
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_umf_scraper(output_dir: str) -> Tuple[str, str, None]:
    """Run UMF scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running UMF Scraper")
    print("="*60)
    from scraping.umf.scraper import main as umf_main
    return umf_main(output_dir), None


def run_uma_scraper(output_dir: str) -> Tuple[str, str, None]:
    """Run UMA scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running UMA Scraper")
    print("="*60)
    from scraping.uma.scraper import main as uma_main
    return uma_main(output_dir), None


def run_umo_scraper(output_dir: str) -> Tuple[str, str, str]:
    """Run UMO scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running UMO Scraper")
    print("="*60)
    from scraping.umo.pipeline import main as umo_main
    return umo_main(output_dir)


def run_usm_scraper(output_dir: str) -> Tuple[str, str, None]:
    """Run USM scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running USM Scraper")
    print("="*60)
    from scraping.usm.scraper import main as usm_main
    return usm_main(output_dir), None


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
        ("UMF", run_umf_scraper, "umf_faculty.jsonl", "umf_institution.json", None),
        ("UMA", run_uma_scraper, "uma_faculty.jsonl", "uma_institution.json", None),
        ("UMO", run_umo_scraper, "umo_faculty.jsonl", "umo_institution.json", "umo_publications.jsonl"),
        ("USM", run_usm_scraper, "usm_faculty.jsonl", "usm_institution.json", None),
    ]
    
    all_faculty_files: List[str] = []
    all_institution_files: List[str] = []
    all_publications_files: List[str] = []
    
    for name, scraper_func, faculty_filename, institution_filename, publications_filename in scrapers:
        faculty_file = os.path.join(output_dir, faculty_filename)
        institution_file = os.path.join(output_dir, institution_filename)
        if publications_filename:
            publications_file = os.path.join(output_dir, publications_filename)
        else:
            publications_file = None
        
        if os.path.exists(faculty_file) and os.path.exists(institution_file) and (not publications_file or os.path.exists(publications_file)):
            print(f"\n[SKIP] {name} scraper - output files already exist")
            all_faculty_files.append(faculty_file)
            all_institution_files.append(institution_file)
            if publications_file:
                all_publications_files.append(publications_file)
            print(f"[OK] {name} faculty data: {faculty_file}")
            print(f"[OK] {name} institution data: {institution_file}")
            if publications_file:
                print(f"[OK] {name} publications data: {publications_file}")
            continue
        
        try:
            print(f"\n[INFO] Running {name} scraper...")
            faculty_file, institution_file, publications_file = scraper_func(output_dir)
            
            if faculty_file and os.path.exists(faculty_file):
                all_faculty_files.append(faculty_file)
                print(f"[OK] {name} faculty data: {faculty_file}")
            
            if institution_file and os.path.exists(institution_file):
                all_institution_files.append(institution_file)
                print(f"[OK] {name} institution data: {institution_file}")

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
    
    print(f"Institution files: {len(all_institution_files)}")
    for inst_file in all_institution_files:
        size = os.path.getsize(inst_file)
        print(f"  - {inst_file} ({size} bytes)")
    
    print(f"\nFaculty files: {len(all_faculty_files)}")
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
