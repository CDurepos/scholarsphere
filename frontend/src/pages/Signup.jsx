import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { checkFacultyExists, createFaculty, updateFaculty, registerCredentials } from '../services/api';
import ConnectionParticles from '../components/ConnectionParticles';
import { SignupStep1, SignupStep2, SignupStep3 } from '../features/signup/SignupSteps';
import './Signup.css';
import { getInstitutions } from '../services/api';

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
  const [signupData, setSignupData] = useState({
    first_name: '',
    last_name: '',
    institution_name: '',
    faculty_id: null,
    exists: false,
    doPrefill: false, // Whether to prefill the form
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

  useEffect(() => {
    const fetchInstitutions = async () => {
      const institutions = await getInstitutions();
      setInstitutions(institutions);
    };
    fetchInstitutions();
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
        setSignupData({
          ...signupData,
          first_name: data.first_name,
          last_name: data.last_name,
          institution_name: data.institution_name,
          faculty_id: response.faculty.faculty_id,
          exists: true,
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
  const handleConfirmationYes = () => {
    setSignupData({
      ...signupData,
      doPrefill: true, // Prefill the form with existing data
    });
    setShowConfirmation(false); // Hide confirmation, show form
  };

  // Handle confirmation step - user clicked "No, this is not me"
  const handleConfirmationNo = () => {
    // Clear all existing data and treat as new user
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
      // Determine if we should update (PUT) or create (POST)
      // If user exists and has a faculty_id, update them
      // Otherwise, create a new faculty record
      const shouldUpdate = signupData.exists && signupData.faculty_id;

      if (shouldUpdate) {
        // Update existing faculty - PUT /api/faculty/:faculty_id
        await updateFaculty(signupData.faculty_id, formData);
        setSignupData({
          ...signupData,
          ...formData,
        });
      } else {
        // Create new faculty - POST /api/faculty/create
        const response = await createFaculty(formData);
        setSignupData({
          ...signupData,
          faculty_id: response.faculty_id,
          exists: true, // Now they exist in the database
          ...formData,
        });
      }

      // Move to credentials step
      setStep(3);
    } catch (err) {
      const shouldUpdate = signupData.exists && signupData.faculty_id;
      setError(shouldUpdate
        ? 'Failed to update faculty information. Please try again.'
        : 'Failed to create faculty. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStep3Submit = async (credentials) => {
    setLoading(true);
    setError('');

    try {
      // API Endpoint: POST /api/auth/register
      // Body: { faculty_id: string, username: string, password: string }
      // Returns: { message: string } or { error: string }
      const response = await registerCredentials({
        faculty_id: signupData.faculty_id,
        username: credentials.username,
        password: credentials.password,
      });

      if (response.error) {
        setError(response.error);
        setLoading(false);
        return;
      }

      // Registration successful - redirect to login or auto-login
      navigate('/login', { state: { message: 'Registration successful! Please login.' } });
    } catch (err) {
      setError('Failed to register credentials. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <ConnectionParticles
        className="signup-particles"
        colors={['#ffffff', '#dfe8ff']}
        linkColor="#c6d6ff"
        quantity={75}
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
          <SignupStep1
            onSubmit={handleStep1Submit}
            institutions={institutions}
            loading={loading}
          />
        )}

        {step === 2 && (
          <SignupStep2
            initialData={signupData}
            onSubmit={handleFormSubmit}
            loading={loading}
            institutions={institutions}
            showConfirmation={showConfirmation}
            onConfirm={handleConfirmationYes}
            onDeny={handleConfirmationNo}
            doPrefill={signupData.doPrefill}
            isExisting={signupData.exists}
          />
        )}

        {step === 3 && (
          <SignupStep3
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

