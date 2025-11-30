#!/usr/bin/env python3
"""
Data insertion script for scraped JSON data.

Reads JSON/JSONL files from scraping/out directory and inserts all data into
the database using stored procedures. Generates random UUIDs for
institutions, faculty, and publications using UUID v4.

Usage:
    python scraping/insert.py
"""
from backend.app.utils.llama import generate_keywords_with_llama, unload_model

import os
import sys
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import date

import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Database configuration from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "scholarsphere"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": False,
}


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


def load_json(file_path: str) -> Dict[str, Any]:
    """Load a JSON file and return dictionary."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_scraped_files(output_dir: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Find all scraped JSON/JSONL files in the output directory.

    Args:
        output_dir: Directory to search for files

    Returns:
        Tuple of (institution_files, faculty_files, publication_files)
    """
    faculty_files = []
    institution_files = []
    publication_files = []

    if not os.path.exists(output_dir):
        print(f"[ERROR] Output directory does not exist: {output_dir}")
        return institution_files, faculty_files, publication_files

    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        if filename.endswith("_faculty.jsonl"):
            faculty_files.append(filepath)
        elif filename.endswith("_institution.json"):
            institution_files.append(filepath)
        elif filename.endswith("_publications.jsonl"):
            publication_files.append(filepath)

    return sorted(institution_files), sorted(faculty_files), sorted(publication_files)


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
    Load institutions from the backend/data/institutions.json file.
    Returns a list of institution dictionaries.
    """
    # Get the path to the JSON file (backend/data/institutions.json)
    script_dir = Path(__file__).parent.parent
    json_path = script_dir / "backend" / "data" / "institutions.json"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] institutions.json not found at {json_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error parsing institutions.json: {e}")
        return []


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


def insert_institution_record(
    record: Dict[str, Any], db: DatabaseConnection
) -> Optional[str]:
    """
    Insert institution record into the database.
    
    Uses the new approach: checks if institution exists by name first,
    then looks in JSON file, then falls back to scraped data.

    Args:
        record: Institution dictionary
        db: DatabaseConnection instance

    Returns:
        The institution_id that was used, or None if failed
    """
    institution_name = record.get("name", "")
    if not institution_name:
        print("[ERROR] Institution record missing name")
        return None
    
    # Try to get or create from JSON first
    institution_id = get_or_create_institution_by_name(institution_name, db)
    
    if institution_id:
        print(f"[OK] Institution found/created from JSON: {institution_name} ({institution_id})")
        return institution_id
    
    # Not in JSON - create from scraped data
    conn = None
    cursor = None

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        institution_id = str(uuid.uuid4())

        db.call_procedure(
            cursor,
            "create_institution",
            (
                institution_id,
                record.get("name"),
                record.get("street_addr"),
                record.get("city"),
                record.get("state"),
                record.get("country", "USA"),
                record.get("zip"),
                record.get("website_url"),
                record.get("type"),
            ),
        )

        conn.commit()
        print(f"[OK] Inserted institution from scraped data: {institution_name} ({institution_id})")
        return institution_id

    except Exception as e:
        if conn and conn.in_transaction:
            conn.rollback()
        print(f"[ERROR] Failed to insert institution {record.get('name')}: {str(e)}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_faculty_record(
    record: Dict[str, Any], db: DatabaseConnection, institution_name_map: Dict[str, str]
) -> bool:
    """
    Insert a single faculty record into the database.

    Args:
        record: Faculty dictionary with MV attributes as arrays
        db: DatabaseConnection instance
        institution_name_map: Mapping from original institution_id to institution name

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

        # Handle institution relationship using the new approach
        original_institution_id = record.get("institution_id")
        start_date = record.get("start_date")
        if original_institution_id:
            # Get institution name from the map
            institution_name = institution_name_map.get(original_institution_id)
            if institution_name:
                # Get or create institution by name
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
        print(f"[ERROR] Failed to insert institution {record.get('name')}: {str(e)}")
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

    try:
        if faculty_record.get("faculty_id") is None or faculty_record.get("faculty_id").strip() == "":
            raise ValueError(f"At keyword insertion time, faculty ID is None for faculty: {faculty_record}")
        if not isinstance(faculty_record.get("faculty_id"), str):
            raise ValueError(f"At keyword insertion time, faculty ID is not a string for faculty: {faculty_record}")
        biography = faculty_record.get("biography")
        keywords = generate_keywords_with_llama(biography, num_keywords=5)

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

