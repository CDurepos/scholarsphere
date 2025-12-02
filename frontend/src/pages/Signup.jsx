import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { checkFacultyExists, saveFaculty, registerCredentials, login, checkCredentialsExist } from '../services/api';
import ConnectionParticles from '../components/ConnectionParticles';
import { BasicInfoForm, ConfirmationStep, CredentialsForm } from '../features/signup/SignupSteps';
import './Signup.css';
import { getInstitutions } from '../services/api';

// Stable particle config to prevent re-renders
const SIGNUP_PARTICLE_COLORS = ['#ffffff', '#dfe8ff'];
const SIGNUP_PARTICLE_LINK_COLOR = '#c6d6ff';
const SIGNUP_PARTICLE_QUANTITY = 75;

// localStorage keys for signup flow
const SIGNUP_FACULTY_ID_KEY = 'scholarsphere_signup_faculty_id';
const SIGNUP_TIMESTAMP_KEY = 'scholarsphere_signup_timestamp';
const SIGNUP_EXPIRY_HOURS = 24; // Expire signup data after 24 hours

/**
 * Multi-step signup component
 * Step 1: Name and institution check
 * Step 2: "Is this you?" confirmation (if exists) + Additional information form
 * Step 3: Credentials setup
 */
function Signup() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [showConfirmation, setShowConfirmation] = useState(false); // Whether to show confirmation in step 2
  const [institutions, setInstitutions] = useState([]);
  
  // Helper functions for localStorage management
  const getStoredFacultyId = () => {
    try {
      const storedId = localStorage.getItem(SIGNUP_FACULTY_ID_KEY);
      const timestamp = localStorage.getItem(SIGNUP_TIMESTAMP_KEY);
      
      if (!storedId || !timestamp) {
        return null;
      }
      
      // Check if expired (24 hours)
      const now = Date.now();
      const storedTime = parseInt(timestamp, 10);
      if (now - storedTime > SIGNUP_EXPIRY_HOURS * 60 * 60 * 1000) {
        clearSignupData();
        return null;
      }
      
      return storedId;
    } catch (error) {
      return null;
    }
  };
  
  const setStoredFacultyId = (facultyId) => {
    try {
      if (facultyId) {
        localStorage.setItem(SIGNUP_FACULTY_ID_KEY, facultyId);
        localStorage.setItem(SIGNUP_TIMESTAMP_KEY, Date.now().toString());
      } else {
        clearSignupData();
      }
    } catch (error) {
      // Failed to write to localStorage
    }
  };
  
  const clearSignupData = () => {
    try {
      localStorage.removeItem(SIGNUP_FACULTY_ID_KEY);
      localStorage.removeItem(SIGNUP_TIMESTAMP_KEY);
    } catch (error) {
      // Failed to clear localStorage
    }
  };
  
  const [signupData, setSignupData] = useState({
    first_name: '',
    last_name: '',
    institution_name: '',
    faculty_id: null,
    exists: false,
    doPrefill: false, // Whether to prefill the form
    matchType: null, // 'perfect' or 'name_only', or null
    emails: [],
    phones: [],
    departments: [],
    titles: [],
    biography: '',
    orcid: '',
    google_scholar_url: '',
    research_gate_url: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasExistingCredentials, setHasExistingCredentials] = useState(false);

  // Load faculty_id from localStorage on mount
  useEffect(() => {
    const storedFacultyId = getStoredFacultyId();
    if (storedFacultyId) {
      setSignupData(prev => ({
        ...prev,
        faculty_id: storedFacultyId,
        exists: true, // If we have a stored ID, they exist
      }));
      // If user refreshes, they will start from step 1
    }
    
    const fetchInstitutions = async () => {
      const institutions = await getInstitutions();
      setInstitutions(institutions);
    };
    fetchInstitutions();
    
    // Cleanup: Clear signup data if user navigates away (optional - you may want to keep it)
    // Uncomment if you want to clear on unmount:
    // return () => {
    //   // Only clear if signup is incomplete (not on step 3)
    //   // Actually, let's keep it so they can resume
    // };
  }, []);

  const handleStep1Submit = async (data) => {
    setLoading(true);
    setError('');

    try {
      // API Endpoint: POST /api/faculty/check
      // Body: { first_name: string, last_name: string, institution_name: string }
      // Returns: { exists: boolean, faculty: object | null }
      const response = await checkFacultyExists({
        first_name: data.first_name,
        last_name: data.last_name,
        institution_name: data.institution_name,
      });

      if (response.exists && response.faculty) {
        // User exists - show confirmation first
        const facultyId = response.faculty.faculty_id;
        setStoredFacultyId(facultyId); // Store in localStorage
        setSignupData({
          ...signupData,
          first_name: data.first_name,
          last_name: data.last_name,
          institution_name: data.institution_name,
          faculty_id: facultyId,
          exists: true,
          matchType: response.matchType || 'perfect', // Track match type
          doPrefill: false, // Will be set to true if user confirms
          emails: response.faculty.emails || [],
          phones: response.faculty.phones || [],
          departments: response.faculty.departments || [],
          titles: response.faculty.titles || [],
          biography: response.faculty.biography || '',
          orcid: response.faculty.orcid || '',
          google_scholar_url: response.faculty.google_scholar_url || '',
          research_gate_url: response.faculty.research_gate_url || '',
        });
        setShowConfirmation(true);
        setStep(2); // Step 2 - show confirmation first
      } else {
        // User doesn't exist - go directly to form (empty)
        clearSignupData(); // Clear any old signup data
        setSignupData({
          ...signupData,
          first_name: data.first_name,
          last_name: data.last_name,
          institution_name: data.institution_name,
          exists: false,
          doPrefill: false,
        });
        setShowConfirmation(false);
        setStep(2); // Step 2 - form (skip confirmation)
      }
    } catch (err) {
      setError('Failed to check faculty. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle confirmation step - user clicked "Yes, this is me"
  const handleConfirmationYes = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Check if credentials already exist for this faculty_id
      const credentialsCheck = await checkCredentialsExist(signupData.faculty_id);
      
      if (credentialsCheck.has_credentials) {
        // Credentials already exist - show message and allow redirect to login
        setHasExistingCredentials(true);
        setLoading(false);
        return;
      }
      
      // No credentials exist - continue with normal flow
      setSignupData({
        ...signupData,
        doPrefill: true, // Prefill the form with existing data
      });
      setShowConfirmation(false); // Hide confirmation, show form
      setLoading(false);
    } catch (err) {
      setError('Failed to check credentials. Please try again.');
      setLoading(false);
    }
  };

  // Handle confirmation step - user clicked "No, this is not me"
  const handleConfirmationNo = () => {
    // Clear all existing data and treat as new user
    clearSignupData(); // Clear stored faculty_id
    setSignupData({
      first_name: signupData.first_name, // Keep name from step 1
      last_name: signupData.last_name,
      institution_name: signupData.institution_name,
      faculty_id: null,
      exists: false, // Important: set to false so it creates new, not updates
      doPrefill: false, // Don't prefill - start with empty form
      emails: [],
      phones: [],
      departments: [],
      titles: [],
      biography: '',
      orcid: '',
      google_scholar_url: '',
      research_gate_url: '',
    });
    setShowConfirmation(false); // Hide confirmation, show form
  };

  // Handle form submission (step 2)
  const handleFormSubmit = async (formData) => {
    setLoading(true);
    setError('');

    try {
      // Use unified saveFaculty function - it will create or update based on faculty_id
      // If faculty_id is null/undefined, it creates a new faculty
      // If faculty_id exists, it updates the existing faculty
      const response = await saveFaculty(signupData.faculty_id, formData);
      
      // Get the faculty_id (either from response if created, or existing one if updated)
      const facultyId = response.faculty_id || signupData.faculty_id;
      
      // Store faculty_id in localStorage
      setStoredFacultyId(facultyId);
      
      // Update signup data
      setSignupData({
        ...signupData,
        faculty_id: facultyId,
        exists: true, // They now exist in the database (either created or updated)
        ...formData,
      });

      // Move to credentials step
      setStep(3);
    } catch (err) {
      setError('Failed to save faculty information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStep3Submit = async (credentials) => {
    setLoading(true);
    setError('');

    try {
      // Get faculty_id from state or localStorage (fallback)
      const facultyId = signupData.faculty_id || getStoredFacultyId();
      
      if (!facultyId) {
        setError('Faculty ID not found. Please start the signup process again.');
        setLoading(false);
        return;
      }

      // API Endpoint: POST /api/auth/register
      // Body: { faculty_id: string, username: string, password: string }
      // Returns: { message: string } or { error: string }
      const response = await registerCredentials({
        faculty_id: facultyId,
        username: credentials.username,
        password: credentials.password,
      });

      if (response.error) {
        setError(response.error);
        setLoading(false);
        return;
      }

      // Registration successful - automatically log the user in
      try {
        const loginResponse = await login({
          username: credentials.username,
          password: credentials.password,
        });

        if (loginResponse.error) {
          // If auto-login fails, redirect to login page with message
          clearSignupData();
          navigate('/login', { state: { message: 'Registration successful! Please login with your new credentials.' } });
          return;
        }

        // Auto-login successful - store faculty data and redirect to dashboard
        localStorage.setItem('faculty', JSON.stringify(loginResponse.faculty));
        localStorage.setItem('faculty_id', loginResponse.faculty?.faculty_id);
        
        // Clear signup data
        clearSignupData();
        
        // Redirect to dashboard with welcome message
        navigate('/dashboard', { state: { welcomeMessage: 'Welcome to ScholarSphere! Your account has been created successfully.' } });
      } catch (loginErr) {
        // If auto-login fails, redirect to login page
        clearSignupData();
        navigate('/login', { state: { message: 'Registration successful! Please login with your new credentials.' } });
      }
    } catch (err) {
      setError('Failed to register credentials. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <ConnectionParticles
        className="signup-particles"
        colors={SIGNUP_PARTICLE_COLORS}
        linkColor={SIGNUP_PARTICLE_LINK_COLOR}
        quantity={SIGNUP_PARTICLE_QUANTITY}
      />
      <div className="signup-card">
        <h1 className="signup-title">Sign Up for ScholarSphere</h1>
        
        {error && <div className="error-message">{error}</div>}

        <div className="signup-progress">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>1</div>
          <div className={`progress-line ${step >= 2 ? 'active' : ''}`}></div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>2</div>
          <div className={`progress-line ${step >= 3 ? 'active' : ''}`}></div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>3</div>
        </div>

        {step === 1 && (
          <BasicInfoForm
            onSubmit={handleStep1Submit}
            institutions={institutions}
            loading={loading}
          />
        )}

        {step === 2 && (
          <>
            {hasExistingCredentials ? (
              <div className="signup-step">
                <h2 className="step-title">Account Already Exists</h2>
                <p className="step-description">
                  It looks like you already have an account with ScholarSphere. 
                  Please log in with your existing credentials.
                </p>
                <div className="confirmation-buttons">
                  <button
                    type="button"
                    onClick={() => navigate('/login')}
                    className="step-button step-button-primary"
                  >
                    Go to Login
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setHasExistingCredentials(false);
                      setShowConfirmation(true);
                    }}
                    className="step-button step-button-secondary"
                  >
                    Back
                  </button>
                </div>
              </div>
            ) : (
              <ConfirmationStep
                initialData={signupData}
                onSubmit={handleFormSubmit}
                loading={loading}
                institutions={institutions}
                showConfirmation={showConfirmation}
                onConfirm={handleConfirmationYes}
                onDeny={handleConfirmationNo}
                doPrefill={signupData.doPrefill}
                isExisting={signupData.exists}
                matchType={signupData.matchType}
              />
            )}
          </>
        )}

        {step === 3 && (
          <CredentialsForm
            onSubmit={handleStep3Submit}
            loading={loading}
            stepNumber={3}
          />
        )}

        <p className="signup-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}

export default Signup;

