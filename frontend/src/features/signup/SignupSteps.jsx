import { useState, useEffect, useRef } from 'react';
import { checkUsernameAvailable } from '../../services/api';
import styles from './SignupSteps.module.css';

/**
 * Combined Signup Steps Component
 * Contains all signup step components in a single file
 */

// Step 1: Basic Information (Name and Institution)
export function BasicInfoForm({ onSubmit, institutions, loading }) {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    institution_name: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className={styles['signup-step']}>
      <h2 className={styles['step-title']}>Get started</h2>
      <p className={styles['step-description']}>
        Let's begin with some basic information.
      </p>

      <form onSubmit={handleSubmit} className={styles['signup-form']}>
        <div className={styles['form-group']}>
          <label htmlFor="first_name">First Name *</label>
          <input
            type="text"
            id="first_name"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            required
            autoComplete="given-name"
          />
        </div>

        <div className={styles['form-group']}>
          <label htmlFor="last_name">Last Name *</label>
          <input
            type="text"
            id="last_name"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            required
            autoComplete="family-name"
          />
        </div>

        <div className={styles['form-group']}>
          <label htmlFor="institution_name">Institution *</label>
          {institutions.length > 0 ? (
            <select
              id="institution_name"
              name="institution_name"
              value={formData.institution_name}
              onChange={handleChange}
              required
            >
              <option value="">Select an institution</option>
              {institutions.map((inst) => (
                <option key={inst.institution_id} value={inst.name}>
                  {inst.name}
                </option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              id="institution_name"
              name="institution_name"
              value={formData.institution_name}
              onChange={handleChange}
              required
              placeholder="Enter institution name"
            />
          )}
        </div>

        <button type="submit" className={styles['step-button']} disabled={loading}>
          {loading ? 'Checking...' : 'Continue'}
        </button>
      </form>
    </div>
  );
}

// Step 2: Confirmation wrapper (shows confirmation or profile form)
export function ConfirmationStep({ initialData, onSubmit, loading, showConfirmation, onConfirm, onDeny, doPrefill, isExisting, matchType }) {
  // If we need to show confirmation first, show that
  if (showConfirmation) {
    // Get the institution name to display (use the one from DB if available, otherwise from search)
    const displayInstitution = initialData.institution_name || 'Not specified';
    
    return (
      <div className={styles['signup-step']}>
        <h2 className={styles['step-title']}>Is this you?</h2>
        <p className={styles['step-description']}>
          {matchType === 'name_only' 
            ? 'We found someone with the same name, but at a different institution:'
            : 'We found someone in our database matching this information:'}
        </p>

        <div className={styles['faculty-info-summary']}>
          <p><strong>Name:</strong> {initialData.first_name} {initialData.last_name}</p>
          <p><strong>Institution:</strong> {displayInstitution}</p>
        </div>

        {matchType === 'name_only' && (
          <div className={styles['match-warning-box']}>
            <p className={styles['match-warning']}>
              ⚠️ Note: The institution in our database differs from what you entered. 
              If this is you, you can update your institution information.
            </p>
          </div>
        )}

        <div className={styles['confirmation-buttons']}>
          <button
            type="button"
            onClick={onConfirm}
            className={`${styles['step-button']} ${styles['step-button-primary']}`}
            disabled={loading}
          >
            Yes, this is me
          </button>
          <button
            type="button"
            onClick={onDeny}
            className={`${styles['step-button']} ${styles['step-button-secondary']}`}
            disabled={loading}
          >
            No, this is not me
          </button>
        </div>
      </div>
    );
  }

  // Otherwise, show the form
  return <ProfileInfoForm 
    initialData={initialData}
    onSubmit={onSubmit}
    loading={loading}
    doPrefill={doPrefill}
    stepNumber={2}
    isExisting={isExisting}
  />;
}

// Profile Information Form (used in Step 2 - can be prefilled or empty)
export function ProfileInfoForm({ initialData, onSubmit, loading, doPrefill = false, stepNumber = 2, isExisting = false }) {
  // Initialize form data based on whether it should be prefilled
  const getInitialFormData = () => {
    if (doPrefill) {
      // Prefill with existing data (only first item from arrays)
      return {
        first_name: initialData.first_name || '',
        last_name: initialData.last_name || '',
        institution_name: initialData.institution_name || '',
        emails: initialData.emails && initialData.emails.length > 0 ? [initialData.emails[0]] : [''],
        phones: initialData.phones && initialData.phones.length > 0 ? [initialData.phones[0]] : [''],
        departments: initialData.departments && initialData.departments.length > 0 ? [initialData.departments[0]] : [''],
        titles: initialData.titles && initialData.titles.length > 0 ? [initialData.titles[0]] : [''],
        biography: initialData.biography || '',
        orcid: initialData.orcid || '',
        google_scholar_url: initialData.google_scholar_url || '',
        research_gate_url: initialData.research_gate_url || '',
      };
    } else {
      // Empty form (only keep name and institution from step 1)
      return {
        first_name: initialData.first_name || '',
        last_name: initialData.last_name || '',
        institution_name: initialData.institution_name || '',
        emails: [''],
        phones: [''],
        departments: [''],
        titles: [''],
        biography: '',
        orcid: '',
        google_scholar_url: '',
        research_gate_url: '',
      };
    }
  };

  const [formData, setFormData] = useState(getInitialFormData);

  // Update form data when doPrefill changes (user clicks Yes/No)
  useEffect(() => {
    if (!doPrefill) {
      // User clicked "No" or is new - clear all DB data, keep only name/institution from step 1
      setFormData({
        first_name: initialData.first_name || '',
        last_name: initialData.last_name || '',
        institution_name: initialData.institution_name || '',
        emails: [''],
        phones: [''],
        departments: [''],
        titles: [''],
        biography: '',
        orcid: '',
        google_scholar_url: '',
        research_gate_url: '',
      });
    } else {
      // User clicked "Yes" - prefill with existing data (only first item from arrays)
      setFormData({
        first_name: initialData.first_name || '',
        last_name: initialData.last_name || '',
        institution_name: initialData.institution_name || '',
        emails: initialData.emails && initialData.emails.length > 0 ? [initialData.emails[0]] : [''],
        phones: initialData.phones && initialData.phones.length > 0 ? [initialData.phones[0]] : [''],
        departments: initialData.departments && initialData.departments.length > 0 ? [initialData.departments[0]] : [''],
        titles: initialData.titles && initialData.titles.length > 0 ? [initialData.titles[0]] : [''],
        biography: initialData.biography || '',
        orcid: initialData.orcid || '',
        google_scholar_url: initialData.google_scholar_url || '',
        research_gate_url: initialData.research_gate_url || '',
      });
    }
  }, [doPrefill]);

  const handleArrayChange = (field, index, value) => {
    const newArray = [...formData[field]];
    newArray[index] = value;
    setFormData({ ...formData, [field]: newArray });
  };

  const addArrayItem = (field) => {
    setFormData({
      ...formData,
      [field]: [...formData[field], ''],
    });
  };

  const removeArrayItem = (field, index) => {
    setFormData({
      ...formData,
      [field]: formData[field].filter((_, i) => i !== index),
    });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Filter out empty strings from arrays
    const cleanedData = {
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim(),
      institution_name: formData.institution_name.trim(),
      emails: formData.emails.filter(email => email.trim() !== ''),
      phones: formData.phones.filter(phone => phone.trim() !== ''),
      departments: formData.departments.filter(dept => dept.trim() !== ''),
      titles: formData.titles.filter(title => title.trim() !== ''),
      biography: formData.biography.trim(),
      orcid: formData.orcid.trim(),
      google_scholar_url: formData.google_scholar_url.trim(),
      research_gate_url: formData.research_gate_url.trim(),
    };

    onSubmit(cleanedData);
  };

  return (
    <div className={styles['signup-step']}>
      <h2 className={styles['step-title']}>Tell us about yourself</h2>
      <p className={styles['step-description']}>
        {doPrefill 
          ? 'Review and update your information below.'
          : 'Help us learn more about you to complete your profile.'}
      </p>

      <form onSubmit={handleSubmit} className={styles['signup-form']}>
        <div className={styles['form-group']}>
          <label htmlFor="first_name">First Name *</label>
          <input
            type="text"
            id="first_name"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            required
            autoComplete="given-name"
          />
        </div>

        <div className={styles['form-group']}>
          <label htmlFor="last_name">Last Name *</label>
          <input
            type="text"
            id="last_name"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            required
            autoComplete="family-name"
          />
        </div>

        <div className={styles['form-group']}>
          <label htmlFor="institution_name">Institution *</label>
          <input
            type="text"
            id="institution_name"
            name="institution_name"
            value={formData.institution_name}
            onChange={handleChange}
            required
            placeholder=""
          />
        </div>

        <div className={styles['form-group']}>
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={formData.emails[0] || ''}
            onChange={(e) => handleArrayChange('emails', 0, e.target.value)}
            placeholder=""
          />
        </div>

        <div className={styles['form-group']}>
          <label htmlFor="department">Department</label>
          <input
            type="text"
            id="department"
            value={formData.departments[0] || ''}
            onChange={(e) => handleArrayChange('departments', 0, e.target.value)}
            placeholder=""
          />
        </div>

        <div className={styles['form-group']}>
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            value={formData.titles[0] || ''}
            onChange={(e) => handleArrayChange('titles', 0, e.target.value)}
            placeholder=""
          />
        </div>

        <button type="submit" className={styles['step-button']} disabled={loading}>
          {loading ? (isExisting ? 'Updating...' : 'Creating...') : 'Continue to Credentials'}
        </button>
      </form>
    </div>
  );
}

// Step 3: Credentials Setup (Username and Password)
export function CredentialsForm({ onSubmit, loading, stepNumber = 3 }) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [usernameStatus, setUsernameStatus] = useState(null); // null = not checked, true = available, false = taken
  const [checkingUsername, setCheckingUsername] = useState(false);
  const usernameTimeoutRef = useRef(null);

  // Debounced username checking
  useEffect(() => {
    // Clear previous timeout
    if (usernameTimeoutRef.current) {
      clearTimeout(usernameTimeoutRef.current);
    }

    // Reset status if username is too short or too long
    if (!formData.username || formData.username.trim().length < 3 || formData.username.trim().length > 16) {
      setUsernameStatus(null);
      setCheckingUsername(false);
      return;
    }

    // Set checking state
    setCheckingUsername(true);
    setUsernameStatus(null);

    // Debounce the API call
    usernameTimeoutRef.current = setTimeout(async () => {
      try {
        const result = await checkUsernameAvailable(formData.username.trim());
        if (result.username === formData.username.trim()) {
          setUsernameStatus(result.available);
        }
      } catch (err) {
        setUsernameStatus(false);
      } finally {
        setCheckingUsername(false);
      }
    }, 500); // Wait 500ms after user stops typing

    // Cleanup
    return () => {
      if (usernameTimeoutRef.current) {
        clearTimeout(usernameTimeoutRef.current);
      }
    };
  }, [formData.username]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error when user types
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: '',
      });
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 4) {
      newErrors.username = 'Username must be at least 4 characters';
    } else if (formData.username.length > 16) {
      newErrors.username = 'Username must be 16 characters or less';
    } else if (usernameStatus === false) {
      newErrors.username = 'Username is already taken';
    } else if (usernameStatus === null && formData.username.trim().length >= 3) {
      newErrors.username = 'Please wait while we check username availability';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }

    onSubmit({
      username: formData.username,
      password: formData.password,
    });
  };

  return (
    <div className={styles['signup-step']}>
      <h2 className={styles['step-title']}>Create your account</h2>
      <p className={styles['step-description']}>
        Choose a username and password to secure your ScholarSphere account.
      </p>

      <form onSubmit={handleSubmit} className={styles['signup-form']}>
        <div className={styles['form-group']}>
          <label htmlFor="username">Username *</label>
          <div className={styles['username-input-wrapper']}>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              autoComplete="username"
              maxLength={16}
              className={
                errors.username 
                  ? styles.error 
                  : usernameStatus === true 
                    ? styles.success 
                    : usernameStatus === false 
                      ? styles.error 
                      : ''
              }
            />
            {checkingUsername && formData.username.trim().length >= 3 && (
              <span className={`${styles['username-status-icon']} ${styles.checking}`}>⟳</span>
            )}
            {!checkingUsername && usernameStatus === true && (
              <span className={`${styles['username-status-icon']} ${styles.available}`}>✓</span>
            )}
            {!checkingUsername && usernameStatus === false && (
              <span className={`${styles['username-status-icon']} ${styles.taken}`}>✗</span>
            )}
          </div>
          {errors.username && (
            <span className={styles['error-text']}>{errors.username}</span>
          )}
          <small className={styles['form-hint']}>Must be 4-16 characters</small>
        </div>

        <div className={styles['form-group']}>
          <label htmlFor="password">Password *</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            autoComplete="new-password"
            className={errors.password ? styles.error : ''}
          />
          {errors.password && (
            <span className={styles['error-text']}>{errors.password}</span>
          )}
          <small className={styles['form-hint']}>Must be at least 8 characters</small>
        </div>

        <div className={styles['form-group']}>
          <label htmlFor="confirmPassword">Confirm Password *</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            autoComplete="new-password"
            className={errors.confirmPassword ? styles.error : ''}
          />
          {errors.confirmPassword && (
            <span className={styles['error-text']}>{errors.confirmPassword}</span>
          )}
        </div>

        <button type="submit" className={styles['step-button']} disabled={loading}>
          {loading ? 'Registering...' : 'Complete Registration'}
        </button>
      </form>
    </div>
  );
}
