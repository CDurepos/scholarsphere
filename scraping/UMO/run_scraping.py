import importlib
from tqdm import tqdm

compiler_names = ["bc1", "bc2", "bc3", "bc4", "bc5"]

for name in tqdm(compiler_names, "Gathering biography links.", total = len(compiler_names)):
    module = importlib.import_module(f"scraping.UMO.parsers.biography_compilers.{name}")
    compiler_class = getattr(module, f"B{name[1:].capitalize()}Compiler")
    compiler_class().collect()