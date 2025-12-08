#!/usr/bin/env python3
"""
UMA Faculty Scraper
Scrapes faculty data from University of Maine at Augusta directory.
"""

import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import date
from typing import List, Dict, Tuple

from scraping.utils.json_output import write_faculty_jsonl

base_url = 'https://www.uma.edu/directory/'

# Institution name must match exactly what's in data/institutions.json
INSTITUTION_NAME = "University of Maine at Augusta"


def scrape_faculty_url(url: str, first_name: str, middle: str, last_name: str) -> Dict:
    """Scrape individual faculty profile page."""
    r = requests.get(url)
    if r.status_code != 200:
        print(f"ERROR {r.status_code} for {url}")
        return None
    
    soup = BeautifulSoup(r.text, "html.parser")
    data = {
        "url": url,
        "first_name": first_name,
        "last_name": last_name
    }
    
    # NAME
    h1 = soup.find("h1")
    if h1:
        data["name"] = h1.get_text(strip=True)
    else:
        data["name"] = None
    
    # TITLE
    title = None
    rows = soup.find_all("tr")
    for row in rows:
        title_header = row.find("th")
        title_data = row.find("td")
        if title_header and title_data:
            if "title" in title_header.get_text(strip=True).lower():
                title = title_data.get_text(strip=True)
                break
    data["title"] = title
    
    # EMAIL
    email = None
    email_tag = soup.find("a", href=re.compile(r"^mailto:"))
    if email_tag:
        email = email_tag.get_text(strip=True)
    data["email"] = email
    
    # PHONE
    phone = None
    rows = soup.find_all("tr")
    for row in rows:
        phone_header = row.find("th")
        phone_data = row.find("td")
        if phone_header and phone_data:
            if "telephone" in phone_header.get_text(strip=True).lower():
                phone = phone_data.get_text(strip=True)
                break
    data["phone"] = phone
    
    return data


def clean_name(full_name: str) -> Tuple[str, str, str]:
    """Parse and clean full name into first, middle, last."""
    # Remove parenthesis from nicknames
    full_name = re.sub(r"\([^)]*\)", "", full_name)
    # Split full name by spaces
    split = full_name.strip().split()
    
    if len(split) >= 3:
        return split[0], "-".join(split[1:-1]), split[-1]
    elif len(split) == 2:
        return split[0], "", split[-1]
    else:
        return split[0] if split else "", "", ""


def build_url(first_name: str, middle: str, last_name: str) -> str:
    """Build faculty profile URL from name components."""
    first = first_name.lower()
    last = last_name.lower()
    
    if middle:
        middle = middle.lower()
        return f"https://www.uma.edu/directory/staff/{first}-{middle}-{last}/"
    else:
        return f"https://www.uma.edu/directory/staff/{first}-{last}/"


def scrape_uma() -> List[Dict]:
    """
    Scrape UMA faculty data and return faculty records.
    
    Returns:
        List of faculty dictionaries with all attributes including MV attributes as arrays.
        Each record includes institution_name which references data/institutions.json.
    """
    first_names = []
    middle_names = []
    last_names = []
    faculty_records = []
    
    print("[INFO] Scraping directory pages...")
    # Scrape directory pages (1-34)
    for i in range(1, 35):
        if i == 1:
            url = base_url
        else:
            url = f"{base_url}page/{i}/"
        
        print(f"[INFO] Scraping: {url}")
        
        try:
            request = requests.get(url)
            soup = BeautifulSoup(request.text, "html.parser")
            
            people = soup.find_all("h3")
            print(f"[INFO] Found {len(people)} h3 elements")
            
            ignore = {"Locations", "Resources", "Community", "University of Maine at Augusta"}
            
            for p in people:
                text = p.get_text(strip=True)
                
                if text in ignore:
                    continue
                
                first, middle, last = clean_name(text)
                first_names.append(first)
                middle_names.append(middle)
                last_names.append(last)
                
        except Exception as e:
            print(f"[WARN] Failed to scrape page {i}: {e}")
            continue
    
    print(f"[INFO] Total names found: {len(first_names)}")
    
    # Scrape individual faculty pages
    print("[INFO] Scraping individual faculty pages...")
    for first, mid, last in zip(first_names, middle_names, last_names):
        url = build_url(first, mid, last)
        info = scrape_faculty_url(url, first, mid, last)
        
        if info:
            # Only include professors
            title = info.get('title', '')
            if title and "professor" in title.lower():
                # Build faculty record with MV attributes as arrays
                emails = [info['email']] if info.get('email') and info['email'] != "N/A" else []
                phones = [info['phone']] if info.get('phone') and info['phone'] != "N/A" else []
                titles = [info['title']] if info.get('title') and info['title'] != "N/A" else []
                departments = []  # UMA scraper doesn't extract departments
                
                faculty_record = {
                    'first_name': info.get('first_name'),
                    'last_name': info.get('last_name'),
                    'biography': None,  # UMA scraper doesn't extract biography
                    'orcid': None,
                    'google_scholar_url': None,
                    'research_gate_url': None,
                    'scraped_from': info.get('url'),
                    'emails': emails,
                    'phones': phones,
                    'departments': departments,
                    'titles': titles,
                    'institution_name': INSTITUTION_NAME,
                    'start_date': date.today().isoformat(),
                    'end_date': None,
                }
                
                faculty_records.append(faculty_record)
                print(f"[OK] {info.get('first_name')} {info.get('last_name')} | {info.get('title')}")
    
    return faculty_records


def main(output_dir: str = "scraping/out"):
    """
    Main function to scrape UMA data and output JSON files.
    
    Args:
        output_dir: Directory to write output files (default: scraping/out)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    faculty_records = scrape_uma()
    print(f"[INFO] Scraped {len(faculty_records)} faculty records")
    
    # Write faculty JSONL file
    faculty_output = os.path.join(output_dir, "uma_faculty.jsonl")
    write_faculty_jsonl(faculty_records, faculty_output)
    print(f"[INFO] Wrote: {faculty_output}")
    
    return faculty_output


if __name__ == "__main__":
    main()

