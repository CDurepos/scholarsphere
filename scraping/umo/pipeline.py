from scraping.umo.dataclass_instances.orono import umaine
from scraping.utils.json_output import write_faculty_jsonl, write_institution_json
from scraping.schemas import (
    Faculty,
    Publication,
    Institution,
    PublicationAuthoredByFaculty,
)

import os
import json
import uuid
import importlib
from tqdm import tqdm
from pathlib import Path
from datetime import date
from difflib import SequenceMatcher
from typing import Union, List, Dict, Tuple

# CFG
COMPILER_OUTPUT_DIR = os.path.join(
    "scraping", "umo", "scrape_storage", "biography_pages"
)  # Relative to cwd

TOTAL_COMPILERS = 5
TOTAL_PARSERS = 5

UMO_INSTITUTION_ID = "umo"
FACULTY_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "Faculty")


def pipeline(steps: Union[int, list[int]] = None) -> None:
    """
    Run the full UMO faculty data scraping pipeline, or specific steps of the pipeline.

    Args:
        steps: A single int value specifying which step to start at, or a list of ints specifying which steps to perform. If None, all steps will be performed.
    """
    STEPS = [step_1, step_2]
    if steps is None:
        step_choices = STEPS
    elif type(steps) == int:
        step_choices = [STEPS[i] for i in range(steps - 1, len(STEPS))]
    elif type(steps) == list:
        step_choices = [STEPS[i] for i in steps]
    else:
        print("Invalid type for 'steps' arg. No steps were performed.")
        return

    for step in step_choices:
        step()


def step_1():
    # Output .csv files containing links to faculty biography pages
    compiler_names = ["bc" + str(i + 1) for i in range(TOTAL_COMPILERS)]
    for idx, name in enumerate(
        tqdm(compiler_names, "Gathering biography links", total=len(compiler_names))
    ):
        module = importlib.import_module(
            f"scraping.umo.parsers.biography_compilers.{name}"
        )
        compiler_class = getattr(module, f"B{idx+1}Compiler")
        compiler_class(COMPILER_OUTPUT_DIR).collect()


def step_2():
    # Scrape faculty biography pages and build "Faculty" and "Publication" dataclass instances
    all_fac_instances: List[Faculty] = []
    all_pub_instances: List[List[Publication]] = []
    parser_names = ["bp" + str(i + 1) for i in range(TOTAL_PARSERS)]
    for idx, name in enumerate(
        tqdm(parser_names, "Scraping biographys", total=len(parser_names))
    ):
        module = importlib.import_module(
            f"scraping.umo.parsers.biography_parsers.{name}"
        )
        parser_class = getattr(module, f"B{idx+1}Parser")
        fac_instances, pub_instances = parser_class(COMPILER_OUTPUT_DIR).parse()
        all_fac_instances += fac_instances
        all_pub_instances += pub_instances

    assert len(all_fac_instances) == len(all_pub_instances)
    return all_fac_instances, all_pub_instances


def convert_faculty_to_json_records(faculty_instances: List[Faculty]) -> List[Dict]:
    """
    Convert Faculty dataclass instances to JSON records with MV attributes as arrays.

    Args:
        faculty_instances: List of Faculty dataclass instances

    Returns:
        List of faculty dictionaries ready for JSON output
    """
    records = []

    for fac in faculty_instances:
        emails = []
        if fac.email:
            if isinstance(fac.email, list):
                emails = [e for e in fac.email if e]
            else:
                emails = [fac.email]

        phones = []
        if fac.phone_num:
            if isinstance(fac.phone_num, list):
                phones = [p for p in fac.phone_num if p]
            else:
                phones = [fac.phone_num]

        departments = []
        if fac.department:
            if isinstance(fac.department, list):
                departments = [d for d in fac.department if d]
            else:
                departments = [fac.department]

        titles = []
        if fac.title:
            if isinstance(fac.title, list):
                titles = [t for t in fac.title if t]
            else:
                titles = [fac.title]

        record = {
            "first_name": fac.first_name,
            "last_name": fac.last_name,
            "biography": fac.biography,
            "orcid": fac.orcid,
            "google_scholar_url": fac.google_scholar_url,
            "research_gate_url": fac.research_gate_url,
            "scraped_from": fac.scraped_from,
            "emails": emails,
            "phones": phones,
            "departments": departments,
            "titles": titles,
            "institution_id": UMO_INSTITUTION_ID,
            "start_date": date.today().isoformat(),
            "end_date": None,
        }

        records.append(record)

    return records


def convert_publications_to_json_records(
    faculty_instances: List[Faculty], publication_instances: List[List[Publication]]
) -> List[Dict]:
    """
    Convert Publication dataclass instances to JSON records.

    Args:
        faculty_instances: List of Faculty dataclass instances (aligned with publication_instances)
        publication_instances: List of lists of Publication instances

    Returns:
        List of publication records stored as dicts
    """
    publication_records = []

    for fac_idx, pub_list in enumerate(publication_instances):
        if fac_idx >= len(faculty_instances):
            continue

        fac = faculty_instances[fac_idx]
        fac["faculty_id"] = _generate_faculty_id(
            first_name=fac.first_name,
            last_name=fac.last_name,
            scraped_from=fac.scraped_from,
        )
        for pub in pub_list:
            year = None
            if pub.year is not None:
                if isinstance(pub.year, int):
                    year = pub.year
                elif isinstance(pub.year, str) and pub.year.isdigit():
                    year = int(pub.year)

            citation_count = None
            if pub.citation_count is not None:
                if isinstance(pub.citation_count, int):
                    citation_count = pub.citation_count
                elif (
                    isinstance(pub.citation_count, str) and pub.citation_count.isdigit()
                ):
                    citation_count = int(pub.citation_count)

            pub_record = {
                "written_by": fac["faculty_id"],
                "doi": pub.doi,
                "title": pub.title,
                "abstract": pub.abstract,
                "year": year,
                "citation_count": citation_count,
                "publisher": pub.publisher,
            }
            publication_records.append(pub_record)

    return publication_records


