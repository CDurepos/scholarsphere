"""
Department name mapping for UMO scrapers.
Maps CSV filenames to proper department names.
"""

DEPARTMENT_NAME_MAP = {
    "marine_sciences": "Marine Sciences",
    "biomedical_science_and_engineering": "Biomedical Science and Engineering",
    "forest_resources": "Forest Resources",
    "biology_and_ecology": "Biology and Ecology",
    "physics_and_astronomy": "Physics and Astronomy",
    "business": "Business",
    "history": "History",
    "electrical_and_computer_engineering": "Electrical and Computer Engineering",
    "civil_and_environmental_engineering": "Civil and Environmental Engineering",
    "computing_and_information_science": "Computing and Information Science",
    "mechanical_engineering": "Mechanical Engineering",
    "engineering_technology": "Engineering Technology",
    "chemical_and_biomedical_engineering": "Chemical and Biomedical Engineering",
}


def get_department_name(filename: str) -> str:
    """
    Get the proper department name from a CSV filename.
    
    Args:
        filename: The CSV filename (e.g., "marine_sciences.csv" or just "marine_sciences")
    
    Returns:
        The proper department name, or the original filename if no mapping exists
    """
    # Remove .csv extension if present
    key = filename.replace(".csv", "") if filename.endswith(".csv") else filename
    # Remove path if present
    key = key.split("/")[-1].split("\\")[-1]
    
    return DEPARTMENT_NAME_MAP.get(key, key)

