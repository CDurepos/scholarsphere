# Query Optimization Testing: Process and Results

## Executive Summary

This document describes the process of optimizing faculty profile retrieval queries in the ScholarSphere database system. The optimization reduced database round trips from 6-7 separate queries to a single optimized query, resulting in significant performance improvements.

---

## 1. Problem Statement

### Original Implementation

The original `get_faculty()` function retrieved a complete faculty profile by executing multiple separate database queries:

1. **Query 1**: Fetch base faculty information from `faculty` table
2. **Query 2**: Fetch email addresses from `faculty_email` table
3. **Query 3**: Fetch phone numbers from `faculty_phone` table
4. **Query 4**: Fetch department names from `faculty_department` table
5. **Query 5**: Fetch titles from `faculty_title` table
6. **Query 6**: Fetch institution relationship from `faculty_works_at_institution` table
7. **Query 7**: Fetch institution name from `institution` table (if needed)

**Total: 6-7 database round trips** for a single faculty profile retrieval.

### Performance Issues

- **Network Latency**: Each query requires a separate network round trip
- **Connection Overhead**: Multiple queries increase connection and transaction overhead
- **Scalability**: Performance degrades as network latency increases
- **Database Load**: More queries mean more database processing time

---

## 2. Optimization Approach

### Solution: Single Optimized Query

The optimization consolidates all data retrieval into a **single SQL query** using:

1. **LEFT JOINs**: Combine all related tables in one query
2. **GROUP_CONCAT**: Aggregate multi-valued fields (emails, phones, departments, titles)
3. **Subquery**: Retrieve institution name efficiently
4. **Stored Procedure**: Encapsulate the optimized query for reusability

### Technical Implementation

#### SQL Stored Procedure

Created `read_faculty_complete_optimized` stored procedure that:

```sql
SELECT 
    -- Base faculty fields
    f.faculty_id,
    f.first_name,
    f.last_name,
    f.biography,
    f.orcid,
    f.google_scholar_url,
    f.research_gate_url,
    f.scraped_from,
    
    -- Aggregated multi-valued fields using GROUP_CONCAT
    GROUP_CONCAT(DISTINCT fe.email ORDER BY fe.email SEPARATOR ',') AS emails,
    GROUP_CONCAT(DISTINCT fp.phone_num ORDER BY fp.phone_num SEPARATOR ',') AS phones,
    GROUP_CONCAT(DISTINCT fd.department_name ORDER BY fd.department_name SEPARATOR ',') AS departments,
    GROUP_CONCAT(DISTINCT ft.title ORDER BY ft.title SEPARATOR ',') AS titles,
    
    -- Most recent institution name using subquery
    (SELECT i.name
     FROM faculty_works_at_institution fwi
     INNER JOIN institution i ON fwi.institution_id = i.institution_id
     WHERE fwi.faculty_id = f.faculty_id
     ORDER BY fwi.start_date DESC, fwi.end_date IS NULL DESC
     LIMIT 1) AS institution_name
    
FROM faculty f
LEFT JOIN faculty_email fe ON f.faculty_id = fe.faculty_id
LEFT JOIN faculty_phone fp ON f.faculty_id = fp.faculty_id
LEFT JOIN faculty_department fd ON f.faculty_id = fd.faculty_id
LEFT JOIN faculty_title ft ON f.faculty_id = ft.faculty_id
WHERE f.faculty_id = p_faculty_id
GROUP BY f.faculty_id, f.first_name, f.last_name, ...;
```

**Key Features:**
- **LEFT JOINs**: Ensure faculty records are returned even if they have no related records
- **GROUP_CONCAT**: Efficiently aggregates multiple values into comma-separated strings
- **DISTINCT**: Removes duplicate values
- **ORDER BY**: Ensures consistent ordering of aggregated values
- **Subquery**: Efficiently retrieves the most recent institution name

#### Python Service Layer

Created `get_faculty_optimized()` function that:
1. Calls the stored procedure
2. Parses comma-separated strings into Python lists
3. Returns data in the same format as the original function (ensuring compatibility)

---

## 3. Testing Methodology

### Test Setup

1. **Test Data**: Created sample faculty records with varying amounts of related data:
   - Faculty with 2 emails, 2 phones, 2 departments, 2 titles
   - Faculty with 2 emails, 1 phone, 2 departments, 1 title
   - Faculty with 3 emails, 3 phones, 2 departments, 3 titles

2. **Test Environment**:
   - Database: MySQL (local instance)
   - Test Script: Python performance testing script
   - Iterations: 100 runs of each method

### Testing Process

#### Step 1: Load Test Data
- Inserted sample faculty records with related data (emails, phones, departments, titles)
- Verified data integrity and completeness

