import { useEffect, useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { isAuthenticated } from '../services/api';
import Header from '../components/Header';
import ConnectionParticles from '../components/ConnectionParticles';
import styles from './Dashboard.module.css';

const DASHBOARD_PARTICLE_COLORS = ['#0b264f', '#1a4a7a', '#2d5a8a'];
const DASHBOARD_PARTICLE_LINK_COLOR = '#4a6fa5';
const DASHBOARD_PARTICLE_QUANTITY = 60;

/**
 * Main dashboard/homepage - shown after successful login
 * Displays user recommendations and provides navigation to search
 */
function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();
  const [faculty, setFaculty] = useState(null);
  const [welcomeMessage, setWelcomeMessage] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    const checkAuth = async () => {
      const authenticated = await isAuthenticated();
      
      if (!authenticated) {
        navigate('/login', { replace: true });
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

  useEffect(() => {
    // TODO: Fetch actual recommendations from API
    // For now, use placeholder data
    const placeholderRecommendations = [
      {
        faculty_id: '1',
        first_name: 'Sarah',
        last_name: 'Johnson',
        institution_name: 'University of Maine',
        department: 'Computer Science',
        match_reason: 'Shared research interests in machine learning',
        match_score: 0.92
      },
      {
        faculty_id: '2',
        first_name: 'Michael',
        last_name: 'Chen',
        institution_name: 'University of Southern Maine',
        department: 'Data Science',
        match_reason: 'Similar grant funding history',
        match_score: 0.87
      },
      {
        faculty_id: '3',
        first_name: 'Emily',
        last_name: 'Rodriguez',
        institution_name: 'University of Maine',
        department: 'Computer Science',
        match_reason: 'Common publications and keywords',
        match_score: 0.85
      },
      {
        faculty_id: '4',
        first_name: 'David',
        last_name: 'Thompson',
        institution_name: 'University of Southern Maine',
        department: 'Information Systems',
        match_reason: 'Same institution and department',
        match_score: 0.78
      }
    ];
    setRecommendations(placeholderRecommendations);
  }, []);

  if (!faculty) {
    return <div className={styles['dashboard-loading']}>Loading...</div>;
  }

  return (
    <div className={styles['dashboard-container']}>
      <ConnectionParticles
        className={styles['dashboard-particles']}
        colors={DASHBOARD_PARTICLE_COLORS}
        linkColor={DASHBOARD_PARTICLE_LINK_COLOR}
        quantity={DASHBOARD_PARTICLE_QUANTITY}
      />
      <Header />

      <main className={styles['dashboard-main']}>
        {welcomeMessage && (
          <div className={styles['dashboard-success-message']}>
            <p>{welcomeMessage}</p>
            <button 
              className={styles['close-message-button']} 
              onClick={() => setWelcomeMessage('')}
              aria-label="Close message"
            >
              ×
            </button>
          </div>
        )}
        
        <div className={styles['dashboard-welcome-tile']}>
          <h1 className={styles['dashboard-welcome-title']}>
            Welcome back, {faculty.first_name}
          </h1>
          <p className={styles['dashboard-welcome-subtitle']}>
            Here's what's new for you today
          </p>
        </div>

        <div className={styles['dashboard-recommendations-tile']}>
          <div className={styles['dashboard-section-header']}>
            <h2 className={styles['dashboard-section-title']}>Recommended Collaborators</h2>
            <p className={styles['dashboard-section-description']}>
              Faculty members with similar research interests and collaboration potential
            </p>
          </div>

          {recommendations.length > 0 ? (
            <div className={styles['dashboard-recommendations-grid']}>
              {recommendations.map((rec) => (
                <div 
                  key={rec.faculty_id} 
                  className={styles['dashboard-recommendation-card']}
                >
                  <div className={styles['recommendation-card-header']}>
                    <div className={styles['recommendation-avatar']}>
                      {rec.first_name[0]}{rec.last_name[0]}
                    </div>
                    <div className={styles['recommendation-info']}>
                      <h3 className={styles['recommendation-name']}>
                        {rec.first_name} {rec.last_name}
                      </h3>
                      <p className={styles['recommendation-institution']}>{rec.institution_name}</p>
                      <p className={styles['recommendation-department']}>{rec.department}</p>
                    </div>
                  </div>
                  <div className={styles['recommendation-card-body']}>
                    <p className={styles['recommendation-reason']}>{rec.match_reason}</p>
                    <div className={styles['recommendation-match-score']}>
                      <span className={styles['match-score-label']}>Match</span>
                      <span className={styles['match-score-value']}>{Math.round(rec.match_score * 100)}%</span>
                    </div>
                  </div>
                  <div className={styles['recommendation-card-footer']}>
                    <button 
                      className={styles['recommendation-view-button']}
                      onClick={() => navigate(`/faculty/${rec.faculty_id}`)}
                    >
                      View Profile
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className={styles['dashboard-empty-recommendations']}>
              <p>No recommendations available at this time.</p>
              <Link to="/search/faculty" className={styles['dashboard-search-link']}>
                Browse all faculty instead
              </Link>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
