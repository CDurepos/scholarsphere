import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  getFacultyById, 
  updateFaculty, 
  isAuthenticated,
  getFacultyKeywords,
  searchKeywords,
  updateFacultyKeywords,
} from '../services/api';
import Header from '../components/Header';
import styles from './Profile.module.css';

/**
 * Faculty Profile Page
 * - Displays faculty member information including research interests
 * - Allows editing if viewing own profile
 * - Keyword autocomplete for research interests
 */
function Profile() {
  const { facultyId } = useParams();
  const navigate = useNavigate();
  
  const [faculty, setFaculty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [isOwnProfile, setIsOwnProfile] = useState(false);
  
  // Keywords state
  const [keywords, setKeywords] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [keywordSuggestions, setKeywordSuggestions] = useState([]);
  const [showKeywordSuggestions, setShowKeywordSuggestions] = useState(false);
  const [keywordLoading, setKeywordLoading] = useState(false);
  const keywordInputRef = useRef(null);
  const suggestionsRef = useRef(null);
  
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
    keywords: [],
  });

  // Input states for adding new items to arrays
  const [newEmail, setNewEmail] = useState('');
  const [newPhone, setNewPhone] = useState('');
  const [newDepartment, setNewDepartment] = useState('');
  const [newTitle, setNewTitle] = useState('');

  // Fetch faculty data and keywords
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
        
        // Fetch faculty data
        const data = await getFacultyById(facultyId);
        setFaculty(data);
        // Fetch keywords separately
        const keywordsData = await getFacultyKeywords(facultyId);
        setKeywords(keywordsData || []);
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
          keywords: keywordsData || [],
        });
        
        // Fetch keywords
        setKeywords(keywordsData || []);
        setFormData(prev => ({
          ...prev,
          keywords: keywordsData || [],
        }));
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

  // Handle click outside to close keyword suggestions
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        suggestionsRef.current && 
        !suggestionsRef.current.contains(event.target) &&
        keywordInputRef.current &&
        !keywordInputRef.current.contains(event.target)
      ) {
        setShowKeywordSuggestions(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced keyword search
  useEffect(() => {
    const searchTimeout = setTimeout(async () => {
      if (newKeyword.trim().length >= 2 && isEditing) {
        setKeywordLoading(true);
        try {
          const suggestions = await searchKeywords(newKeyword.trim(), 8);
          // Filter out already added keywords (case-insensitive)
          const keywordLower = newKeyword.trim().toLowerCase();
          const filtered = suggestions.filter(s => {
            const sLower = s.toLowerCase();
            return !formData.keywords.some(k => k.toLowerCase() === sLower);
          });
          setKeywordSuggestions(filtered);
          setShowKeywordSuggestions(true);
        } catch (err) {
          console.error('Failed to search keywords:', err);
        } finally {
          setKeywordLoading(false);
        }
      } else {
        setKeywordSuggestions([]);
        setShowKeywordSuggestions(false);
      }
    }, 300);
    
    return () => clearTimeout(searchTimeout);
  }, [newKeyword, formData.keywords, isEditing]);

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

  // Keyword handlers (only used in edit mode)
  const handleAddKeyword = (keywordToAdd) => {
    const keyword = keywordToAdd || newKeyword.trim();
    if (!keyword || keyword.length < 2) {
      return;
    }
    
    // Check if already exists (case-insensitive)
    const keywordLower = keyword.toLowerCase();
    if (formData.keywords.some(k => k.toLowerCase() === keywordLower)) {
      setNewKeyword('');
      setShowKeywordSuggestions(false);
      return;
    }
    
    setFormData(prev => ({
      ...prev,
      keywords: [...prev.keywords, keyword],
    }));
    setNewKeyword('');
    setShowKeywordSuggestions(false);
  };

  const handleRemoveKeyword = (index) => {
    setFormData(prev => ({
      ...prev,
      keywords: prev.keywords.filter((_, i) => i !== index),
    }));
  };

  const handleKeywordKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (keywordSuggestions.length > 0) {
        handleAddKeyword(keywordSuggestions[0]);
      } else if (newKeyword.trim().length >= 2) {
        handleAddKeyword();
      }
    } else if (e.key === 'Escape') {
      setShowKeywordSuggestions(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveMessage('');
    
    try {
      // Save faculty data (excluding keywords)
      const { keywords, ...facultyData } = formData;
      await updateFaculty(facultyId, facultyData);
      
      // Save keywords separately
      await updateFacultyKeywords(facultyId, keywords);
      
      // Refresh faculty data
      const updatedFaculty = await getFacultyById(facultyId);
      const updatedKeywords = await getFacultyKeywords(facultyId);
      
      setFaculty(updatedFaculty);
      setKeywords(updatedKeywords || []);
      
      setFormData({
        first_name: updatedFaculty.first_name || '',
        last_name: updatedFaculty.last_name || '',
        biography: updatedFaculty.biography || '',
        orcid: updatedFaculty.orcid || '',
        google_scholar_url: updatedFaculty.google_scholar_url || '',
        research_gate_url: updatedFaculty.research_gate_url || '',
        emails: updatedFaculty.emails || [],
        phones: updatedFaculty.phones || [],
        departments: updatedFaculty.departments || [],
        titles: updatedFaculty.titles || [],
        keywords: updatedKeywords || [],
      });
      
      // Update localStorage if own profile
      if (isOwnProfile) {
        const storedFaculty = localStorage.getItem('faculty');
        if (storedFaculty) {
          const parsed = JSON.parse(storedFaculty);
          localStorage.setItem('faculty', JSON.stringify({
            ...parsed,
            ...updatedFaculty,
          }));
        }
      }
      
      setSaveMessage('Profile updated successfully!');
      setIsEditing(false);
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (err) {
      const errorMessage = err.message || 'Failed to save changes. Please try again.';
      setSaveMessage(`Error: ${errorMessage}`);
      console.error('Failed to update faculty profile:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
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
      keywords: keywords || [],
    });
    setIsEditing(false);
    setSaveMessage('');
    setNewKeyword('');
    setShowKeywordSuggestions(false);
  };

  if (loading) {
    return (
      <div className={styles['profile-container']}>
        <Header />
        <main className={styles['profile-main']}>
          <div className={styles['profile-loading']}>Loading profile...</div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles['profile-container']}>
        <Header />
        <main className={styles['profile-main']}>
          <div className={styles['profile-error']}>
            <h2>Error Loading Profile</h2>
            <p>{error}</p>
            <button className={styles['profile-button']} onClick={() => navigate(-1)}>
              Go Back
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className={styles['profile-container']}>
      <Header />
      
      <main className={styles['profile-main']}>
        {saveMessage && (
          <div className={`${styles['profile-message']} ${saveMessage.includes('Error') ? styles['error'] : styles['success']}`}>
            <p>{saveMessage}</p>
            <button 
              className={styles['close-message-btn']}
              onClick={() => setSaveMessage('')}
              aria-label="Close message"
            >
              ×
            </button>
          </div>
        )}

        <div className={styles['profile-header-section']}>
          <button className={styles['back-button']} onClick={() => navigate(-1)}>
            ← Back
          </button>
          
          <div className={styles['profile-title-row']}>
            <h1 className={styles['profile-name']}>
              {isEditing ? (
                <div className={styles['name-edit-row']}>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    placeholder="First Name"
                    className={styles['name-input']}
                  />
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    placeholder="Last Name"
                    className={styles['name-input']}
                  />
                </div>
              ) : (
                `${faculty.first_name} ${faculty.last_name}`
              )}
            </h1>
            
            {isOwnProfile && !isEditing && (
              <button 
                className={styles['edit-button']}
                onClick={() => setIsEditing(true)}
              >
                Edit Profile
              </button>
            )}
          </div>
          
          {faculty.institution_name && (
            <p className={styles['profile-institution']}>{faculty.institution_name}</p>
          )}
        </div>

        <div className={styles['profile-content']}>
          {/* Left Column - Main Info */}
          <div className={`${styles['profile-column']} ${styles['profile-column-main']}`}>
            {/* Research Interests */}
            <div className={styles['profile-card']}>
              <h3>Research Interests</h3>
              {isEditing ? (
                <div className={styles['editable-list']}>
                  {formData.keywords.map((keyword, index) => (
                    <div key={index} className={styles['list-item-editable']}>
                      <span>{keyword}</span>
                      <button 
                        type="button"
                        className={styles['remove-item-btn']}
                        onClick={() => handleRemoveKeyword(index)}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <div className={styles['keyword-input-container']}>
                    <div className={styles['keyword-input-wrapper']}>
                      <input
                        ref={keywordInputRef}
                        type="text"
                        value={newKeyword}
                        onChange={(e) => setNewKeyword(e.target.value)}
                        onKeyDown={handleKeywordKeyDown}
                        onFocus={() => newKeyword.length >= 2 && setShowKeywordSuggestions(true)}
                        placeholder="Add a research interest..."
                        className={styles['keyword-input']}
                      />
                      {keywordLoading && (
                        <span className={styles['keyword-loading']}>...</span>
                      )}
                    </div>
                    <button
                      type="button"
                      className={styles['add-item-btn']}
                      onClick={() => handleAddKeyword()}
                      disabled={newKeyword.trim().length < 2}
                    >
                      Add
                    </button>
                    
                    {/* Autocomplete dropdown */}
                    {showKeywordSuggestions && keywordSuggestions.length > 0 && (
                      <div ref={suggestionsRef} className={styles['keyword-suggestions']}>
                        {keywordSuggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            type="button"
                            className={styles['keyword-suggestion']}
                            onClick={() => handleAddKeyword(suggestion)}
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className={styles['list-display']}>
                  {keywords && keywords.length > 0 ? (
                    keywords.map((keyword, index) => (
                      <span key={index} className={styles['list-tag']}>{keyword}</span>
                    ))
                  ) : (
                    <p className={styles['no-data']}>No research interests listed</p>
                  )}
                </div>
              )}
            </div>

            {/* Titles */}
            <div className={styles['profile-card']}>
              <h3>Titles</h3>
              {isEditing ? (
                <div className={styles['editable-list']}>
                  {formData.titles.map((title, index) => (
                    <div key={index} className={styles['list-item-editable']}>
                      <span>{title}</span>
                      <button 
                        type="button"
                        className={styles['remove-item-btn']}
                        onClick={() => removeFromArray('titles', index)}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <div className={styles['add-item-row']}>
                    <input
                      type="text"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      placeholder="Add a title..."
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('titles', newTitle, setNewTitle))}
                    />
                    <button 
                      type="button"
                      className={styles['add-item-btn']}
                      onClick={() => addToArray('titles', newTitle, setNewTitle)}
                    >
                      Add
                    </button>
                  </div>
                </div>
              ) : (
                <div className={styles['list-display']}>
                  {faculty.titles && faculty.titles.length > 0 ? (
                    faculty.titles.map((title, index) => (
                      <span key={index} className={styles['list-tag']}>{title}</span>
                    ))
                  ) : (
                    <p className={styles['no-data']}>No titles listed</p>
                  )}
                </div>
              )}
            </div>

            {/* Departments */}
            <div className={styles['profile-card']}>
              <h3>Departments</h3>
              {isEditing ? (
                <div className={styles['editable-list']}>
                  {formData.departments.map((dept, index) => (
                    <div key={index} className={styles['list-item-editable']}>
                      <span>{dept}</span>
                      <button 
                        type="button"
                        className={styles['remove-item-btn']}
                        onClick={() => removeFromArray('departments', index)}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <div className={styles['add-item-row']}>
                    <input
                      type="text"
                      value={newDepartment}
                      onChange={(e) => setNewDepartment(e.target.value)}
                      placeholder="Add a department..."
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('departments', newDepartment, setNewDepartment))}
                    />
                    <button 
                      type="button"
                      className={styles['add-item-btn']}
                      onClick={() => addToArray('departments', newDepartment, setNewDepartment)}
                    >
                      Add
                    </button>
                  </div>
                </div>
              ) : (
                <div className={styles['list-display']}>
                  {faculty.departments && faculty.departments.length > 0 ? (
                    faculty.departments.map((dept, index) => (
                      <span key={index} className={styles['list-tag']}>{dept}</span>
                    ))
                  ) : (
                    <p className={styles['no-data']}>No departments listed</p>
                  )}
                </div>
              )}
            </div>

            {/* Biography */}
            <div className={styles['profile-card']}>
              <h3>Biography</h3>
              {isEditing ? (
                <textarea
                  name="biography"
                  value={formData.biography}
                  onChange={handleInputChange}
                  placeholder="Write a biography..."
                  className={styles['biography-textarea']}
                  rows={6}
                />
              ) : (
                <p className={styles['biography-text']}>
                  {faculty.biography || <span className={styles['no-data']}>No biography available</span>}
                </p>
              )}
            </div>
          </div>

          {/* Right Column - Contact & Links */}
          <div className={`${styles['profile-column']} ${styles['profile-column-side']}`}>
            {/* Contact Information */}
            <div className={styles['profile-card']}>
              <h3>Contact</h3>
              
              <div className={styles['contact-section']}>
                <h4>Email</h4>
                {isEditing ? (
                  <div className={styles['editable-list']}>
                    {formData.emails.map((email, index) => (
                      <div key={index} className={styles['list-item-editable']}>
                        <span>{email}</span>
                        <button 
                          type="button"
                          className={styles['remove-item-btn']}
                          onClick={() => removeFromArray('emails', index)}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    <div className={styles['add-item-row']}>
                      <input
                        type="email"
                        value={newEmail}
                        onChange={(e) => setNewEmail(e.target.value)}
                        placeholder="Add email..."
                        onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('emails', newEmail, setNewEmail))}
                      />
                      <button 
                        type="button"
                        className={styles['add-item-btn']}
                        onClick={() => addToArray('emails', newEmail, setNewEmail)}
                      >
                        Add
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className={styles['contact-list']}>
                    {faculty.emails && faculty.emails.length > 0 ? (
                      faculty.emails.map((email, index) => (
                        <a key={index} href={`mailto:${email}`} className={styles['contact-link']}>
                          {email}
                        </a>
                      ))
                    ) : (
                      <p className={styles['no-data']}>No email listed</p>
                    )}
                  </div>
                )}
              </div>

              <div className={styles['contact-section']}>
                <h4>Phone</h4>
                {isEditing ? (
                  <div className={styles['editable-list']}>
                    {formData.phones.map((phone, index) => (
                      <div key={index} className={styles['list-item-editable']}>
                        <span>{phone}</span>
                        <button 
                          type="button"
                          className={styles['remove-item-btn']}
                          onClick={() => removeFromArray('phones', index)}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    <div className={styles['add-item-row']}>
                      <input
                        type="tel"
                        value={newPhone}
                        onChange={(e) => setNewPhone(e.target.value)}
                        placeholder="Add phone..."
                        onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('phones', newPhone, setNewPhone))}
                      />
                      <button 
                        type="button"
                        className={styles['add-item-btn']}
                        onClick={() => addToArray('phones', newPhone, setNewPhone)}
                      >
                        Add
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className={styles['contact-list']}>
                    {faculty.phones && faculty.phones.length > 0 ? (
                      faculty.phones.map((phone, index) => (
                        <a key={index} href={`tel:${phone}`} className={styles['contact-link']}>
                          {phone}
                        </a>
                      ))
                    ) : (
                      <p className={styles['no-data']}>No phone listed</p>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Academic Links */}
            <div className={styles['profile-card']}>
              <h3>Academic Profiles</h3>
              
              {isEditing ? (
                <div className={styles['links-edit']}>
                  <div className={styles['link-input-group']}>
                    <label>ORCID</label>
                    <input
                      type="text"
                      name="orcid"
                      value={formData.orcid}
                      onChange={handleInputChange}
                      placeholder="0000-0000-0000-0000"
                    />
                  </div>
                  <div className={styles['link-input-group']}>
                    <label>Google Scholar</label>
                    <input
                      type="url"
                      name="google_scholar_url"
                      value={formData.google_scholar_url}
                      onChange={handleInputChange}
                      placeholder="https://scholar.google.com/..."
                    />
                  </div>
                  <div className={styles['link-input-group']}>
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
                <div className={styles['links-display']}>
                  {faculty.orcid && (
                    <a 
                      href={`https://orcid.org/${faculty.orcid}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className={styles['academic-link']}
                    >
                      <span className={styles['link-icon']}>🔗</span>
                      ORCID
                    </a>
                  )}
                  {faculty.google_scholar_url && (
                    <a 
                      href={faculty.google_scholar_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className={styles['academic-link']}
                    >
                      <span className={styles['link-icon']}>📚</span>
                      Google Scholar
                    </a>
                  )}
                  {faculty.research_gate_url && (
                    <a 
                      href={faculty.research_gate_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className={styles['academic-link']}
                    >
                      <span className={styles['link-icon']}>🔬</span>
                      ResearchGate
                    </a>
                  )}
                  {!faculty.orcid && !faculty.google_scholar_url && !faculty.research_gate_url && (
                    <p className={styles['no-data']}>No academic profiles linked</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Edit Mode Actions */}
        {isEditing && (
          <div className={styles['edit-actions']}>
            <button 
              className={styles['cancel-button']}
              onClick={handleCancel}
              disabled={saving}
            >
              Cancel
            </button>
            <button 
              className={styles['save-button']}
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

export default Profile;
