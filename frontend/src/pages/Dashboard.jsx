import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

/**
 * Main dashboard/index page - shown after successful login
 */
function Dashboard() {
  const navigate = useNavigate();
  const [faculty, setFaculty] = useState(null);

  useEffect(() => {
    // Check if user is logged in
    const facultyId = localStorage.getItem('faculty_id');
    const facultyData = localStorage.getItem('faculty');

    if (!facultyId || !facultyData) {
      // Not logged in - redirect to landing
      navigate('/');
      return;
    }

    try {
      setFaculty(JSON.parse(facultyData));
    } catch (err) {
      console.error('Failed to parse faculty data:', err);
      navigate('/');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('faculty');
    localStorage.removeItem('faculty_id');
    navigate('/');
  };

  if (!faculty) {
    return <div className="dashboard-loading">Loading...</div>;
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>ScholarSphere</h1>
        <div className="dashboard-user-info">
          <span>Welcome, {faculty.first_name} {faculty.last_name}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-main">
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


