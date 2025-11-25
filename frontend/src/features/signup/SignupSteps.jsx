import { useState, useEffect } from 'react';
import './SignupSteps.css';

/**
 * Combined Signup Steps Component
 * Contains all signup step components in a single file
 */

// Step 1: Name and Institution
export function SignupStep1({ onSubmit, institutions, loading }) {
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
    <div className="signup-step">
      <h2 className="step-title">Step 1: Basic Information</h2>
      <p className="step-description">
        Enter your name and institution to check if you already exist in our database.
      </p>

      <form onSubmit={handleSubmit} className="signup-form">
        <div className="form-group">
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

        <div className="form-group">
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

        <div className="form-group">
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

        <button type="submit" className="step-button" disabled={loading}>
          {loading ? 'Checking...' : 'Continue'}
        </button>
      </form>
    </div>
  );
}

// Step 2: Combined confirmation + form component
export function SignupStep2({ initialData, onSubmit, loading, showConfirmation, onConfirm, onDeny, doPrefill, isExisting }) {
  // If we need to show confirmation first, show that
  if (showConfirmation) {
    return (
      <div className="signup-step">
        <h2 className="step-title">Step 2: Is this you?</h2>
        <p className="step-description">
          We found a faculty member in our database with this information:
        </p>

        <div className="faculty-info-summary">
          <p><strong>Name:</strong> {initialData.first_name} {initialData.last_name}</p>
          <p><strong>Institution:</strong> {initialData.institution_name}</p>
        </div>

        <div className="confirmation-buttons">
          <button
            type="button"
            onClick={onConfirm}
            className="step-button step-button-primary"
            disabled={loading}
          >
            Yes, this is me
          </button>
          <button
            type="button"
            onClick={onDeny}
            className="step-button step-button-secondary"
            disabled={loading}
          >
            No, this is not me
          </button>
        </div>
      </div>
    );
  }

  // Otherwise, show the form
  return <SignupStep3Form 
    initialData={initialData}
    onSubmit={onSubmit}
    loading={loading}
    doPrefill={doPrefill}
    stepNumber={2}
    isExisting={isExisting}
  />;
}

// Step 3: Unified form for all faculty information (can be prefilled or empty)
export function SignupStep3Form({ initialData, onSubmit, loading, doPrefill = false, stepNumber = 2, isExisting = false }) {
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
    <div className="signup-step">
      <h2 className="step-title">Step {stepNumber}: Additional Information</h2>
      <p className="step-description">
        {doPrefill 
          ? 'Please review and update your information below.'
          : 'Please provide the following information to complete your profile.'}
      </p>

      <form onSubmit={handleSubmit} className="signup-form">
        <div className="form-group">
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

        <div className="form-group">
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

        <div className="form-group">
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

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={formData.emails[0] || ''}
            onChange={(e) => handleArrayChange('emails', 0, e.target.value)}
            placeholder=""
          />
        </div>

        <div className="form-group">
          <label htmlFor="department">Department</label>
          <input
            type="text"
            id="department"
            value={formData.departments[0] || ''}
            onChange={(e) => handleArrayChange('departments', 0, e.target.value)}
            placeholder=""
          />
        </div>

        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            value={formData.titles[0] || ''}
            onChange={(e) => handleArrayChange('titles', 0, e.target.value)}
            placeholder=""
          />
        </div>

        <button type="submit" className="step-button" disabled={loading}>
          {loading ? (isExisting ? 'Updating...' : 'Creating...') : 'Continue to Credentials'}
        </button>
      </form>
    </div>
  );
}

