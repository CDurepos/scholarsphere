import { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import ConnectionParticles from '../components/ConnectionParticles';
import { login } from '../services/api';
import './Login.css';

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
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // API Endpoint: POST /api/auth/login
      // Body: { username: string, password: string }
      // Returns: { token: string, faculty: object } or { error: string }
      const response = await login(formData);

      if (response.error) {
        setError(response.error);
        setLoading(false);
        return;
      }

      // Store token and faculty data (you may want to use context or localStorage)
      localStorage.setItem('token', response.token);
      localStorage.setItem('faculty', JSON.stringify(response.faculty));

      // Redirect to dashboard
      navigate('/');
    } catch (err) {
      setError('An error occurred. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <ConnectionParticles
        className="auth-particles"
        colors={['#ffffff', '#dfe8ff']}
        linkColor="#c6d6ff"
        quantity={60}
      />
      <div className="auth-card">
        <h3 className="auth-title">Login to ScholarSphere</h3>
        
        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
            />
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

