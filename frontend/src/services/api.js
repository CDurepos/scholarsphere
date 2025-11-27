/**
 * API Service for ScholarSphere
 * 
 * This file contains placeholder API endpoints for authentication and faculty operations.
 * Replace the base URL with your actual backend API endpoint when ready.
 */

const API_BASE_URL = 'http://127.0.0.1:5000/api'; // Backend API URL

/**
 * Get institution list from the DB
 * @returns {Promise<Array>} Array of institution objects
 */
export const getInstitutions = async () => {
  const response = await fetch(`${API_BASE_URL}/institution`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.json();
};

/**
 * Search for faculty members using the search endpoint
 * 
 * @param {Object} params - Query parameters
 * @param {string} [params.query] - General search query (searches across name, department, institution)
 * @param {string} [params.first_name] - Faculty member's first name (partial match)
 * @param {string} [params.last_name] - Faculty member's last name (partial match)
 * @param {string} [params.department] - Department name (partial match)
 * @param {string} [params.institution] - Institution name (partial match)
 * 
 * @returns {Promise<Array>} Array of faculty members matching the search criteria
 * 
 * Example response:
 * [
 *   {
 *     "faculty_id": "uuid",
 *     "first_name": "John",
 *     "last_name": "Doe",
 *     "department_name": "Computer Science",
 *     "institution_name": "University of Maine"
 *   },
 *   ...
 * ]
 */
export const searchFaculty = async (params = {}) => {
  const queryParams = new URLSearchParams();
  
  // If a general query is provided, pass it directly to the backend
  // The backend should handle parsing it appropriately
  if (params.query) {
    queryParams.append('query', params.query.trim());
  }
  
  if (params.first_name) queryParams.append('first_name', params.first_name);
  if (params.last_name) queryParams.append('last_name', params.last_name);
  if (params.department) queryParams.append('department', params.department);
  if (params.institution) queryParams.append('institution', params.institution);
  
  // Backend search endpoint is at /search/ (no /api prefix)
  const response = await fetch(`${API_BASE_URL}/search?${queryParams.toString()}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.json();
};

/**
 * Check if a faculty member exists in the database by name and institution
 * Uses the search endpoint to find matches, prioritizing exact matches first,
 * then falling back to name-only matches
 * 
 * @param {Object} data - Request body
 * @param {string} data.first_name - Faculty member's first name
 * @param {string} data.last_name - Faculty member's last name
 * @param {string} data.institution_name - Institution name
 * 
 * @returns {Promise<Object>} Response object
 * @returns {boolean} exists - Whether the faculty member exists
 * @returns {Object|null} faculty - Faculty data if exists, null otherwise
 * 
 * Note: The search endpoint returns basic info (faculty_id, first_name, last_name, 
 * department_name, institution_name). Multi-valued fields (emails, phones, etc.)
 * are initialized as empty arrays and will need to be fetched separately if needed.
 */
export const checkFacultyExists = async (data) => {
  // First, try to find exact match (first_name, last_name, institution_name)
  const searchResultsWithInstitution = await searchFaculty({
    first_name: data.first_name,
    last_name: data.last_name,
    institution: data.institution_name,
  });
  
  // Check for exact match (case-insensitive)
  const exactMatch = searchResultsWithInstitution.find(
    (faculty) =>
      faculty.first_name?.toLowerCase() === data.first_name.toLowerCase() &&
      faculty.last_name?.toLowerCase() === data.last_name.toLowerCase() &&
      faculty.institution_name?.toLowerCase() === data.institution_name.toLowerCase()
  );
  
  if (exactMatch) {
    // Return exact match with structure expected by signup flow
    return {
      exists: true,
      faculty: {
        faculty_id: exactMatch.faculty_id,
        first_name: exactMatch.first_name,
        last_name: exactMatch.last_name,
        institution_name: exactMatch.institution_name,
        // Search endpoint doesn't return these, so initialize as empty
        // These would need to be fetched from a full faculty details endpoint
        emails: [],
        phones: [],
        departments: exactMatch.department_name ? [exactMatch.department_name] : [],
        titles: [],
        biography: '',
        orcid: '',
        google_scholar_url: '',
        research_gate_url: '',
      },
    };
  }
  
  // Fallback: search by first_name and last_name only (no institution filter)
  const searchResultsByNameOnly = await searchFaculty({
    first_name: data.first_name,
    last_name: data.last_name,
  });
  
  // Find match by name only (case-insensitive)
  const nameMatch = searchResultsByNameOnly.find(
    (faculty) =>
      faculty.first_name?.toLowerCase() === data.first_name.toLowerCase() &&
      faculty.last_name?.toLowerCase() === data.last_name.toLowerCase()
  );
  
  if (nameMatch) {
    // Return name-only match
    return {
      exists: true,
      faculty: {
        faculty_id: nameMatch.faculty_id,
        first_name: nameMatch.first_name,
        last_name: nameMatch.last_name,
        institution_name: nameMatch.institution_name || data.institution_name,
        // Search endpoint doesn't return these, so initialize as empty
        emails: [],
        phones: [],
        departments: nameMatch.department_name ? [nameMatch.department_name] : [],
        titles: [],
        biography: '',
        orcid: '',
        google_scholar_url: '',
        research_gate_url: '',
      },
    };
  }
  
  // No match found
  return {
    exists: false,
    faculty: null,
  };
};

/**
 * Create a new faculty member
 * 
 * @param {Object} data - Request body
 * @param {string} data.first_name - Faculty member's first name
 * @param {string} data.last_name - Faculty member's last name
 * @param {string} data.institution_name - Institution name
 * @param {string[]} data.emails - Array of email addresses
 * @param {string[]} data.phones - Array of phone numbers
 * @param {string[]} data.departments - Array of department names
 * @param {string[]} data.titles - Array of titles
 * @param {string} [data.biography] - Biography text
 * @param {string} [data.orcid] - ORCID ID
 * @param {string} [data.google_scholar_url] - Google Scholar URL
 * @param {string} [data.research_gate_url] - ResearchGate URL
 * 
 * @returns {Promise<Object>} Response object
 * @returns {string} faculty_id - UUID of created faculty member
 * 
 * Example response:
 * {
 *   "faculty_id": "uuid",
 *   "message": "Faculty member created successfully"
 * }
 */
export const createFaculty = async (data) => {
  const response = await fetch(`${API_BASE_URL}/faculty`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
};

/**
 * Update an existing faculty member
 * 
 * @param {string} faculty_id - UUID of the faculty member
 * @param {Object} data - Request body with fields to update
 * @param {string} [data.first_name] - First name
 * @param {string} [data.last_name] - Last name
 * @param {string[]} [data.emails] - Array of email addresses
 * @param {string[]} [data.phones] - Array of phone numbers
 * @param {string[]} [data.departments] - Array of department names
 * @param {string[]} [data.titles] - Array of titles
 * @param {string} [data.biography] - Biography text
 * @param {string} [data.orcid] - ORCID ID
 * @param {string} [data.google_scholar_url] - Google Scholar URL
 * @param {string} [data.research_gate_url] - ResearchGate URL
 * 
 * @returns {Promise<Object>} Response object
 * 
 * Example response:
 * {
 *   "message": "Faculty member updated successfully"
 * }
 */
export const updateFaculty = async (faculty_id, data) => {
  const response = await fetch(`${API_BASE_URL}/faculty/${faculty_id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
};

/**
 * Save a faculty member (create or update based on faculty_id)
 * 
 * @param {string|null|undefined} faculty_id - UUID of the faculty member (null/undefined to create new)
 * @param {Object} data - Request body with faculty information
 * @param {string} data.first_name - First name
 * @param {string} [data.last_name] - Last name
 * @param {string} data.institution_name - Institution name
 * @param {string[]} [data.emails] - Array of email addresses
 * @param {string[]} [data.phones] - Array of phone numbers
 * @param {string[]} [data.departments] - Array of department names
 * @param {string[]} [data.titles] - Array of titles
 * @param {string} [data.biography] - Biography text
 * @param {string} [data.orcid] - ORCID ID
 * @param {string} [data.google_scholar_url] - Google Scholar URL
 * @param {string} [data.research_gate_url] - ResearchGate URL
 * 
 * @returns {Promise<Object>} Response object
 * @returns {string} faculty_id - UUID of the faculty member (new or existing)
 * 
 * Example response (create):
 * {
 *   "faculty_id": "uuid",
 *   "message": "Faculty member created successfully"
 * }
 * 
 * Example response (update):
 * {
 *   "message": "Faculty member updated successfully"
 * }
 */
export const saveFaculty = async (faculty_id, data) => {
  if (!faculty_id) {
    // Create new faculty
    const response = await createFaculty(data);
    return {
      faculty_id: response.faculty_id,
      ...response
    };
  } else {
    // Update existing faculty
    await updateFaculty(faculty_id, data);
    return {
      faculty_id: faculty_id
    };
  }
};

/**
 * Register credentials for a faculty member
 * 
 * @param {Object} data - Request body
 * @param {string} data.faculty_id - UUID of the faculty member
 * @param {string} data.username - Username (must be unique)
 * @param {string} data.password - Plain text password (will be hashed on backend)
 * 
 * @returns {Promise<Object>} Response object
 * 
 * Example response:
 * {
 *   "message": "Credentials registered successfully"
 * }
 * 
 * Example error response:
 * {
 *   "error": "Username already exists"
 * }
 */
export const registerCredentials = async (data) => {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  const result = await response.json();
  
  // If the response is not ok, return error object
  if (!response.ok) {
    return {
      error: result.error || 'Failed to register credentials'
    };
  }
  
  return result;
};

/**
 * Login with username and password
 * 
 * @param {Object} data - Request body
 * @param {string} data.username - Username
 * @param {string} data.password - Plain text password
 * 
 * @returns {Promise<Object>} Response object
 * @returns {string} token - JWT token for authenticated sessions
 * @returns {Object} faculty - Faculty data
 * 
 * Example response:
 * {
 *   "token": "jwt_token_here",
 *   "faculty": {
 *     "faculty_id": "uuid",
 *     "username": "johndoe",
 *     "first_name": "John",
 *     "last_name": "Doe",
 *     ...
 *   }
 * }
 * 
 * Example error response:
 * {
 *   "error": "Invalid username or password"
 * }
 */
export const login = async (data) => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  const result = await response.json();
  
  // If the response is not ok, return error object
  if (!response.ok) {
    return {
      error: result.error || 'Failed to login'
    };
  }
  
  return result;
};

/**
 * Check if a username is available
 * 
 * @param {string} username - Username to check
 * 
 * @returns {Promise<Object>} Response object
 * @returns {boolean} available - Whether the username is available
 * @returns {string} username - The username that was checked
 * 
 * Example response:
 * {
 *   "username": "johndoe",
 *   "available": true
 * }
 */
export const checkUsernameAvailable = async (username) => {
  if (!username || username.trim().length < 4) {
    return { available: null, username }; // Don't check if too short
  }
  
  const response = await fetch(`${API_BASE_URL}/auth/check-username?username=${encodeURIComponent(username)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  const result = await response.json();
  
  // If the response is not ok, assume username is not available
  if (!response.ok) {
    return {
      available: false,
      username
    };
  }
  
  return result;
};