import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getFacultyById, updateFaculty, isAuthenticated } from '../services/api';
import Header from '../components/Header';
import './FacultyProfile.css';

/**
 * Faculty Profile Page
 * - Displays faculty member information
 * - Allows editing if viewing own profile
 */
function FacultyProfile() {
  const { facultyId } = useParams();
  const navigate = useNavigate();
  
  const [faculty, setFaculty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [isOwnProfile, setIsOwnProfile] = useState(false);
  
  // Form state for editing
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    biography: '',
    orcid: '',
    google_scholar_url: '',
    research_gate_url: '',
    emails: [],
    phones: [],
    departments: [],
    titles: [],
  });

  // Input states for adding new items to arrays
  const [newEmail, setNewEmail] = useState('');
  const [newPhone, setNewPhone] = useState('');
  const [newDepartment, setNewDepartment] = useState('');
  const [newTitle, setNewTitle] = useState('');

  useEffect(() => {
    const fetchFaculty = async () => {
      setLoading(true);
      setError('');
      
      try {
        // Check if authenticated and if this is the user's own profile
        const authenticated = await isAuthenticated();
        if (authenticated) {
          const storedFacultyId = localStorage.getItem('faculty_id');
          setIsOwnProfile(storedFacultyId === facultyId);
        }
        
        const data = await getFacultyById(facultyId);
        setFaculty(data);
        setFormData({
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          biography: data.biography || '',
          orcid: data.orcid || '',
          google_scholar_url: data.google_scholar_url || '',
          research_gate_url: data.research_gate_url || '',
          emails: data.emails || [],
          phones: data.phones || [],
          departments: data.departments || [],
          titles: data.titles || [],
        });
      } catch (err) {
        setError(err.message || 'Failed to load faculty profile');
      } finally {
        setLoading(false);
      }
    };

    if (facultyId) {
      fetchFaculty();
    }
  }, [facultyId]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  // Array field handlers
  const addToArray = (field, value, setter) => {
    if (value.trim()) {
      setFormData(prev => ({
        ...prev,
        [field]: [...prev[field], value.trim()],
      }));
      setter('');
    }
  };

  const removeFromArray = (field, index) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index),
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveMessage('');
    
    try {
      await updateFaculty(facultyId, formData);
      
      // Update local faculty state with new data
      setFaculty(prev => ({
        ...prev,
        ...formData,
      }));
      
      // Also update localStorage if it's own profile
      if (isOwnProfile) {
        const storedFaculty = localStorage.getItem('faculty');
        if (storedFaculty) {
          const parsed = JSON.parse(storedFaculty);
          localStorage.setItem('faculty', JSON.stringify({
            ...parsed,
            ...formData,
          }));
        }
      }
      
      setSaveMessage('Profile updated successfully!');
      setIsEditing(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (err) {
      setSaveMessage('Failed to save changes. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    // Reset form data to original faculty data
    setFormData({
      first_name: faculty.first_name || '',
      last_name: faculty.last_name || '',
      biography: faculty.biography || '',
      orcid: faculty.orcid || '',
      google_scholar_url: faculty.google_scholar_url || '',
      research_gate_url: faculty.research_gate_url || '',
      emails: faculty.emails || [],
      phones: faculty.phones || [],
      departments: faculty.departments || [],
      titles: faculty.titles || [],
    });
    setIsEditing(false);
    setSaveMessage('');
  };

  if (loading) {
    return (
      <div className="profile-container">
        <Header />
        <main className="profile-main">
          <div className="profile-loading">Loading profile...</div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-container">
        <Header />
        <main className="profile-main">
          <div className="profile-error">
            <h2>Error Loading Profile</h2>
            <p>{error}</p>
            <button className="profile-button" onClick={() => navigate(-1)}>
              Go Back
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <Header />
      
      <main className="profile-main">
        {saveMessage && (
          <div className={`profile-message ${saveMessage.includes('Failed') ? 'error' : 'success'}`}>
            <p>{saveMessage}</p>
            <button 
              className="close-message-btn"
              onClick={() => setSaveMessage('')}
              aria-label="Close message"
            >
              ×
            </button>
          </div>
        )}

        <div className="profile-header-section">
          <button className="back-button" onClick={() => navigate(-1)}>
            ← Back
          </button>
          
          <div className="profile-title-row">
            <h1 className="profile-name">
              {isEditing ? (
                <div className="name-edit-row">
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    placeholder="First Name"
                    className="name-input"
                  />
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    placeholder="Last Name"
                    className="name-input"
                  />
                </div>
              ) : (
                `${faculty.first_name} ${faculty.last_name}`
              )}
            </h1>
            
            {isOwnProfile && !isEditing && (
              <button 
                className="edit-button"
                onClick={() => setIsEditing(true)}
              >
                Edit Profile
              </button>
            )}
          </div>
          
          {faculty.institution_name && (
            <p className="profile-institution">{faculty.institution_name}</p>
          )}
        </div>

        <div className="profile-content">
          {/* Left Column - Main Info */}
          <div className="profile-column profile-column-main">
            {/* Titles */}
            <div className="profile-card">
              <h3>Titles</h3>
              {isEditing ? (
                <div className="editable-list">
                  {formData.titles.map((title, index) => (
                    <div key={index} className="list-item-editable">
                      <span>{title}</span>
                      <button 
                        type="button"
                        className="remove-item-btn"
                        onClick={() => removeFromArray('titles', index)}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <div className="add-item-row">
                    <input
                      type="text"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      placeholder="Add a title..."
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('titles', newTitle, setNewTitle))}
                    />
                    <button 
                      type="button"
                      className="add-item-btn"
                      onClick={() => addToArray('titles', newTitle, setNewTitle)}
                    >
                      Add
                    </button>
                  </div>
                </div>
              ) : (
                <div className="list-display">
                  {faculty.titles && faculty.titles.length > 0 ? (
                    faculty.titles.map((title, index) => (
                      <span key={index} className="list-tag">{title}</span>
                    ))
                  ) : (
                    <p className="no-data">No titles listed</p>
                  )}
                </div>
              )}
            </div>

            {/* Departments */}
            <div className="profile-card">
              <h3>Departments</h3>
              {isEditing ? (
                <div className="editable-list">
                  {formData.departments.map((dept, index) => (
                    <div key={index} className="list-item-editable">
                      <span>{dept}</span>
                      <button 
                        type="button"
                        className="remove-item-btn"
                        onClick={() => removeFromArray('departments', index)}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <div className="add-item-row">
                    <input
                      type="text"
                      value={newDepartment}
                      onChange={(e) => setNewDepartment(e.target.value)}
                      placeholder="Add a department..."
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('departments', newDepartment, setNewDepartment))}
                    />
                    <button 
                      type="button"
                      className="add-item-btn"
                      onClick={() => addToArray('departments', newDepartment, setNewDepartment)}
                    >
                      Add
                    </button>
                  </div>
                </div>
              ) : (
                <div className="list-display">
                  {faculty.departments && faculty.departments.length > 0 ? (
                    faculty.departments.map((dept, index) => (
                      <span key={index} className="list-tag">{dept}</span>
                    ))
                  ) : (
                    <p className="no-data">No departments listed</p>
                  )}
                </div>
              )}
            </div>

            {/* Biography */}
            <div className="profile-card">
              <h3>Biography</h3>
              {isEditing ? (
                <textarea
                  name="biography"
                  value={formData.biography}
                  onChange={handleInputChange}
                  placeholder="Write a biography..."
                  className="biography-textarea"
                  rows={6}
                />
              ) : (
                <p className="biography-text">
                  {faculty.biography || <span className="no-data">No biography available</span>}
                </p>
              )}
            </div>
          </div>

          {/* Right Column - Contact & Links */}
          <div className="profile-column profile-column-side">
            {/* Contact Information */}
            <div className="profile-card">
              <h3>Contact</h3>
              
              <div className="contact-section">
                <h4>Email</h4>
                {isEditing ? (
                  <div className="editable-list">
                    {formData.emails.map((email, index) => (
                      <div key={index} className="list-item-editable">
                        <span>{email}</span>
                        <button 
                          type="button"
                          className="remove-item-btn"
                          onClick={() => removeFromArray('emails', index)}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    <div className="add-item-row">
                      <input
                        type="email"
                        value={newEmail}
                        onChange={(e) => setNewEmail(e.target.value)}
                        placeholder="Add email..."
                        onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('emails', newEmail, setNewEmail))}
                      />
                      <button 
                        type="button"
                        className="add-item-btn"
                        onClick={() => addToArray('emails', newEmail, setNewEmail)}
                      >
                        Add
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="contact-list">
                    {faculty.emails && faculty.emails.length > 0 ? (
                      faculty.emails.map((email, index) => (
                        <a key={index} href={`mailto:${email}`} className="contact-link">
                          {email}
                        </a>
                      ))
                    ) : (
                      <p className="no-data">No email listed</p>
                    )}
                  </div>
                )}
              </div>

              <div className="contact-section">
                <h4>Phone</h4>
                {isEditing ? (
                  <div className="editable-list">
                    {formData.phones.map((phone, index) => (
                      <div key={index} className="list-item-editable">
                        <span>{phone}</span>
                        <button 
                          type="button"
                          className="remove-item-btn"
                          onClick={() => removeFromArray('phones', index)}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    <div className="add-item-row">
                      <input
                        type="tel"
                        value={newPhone}
                        onChange={(e) => setNewPhone(e.target.value)}
                        placeholder="Add phone..."
                        onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('phones', newPhone, setNewPhone))}
                      />
                      <button 
                        type="button"
                        className="add-item-btn"
                        onClick={() => addToArray('phones', newPhone, setNewPhone)}
                      >
                        Add
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="contact-list">
                    {faculty.phones && faculty.phones.length > 0 ? (
                      faculty.phones.map((phone, index) => (
                        <a key={index} href={`tel:${phone}`} className="contact-link">
                          {phone}
                        </a>
                      ))
                    ) : (
                      <p className="no-data">No phone listed</p>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Academic Links */}
            <div className="profile-card">
              <h3>Academic Profiles</h3>
              
              {isEditing ? (
                <div className="links-edit">
                  <div className="link-input-group">
                    <label>ORCID</label>
                    <input
                      type="text"
                      name="orcid"
                      value={formData.orcid}
                      onChange={handleInputChange}
                      placeholder="0000-0000-0000-0000"
                    />
                  </div>
                  <div className="link-input-group">
                    <label>Google Scholar</label>
                    <input
                      type="url"
                      name="google_scholar_url"
                      value={formData.google_scholar_url}
                      onChange={handleInputChange}
                      placeholder="https://scholar.google.com/..."
                    />
                  </div>
                  <div className="link-input-group">
                    <label>ResearchGate</label>
                    <input
                      type="url"
                      name="research_gate_url"
                      value={formData.research_gate_url}
                      onChange={handleInputChange}
                      placeholder="https://researchgate.net/..."
                    />
                  </div>
                </div>
              ) : (
                <div className="links-display">
                  {faculty.orcid && (
                    <a 
                      href={`https://orcid.org/${faculty.orcid}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="academic-link"
                    >
                      <span className="link-icon">🔗</span>
                      ORCID
                    </a>
                  )}
                  {faculty.google_scholar_url && (
                    <a 
                      href={faculty.google_scholar_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="academic-link"
                    >
                      <span className="link-icon">📚</span>
                      Google Scholar
                    </a>
                  )}
                  {faculty.research_gate_url && (
                    <a 
                      href={faculty.research_gate_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="academic-link"
                    >
                      <span className="link-icon">🔬</span>
                      ResearchGate
                    </a>
                  )}
                  {!faculty.orcid && !faculty.google_scholar_url && !faculty.research_gate_url && (
                    <p className="no-data">No academic profiles linked</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Edit Mode Actions */}
        {isEditing && (
          <div className="edit-actions">
            <button 
              className="cancel-button"
              onClick={handleCancel}
              disabled={saving}
            >
              Cancel
            </button>
            <button 
              className="save-button"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default FacultyProfile;

