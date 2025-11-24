import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { checkFacultyExists, createFaculty, updateFaculty, registerCredentials } from '../services/api';
import ConnectionParticles from '../components/ConnectionParticles';
import { SignupStep1, SignupStep2Exists, SignupStep2New, SignupStep3 } from '../features/signup/SignupSteps';
import './Signup.css';

/**
 * Multi-step signup component
 * Step 1: Name and institution check
 * Step 2a: "Does this look right?" if user exists
 * Step 2b: Additional info if user doesn't exist
 * Step 3: Credentials setup
 */
function Signup() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [institutions, setInstitutions] = useState([]);
  const [signupData, setSignupData] = useState({
    first_name: '',
    last_name: '',
    institution_name: '',
    faculty_id: null,
    exists: false,
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
    // Load institutions on mount
    loadInstitutions();
  }, []);

  const loadInstitutions = async () => {
    try {
      // API Endpoint: GET /api/institutions
      // Returns: { institutions: Array }
      const response = await getInstitutions();
      if (response.institutions) {
        setInstitutions(response.institutions);
      }
    } catch (err) {
      console.error('Failed to load institutions:', err);
    }
  };

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
        // User exists - go to "Does this look right?" page
        setSignupData({
          ...signupData,
          first_name: data.first_name,
          last_name: data.last_name,
          institution_name: data.institution_name,
          faculty_id: response.faculty.faculty_id,
          exists: true,
          emails: response.faculty.emails || [],
          phones: response.faculty.phones || [],
          departments: response.faculty.departments || [],
          titles: response.faculty.titles || [],
          biography: response.faculty.biography || '',
          orcid: response.faculty.orcid || '',
          google_scholar_url: response.faculty.google_scholar_url || '',
          research_gate_url: response.faculty.research_gate_url || '',
        });
        setStep(2); // Step 2a - exists
      } else {
        // User doesn't exist - collect additional info
        setSignupData({
          ...signupData,
          first_name: data.first_name,
          last_name: data.last_name,
          institution_name: data.institution_name,
          exists: false,
        });
        setStep(2); // Step 2b - new user (step 2 for new users)
      }
    } catch (err) {
      setError('Failed to check faculty. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStep2ExistsSubmit = async (updatedData) => {
    setLoading(true);
    setError('');

    try {
      // API Endpoint: PUT /api/faculty/:faculty_id
      // Body: { ...updated fields }
      // Returns: { message: string }
      await updateFaculty(signupData.faculty_id, updatedData);

      // Update local data
      setSignupData({
        ...signupData,
        ...updatedData,
      });

      // Move to credentials step
      setStep(3);
    } catch (err) {
      setError('Failed to update faculty information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStep2NewSubmit = async (data) => {
    setLoading(true);
    setError('');

    try {
      // API Endpoint: POST /api/faculty/create
      // Body: { first_name, last_name, institution_name, emails, phones, departments, titles, ... }
      // Returns: { faculty_id: string, message: string }
      const response = await createFaculty({
        first_name: signupData.first_name,
        last_name: signupData.last_name,
        institution_name: signupData.institution_name,
        ...data,
      });

      setSignupData({
        ...signupData,
        faculty_id: response.faculty_id,
        ...data,
      });

      // Move to credentials step
      setStep(3);
    } catch (err) {
      setError('Failed to create faculty. Please try again.');
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

        {step === 2 && signupData.exists && (
          <SignupStep2Exists
            facultyData={signupData}
            onSubmit={handleStep2ExistsSubmit}
            loading={loading}
          />
        )}

        {step === 2 && !signupData.exists && (
          <SignupStep2New
            initialData={signupData}
            onSubmit={handleStep2NewSubmit}
            loading={loading}
          />
        )}

        {step === 3 && (
          <SignupStep3
            onSubmit={handleStep3Submit}
            loading={loading}
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