def scrape_umo(
    output_dir: str = "scraping/out",
) -> Tuple[Institution, List[Dict], List[Dict]]:
    """
    Scrape UMO faculty data and return institution, faculty, and publication records.

    Args:
        output_dir: Directory to write output files (default: scraping/out)

    Returns:
        Tuple of (Institution, faculty_records, publication_records)
    """
    os.makedirs(output_dir, exist_ok=True)

    inst = umaine

    print("[INFO] Step 1: Gathering biography links...")
    step_1()

    print("[INFO] Step 2: Scraping biography pages...")
    all_fac_instances, all_pub_instances = step_2()

    filtered_faculty = []
    filtered_pub_instances = []
    for fac, pubs in zip(all_fac_instances, all_pub_instances):
        if fac.first_name and fac.first_name.strip():
            if not _is_junk_name(
                fac
            ):  # Filter out any "first names" that are probably not names
                filtered_faculty.append(fac)
                filtered_pub_instances.append(pubs)

    seen = set()
    unique_faculty = []
    unique_pub_instances = []
    for fac, pubs in zip(filtered_faculty, filtered_pub_instances):
        key = (fac.first_name, fac.last_name, fac.email)
        if key not in seen:
            seen.add(key)
            unique_faculty.append(fac)
            unique_pub_instances.append(pubs)

    print(
        f"[INFO] Filtered out {len(all_fac_instances)} faculty -> Now have {len(unique_faculty)} faculty."
    )

    faculty_records = convert_faculty_to_json_records(unique_faculty)
    publication_records = convert_publications_to_json_records(
        unique_faculty, unique_pub_instances
    )

    return inst, faculty_records, publication_records


# Util function to identify possible junk names
def _is_junk_name(fac: Faculty, threshold: float = 0.6) -> bool:
    first_name = fac.first_name
    if not first_name:
        raise ValueError(
            f"No first_name attribute when trying to test for junk name for faculty: {fac}"
        )
    parts = first_name.split()
    if len(parts) < 5:
        return False
    if len(first_name) <= 40:
        return False

    email = fac.email
    if email or email.strip() == "":
        return False

    candidate = f"{parts[0].lower()}.{parts[-1].lower()}"
    username = email.split("@")[0].lower()
    sim = SequenceMatcher(None, candidate, username).ratio()
    return sim < threshold


# Util function (borrowed from insert.py) since a uuid is needed now to ensure join table is correct
def _generate_faculty_id(first_name: str, last_name: str, scraped_from: str) -> str:
    """
    Generate deterministic UUID for a faculty member.

    Args:
        first_name: Faculty first name
        last_name: Faculty last name
        scraped_from: Source URL for the faculty data

    Returns:
        UUID string
    """
    if not first_name:
        raise ValueError("Faculty first_name is required for UUID generation")

    identifier = f"{first_name}:{last_name}:{scraped_from}".strip(":")
    return str(uuid.uuid5(FACULTY_NAMESPACE, identifier))


def write_publications_jsonl(publication_records: List[Dict], output_path: str):
    """Write publication records to a JSONL file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for record in publication_records:
            json_line = json.dumps(record, ensure_ascii=False)
            f.write(json_line + "\n")


def main(output_dir: str = "scraping/out"):
    """
    Main function to scrape UMO data and output JSON files.

    Args:
        output_dir: Directory to write output files (default: scraping/out)

    Returns:
        Tuple of (faculty_output, institution_output, publications_output)
    """
    inst, faculty_records, publication_records = scrape_umo(output_dir)
    print(f"[INFO] Scraped {len(faculty_records)} faculty records")
    print(f"[INFO] Scraped {len(publication_records)} publication records")

    faculty_output = os.path.join(output_dir, "umo_faculty.jsonl")
    write_faculty_jsonl(faculty_records, faculty_output)
    print(f"[INFO] Wrote: {faculty_output}")

    institution_output = os.path.join(output_dir, "umo_institution.json")
    institution_dict = {
        "institution_id": inst.institution_id,
        "name": inst.name,
        "website_url": inst.website_url,
        "type": inst.institution_type,
        "street_addr": inst.street_addr,
        "city": inst.city,
        "state": inst.state,
        "country": inst.country,
        "zip": inst.zip_code,
    }
    write_institution_json(institution_dict, institution_output)
    print(f"[INFO] Wrote: {institution_output}")

    publications_output = os.path.join(output_dir, "umo_publications.jsonl")
    write_publications_jsonl(publication_records, publications_output)
    print(f"[INFO] Wrote: {publications_output}")

    return faculty_output, institution_output, publications_output


if __name__ == "__main__":
    main()