def main():
    """Main insertion function."""
    output_dir = "scraping/out"

    print("\n" + "=" * 60)
    print("ScholarSphere Data Insertion")
    print("=" * 60)

    db = DatabaseConnection(DB_CONFIG)
    institution_files, faculty_files, publication_files = find_scraped_files(output_dir)

    if not institution_files and not faculty_files:
        print(f"[ERROR] No scraped files found in {output_dir}")
        print("[INFO] Run scraping/scrape.py first to generate data files")
        sys.exit(1)

    print(f"\n[INFO] Found {len(institution_files)} institution file(s)")
    print(f"[INFO] Found {len(faculty_files)} faculty file(s)")

    print("\n" + "=" * 60)
    print("Step 1: Inserting Institutions")
    print("=" * 60)

    # Map from original institution_id to institution name (for faculty linking)
    institution_name_map: Dict[str, str] = {}
    institutions_inserted = 0

    for inst_file in institution_files:
        if not os.path.exists(inst_file):
            print(f"[WARN] File not found: {inst_file}")
            continue

        try:
            institution = load_json(inst_file)
            original_id = institution.get("institution_id")
            institution_name = institution.get("name", "")
            db_id = insert_institution_record(institution, db)

            if db_id:
                institutions_inserted += 1
                # Map original ID to institution name (for faculty records)
                if original_id and institution_name:
                    institution_name_map[original_id] = institution_name
        except Exception as e:
            print(f"[ERROR] Failed to process {inst_file}: {e}")
            import traceback

            traceback.print_exc()

    print(f"\n[INFO] Inserted {institutions_inserted} institutions")
    print(f"[INFO] Institution name mapping: {len(institution_name_map)} mappings created")

    print("\n" + "=" * 60)
    print("Step 2: Inserting Faculty Records")
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

            for i, record in enumerate(records, start=1):
                success = insert_faculty_record(record, db, institution_name_map)
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

    # Unload model and tokenizer from memory after all faculty keywords have been generated
    print("\n[INFO] Unloading model from memory...")
    try:
        unload_model()
        print("[OK] Model unloaded successfully")
    except Exception as e:
        print(f"[WARN] Failed to unload model: {str(e)}")

    print("\n" + "=" * 60)
    print("Insertion Summary")
    print("=" * 60)
    print(f"Institutions: {institutions_inserted} inserted")
    print(f"Faculty Records:")
    print(f"  - Total: {total_stats['total_records']}")
    print(f"  - Successful: {total_stats['successful']}")
    print(f"  - Failed: {total_stats['failed']}")

    if total_stats["failed"] > 0:
        print(
            f"\n[WARN] {total_stats['failed']} records failed to insert. Check errors above."
        )

    publications_inserted = 0
    for pub_file in publication_files:
        if not os.path.exists(pub_file):
            print(f"[WARN] File not found: {pub_file}")
            continue

        try:
            print(f"\n[INFO] Processing {pub_file}...")
            publications = load_jsonl(pub_file)
            
            for publication in publications:
                db_id = insert_publication_record(publication, db)
                if db_id:
                    publications_inserted += 1
        except Exception as e:
            print(f"[ERROR] Failed to process {pub_file}: {e}")
            import traceback

            traceback.print_exc()

    print(f"\n[INFO] Inserted {publications_inserted} publications")
    print("\n[INFO] Data insertion complete!")


if __name__ == "__main__":
    main()
