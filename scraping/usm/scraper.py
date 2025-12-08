"""
Author: Abby Pitcairn
"""

#!/usr/bin/env python3
"""
USM Faculty Scraper
Scrapes faculty data from University of Southern Maine directory.
"""

import requests
from bs4 import BeautifulSoup
import regex as re
import os
from datetime import date
from typing import List, Dict

from scraping.utils.json_output import write_faculty_jsonl

# Use this Boolean to toggle on/off biography retrieval
retrieve_biography = False

alphabet = "abcdefghijklmnopqrstuvwxyz"
abbreviations = [
    "aama", "aprn", "ba", "bcba-d", "bcba", "bsn", "cas", "ccep", "cefp", "ccc-slp", "cpia", "cip",
    "ccs", "cma", "cne", "cpnp-pc", "dr.", "dnp", "dnp-c", "dpt", "dma", "edd", "eed", "ncc",
    "faota", "fnp-bc", "fnp-c", "jd", "lcpc", "lcsw", "med", "m.ed", "ma", "md", "mfa",
    "mhft/c", "mph", "mot", "ms", "msed", "msc", "msls", "msn", "msot", "msw", "ph.d.", "acs",
    "mt-bc", "ncsp", "nic", "np-c", "otd", "otr/l", "pe", "phd", "pmhnp-bc", "dsw", "ctmh",
    "pt", "rpt-s", "rn", "rn-bc", "licsw", "dvm", "anp-bc", "agpcnp-bc", "mpa", "mhrt-c",
    "psyd", "mhrt/c", "cota/l", "ceeaa", "ed:k-", "chse", "msn-ed", "mba", "cpps", "dhed", "mches",
    "esq.", "sc:l", "nic-m", "bc", "msph", "pmhnp", "atc", "aprn-bc"
]

base_url = "https://usm.maine.edu/directories/faculty-and-staff/"

# Institution name must match exactly what's in data/institutions.json
INSTITUTION_NAME = "University of Southern Maine"


