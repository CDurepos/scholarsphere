"""
Author(s): Aidan Bell, Clayton Durepos, Abby Pitcairn
"""

#!/usr/bin/env python3
"""
Data insertion script for scraped JSON data.

Reads JSON/JSONL files from scraping/out directory and inserts all data into
the database using stored procedures. Generates random UUIDs for
institutions, faculty, and publications using UUID v4.

Usage:
    python scraping/insert.py
"""

import os
import sys
from tqdm import tqdm
from pathlib import Path

# Add parent directory to path for imports (must be before backend imports)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models.qwen import (
    generate_faculty_keywords_with_qwen,
    generate_publication_keywords_with_qwen,
    unload_qwen_model,
)

import json
import uuid
import csv
from typing import List, Dict, Any, Optional, Tuple
from datetime import date

import mysql.connector
from mysql.connector import Error, pooling
from scraping.scrape_config import ScrapeConfig


class DatabaseConnection:
    """Manages database connections and stored procedure calls."""

    def __init__(self, db_config: Dict[str, Any]):
        """Initialize database connection pool."""
        self.db_config = db_config
        self.connection_pool = None
        self._init_connection_pool()

    def _init_connection_pool(self):
        """Create MySQL connection pool."""
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="scholarsphere_pool",
                pool_size=5,
                pool_reset_session=True,
                **self.db_config,
            )
        except Error as e:
            raise ConnectionError(f"Failed to create connection pool: {e}")

    def get_connection(self):
        """Get a connection from the pool."""
        try:
            return self.connection_pool.get_connection()
        except Error as e:
            raise ConnectionError(f"Failed to get connection from pool: {e}")

    def call_procedure(
        self, cursor, procedure_name: str, args: tuple
    ) -> Optional[Dict[str, Any]]:
        """
        Call a stored procedure and return the result.

        Args:
            cursor: Database cursor
            procedure_name: Name of the procedure to call
            args: Arguments to pass to the procedure

        Returns:
            Result from the procedure call as dict, or None if no result
        """
        cursor.callproc(procedure_name, args)
        for result in cursor.stored_results():
            columns = [desc[0] for desc in result.description]
            row = result.fetchone()
            if row:
                return dict(zip(columns, row))
        return None


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load a JSONL file and return list of records."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records




def find_scraped_files(output_dir: str) -> Tuple[List[str], List[str]]:
    """
    Find all scraped JSON/JSONL files in the output directory.

    Args:
        output_dir: Directory to search for files

    Returns:
        Tuple of (faculty_files, publication_files)
    """
    faculty_files = []
    publication_files = []

    if not os.path.exists(output_dir):
        print(f"[ERROR] Output directory does not exist: {output_dir}")
        return faculty_files, publication_files

    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        if filename.endswith("_faculty.jsonl"):
            faculty_files.append(filepath)
        elif filename.endswith("_publications.jsonl"):
            publication_files.append(filepath)

    return sorted(faculty_files), sorted(publication_files)


