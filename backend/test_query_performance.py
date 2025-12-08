"""
Query Performance Testing Script

Compares the performance of:
1. Current implementation (multiple queries)
2. Optimized implementation (single query with JOINs)

Usage:
    python backend/test_query_performance.py [faculty_id]

If no faculty_id is provided, the script will find a faculty member from the database.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app import create_app
from backend.app.db.transaction_context import start_transaction
from backend.app.services.faculty import get_faculty, get_faculty_optimized
from backend.app.db.procedures import sql_search_faculty


def get_sample_faculty_id():
    """Get a sample faculty_id from the database for testing."""
    app = create_app()
    with app.app_context():
        try:
            with start_transaction() as tx:
                # Get first faculty member from search
                results = sql_search_faculty(tx, first_name=None, last_name=None, department=None, institution=None)
                if results and len(results) > 0:
                    return results[0].get('faculty_id')
        except Exception as e:
            print(f"Error finding sample faculty: {e}")
    return None


def test_current_implementation(faculty_id: str, iterations: int = 100):
    """Test the current multi-query implementation."""
    app = create_app()
    times = []
    
    with app.app_context():
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                result = get_faculty(faculty_id)
                if not result:
                    print(f"Warning: Faculty {faculty_id} not found")
                    return None
            except Exception as e:
                print(f"Error in current implementation: {e}")
                return None
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds
    
    return {
        "times": times,
        "avg": sum(times) / len(times),
        "min": min(times),
        "max": max(times),
        "total": sum(times)
    }


def test_optimized_implementation(faculty_id: str, iterations: int = 100):
    """Test the optimized single-query implementation."""
    app = create_app()
    times = []
    
    with app.app_context():
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                result = get_faculty_optimized(faculty_id)
                if not result:
                    print(f"Warning: Faculty {faculty_id} not found")
                    return None
            except Exception as e:
                error_msg = str(e).lower()
                if "procedure" in error_msg or "does not exist" in error_msg:
                    print(f"\n⚠ Error: Optimized procedure not found in database.")
                    print(f"   Please run: SOURCE db/procedures/read/read_faculty_complete_optimized.sql;")
                    print(f"   Or regenerate procedures: bash db/generate_procedures.sh\n")
                else:
                    print(f"Error in optimized implementation: {e}")
                return None
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds
    
    return {
        "times": times,
        "avg": sum(times) / len(times),
        "min": min(times),
        "max": max(times),
        "total": sum(times)
    }


def print_results(current_stats, optimized_stats):
    """Print formatted comparison results."""
    print("\n" + "="*70)
    print("QUERY PERFORMANCE COMPARISON")
    print("="*70)
    print(f"\n{'Metric':<30} {'Current (Multi-Query)':<25} {'Optimized (Single Query)':<25}")
    print("-"*70)
    print(f"{'Average Time (ms)':<30} {current_stats['avg']:<25.3f} {optimized_stats['avg']:<25.3f}")
    print(f"{'Min Time (ms)':<30} {current_stats['min']:<25.3f} {optimized_stats['min']:<25.3f}")
    print(f"{'Max Time (ms)':<30} {current_stats['max']:<25.3f} {optimized_stats['max']:<25.3f}")
    print(f"{'Total Time (ms)':<30} {current_stats['total']:<25.3f} {optimized_stats['total']:<25.3f}")
    
    improvement = ((current_stats['avg'] - optimized_stats['avg']) / current_stats['avg']) * 100
    speedup = current_stats['avg'] / optimized_stats['avg']
    
    print("\n" + "-"*70)
    print(f"Performance Improvement: {improvement:.2f}% faster")
    print(f"Speedup Factor: {speedup:.2f}x")
    print("="*70 + "\n")


def main():
    """Main testing function."""
    # Get faculty_id from command line or find one
    if len(sys.argv) > 1:
        faculty_id = sys.argv[1]
    else:
        print("No faculty_id provided. Finding a sample faculty member...")
        faculty_id = get_sample_faculty_id()
        if not faculty_id:
            print("Error: Could not find a faculty member to test with.")
            sys.exit(1)
        print(f"Using faculty_id: {faculty_id}")
    
    iterations = 100
    print(f"\nTesting with {iterations} iterations...")
    print("Testing current implementation (multiple queries)...")
    
    # Test current implementation
    current_stats = test_current_implementation(faculty_id, iterations)
    if not current_stats:
        print("Failed to test current implementation")
        sys.exit(1)
    
    print("Testing optimized implementation (single query)...")
    
    # Test optimized implementation
    optimized_stats = test_optimized_implementation(faculty_id, iterations)
    if not optimized_stats:
        print("Failed to test optimized implementation")
        sys.exit(1)
    
    # Print results
    print_results(current_stats, optimized_stats)
    
    # Verify both return the same data
    print("Verifying data consistency...")
    app = create_app()
    with app.app_context():
        current_data = get_faculty(faculty_id)
        optimized_data = get_faculty_optimized(faculty_id)
        
        # Compare key fields
        if (current_data.get('faculty_id') == optimized_data.get('faculty_id') and
            current_data.get('first_name') == optimized_data.get('first_name') and
            current_data.get('last_name') == optimized_data.get('last_name') and
            set(current_data.get('emails', [])) == set(optimized_data.get('emails', [])) and
            set(current_data.get('phones', [])) == set(optimized_data.get('phones', [])) and
            set(current_data.get('departments', [])) == set(optimized_data.get('departments', [])) and
            set(current_data.get('titles', [])) == set(optimized_data.get('titles', []))):
            print("✓ Data consistency verified - both methods return identical results")
        else:
            print("⚠ Warning: Data mismatch detected between implementations")
            print(f"  Current emails: {current_data.get('emails')}")
            print(f"  Optimized emails: {optimized_data.get('emails')}")


if __name__ == "__main__":
    main()

