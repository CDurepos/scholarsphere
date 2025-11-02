import csv
from typing import List, Any
from dataclasses import fields, is_dataclass

def dataclass_instances_to_csv(dataclass_instances: List[Any], output_path: str, overwrite: bool = False) -> None:
    """
    Args:
        dataclass_instances (List[Any]): List of dataclass instances. All instances must be of the same dataclass type.
        output_path (str): Path to output the .csv file.
        overwrite (bool) (default = false): If True, output .csv file will be overwritten if it already exists.
    """
    if not dataclass_instances:
        return
    
    # Type safety
    first_item = dataclass_instances[0]
    if not is_dataclass(first_item):
        raise TypeError(f"Expected dataclass instances, got {type(first_item)}")
    
    first_type = type(first_item)
    if not all(isinstance(x, first_type) for x in dataclass_instances):
        raise ValueError("All instances must be of the same dataclass type")

    # Get column headers from dataclass field names
    headers = [f.name for f in fields(type(dataclass_instances[0]))]
    with open(output_path, mode="w" if overwrite else "x", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for inst in dataclass_instances:
            writer.writerow([getattr(inst, name) for name in headers])