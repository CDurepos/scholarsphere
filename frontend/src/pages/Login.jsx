/**
 * @author Clayton Durepos
 */

import { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import ConnectionParticles from '../components/ConnectionParticles';
import { login, isAuthenticated } from '../services/api';
import styles from './Login.module.css';

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
    remember_me: false,
  });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [fieldErrors, setFieldErrors] = useState({
    username: false,
    password: false,
  });

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    const checkAuth = async () => {
      const authenticated = await isAuthenticated();
      if (authenticated) {
        navigate('/dashboard', { replace: true });
      } else {
        setCheckingAuth(false);
      }
    };
    checkAuth();
  }, [navigate]);

  useEffect(() => {
    // Check for redirect message from signup
    if (location.state?.message) {
      setMessage(location.state.message);
    }
  }, [location]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
    setError('');
    // Clear field error when user types
    if (type !== 'checkbox') {
      setFieldErrors({
        ...fieldErrors,
        [name]: false,
      });
    }
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

  // Show nothing while checking auth to prevent flash
  if (checkingAuth) {
    return (
      <div className={styles['auth-container']}>
        <ConnectionParticles
          className={styles['auth-particles']}
          colors={PARTICLE_COLORS}
          linkColor={PARTICLE_LINK_COLOR}
          quantity={PARTICLE_QUANTITY}
        />
      </div>
    );
  }

  return (
    <div className={styles['auth-container']}>
      <ConnectionParticles
        className={styles['auth-particles']}
        colors={PARTICLE_COLORS}
        linkColor={PARTICLE_LINK_COLOR}
        quantity={PARTICLE_QUANTITY}
      />
      <div className={styles['auth-card']}>
        <h3 className={styles['auth-title']}>Login to ScholarSphere</h3>

        {message && <div className={styles['success-message']}>{message}</div>}
        {error && <div className={styles['error-message']}>{error}</div>}

        <form onSubmit={handleSubmit} className={styles['auth-form']}>
          <div className={styles['form-group']}>
            <label htmlFor="username">Username</label>
            <div className={styles['auth-input-wrapper']}>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                autoComplete="username"
                className={fieldErrors.username ? styles.error : ''}
              />
              {fieldErrors.username && (
                <span className={`${styles['auth-status-icon']} ${styles.error}`}>✗</span>
              )}
            </div>
          </div>

          <div className={styles['form-group']}>
            <label htmlFor="password">Password</label>
            <div className={styles['auth-input-wrapper']}>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                autoComplete="current-password"
                className={fieldErrors.password ? styles.error : ''}
              />
              {fieldErrors.password && (
                <span className={`${styles['auth-status-icon']} ${styles.error}`}>✗</span>
              )}
            </div>
          </div>

          <div className={styles['remember-me-group']}>
            <label className={styles['remember-me-label']}>
              <input
                type="checkbox"
                name="remember_me"
                checked={formData.remember_me}
                onChange={handleChange}
                className={styles['remember-me-checkbox']}
              />
              <span className={styles['remember-me-checkmark']}></span>
              <span className={styles['remember-me-text']}>Remember me for 30 days</span>
            </label>
          </div>

          <button type="submit" className={styles['auth-button']} disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className={styles['auth-footer']}>
          Don't have an account? <Link to="/signup">Sign up</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
