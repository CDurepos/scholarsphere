from scraping.schemas import Faculty, Publication
from scraping.umo.dataclass_instances.orono import umaine
from scraping.utils.conversion import dataclass_instances_to_csv  

import os
import importlib
from tqdm import tqdm
from typing import Union, List, Any

# CFG
COMPILER_OUTPUT_DIR = os.path.join("scraping", "umo", "scrape_storage", "biography_pages") # Relative to cwd

TOTAL_COMPILERS = 5
TOTAL_PARSERS = 5

FAC_OUTPUT_DIR = os.path.join("scraping", "umo", "scrape_storage", "faculty_data", "faculty_data.csv")
PUB_OUTPUT_DIR = os.path.join("scraping", "umo", "scrape_storage", "publication_data", "publication_data.csv")
os.makedirs(os.path.dirname(FAC_OUTPUT_DIR), exist_ok=True)
os.makedirs(os.path.dirname(PUB_OUTPUT_DIR), exist_ok=True)

if os.path.exists(FAC_OUTPUT_DIR):
    raise FileExistsError(
        f"The output file '{FAC_OUTPUT_DIR}' already exists."
    )
if os.path.exists(PUB_OUTPUT_DIR):
    raise FileExistsError(
        f"The output file '{PUB_OUTPUT_DIR}' already exists."
    )

def pipeline(steps: Union[int, list[int]] = None)->None:
    """
    Run the full UMO faculty data scraping pipeline, or specific steps of the pipeline.

    Args:
        steps: A single int value specifying which step to start at, or a list of ints specifying which steps to perform. If None, all steps will be performed.
    """
    STEPS = [step_1, step_2, step_3, step_4]
    if steps is None:
        step_choices = STEPS
    elif type(steps) == int:
        step_choices = [STEPS[i] for i in range(steps-1, len(STEPS))]
    elif type(steps) == list:
        step_choices = [STEPS[i] for i in steps]
    else:
        print("Invalid type for 'steps' arg. No steps were performed.")
        return
    
    for step in step_choices:
        step()
    
def step_1():
    # Output .csv files containing links to faculty biography pages
    compiler_names = ["bc" + str(i+1) for i in range(TOTAL_COMPILERS)]
    for idx, name in enumerate(tqdm(compiler_names, "Gathering biography links", total = len(compiler_names))):
        module = importlib.import_module(f"scraping.umo.parsers.biography_compilers.{name}")
        compiler_class = getattr(module, f"B{idx+1}Compiler")
        compiler_class(COMPILER_OUTPUT_DIR).collect()

def step_2():
    # Scrape faculty biography pages and build "Faculty" and "Publication" dataclass instances
    all_fac_instances:List[Faculty] = []
    all_pub_instances:List[List[Publication]] = []
    parser_names = ["bp" + str(i+1) for i in range(TOTAL_PARSERS)]
    for idx, name in enumerate(tqdm(parser_names, "Scraping biographys", total = len(parser_names))):
        module = importlib.import_module(f"scraping.umo.parsers.biography_parsers.{name}")
        parser_class = getattr(module, f"B{idx+1}Parser")
        fac_instances, pub_instances = parser_class(COMPILER_OUTPUT_DIR).parse()
        all_fac_instances += fac_instances
        all_pub_instances += pub_instances

    # TODO: Make join table here, and then unwind publications (need uuid here?)
    dataclass_instances_to_csv(all_fac_instances, output_path=FAC_OUTPUT_DIR, overwrite=True)
    # dataclass_instances_to_csv(all_pub_instances, output_path=PUB_OUTPUT_DIR, overwrite=True)

def step_3():
    return

def step_4():
    return

if __name__ == "__main__":
    pipeline(2)
