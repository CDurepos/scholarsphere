import pandas as pd
import requests
from bs4 import BeautifulSoup
from scraping.dataclasses import faculty
from dataclasses import asdict

alphabet = "abcdefghijklmnopqrstuvwxyz"
base_url = "https://usm.maine.edu/directories/faculty-and-staff/"

def get_faculty_csv_from_url(url):
    faculty_list = []

    for letter in alphabet:
        current_url = url + letter + "/"
        response = requests.get(current_url)
        if response.status_code != 200:
            print(f"Failed to retrieve {current_url}. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "lxml")
        container = soup.find(id="peoplewrapper")
        if not container:
            continue

        people_items = container.select(".grid_item.people_item")
        for person in people_items:
            # Parse name
            name_tag = person.select_one("div.people_item_info h3")
            first_name, last_name = None, None
            if name_tag:
                name_parts = name_tag.text.strip().split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else None

            # Parse title
            title_tag = person.select_one("div.people-title li")
            title = title_tag.get_text(strip=True) if title_tag else None

            # Parse email
            email_tag = person.select_one("div.people_email a[href^='mailto:']")
            email = email_tag.text.strip() if email_tag else None

            # Parse phone
            phone_tag = person.select_one("div.people_telephone a[href^='tel:']")
            phone = phone_tag.text.strip() if phone_tag else None

            # Build Faculty object
            faculty_member = faculty.Faculty(
                first_name=first_name,
                last_name=last_name,
                title=title,
                email=email,
                phone_num=phone,
                scraped_from=current_url
            )
            faculty_list.append(asdict(faculty_member))

    # Convert to DataFrame and save
    df = pd.DataFrame(faculty_list)
    df.to_csv("usm_faculty.csv", index=False)
    print(f"Saved {len(df)} faculty entries to usm_faculty.csv")

get_faculty_csv_from_url(base_url)
