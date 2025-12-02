import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import ConnectionParticles from '../components/ConnectionParticles';
import { login } from '../services/api';
import './Login.css';

// Stable particle config to prevent re-renders
const PARTICLE_COLORS = ['#ffffff', '#dfe8ff'];
const PARTICLE_LINK_COLOR = '#c6d6ff';
const PARTICLE_QUANTITY = 60;

/**
 * Login component - handles user authentication
 */
function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({
    username: false,
    password: false,
  });

  useEffect(() => {
    // Check for redirect message from signup
    if (location.state?.message) {
      setMessage(location.state.message);
    }
  }, [location]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
    // Clear field error when user types
    setFieldErrors({
      ...fieldErrors,
      [e.target.name]: false,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await login(formData);

      if (response.error) {
        setError(response.error);
        const errorMsg = response.error.toLowerCase();
        if (errorMsg.includes('username not found') || errorMsg.includes('username')) {
          setFieldErrors({ username: true, password: false });
        } else if (errorMsg.includes('password') || errorMsg.includes('invalid password')) {
          setFieldErrors({ username: false, password: true });
        } else {
          setFieldErrors({ username: false, password: false });
        }
        setLoading(false);
        return;
      }

      if (!response.access_token) {
        setError('Login successful but access token not received. Please try again.');
        setLoading(false);
        return;
      }

      localStorage.setItem('faculty', JSON.stringify(response.faculty));
      localStorage.setItem('faculty_id', response.faculty?.faculty_id);

      navigate('/dashboard');
    } catch (err) {
      setError('An error occurred. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <ConnectionParticles
        className="auth-particles"
        colors={PARTICLE_COLORS}
        linkColor={PARTICLE_LINK_COLOR}
        quantity={PARTICLE_QUANTITY}
      />
      <div className="auth-card">
        <h3 className="auth-title">Login to ScholarSphere</h3>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <div className="auth-input-wrapper">
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                autoComplete="username"
                className={fieldErrors.username ? 'error' : ''}
              />
              {fieldErrors.username && (
                <span className="auth-status-icon error">✗</span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="auth-input-wrapper">
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                autoComplete="current-password"
                className={fieldErrors.password ? 'error' : ''}
              />
              {fieldErrors.password && (
                <span className="auth-status-icon error">✗</span>
              )}
            </div>
          </div>

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="auth-footer">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;

