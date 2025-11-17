#!/usr/bin/env python3
"""
Master script to run all scrapers and collect JSON output.

This script:
1. Runs each scraper (uma, umf, umo, usm)
2. Collects JSON output from each
3. Saves all output to the scraping/out directory

Usage:
    python scraping/run_all_scrapers.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_umf_scraper(output_dir: str) -> tuple:
    """Run UMF scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running UMF Scraper")
    print("="*60)
    from scraping.umf.scraper import main as umf_main
    faculty_file, institution_file = umf_main(output_dir)
    return faculty_file, institution_file


def run_uma_scraper(output_dir: str) -> tuple:
    """Run UMA scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running UMA Scraper")
    print("="*60)
    from scraping.uma.scraper import main as uma_main
    faculty_file, institution_file = uma_main(output_dir)
    return faculty_file, institution_file


def run_umo_scraper(output_dir: str) -> tuple:
    """Run UMO scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running UMO Scraper")
    print("="*60)
    from scraping.umo.pipeline import main as umo_main
    faculty_file, institution_file = umo_main(output_dir)
    return faculty_file, institution_file


def run_usm_scraper(output_dir: str) -> tuple:
    """Run USM scraper and return output file paths."""
    print("\n" + "="*60)
    print("Running USM Scraper")
    print("="*60)
    from scraping.usm.scraper import main as usm_main
    faculty_file, institution_file = usm_main(output_dir)
    return faculty_file, institution_file


def main():
    """Main orchestration function."""
    output_dir = "scraping/out"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("ScholarSphere Scraper Orchestration")
    print("="*60)
    
    # Track all scraped files
    all_faculty_files = []
    all_institution_files = []
    
    # Run each scraper
    scrapers = [
        ("UMF", run_umf_scraper),
        ("UMA", run_uma_scraper),
        ("UMO", run_umo_scraper),
        ("USM", run_usm_scraper),
    ]
    
    for name, scraper_func in scrapers:
        try:
            print(f"\n[INFO] Running {name} scraper...")
            faculty_file, institution_file = scraper_func(output_dir)
            if faculty_file:
                all_faculty_files.append(faculty_file)
                print(f"[OK] {name} faculty data: {faculty_file}")
            if institution_file:
                all_institution_files.append(institution_file)
                print(f"[OK] {name} institution data: {institution_file}")
        except Exception as e:
            print(f"[ERROR] {name} scraper failed: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Print final summary
    print("\n" + "="*60)
    print("Scraping Summary")
    print("="*60)
    print(f"Institution files: {len(all_institution_files)}")
    for inst_file in all_institution_files:
        if inst_file and os.path.exists(inst_file):
            size = os.path.getsize(inst_file)
            print(f"  - {inst_file} ({size} bytes)")
    
    print(f"\nFaculty files: {len(all_faculty_files)}")
    for faculty_file in all_faculty_files:
        if faculty_file and os.path.exists(faculty_file):
            size = os.path.getsize(faculty_file)
            # Count lines in JSONL file
            try:
                with open(faculty_file, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for line in f if line.strip())
                print(f"  - {faculty_file} ({line_count} records, {size} bytes)")
            except Exception as e:
                print(f"  - {faculty_file} ({size} bytes)")
    
    print(f"\n[INFO] All scrapers completed! Output saved to: {output_dir}")
    print("[INFO] Ready for data insertion (not performed in this script)")


if __name__ == "__main__":
    main()
