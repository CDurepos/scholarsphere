from scraping.umo.dataclass_instances.orono import umaine

import importlib
from tqdm import tqdm

# Output .csv files containing links to faculty biography pages
compiler_names = ["bc1", "bc2", "bc3", "bc4", "bc5"]
for name in tqdm(compiler_names, "Gathering biography links.", total = len(compiler_names)):
    module = importlib.import_module(f"scraping.UMO.parsers.biography_compilers.{name}")
    compiler_class = getattr(module, f"B{name[1:].capitalize()}Compiler")
    compiler_class().collect()

# Scrape faculty biography pages and build "Faculty" and "Publication" dataclass instances
# add uuids here

# Clean data and write results to .csv