#### Step 2: Add Optimized Procedure
- Created the `read_faculty_complete_optimized` stored procedure in the database
- Verified procedure was created successfully

#### Step 3: Performance Testing
- **Current Method**: Executed `get_faculty()` 100 times
  - Measured execution time for each iteration
  - Calculated average, min, max, and total execution times
  
- **Optimized Method**: Executed `get_faculty_optimized()` 100 times
  - Measured execution time for each iteration
  - Calculated average, min, max, and total execution times

#### Step 4: Data Verification
- Compared results from both methods
- Verified that both return identical data structures
- Confirmed data consistency (emails, phones, departments, titles match)

### Metrics Collected

For each method, we measured:
- **Average Time**: Mean execution time across 100 iterations
- **Min Time**: Fastest execution time
- **Max Time**: Slowest execution time
- **Total Time**: Sum of all execution times
- **Speedup Factor**: Ratio of current method time to optimized method time
- **Performance Improvement**: Percentage reduction in execution time


#### Database Load Reduction
- **6-7 queries reduced to 1 query** = 83-86% reduction in query count
- Less database connection overhead
- Better database resource utilization

---

## 5. Technical Details

### Why GROUP_CONCAT Works

`GROUP_CONCAT` efficiently aggregates multiple rows into a single string:
- **Before**: 6 separate queries return 6 result sets
- **After**: 1 query returns 1 result set with comma-separated values
- **Parsing**: Python splits the comma-separated string into a list

### Why LEFT JOINs Are Used

- **INNER JOIN**: Would exclude faculty with no related records
- **LEFT JOIN**: Includes all faculty, even if they have no emails/phones/departments
- **Result**: Maintains data completeness

### Why a Subquery for Institution

- Faculty can have multiple institution relationships over time
- Subquery selects the most recent (by `start_date`)
- More efficient than joining and filtering in the main query

### Data Consistency Verification

Both methods return identical data:
- Same faculty_id, first_name, last_name
- Same sets of emails, phones, departments, titles
- Same data structure (Python dictionaries with lists)

---

## 6. Conclusion

### Key Achievements

1. **Efficiency**: Reduced from 6-7 queries to 1 query
2. **Scalability**: Better performance under load
3. **Compatibility**: Same data structure, no code changes needed elsewhere

### Best Practices Demonstrated

1. **Query Optimization**: Consolidating multiple queries into one
2. **Stored Procedures**: Encapsulating complex queries for reusability
3. **Performance Testing**: Systematic measurement and comparison
4. **Data Verification**: Ensuring optimization doesn't change results

---

## 7. Files Created

### SQL Files
- `db/procedures/read/read_faculty_complete_optimized.sql` - Optimized stored procedure
- `db/seed_test_faculty.sql` - Test data for performance testing
- `db/test_performance_in_mysql.sql` - SQL-based performance test

### Python Files
- `backend/app/db/procedures.py` - Added `sql_read_faculty_complete_optimized()` wrapper
- `backend/app/services/faculty.py` - Added `get_faculty_optimized()` service function
- `backend/test_query_performance.py` - Performance testing script
- `run_all_tests.py` - Comprehensive test script

### Documentation
- `backend/QUERY_OPTIMIZATION_README.md` - Technical documentation
- `HOW_TO_RUN_OPTIMIZED_QUERY.md` - User guide
- `QUERY_OPTIMIZATION_WRITEUP.md` - This document

---

## Appendix: Code Comparison

### Original Implementation (Multiple Queries)

```python
def get_faculty(faculty_id):
    # Query 1: Base faculty
    faculty = sql_read_faculty(tx, faculty_id)
    
    # Query 2: Emails
    emails = sql_read_faculty_email(tx, faculty_id)
    
    # Query 3: Phones
    phones = sql_read_faculty_phone(tx, faculty_id)
    
    # Query 4: Departments
    departments = sql_read_faculty_department(tx, faculty_id)
    
    # Query 5: Titles
    titles = sql_read_faculty_title(tx, faculty_id)
    
    # Query 6: Institution
    institution = sql_read_faculty_institution(tx, faculty_id)
    
    return combine_results(faculty, emails, phones, departments, titles, institution)
```

### Optimized Implementation (Single Query)

```python
def get_faculty_optimized(faculty_id):
    # Single query that gets everything
    result = sql_read_faculty_complete_optimized(tx, faculty_id)
    
    # Parse comma-separated strings into lists
    result['emails'] = result['emails'].split(',') if result['emails'] else []
    result['phones'] = result['phones'].split(',') if result['phones'] else []
    result['departments'] = result['departments'].split(',') if result['departments'] else []
    result['titles'] = result['titles'].split(',') if result['titles'] else []
    
    return result
```

---

