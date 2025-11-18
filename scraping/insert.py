#!/usr/bin/env python3
"""
Data insertion script for scraped JSON data.

Reads JSON/JSONL files from scraping/out directory and inserts all data into
the database using stored procedures. Generates deterministic UUIDs for
institutions and faculty using UUID v5 with namespace strings.

Usage:
    python scraping/insert.py
"""

import os
import sys
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import mysql.connector
from mysql.connector import Error, pooling

# Namespace UUIDs for deterministic UUID generation (UUID v5)
FACULTY_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "Faculty")
INSTITUTION_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "Institution")
PUBLICATION_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "Publication")

# Database configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "user": "root",
    "password": "scholarsphere123",
    "database": "scholarsphere",
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


def find_scraped_files(output_dir: str) -> Tuple[List[str], List[str]]:
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
        return institution_files, faculty_files

    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        if filename.endswith("_faculty.jsonl"):
            faculty_files.append(filepath)
        elif filename.endswith("_institution.json"):
            institution_files.append(filepath)
        elif filename.endswith("_publications.jsonl"):
            publication_files.append(filepath)

    return sorted(faculty_files), sorted(institution_files), sorted(publication_files)


def generate_institution_id(name: str) -> str:
    """
    Generate deterministic UUID for an institution.

    Args:
        name: Institution name

    Returns:
        UUID string
    """
    if not name:
        raise ValueError("Institution name is required for UUID generation")
    return str(uuid.uuid5(INSTITUTION_NAMESPACE, name))

def generate_publication_id(title: str, written_by_uuid: str) -> str:
    """
    Generate deterministic UUID for a publication.

    Args:
        title: Publication title
        written_by_uuid: The UUID of the publication's author

    Returns:
        UUID string
    """
    if not title or not written_by_uuid:
        raise ValueError("Publication title and author UUID is required for UUID generation")
    identifier = f"{title}:{written_by_uuid}".strip(":")
    return str(uuid.uuid5(PUBLICATION_NAMESPACE, identifier))


def generate_faculty_id(first_name: str, last_name: str, scraped_from: str) -> str:
    """
    Generate deterministic UUID for a faculty member.

    Args:
        first_name: Faculty first name
        last_name: Faculty last name
        scraped_from: Source URL for the faculty data

    Returns:
        UUID string
    """
    if not first_name or not last_name or not scraped_from:
        raise ValueError("Faculty first_name, last_name, and scraped_from is required for UUID generation")

    identifier = f"{first_name}:{last_name}:{scraped_from}".strip(":")
    return str(uuid.uuid5(FACULTY_NAMESPACE, identifier))


def insert_institution_record(
    record: Dict[str, Any], db: DatabaseConnection
) -> Optional[str]:
    """
    Insert institution record into the database.

    Args:
        record: Institution dictionary
        db: DatabaseConnection instance

    Returns:
        The institution_id that was used, or None if failed
    """
    conn = None
    cursor = None

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        institution_name = record.get("name", "")
        #NOTE: SAME INSTITUTION ACRONYM WOULD GIVE SAME UUID
        institution_id = generate_institution_id(institution_name)

        db.call_procedure(
            cursor,
            "create_institution",
            (
                institution_id,
                record.get("name"),
                record.get("street_addr"),
                record.get("city"),
                record.get("state"),
                record.get("country"),
                record.get("zip"),
                record.get("website_url"),
                record.get("type"),
            ),
        )

        conn.commit()
        print(f"[OK] Inserted institution: {institution_name} ({institution_id})")
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
    record: Dict[str, Any], db: DatabaseConnection, institution_id_map: Dict[str, str]
) -> bool:
    """
    Insert a single faculty record into the database.

    Args:
        record: Faculty dictionary with MV attributes as arrays
        db: DatabaseConnection instance
        institution_id_map: Mapping from original institution_id to database UUID

    Returns:
        True if insertiong is successful, else False
    """
    conn = None
    cursor = None

    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        conn.start_transaction()

        first_name = record.get("first_name", "")
        last_name = record.get("last_name", "")
        scraped_from = record.get("scraped_from", "")

        existing_fac_id = record.get("faculty_id", None)
        faculty_id = existing_fac_id if existing_fac_id else generate_faculty_id(first_name, last_name, scraped_from)

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

        emails = record.get("emails", []) or []
        for email in emails:
            if email:
                db.call_procedure(cursor, "create_faculty_email", (faculty_id, email))

        phones = record.get("phones", []) or []
        for phone in phones:
            if phone:
                db.call_procedure(cursor, "create_faculty_phone", (faculty_id, phone))

        departments = record.get("departments", []) or []
        for dept in departments:
            if dept:
                db.call_procedure(
                    cursor, "create_faculty_department", (faculty_id, dept)
                )

        titles = record.get("titles", []) or []
        for title in titles:
            if title:
                db.call_procedure(cursor, "create_faculty_title", (faculty_id, title))

        original_institution_id = record.get("institution_id")
        start_date = record.get("start_date")
        if original_institution_id and start_date:
            db_institution_id = institution_id_map.get(original_institution_id)
            if db_institution_id:
                end_date = record.get("end_date")
                db.call_procedure(
                    cursor,
                    "create_faculty_works_at_institution",
                    (faculty_id, db_institution_id, start_date, end_date),
                )

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

        title = record["title"]
        author_uuid = record["written_by"]
        publication_id = generate_publication_id(title, author_uuid)

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
                record.get("citation_count")
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

    institution_id_map: Dict[str, str] = {}
    institutions_inserted = 0

    for inst_file in institution_files:
        if not os.path.exists(inst_file):
            print(f"[WARN] File not found: {inst_file}")
            continue

        try:
            institution = load_json(inst_file)
            original_id = institution.get("institution_id")
            db_id = insert_institution_record(institution, db)

            if db_id:
                institutions_inserted += 1
                if original_id:
                    institution_id_map[original_id] = db_id
        except Exception as e:
            print(f"[ERROR] Failed to process {inst_file}: {e}")
            import traceback

            traceback.print_exc()

    print(f"\n[INFO] Inserted {institutions_inserted} institutions")
    print(f"[INFO] Institution ID mapping: {len(institution_id_map)} mappings created")

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
                success = insert_faculty_record(record, db, institution_id_map)
                if success:
                    total_stats["successful"] += 1
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
            publication = load_json(pub_file)
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