// Step 2a: "Does this look right?" - for existing faculty (DEPRECATED - keeping for reference)
export function SignupStep2Exists({ facultyData, onSubmit, loading }) {
  const [formData, setFormData] = useState({
    emails: facultyData.emails || [],
    phones: facultyData.phones || [],
    departments: facultyData.departments || [],
    titles: facultyData.titles || [],
    biography: facultyData.biography || '',
    orcid: facultyData.orcid || '',
    google_scholar_url: facultyData.google_scholar_url || '',
    research_gate_url: facultyData.research_gate_url || '',
  });

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
    onSubmit(formData);
  };

  return (
    <div className="signup-step">
      <h2 className="step-title">Does this look right?</h2>
      <p className="step-description">
        We found your information in our database. Please review and update if needed.
      </p>

      <div className="faculty-info-summary">
        <p><strong>Name:</strong> {facultyData.first_name} {facultyData.last_name}</p>
        <p><strong>Institution:</strong> {facultyData.institution_name}</p>
      </div>

      <form onSubmit={handleSubmit} className="signup-form">
        <div className="form-group">
          <label>Email Addresses</label>
          {formData.emails.map((email, index) => (
            <div key={index} className="array-input-group">
              <input
                type="email"
                value={email}
                onChange={(e) => handleArrayChange('emails', index, e.target.value)}
                placeholder="email@example.com"
              />
              {formData.emails.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeArrayItem('emails', index)}
                  className="remove-button"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('emails')}
            className="add-button"
          >
            + Add Email
          </button>
        </div>

        <div className="form-group">
          <label>Phone Numbers</label>
          {formData.phones.map((phone, index) => (
            <div key={index} className="array-input-group">
              <input
                type="tel"
                value={phone}
                onChange={(e) => handleArrayChange('phones', index, e.target.value)}
                placeholder="207-555-1234"
              />
              {formData.phones.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeArrayItem('phones', index)}
                  className="remove-button"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('phones')}
            className="add-button"
          >
            + Add Phone
          </button>
        </div>

        <div className="form-group">
          <label>Departments</label>
          {formData.departments.map((dept, index) => (
            <div key={index} className="array-input-group">
              <input
                type="text"
                value={dept}
                onChange={(e) => handleArrayChange('departments', index, e.target.value)}
                placeholder="Computer Science"
              />
              {formData.departments.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeArrayItem('departments', index)}
                  className="remove-button"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('departments')}
            className="add-button"
          >
            + Add Department
          </button>
        </div>

        <div className="form-group">
          <label>Titles</label>
          {formData.titles.map((title, index) => (
            <div key={index} className="array-input-group">
              <input
                type="text"
                value={title}
                onChange={(e) => handleArrayChange('titles', index, e.target.value)}
                placeholder="Professor"
              />
              {formData.titles.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeArrayItem('titles', index)}
                  className="remove-button"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('titles')}
            className="add-button"
          >
            + Add Title
          </button>
        </div>

        <div className="form-group">
          <label htmlFor="biography">Biography</label>
          <textarea
            id="biography"
            name="biography"
            value={formData.biography}
            onChange={handleChange}
            placeholder="Your research interests and background..."
          />
        </div>

        <div className="form-group">
          <label htmlFor="orcid">ORCID ID</label>
          <input
            type="text"
            id="orcid"
            name="orcid"
            value={formData.orcid}
            onChange={handleChange}
            placeholder="0000-0000-0000-0000"
          />
        </div>

        <div className="form-group">
          <label htmlFor="google_scholar_url">Google Scholar URL</label>
          <input
            type="url"
            id="google_scholar_url"
            name="google_scholar_url"
            value={formData.google_scholar_url}
            onChange={handleChange}
            placeholder="https://scholar.google.com/..."
          />
        </div>

        <div className="form-group">
          <label htmlFor="research_gate_url">ResearchGate URL</label>
          <input
            type="url"
            id="research_gate_url"
            name="research_gate_url"
            value={formData.research_gate_url}
            onChange={handleChange}
            placeholder="https://www.researchgate.net/..."
          />
        </div>

        <button type="submit" className="step-button" disabled={loading}>
          {loading ? 'Updating...' : 'Continue to Credentials'}
        </button>
      </form>
    </div>
  );
}

// Step 2b: Additional Information - for new faculty
export function SignupStep2New({ initialData, onSubmit, loading }) {
  const [formData, setFormData] = useState({
    emails: [''],
    phones: [''],
    departments: [''],
    titles: [''],
    biography: '',
    orcid: '',
    google_scholar_url: '',
    research_gate_url: '',
  });

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
    <div className="signup-step">
      <h2 className="step-title">Step 2: Additional Information</h2>
      <p className="step-description">
        We couldn't find you in our database. Please provide the following information.
      </p>

      <div className="faculty-info-summary">
        <p><strong>Name:</strong> {initialData.first_name} {initialData.last_name}</p>
        <p><strong>Institution:</strong> {initialData.institution_name}</p>
      </div>

      <form onSubmit={handleSubmit} className="signup-form">
        <div className="form-group">
          <label>Email *</label>
          {formData.emails.map((email, index) => (
            <div key={index} className="array-input-group">
              <input
                type="email"
                value={email}
                onChange={(e) => handleArrayChange('emails', index, e.target.value)}
                placeholder="email@example.com"
                required={index === 0}
              />
              {formData.emails.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeArrayItem('emails', index)}
                  className="remove-button"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('emails')}
            className="add-button"
          >
            + Add Email
          </button>
        </div>

        <div className="form-group">
          <label>Phone</label>
          {formData.phones.map((phone, index) => (
            <div key={index} className="array-input-group">
              <input
                type="tel"
                value={phone}
                onChange={(e) => handleArrayChange('phones', index, e.target.value)}
                placeholder="207-555-1234"
              />
              {formData.phones.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeArrayItem('phones', index)}
                  className="remove-button"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('phones')}
            className="add-button"
          >
            + Add Phone
          </button>
        </div>

        <div className="form-group">
          <label>Department</label>
          {formData.departments.map((dept, index) => (
            <div key={index} className="array-input-group">
              <input
                type="text"
                value={dept}
                onChange={(e) => handleArrayChange('departments', index, e.target.value)}
                placeholder="Computer Science"
              />
              {formData.departments.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeArrayItem('departments', index)}
                  className="remove-button"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('departments')}
            className="add-button"
          >
            + Add Department
          </button>
        </div>

        <div className="form-group">
          <label>Title</label>
          {formData.titles.map((title, index) => (
            <div key={index} className="array-input-group">
              <input
                type="text"
                value={title}
                onChange={(e) => handleArrayChange('titles', index, e.target.value)}
                placeholder="Professor"
              />
              {formData.titles.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeArrayItem('titles', index)}
                  className="remove-button"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addArrayItem('titles')}
            className="add-button"
          >
            + Add Title
          </button>
        </div>

        <div className="form-group">
          <label htmlFor="biography">Biography</label>
          <textarea
            id="biography"
            name="biography"
            value={formData.biography}
            onChange={handleChange}
            placeholder="Your research interests and background..."
          />
        </div>

        <div className="form-group">
          <label htmlFor="orcid">ORCID ID</label>
          <input
            type="text"
            id="orcid"
            name="orcid"
            value={formData.orcid}
            onChange={handleChange}
            placeholder="0000-0000-0000-0000"
          />
        </div>

        <div className="form-group">
          <label htmlFor="google_scholar_url">Google Scholar URL</label>
          <input
            type="url"
            id="google_scholar_url"
            name="google_scholar_url"
            value={formData.google_scholar_url}
            onChange={handleChange}
            placeholder="https://scholar.google.com/..."
          />
        </div>

        <div className="form-group">
          <label htmlFor="research_gate_url">ResearchGate URL</label>
          <input
            type="url"
            id="research_gate_url"
            name="research_gate_url"
            value={formData.research_gate_url}
            onChange={handleChange}
            placeholder="https://www.researchgate.net/..."
          />
        </div>

        <button type="submit" className="step-button" disabled={loading}>
          {loading ? 'Creating...' : 'Continue to Credentials'}
        </button>
      </form>
    </div>
  );
}

// Step 3: Credentials Setup
export function SignupStep3({ onSubmit, loading, stepNumber = 3 }) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});

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
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
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
    <div className="signup-step">
      <h2 className="step-title">Step {stepNumber}: Create Credentials</h2>
      <p className="step-description">
        Create a username and password to access your ScholarSphere account.
      </p>

      <form onSubmit={handleSubmit} className="signup-form">
        <div className="form-group">
          <label htmlFor="username">Username *</label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
            autoComplete="username"
            className={errors.username ? 'error' : ''}
          />
          {errors.username && (
            <span className="error-text">{errors.username}</span>
          )}
          <small className="form-hint">Must be at least 3 characters and unique</small>
        </div>

        <div className="form-group">
          <label htmlFor="password">Password *</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            autoComplete="new-password"
            className={errors.password ? 'error' : ''}
          />
          {errors.password && (
            <span className="error-text">{errors.password}</span>
          )}
          <small className="form-hint">Must be at least 8 characters</small>
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password *</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            autoComplete="new-password"
            className={errors.confirmPassword ? 'error' : ''}
          />
          {errors.confirmPassword && (
            <span className="error-text">{errors.confirmPassword}</span>
          )}
        </div>

        <button type="submit" className="step-button" disabled={loading}>
          {loading ? 'Registering...' : 'Complete Registration'}
        </button>
      </form>
    </div>
  );
}