def generate_institution_id() -> str:
    """
    Generate random UUID for an institution.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def generate_publication_id() -> str:
    """
    Generate random UUID for a publication.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def generate_faculty_id() -> str:
    """
    Generate random UUID for a faculty member.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def get_institutions_from_json() -> List[Dict[str, Any]]:
    """
    Load institutions from the data/institutions.json file.
    Returns a list of institution dictionaries.
    """
    # Get the path to the JSON file (data/institutions.json at project root)
    project_root = Path(__file__).parent.parent
    json_path = project_root / "data" / "institutions.json"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] institutions.json not found at {json_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error parsing institutions.json: {e}")
        return []


def insert_all_institutions_from_json(db: DatabaseConnection):
    """
    Insert all institutions from data/institutions.json into the database.
    
    Args:
        db: DatabaseConnection instance
    """
    institutions = get_institutions_from_json()
    
    if not institutions:
        return
    
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    for institution_data in tqdm(institutions, desc="Inserting institutions"):
        institution_name = institution_data.get('name')
        
        # Check if institution already exists
        cursor.execute(
            "SELECT institution_id FROM institution WHERE name = %s",
            (institution_name.strip(),)
        )
        result = cursor.fetchone()
        
        if result:
            # Institution already exists, skip
            continue
        
        # Generate unique institution_id
        institution_id = str(uuid.uuid4())
        
        cursor.callproc(
            "create_institution",
            (
                institution_id,
                institution_data.get('name'),
                institution_data.get('street_addr'),
                institution_data.get('city'),
                institution_data.get('state'),
                institution_data.get('country', 'USA'),
                institution_data.get('zip'),
                institution_data.get('website_url'),
                institution_data.get('type'),
            )
        )
        
        # Consume any result set
        try:
            stored_results = list(cursor.stored_results())
            if stored_results:
                stored_results[0].fetchall()
        except:
            pass
        
        print(f"[OK] Inserted institution: {institution_name} ({institution_id})")
    
    conn.commit()
    cursor.close()
    conn.close()


def get_or_create_institution_by_name(
    institution_name: str, db: DatabaseConnection, cursor=None
) -> Optional[str]:
    """
    Get or create an institution in the database by name.
    
    First checks if the institution exists in the DB by name.
    If not found, looks it up in the JSON file and creates it in the DB.
    If not found in JSON, uses the scraped data if provided.
    
    Args:
        institution_name: Name of the institution
        db: DatabaseConnection instance
        cursor: Optional database cursor (if provided, won't close it)
    
    Returns:
        str: institution_id (UUID) if found/created, None otherwise
    """
    if not institution_name or not institution_name.strip():
        return None
    
    institution_name = institution_name.strip()
    should_close_conn = cursor is None
    
    try:
        if cursor is None:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
        else:
            conn = None
        
        # First, check if institution exists in DB
        cursor.execute(
            "SELECT institution_id FROM institution WHERE name = %s",
            (institution_name,)
        )
        result = cursor.fetchone()
        
        if result:
            return result['institution_id']
        
        # Institution not in DB - look it up in JSON
        institutions = get_institutions_from_json()
        institution_data = None
        
        for inst in institutions:
            if inst.get('name') == institution_name:
                institution_data = inst
                break
        
        # If not found in JSON, we'll use scraped data (handled by caller)
        if not institution_data:
            return None
        
        # Create the institution in the database using JSON data
        institution_id = str(uuid.uuid4())
        
        cursor.callproc(
            "create_institution",
            (
                institution_id,
                institution_data.get('name'),
                institution_data.get('street_addr'),
                institution_data.get('city'),
                institution_data.get('state'),
                institution_data.get('country', 'USA'),
                institution_data.get('zip'),
                institution_data.get('website_url'),
                institution_data.get('type'),
            )
        )
        # Consume any result set
        try:
            stored_results = list(cursor.stored_results())
            if stored_results:
                stored_results[0].fetchall()
        except:
            pass
        
        # Only commit if we created our own connection
        if conn:
            conn.commit()
        
        return institution_id
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[ERROR] Error in get_or_create_institution_by_name: {str(e)}")
        return None
    finally:
        if should_close_conn:
            if cursor:
                cursor.close()
            if conn:
                conn.close()



def insert_faculty_record(
    record: Dict[str, Any], db: DatabaseConnection
) -> bool:
    """
    Insert a single faculty record into the database.

    Args:
        record: Faculty dictionary with MV attributes as arrays
        db: DatabaseConnection instance

    Returns:
        True if insertion is successful, else False
    """
    conn = None
    cursor = None

    try:
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()

        scraped_from = record.get("scraped_from", "")

        existing_fac_id = record.get("faculty_id", None)
        faculty_id = (
            existing_fac_id
            if existing_fac_id
            else generate_faculty_id()
        )
        # TODO: This is not a great idea. The scrapers themselves should generate the faculty-keyword relationships (like written_by in publications schema).
        record["faculty_id"] = faculty_id # Store the faculty_id in the record for later use (in the keyword insertion).

        first_name = record.get("first_name")
        last_name = record.get("last_name")

        db.call_procedure(
            cursor,
            "create_faculty",
            (
                faculty_id,
                first_name,
                last_name,
                record.get("biography"),
                record.get("orcid"),
                record.get("google_scholar_url"),
                record.get("research_gate_url"),
                scraped_from,
            ),
        )
        # Consume result set
        try:
            stored_results = list(cursor.stored_results())
            if stored_results:
                stored_results[0].fetchall()
        except:
            pass

        emails = record.get("emails", []) or []
        for email in emails:
            if email:
                db.call_procedure(cursor, "create_faculty_email", (faculty_id, email))
                # Consume result set
                try:
                    stored_results = list(cursor.stored_results())
                    if stored_results:
                        stored_results[0].fetchall()
                except:
                    pass

        phones = record.get("phones", []) or []
        for phone in phones:
            if phone:
                db.call_procedure(cursor, "create_faculty_phone", (faculty_id, phone))
                # Consume result set
                try:
                    stored_results = list(cursor.stored_results())
                    if stored_results:
                        stored_results[0].fetchall()
                except:
                    pass

        departments = record.get("departments", []) or []
        for dept in departments:
            if dept:
                db.call_procedure(
                    cursor, "create_faculty_department", (faculty_id, dept)
                )
                # Consume result set
                try:
                    stored_results = list(cursor.stored_results())
                    if stored_results:
                        stored_results[0].fetchall()
                except:
                    pass

        titles = record.get("titles", []) or []
        for title in titles:
            if title:
                db.call_procedure(cursor, "create_faculty_title", (faculty_id, title))
                # Consume result set
                try:
                    stored_results = list(cursor.stored_results())
                    if stored_results:
                        stored_results[0].fetchall()
                except:
                    pass

        # Handle institution relationship
        # Support both new format (institution_name)
        institution_name = record.get("institution_name")
        
        start_date = record.get("start_date")
        if institution_name:
            # Get or create institution by name (looks up in data/institutions.json)
            db_institution_id = get_or_create_institution_by_name(
                institution_name, db, cursor
            )
            if db_institution_id and start_date:
                end_date = record.get("end_date")
                db.call_procedure(
                    cursor,
                    "create_faculty_works_at_institution",
                    (faculty_id, db_institution_id, start_date, end_date),
                )
                # Consume result set
                try:
                    stored_results = list(cursor.stored_results())
                    if stored_results:
                        stored_results[0].fetchall()
                except:
                    pass

        conn.commit()
        return True

    except Exception as e:
        if conn and conn.in_transaction:
            conn.rollback()
        print(
            f"[ERROR] Failed to insert faculty {record.get('first_name')} {record.get('last_name')}: {str(e)}"
        )
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_publication_record(
    record: Dict[str, Any], db: DatabaseConnection
) -> Optional[str]:
    """
    Insert publication record into the database.
    NOTE: This function will also take care of inserting
    into the join table between faculty and publication.

    Args:
        record: Publication dictionary
        db: DatabaseConnection instance

    Returns:
        The institution_id that was used, or None if failed
    """
    conn = None
    cursor = None

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        author_uuid = record["written_by"]
        publication_id = generate_publication_id()
        title = record.get("title", "")
        # Crop title to 128 characters if it exceeds the limit
        if title and len(title) > 128:
            title = title[:128]

        db.call_procedure(
            cursor,
            "add_publication_for_faculty",
            (
                author_uuid,
                publication_id,
                title,
                record.get("publisher"),
                record.get("year"),
                record.get("doi"),
                record.get("abstract"),
                record.get("citation_count"),
            ),
        )

        conn.commit()
        print(f"[OK] Inserted publication: {title} ({publication_id})")
        return publication_id

    except Exception as e:
        if conn and conn.in_transaction:
            conn.rollback()
        print(f"[ERROR] Failed to insert publication {record.get('title')}: {str(e)}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_faculty_researches_keyword(
    faculty_record: Dict[str, Any], db: DatabaseConnection
) -> Optional[str]:
    """
    Given a faculty record, generate a list of keywords from the biography and insert them 
    into the database. Then, insert the faculty-keyword relationships into the join table.

    Args:
        faculty_record: Faculty dictionary
        db: DatabaseConnection instance

    Returns:
        True if insertion is successful, else False
    """

    keywords = []
    try:
        if faculty_record.get("faculty_id") is None or faculty_record.get("faculty_id").strip() == "":
            raise ValueError(f"At keyword insertion time, faculty ID is None for faculty: {faculty_record}")
        if not isinstance(faculty_record.get("faculty_id"), str):
            raise ValueError(f"At keyword insertion time, faculty ID is not a string for faculty: {faculty_record}")
        biography = faculty_record.get("biography")
        keywords = generate_faculty_keywords_with_qwen(biography, num_keywords=5)

    except Exception as e:
        print(f"[ERROR] Failed to generate keywords for faculty {faculty_record.get('first_name')} {faculty_record.get('last_name')}: {str(e)}")
        return False

    conn = None
    cursor = None
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        for keyword in keywords:
            db.call_procedure(cursor, "add_keyword_for_faculty", (faculty_record["faculty_id"], keyword))

        conn.commit()

    except Exception as e:
        if conn and conn.in_transaction:
            conn.rollback()
        print(f"[ERROR] Failed to insert keywords for faculty {faculty_record.get('first_name')} {faculty_record.get('last_name')}: {str(e)}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return True


def insert_publication_explores_keyword(
    publication_id: str, abstract: str, db: DatabaseConnection
) -> bool:
    """
    Given a publication, generate a list of keywords from the abstract and insert them
    into the database using the publication_explores_keyword join table.

    Args:
        publication_id: The UUID of the publication
        abstract: The abstract of the publication
        db: DatabaseConnection instance

    Returns:
        True if insertion is successful, else False
    """
    if not publication_id or not publication_id.strip():
        print("[ERROR] Publication ID is required for keyword insertion")
        return False

    if not abstract or not abstract.strip():
        # No abstract means no keywords to generate
        return True

    keywords = []
    try:
        keywords = generate_publication_keywords_with_qwen(abstract, num_keywords=5)
    except Exception as e:
        print(f"[ERROR] Failed to generate keywords for publication {publication_id}: {str(e)}")
        return False

    if not keywords:
        "TODO: This is will throw off the successful insertion count. Edit this and check other insert methods too."
        return True  # No keywords generated, but not an error

    conn = None
    cursor = None
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        for keyword in keywords:
            db.call_procedure(
                cursor, "add_keyword_for_publication", (publication_id, keyword)
            )
            # Consume result set
            try:
                stored_results = list(cursor.stored_results())
                if stored_results:
                    stored_results[0].fetchall()
            except:
                pass

        conn.commit()

    except Exception as e:
        if conn and conn.in_transaction:
            conn.rollback()
        print(f"[ERROR] Failed to insert keywords for publication {publication_id}: {str(e)}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return True


def insert_equipment_record(
    record: Dict[str, Any], db: DatabaseConnection
) -> bool:
    """
    Insert a single equipment record into the database.

    Args:
        record: Equipment dictionary with name, description, availability, institution_name
        db: DatabaseConnection instance

    Returns:
        True if insertion is successful, else False
    """
    conn = None
    cursor = None

    try:
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()

        name = record.get("name")
        description = record.get("description", "")
        availability = record.get("availability", "")
        institution_name = record.get("institution_name")

        # Validate required fields
        if not name or not name.strip():
            print(f"[WARN] Equipment name is required. Skipping equipment record.")
            return False

        if not availability or not availability.strip():
            print(f"[WARN] Equipment availability is required. Skipping equipment '{name}'.")
            return False

        # Look up institution_id from institution_name
        institution_id = None
        if institution_name:
            cursor.execute(
                "SELECT institution_id FROM institution WHERE name = %s",
                (institution_name.strip(),)
            )
            result = cursor.fetchone()
            if result:
                institution_id = result['institution_id']
            else:
                print(f"[WARN] Institution '{institution_name}' not found in database. Skipping equipment '{name}'")
                return False
        else:
            print(f"[WARN] No institution_name provided for equipment '{name}'. Skipping.")
            return False

        # Generate unique equipment_id
        equipment_id = str(uuid.uuid4())

        # Truncate fields to match database constraints
        name = name.strip()[:64] if len(name.strip()) > 64 else name.strip()
        description = description.strip()[:2048] if len(description.strip()) > 2048 else description.strip()
        availability = availability.strip()[:2048] if len(availability.strip()) > 2048 else availability.strip()

        # Call create_equipment stored procedure
        db.call_procedure(
            cursor,
            "create_equipment",
            (
                equipment_id,
                name,
                description if description else None,
                availability,
                institution_id
            )
        )
        
        # Consume result set
        try:
            stored_results = list(cursor.stored_results())
            if stored_results:
                stored_results[0].fetchall()
        except:
            pass

        conn.commit()
        print(f"[OK] Inserted equipment: {name} ({equipment_id})")
        return True

    except Exception as e:
        if conn and conn.in_transaction:
            conn.rollback()
        print(
            f"[ERROR] Failed to insert equipment {record.get('name', 'unknown')}: {str(e)}"
        )
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_equipment_from_csv(db: DatabaseConnection) -> bool:
    """
    Insert equipment records from scraping/equipment/equipment_demo.csv into the database.
    
    Reads the CSV file and for each equipment record:
    - Generates a unique equipment_id
    - Looks up the institution_id from the institution table using institution_name
    - Creates equipment records using the create_equipment stored procedure
    
    Args:
        db: DatabaseConnection instance
    
    Returns:
        True if at least one insertion is successful, else False
    """
    # Get the path to the CSV file
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "scraping" / "equipment" / "equipment_demo.csv"
    
    if not csv_path.exists():
        print(f"[ERROR] Equipment CSV file not found at {csv_path}")
        return False
    
    successful = 0
    failed = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Read CSV, skipping comment lines
            reader = csv.DictReader(
                (line for line in f if not line.strip().startswith('#') and line.strip())
            )
            
            records = list(reader)
            total_records = len(records)
            
            for record in tqdm(records, total=total_records, desc="Inserting equipment records"):
                success = insert_equipment_record(record, db)
                if success:
                    successful += 1
                else:
                    failed += 1
        
        print(f"\n[INFO] Equipment insertion complete: {successful} successful, {failed} failed")
        return successful > 0
        
    except Exception as e:
        print(f"[ERROR] Failed to process equipment CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main insertion function."""
    output_dir = "scraping/out"

    print("\n" + "=" * 60)
    print("ScholarSphere Data Insertion")
    print("=" * 60)

    db = DatabaseConnection(ScrapeConfig.DB_CONFIG)
    faculty_files, publication_files = find_scraped_files(output_dir)

    if not faculty_files:
        print(f"[ERROR] No scraped files found in {output_dir}")
        print("[INFO] Run scraping/scrape.py first to generate data files")
        sys.exit(1)

    print(f"\n[INFO] Found {len(faculty_files)} faculty file(s)")
    print(f"[INFO] Found {len(publication_files)} publication file(s)")
    print("[INFO] Institutions will be loaded from data/institutions.json")

    print("\n" + "=" * 60)
    print("Step 0: Inserting Institutions from JSON")
    print("=" * 60)

    insert_all_institutions_from_json(db)

    print("\n" + "=" * 60)
    print("Step 1: Inserting Faculty Records")
    print("=" * 60)

    total_stats = {
        "total_records": 0,
        "successful": 0,
        "failed": 0,
    }

    for faculty_file in faculty_files:
        if not os.path.exists(faculty_file):
            print(f"[WARN] File not found: {faculty_file}")
            continue

        try:
            print(f"\n[INFO] Processing {faculty_file}...")
            records = load_jsonl(faculty_file)
            total_stats["total_records"] += len(records)

            for i, record in tqdm(enumerate(records, start=1), total=len(records), desc="Inserting faculty records"):
                success = insert_faculty_record(record, db)
                if success:
                    total_stats["successful"] += 1
                    # Insert keywords for this faculty member
                    biography = record.get("biography")
                    if biography and biography.strip() != "":
                        keyword_success = insert_faculty_researches_keyword(record, db)
                        if not keyword_success:
                            print(f"[WARN] Failed to insert keywords for faculty {record.get('first_name')} {record.get('last_name')}")
                else:
                    total_stats["failed"] += 1

                if i % 10 == 0:
                    print(
                        f"[INFO] Processed {i}/{len(records)} records from {os.path.basename(faculty_file)}"
                    )

            print(f"[OK] Completed {faculty_file}: {len(records)} records processed")
        except Exception as e:
            print(f"[ERROR] Failed to process {faculty_file}: {e}")
            import traceback

            traceback.print_exc()
            if "records" in locals():
                total_stats["failed"] += len(records)

    print("\n" + "=" * 60)
    print("Insertion Summary")
    print("=" * 60)
    print(f"Faculty Records:")
    print(f"  - Total: {total_stats['total_records']}")
    print(f"  - Successful: {total_stats['successful']}")
    print(f"  - Failed: {total_stats['failed']}")

    if total_stats["failed"] > 0:
        print(
            f"\n[WARN] {total_stats['failed']} records failed to insert. Check errors above."
        )

    print("\n" + "=" * 60)
    print("Step 4: Inserting Publication Records")
    print("=" * 60)

    publications_inserted = 0
    for pub_file in publication_files:
        if not os.path.exists(pub_file):
            print(f"[WARN] File not found: {pub_file}")
            continue

        try:
            print(f"\n[INFO] Processing {pub_file}...")
            publications = load_jsonl(pub_file)
            
            for publication in tqdm(publications, total=len(publications), desc="Inserting publication records"):
                publication_id = insert_publication_record(publication, db)
                if publication_id:
                    publications_inserted += 1
                    # Insert keywords for this publication
                    abstract = publication.get("abstract")
                    if abstract and abstract.strip():
                        keyword_success = insert_publication_explores_keyword(
                            publication_id, abstract, db
                        )
                        if not keyword_success:
                            print(f"[WARN] Failed to insert keywords for publication {publication.get('title')}")
        except Exception as e:
            print(f"[ERROR] Failed to process {pub_file}: {e}")
            import traceback

            traceback.print_exc()

    # Unload model after all keywords (faculty + publication) have been generated
    print("\n[INFO] Unloading model from memory...")
    try:
        unload_qwen_model()
        print("[OK] Model unloaded successfully")
    except Exception as e:
        print(f"[WARN] Failed to unload model: {str(e)}")

    print(f"\n[INFO] Inserted {publications_inserted} publications")

    print("\n" + "=" * 60)
    print("Step 3: Inserting Equipment Records")
    print("=" * 60)

    try:
        insert_equipment_from_csv(db)
    except Exception as e:
        print(f"[ERROR] Failed to insert equipment: {e}")
        import traceback
        traceback.print_exc()

    print("\n[INFO] Data insertion complete!")


if __name__ == "__main__":
    main()
