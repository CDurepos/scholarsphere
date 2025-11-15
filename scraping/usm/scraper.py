import pandas as pd
import requests
from bs4 import BeautifulSoup
from scraping.schemas import faculty
from dataclasses import asdict
import regex as re

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
    "esq.", "sc:l", "nic-m", "bc", "msph", "pmhnp", "atc", "aprn-bc"]
base_url = "https://usm.maine.edu/directories/faculty-and-staff/"

def get_faculty_csv_from_url(url):
    faculty_list = []
    # Cycle through alphabetically organized directories
    for letter in alphabet:
        current_url = url + letter + "/"
        response = requests.get(current_url)
        # Check URL request validity:
        if response.status_code != 200:
            print(f"Failed to retrieve {current_url}. Status code: {response.status_code}")
            continue
        soup = BeautifulSoup(response.text, "lxml")
        # Find people wrappers in the soup
        container = soup.find(id="peoplewrapper")
        # If no person here, continue
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
                # Special Cases (because usm website is weird)
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
                    print(f"error: only one name found for {name_parts}")
                    continue
                # Back to business as usual:
                elif len(name_parts) >= 2:
                    first_name = " ".join(name_parts[:-1])
                    last_name = name_parts[-1]

                if retrieve_biography:
                    # Inspect the faculty's personal web page based on name
                    specific_url = "https://usm.maine.edu/directories/people/" + first_name + "-" + last_name + "/"
                    response = requests.get(specific_url)
                    # Check URL request validity:
                    if response.status_code != 200:
                        # print(f"Failed to retrieve {specific_url}. Status code: {response.status_code}")
                        continue
                    soup = BeautifulSoup(response.text, "lxml")
                    bio_tag = soup.select_one("div.bio")
                    bio = None
                    if bio_tag:
                        # Extract all paragraph text inside the bio section
                        paragraphs = [p.get_text(strip=True) for p in bio_tag.find_all("p") if p.get_text(strip=True)]
                        bio = " ".join(paragraphs)

            # Parse title
            title_tag = person.select_one("div.people-title li")
            title, department = None, None
            title_keywords = ["professor", "lecturer", "director", "research", "researcher"]
            keyword_match = False
            if title_tag:
                raw_title = title_tag.get_text(strip=True)
                for keyword in title_keywords:
                    if keyword in raw_title.lower():
                        keyword_match = True

                if keyword_match:
                    # Match patterns like "Assistant Professor, Department of Math"
                    match = re.match(r"^(.*?),\s*(Department.*)$", raw_title, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        department = match.group(2).strip()
                    else:
                        title = raw_title
                        department = None

                    # Parse email
                    email_tag = person.select_one("div.people-email a")
                    email = email_tag.get_text(strip=True) if email_tag else None

                    # Parse phone
                    phone_tag = person.select_one("div.people-telephone a")
                    phone = phone_tag.get_text(strip=True) if phone_tag else None

                    # Build Faculty object
                    faculty_member = faculty.Faculty(
                        faculty_id=None,
                        first_name=first_name,
                        last_name=last_name,
                        title=title,
                        department=department,
                        email=email,
                        phone_num=phone,
                        biography=bio,
                        scraped_from=current_url)
                    if faculty_member.first_name is not None:
                        faculty_list.append(asdict(faculty_member))

                else:
                    continue

    # Convert to DataFrame and save
    df = pd.DataFrame(faculty_list)
    df.to_csv("usm_faculty.csv", index=False)
    print(f"Saved {len(df)} faculty entries to usm_faculty.csv")

get_faculty_csv_from_url(base_url)
