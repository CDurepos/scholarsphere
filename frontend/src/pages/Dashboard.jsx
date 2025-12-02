import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { isAuthenticated } from '../services/api';
import Header from '../components/Header';
import './Dashboard.css';

/**
 * Main dashboard/index page - shown after successful login
 */
function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();
  const [faculty, setFaculty] = useState(null);
  const [welcomeMessage, setWelcomeMessage] = useState('');

  useEffect(() => {
    const checkAuth = async () => {
      const authenticated = await isAuthenticated();
      
      if (!authenticated) {
        navigate('/');
        return;
      }

      const facultyData = localStorage.getItem('faculty');
      if (facultyData) {
        try {
          setFaculty(JSON.parse(facultyData));
        } catch (err) {
          // Invalid faculty data
        }
      }

      if (location.state?.welcomeMessage) {
        setWelcomeMessage(location.state.welcomeMessage);
        window.history.replaceState({}, document.title);
      }
    };

    checkAuth();
  }, [navigate, location]);

  if (!faculty) {
    return <div className="dashboard-loading">Loading...</div>;
  }

  return (
    <div className="dashboard-container">
      <Header />

      <main className="dashboard-main">
        {welcomeMessage && (
          <div className="dashboard-success-message">
            <p>{welcomeMessage}</p>
            <button 
              className="close-message-button" 
              onClick={() => setWelcomeMessage('')}
              aria-label="Close message"
            >
              ×
            </button>
          </div>
        )}
        
        <div className="dashboard-welcome">
          <h2>Welcome to ScholarSphere</h2>
          <p>Connect with Maine Faculty for Research Collaboration</p>
        </div>

        <div className="dashboard-content">
          <div className="dashboard-card">
            <h3>Your Profile</h3>
            <div className="profile-info">
              <p><strong>Name:</strong> {faculty.first_name} {faculty.last_name}</p>
              {faculty.emails && faculty.emails.length > 0 && (
                <p><strong>Email:</strong> {faculty.emails[0]}</p>
              )}
              {faculty.departments && faculty.departments.length > 0 && (
                <p><strong>Department:</strong> {faculty.departments.join(', ')}</p>
              )}
              {faculty.titles && faculty.titles.length > 0 && (
                <p><strong>Title:</strong> {faculty.titles.join(', ')}</p>
              )}
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Quick Actions</h3>
            <div className="quick-actions">
              <button className="action-button" onClick={() => navigate('/search')}>Browse Faculty</button>
              <button className="action-button">View Recommendations</button>
              <button className="action-button">Edit Profile</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;


