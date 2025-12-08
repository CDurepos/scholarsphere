"""
Author: Aidan Bell
"""

"""
Faculty Search Performance Test Script

This script tests the speed of the faculty search service with various query types.
Results are saved to a CSV file in the same folder.

Usage:
    python -m backend.optimization_tests.faculty_search_test
    
    Run from the project root directory (scholarsphere).
"""

import time
import csv
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Number of times to run the test suite
NUM_RUNS = 10

# Query configurations for each test case
# Modify these values to test with different search parameters
QUERIES = {
    "q1": {
        "description": "Last name only",
        "filters": {
            "query": "Smith",
        },
        "keywords": None,
    },
    "q2": {
        "description": "First name, last name, department, institution",
        "filters": {
            "query": "John Smith Computer Science University of Maine",
        },
        "keywords": None,
    },
    "q3": {
        "description": "Last name + keyword",
        "filters": {
            "query": "Smith",
        },
        "keywords": "machine learning",
    },
    "q4": {
        "description": "Keyword only",
        "filters": {},
        "keywords": "artificial intelligence",
    },
    "q5": {
        "description": "The letter 'a'",
        "filters": {
            "query": "a",
        },
        "keywords": None,
    },
    "q6": {
        "description": "The letter 'a'",
        "filters": {
            "query": "a",
        },
        "keywords": "computer vision",
    },
}

# Output file configuration
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
OUTPUT_FILENAME = f"faculty_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

from backend.app.services.search import search_faculty_service
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).resolve().parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def run_search(filters: dict, keywords: str | None) -> tuple[list, float]:
    """
    Run a single search and return results and elapsed time in seconds.
    
    Args:
        filters: Dictionary of filter parameters
        keywords: Optional keywords string (comma-separated)
        
    Returns:
        Tuple of (results list, elapsed time in seconds)
    """
    # Merge filters and keywords into kwargs for the service
    kwargs = {**filters}
    if keywords:
        kwargs["keywords"] = keywords
    
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        autocommit=False,
    )
    start_time = time.perf_counter()
    search_results, _ = search_faculty_service(result_limit=100, conn=conn, **kwargs)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    return search_results, elapsed


def run_test_suite(queries: dict) -> dict[str, float]:
    """
    Run all queries once and return timing results.
    
    Args:
        queries: Dictionary of query configurations
        
    Returns:
        Dictionary mapping query names to elapsed times in seconds
    """
    results = {}
    
    for query_name, query_config in queries.items():
        filters = query_config.get("filters", {})
        keywords = query_config.get("keywords")
        
        _, elapsed = run_search(filters, keywords)
        results[query_name] = elapsed
        
    return results


def calculate_average(times: list[float]) -> float:
    """Calculate average of a list of times."""
    return sum(times) / len(times) if times else 0.0


def write_results_to_csv(all_results: list[dict], output_path: str, queries: dict):
    """
    Write timing results to CSV file.
    
    Args:
        all_results: List of dictionaries, each containing timing results for one run
        output_path: Path to output CSV file
        queries: Query configuration dictionary for column ordering
    """
    query_names = list(queries.keys())
    headers = ["Run"] + query_names + ["Avg"]
    
    # Calculate column averages
    column_totals = {qn: 0.0 for qn in query_names}
    row_averages = []
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for i, run_result in enumerate(all_results, 1):
            row_label = f"r{i}"
            row_values = [run_result[qn] for qn in query_names]
            row_avg = calculate_average(row_values)
            row_averages.append(row_avg)
            
            # Update column totals
            for qn in query_names:
                column_totals[qn] += run_result[qn]
            
            # Format values to 6 decimal places
            formatted_row = [row_label] + [f"{v:.6f}" for v in row_values] + [f"{row_avg:.6f}"]
            writer.writerow(formatted_row)
        
        # Write average row
        num_runs = len(all_results)
        col_averages = [column_totals[qn] / num_runs for qn in query_names]
        avg_of_averages = calculate_average(row_averages)
        
        formatted_avg_row = ["avg"] + [f"{v:.6f}" for v in col_averages] + [f"{avg_of_averages:.6f}"]
        writer.writerow(formatted_avg_row)


def print_query_info(queries: dict):
    """Print information about configured queries."""
    print("\n" + "=" * 60)
    print("QUERY CONFIGURATIONS")
    print("=" * 60)
    for query_name, config in queries.items():
        print(f"\n{query_name}: {config['description']}")
        if config['filters']:
            print(f"  Filters: {config['filters']}")
        if config['keywords']:
            print(f"  Keywords: {config['keywords']}")


def main():
    print("\n" + "=" * 60)
    print("FACULTY SEARCH PERFORMANCE TEST")
    print("=" * 60)
    
    print_query_info(QUERIES)
    
    print(f"\nNumber of runs: {NUM_RUNS}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    all_results = []
    
    print("\n" + "-" * 60)
    print("RUNNING TESTS...")
    print("-" * 60)
    
    for run_num in range(1, NUM_RUNS + 1):
        print(f"\nRun {run_num}/{NUM_RUNS}...", end=" ", flush=True)
        
        run_results = run_test_suite(QUERIES)
        all_results.append(run_results)
        
        # Print run summary
        total_time = sum(run_results.values())
        print(f"completed in {total_time:.4f}s")
        for qn, t in run_results.items():
            print(f"    {qn}: {t:.6f}s")
    
    # Write results to CSV
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    write_results_to_csv(all_results, output_path, QUERIES)
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    # Calculate and print averages
    query_names = list(QUERIES.keys())
    for qn in query_names:
        avg_time = calculate_average([r[qn] for r in all_results])
        print(f"{qn} ({QUERIES[qn]['description']}): {avg_time:.6f}s avg")
    
    overall_avg = calculate_average([
        calculate_average([r[qn] for qn in query_names])
        for r in all_results
    ])
    print(f"\nOverall average: {overall_avg:.6f}s")
    
    print(f"\nResults saved to: {output_path}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
