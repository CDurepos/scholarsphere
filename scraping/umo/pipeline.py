from scraping.umo.dataclass_instances.orono import umaine
from scraping.utils.conversion import dataclass_instances_to_csv
from scraping.schemas import Faculty, Publication, PublicationAuthoredByFaculty, Institution
from scraping.umo.processing.post_process_pipeline import post_process_faculty_csv
from scraping.utils.json_output import write_faculty_jsonl, write_institution_json

import os
import importlib
from tqdm import tqdm
from itertools import chain
from typing import Union, List, Any, Dict, Tuple
from datetime import date

# CFG
COMPILER_OUTPUT_DIR = os.path.join(
    "scraping", "umo", "scrape_storage", "biography_pages"
)  # Relative to cwd

TOTAL_COMPILERS = 5
TOTAL_PARSERS = 5

UMO_INSTITUTION_ID = "umo"


def pipeline(steps: Union[int, list[int]] = None) -> None:
    """
    Run the full UMO faculty data scraping pipeline, or specific steps of the pipeline.

    Args:
        steps: A single int value specifying which step to start at, or a list of ints specifying which steps to perform. If None, all steps will be performed.
    """
    STEPS = [step_1, step_2, step_3]
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
        # Convert MV attributes to arrays
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
            'first_name': fac.first_name,
            'last_name': fac.last_name,
            'biography': fac.biography,
            'orcid': fac.orcid,
            'google_scholar_url': fac.google_scholar_url,
            'research_gate_url': fac.research_gate_url,
            'scraped_from': fac.scraped_from,
            'emails': emails,
            'phones': phones,
            'departments': departments,
            'titles': titles,
            'institution_id': UMO_INSTITUTION_ID,
            'start_date': date.today().isoformat(),
            'end_date': None,
        }
        
        records.append(record)
    
    return records


def scrape_umo(output_dir: str = "scraping/out") -> Tuple[Institution, List[Dict]]:
    """
    Scrape UMO faculty data and return institution and faculty records.
    
    Args:
        output_dir: Directory to write output files (default: scraping/out)
    
    Returns:
        Tuple of (Institution, list) where list contains faculty dictionaries
        with all attributes including MV attributes as arrays.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Create institution
    inst = Institution(
        institution_id=UMO_INSTITUTION_ID,
        name=umaine.name,
        website_url=umaine.website_url,
        institution_type=umaine.institution_type,
        street_addr=umaine.street_addr,
        city=umaine.city,
        state=umaine.state,
        country=umaine.country,
        zip_code=umaine.zip_code,
    )
    
    # Run pipeline steps
    print("[INFO] Step 1: Gathering biography links...")
    step_1()
    
    print("[INFO] Step 2: Scraping biography pages...")
    all_fac_instances, all_pub_instances = step_2()
    
    # Filter out faculty without first names
    filtered_faculty = [f for f in all_fac_instances if f.first_name and f.first_name.strip()]
    
    # Remove duplicates (same first name, last name, and email)
    seen = set()
    unique_faculty = []
    for fac in filtered_faculty:
        key = (fac.first_name, fac.last_name, fac.email)
        if key not in seen:
            seen.add(key)
            unique_faculty.append(fac)
    
    print(f"[INFO] Filtered {len(all_fac_instances)} -> {len(unique_faculty)} unique faculty")
    
    # Convert to JSON records
    faculty_records = convert_faculty_to_json_records(unique_faculty)
    
    return inst, faculty_records


def main(output_dir: str = "scraping/out"):
    """
    Main function to scrape UMO data and output JSON files.
    
    Args:
        output_dir: Directory to write output files (default: scraping/out)
    """
    inst, faculty_records = scrape_umo(output_dir)
    print(f"[INFO] Scraped {len(faculty_records)} faculty records")
    
    # Write faculty JSONL file
    faculty_output = os.path.join(output_dir, "umo_faculty.jsonl")
    write_faculty_jsonl(faculty_records, faculty_output)
    print(f"[INFO] Wrote: {faculty_output}")
    
    # Write institution JSON file
    institution_output = os.path.join(output_dir, "umo_institution.json")
    institution_dict = {
        'institution_id': inst.institution_id,
        'name': inst.name,
        'website_url': inst.website_url,
        'type': inst.institution_type,
        'street_addr': inst.street_addr,
        'city': inst.city,
        'state': inst.state,
        'country': inst.country,
        'zip': inst.zip_code,
    }
    write_institution_json(institution_dict, institution_output)
    print(f"[INFO] Wrote: {institution_output}")
    
    return faculty_output, institution_output


if __name__ == "__main__":
    main()
