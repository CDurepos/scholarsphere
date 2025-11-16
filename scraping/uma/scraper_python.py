import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import csv

base_url = 'https://www.uma.edu/directory/'
first_names = []
middle_names = []
last_names = []
data = []
output_filename = "uma_faculty_directory.csv"



def scrape_faculty_url(url, first_name, middle, last_name):
    r = requests.get(url)
    if r.status_code != 200: #200 is the successful code
        print ("ERROR "+ str(r.status_code))
        return None
    
    soup = BeautifulSoup(r.text, "html.parser")
    data = {"url" : url,
            "first_name":first_name,
            "last_name":last_name}
    
    #NAME
    h1 = soup.find("h1")
    if (h1):
        data["name"] = h1.get_text(strip = True)
        print(f"Name: {data['name']}")
    else:
        data["name"] = "N/A"
        print("Name: N/A")


    #TITLE
    title ="N/A"
    rows = soup.find_all("tr")
    for row in rows:
        title_header = row.find("th")
        title_data = row.find("td")
        if (title_header and title_data): #not null
            if "title" in title_header.get_text(strip=True).lower():
                title = title_data.get_text(strip = True)
                break
    data["title"] = title
    print(f" Title: {title}")

    #EMAIL
    email = soup.find("a", href=re.compile(r"^mailto:")) #Chat-GPT helped with this find all statement for mailto
    if (email):
        data["email"] = email.get_text(strip=True)
        print(f" Email: {data['email']}")
    else:
        data["email"] = "N/A"
    
    #Phone number
    phone = "N/A"
    rows = soup.find_all("tr")
    for row in rows:
        phone_header = row.find("th")
        phone_data = row.find("td")
        if (phone_header and phone_data):
            if "telephone" in phone_header.get_text(strip= True).lower():
                phone = phone_data.get_text(strip = True)
                break
    data["phone"] = phone
    print(f" Phone: {phone}")

    #ADDRESS
    address = "N/A"
    rows = soup.find_all("tr")
    for row in rows:
        address_header = row.find("th")
        address_data = row.find("td")
        if (address_header and address_data):
            if "address" in address_header.get_text(strip=True).lower():
                address = " ".join(address_data.stripped_strings)
                break
    data["address"] = address
    print(f" Address: {address}")

    return data


def clean_name(full_name):
    #Remove parenthesis from nicknames
    full_name = re.sub(r"\([^)]*\)", "", full_name)
    #split full name by spaces
    split = full_name.strip().split()
    #Keep only first and last names
    if (len(split) >=3):
        first_names.append(split[0]) 
        middle_names.append( "-".join(split[1:-1]))
        last_names.append(split[-1])
        print(f" Clean name: {split[0]} {'-'.join(split[1:-1])} {split[-1]}")
    #Only a first name (just in case)
    elif len(split) == 2:
        first_names.append(split[0])
        #Add an empty middle name
        middle_names.append("")
        last_names.append(split[-1])
        print(f" Clean name: {split[0]} (no middle name)")
    else:
        first_names.append(split[0])
        middle_names.append("")
        last_names.append("")

def build_url(first_name, middle, last_name):
    first = first_name.lower()
    last = last_name.lower()

    if (middle):
        middle = middle.lower()
        return f"https://www.uma.edu/directory/staff/{first}-{middle}-{last}/"
    else:
        return f"https://www.uma.edu/directory/staff/{first}-{last}/"



def scrape_directory():

    for i in range (1,35): #34 pages of the directory
        #Go through urls based on page number
        if (i == 1):
            url = base_url
        else:
            url = f"{base_url}page/{i}/"

        print("Sraping: ", url)
    
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "html.parser")

        people = soup.find_all("h3")
        print(f" Found {len(people)} h3 elements")

        for p in people:
            text = p.get_text(strip = True)

            ignore = {"Locations", "Resources", "Community", "University of Maine at Augusta"}
            if (text in ignore):
                print(f"ignoring: {text}")
                continue
            else:
                print(f"Processing: {text}")
                clean_name(text)

                link = p.find("a")
                if (link and link.get("href")):
                    print(f"Found url: {link.get('href')}")
                else:
                    print(f"WARNING: No link found")
    print(f"Total names: {len(first_names)}")
    


def scrape_all_faculty():
#Chat-GPT helped me with an error here, it made the correction to add zip
    for first, mid, last in zip (first_names, middle_names, last_names):
        url = build_url(first, mid, last)
        info = scrape_faculty_url(url, first, mid, last)
        if info:
            print(f"Found: {info['name']} - Title: {info['title']}")
            if "professor" in info['title'].lower():
                data.append(info)
                print("Added data is (is professor)")
            else:
                print("skipped not professor")            


def save_to_csv(output_filename):

    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["first_name","last_name","name", "title", "email", "phone", "address", "url"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print("Saved CSV ", output_filename)

if __name__ == "__main__":
    scrape_directory()
    scrape_all_faculty()
    save_to_csv(output_filename)
    print("COMPLETE")
    print(data)