def scrape_usm() -> List[Dict]:
    """
    Scrape USM faculty data and return faculty records.
    
    Returns:
        List of faculty dictionaries with all attributes including MV attributes as arrays.
        Each record includes institution_name which references data/institutions.json.
    """
    faculty_records = []
    
    print("[INFO] Scraping alphabetically organized directories...")
    # Cycle through alphabetically organized directories
    for letter in alphabet:
        current_url = base_url + letter + "/"
        print(f"[INFO] Scraping: {current_url}")
        
        try:
            response = requests.get(current_url)
            if response.status_code != 200:
                print(f"[WARN] Failed to retrieve {current_url}. Status code: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, "lxml")
            container = soup.find(id="peoplewrapper")
            if not container:
                continue
            
            people_items = container.select(".grid_item.people_item")
            
            # For each person wrapper on the page:
            for person in people_items:
                # Parse name
                name_tag = person.select_one("div.people_item_info h3")
                first_name, last_name, bio = None, None, None
                
                if name_tag:
                    # Remove commas, parentheses and digits
                    clean_name = re.sub(r"[,0-9()+]", " ", name_tag.text.strip())
                    # Split into words
                    name_parts = [part.strip() for part in clean_name.split()]
                    # Remove abbreviations
                    name_parts = [part for part in name_parts if part.lower() not in abbreviations]
                    
                    # Special Cases
                    if "De" in name_parts or "Van" in name_parts or "van" in name_parts:
                        first_name = name_parts[0]
                        last_name = " ".join(name_parts[1:])
                    elif "Jr." in name_parts:
                        first_name = name_parts[0] + " " + name_parts[2]
                        last_name = name_parts[1]
                    elif "Hascall" in name_parts or "Rhine" in name_parts or "Thibodeau" in name_parts:
                        first_name = name_parts[0]
                        last_name = name_parts[1]
                    elif len(name_parts) == 1:
                        print(f"[WARN] Only one name found for {name_parts}")
                        continue
                    elif len(name_parts) >= 2:
                        first_name = " ".join(name_parts[:-1])
                        last_name = name_parts[-1]
                    
                    if retrieve_biography:
                        # Inspect the faculty's personal web page based on name
                        specific_url = f"https://usm.maine.edu/directories/people/{first_name}-{last_name}/"
                        bio_response = requests.get(specific_url)
                        if bio_response.status_code == 200:
                            bio_soup = BeautifulSoup(bio_response.text, "lxml")
                            bio_tag = bio_soup.select_one("div.bio")
                            if bio_tag:
                                paragraphs = [p.get_text(strip=True) for p in bio_tag.find_all("p") if p.get_text(strip=True)]
                                bio = " ".join(paragraphs)
                
                # Parse title
                title_tag = person.select_one("div.people-title li")
                title, department = None, None
                title_keywords = ["professor", "lecturer", "research", "researcher"]
                keyword_match = False
                
                if title_tag:
                    raw_title = title_tag.get_text(strip=True)
                    for keyword in title_keywords:
                        if keyword in raw_title.lower():
                            keyword_match = True
                    
                    if keyword_match:
                        raw = raw_title.strip()
                        
                        # Case 1: Contains "Department ..."
                        dept_match = re.search(r"(Department\s+.*)$", raw, re.IGNORECASE)
                        if dept_match:
                            title_part = raw[:dept_match.start()].strip().rstrip(",")
                            title = title_part if title_part else None
                            department = dept_match.group(1).strip()
                        else:
                            # Case 2: Contains "X of Y"
                            of_match = re.search(r"(.+?)\s+of\s+(.*)$", raw, re.IGNORECASE)
                            if of_match:
                                title = of_match.group(1).strip()
                                department = of_match.group(2).strip()
                            else:
                                title = raw
                                department = None
                        
                        # Parse email
                        email_tag = person.select_one("div.people-email a")
                        email = email_tag.get_text(strip=True) if email_tag else None
                        
                        # Parse phone
                        phone_tag = person.select_one("div.people-telephone a")
                        raw_phone = phone_tag.get_text(strip=True) if phone_tag else ""
                        pattern = r'\+?\d[\d\-\s\(\)]{7,}\d'
                        phone_numbers = re.findall(pattern, raw_phone)
                        phone = ", ".join(num.strip() for num in phone_numbers) if phone_numbers else None
                        
                        # Build faculty record with MV attributes as arrays
                        emails = [email] if email else []
                        phones = [phone] if phone else []
                        titles = [title] if title else []
                        departments = [department] if department else []
                        
                        faculty_record = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'biography': bio,
                            'orcid': None,
                            'google_scholar_url': None,
                            'research_gate_url': None,
                            'scraped_from': current_url,
                            'emails': emails,
                            'phones': phones,
                            'departments': departments,
                            'titles': titles,
                            'institution_name': INSTITUTION_NAME,
                            'start_date': date.today().isoformat(),
                            'end_date': None,
                        }
                        
                        if faculty_record['first_name'] is not None:
                            faculty_records.append(faculty_record)
                            print(f"[OK] {first_name} {last_name} | {title}")
        
        except Exception as e:
            print(f"[WARN] Failed to scrape {current_url}: {e}")
            continue
    
    return faculty_records


def main(output_dir: str = "scraping/out"):
    """
    Main function to scrape USM data and output JSON files.
    
    Args:
        output_dir: Directory to write output files (default: scraping/out)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    faculty_records = scrape_usm()
    print(f"[INFO] Scraped {len(faculty_records)} faculty records")
    
    # Write faculty JSONL file
    faculty_output = os.path.join(output_dir, "usm_faculty.jsonl")
    write_faculty_jsonl(faculty_records, faculty_output)
    print(f"[INFO] Wrote: {faculty_output}")
    
    return faculty_output


if __name__ == "__main__":
    main()
