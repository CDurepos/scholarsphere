/**
 * @author Clayton Durepos, Aidan Bell
 */

import { useEffect, useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { isAuthenticated, getRecommendations } from '../services/api';
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
  const [loadingRecommendations, setLoadingRecommendations] = useState(true);
  const [recommendationsError, setRecommendationsError] = useState(null);

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

  // Fetch recommendations when faculty is loaded
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!faculty?.faculty_id) {
        return;
      }

      setLoadingRecommendations(true);
      setRecommendationsError(null);

      try {
        const data = await getRecommendations(faculty.faculty_id);
        setRecommendations(data);
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
        setRecommendationsError('Unable to load recommendations');
        // Don't show error to user, just show empty state
        setRecommendations([]);
      } finally {
        setLoadingRecommendations(false);
      }
    };

    fetchRecommendations();
  }, [faculty?.faculty_id]);

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
            Welcome back, <span className={styles['dashboard-welcome-name']}>{faculty.first_name}</span>
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

          {loadingRecommendations ? (
            <div className={styles['dashboard-recommendations-loading']}>
              <p>Finding collaborators for you...</p>
            </div>
          ) : recommendations.length > 0 ? (
            <div className={styles['dashboard-recommendations-grid']}>
              {recommendations.map((rec) => (
                <div 
                  key={rec.faculty_id} 
                  className={styles['dashboard-recommendation-card']}
                >
                  <div className={styles['recommendation-card-header']}>
                    <div className={styles['recommendation-avatar']}>
                      {rec.first_name?.[0] || '?'}{rec.last_name?.[0] || '?'}
                    </div>
                    <div className={styles['recommendation-info']}>
                      <h3 className={styles['recommendation-name']}>
                        {rec.first_name} {rec.last_name}
                      </h3>
                      <p className={styles['recommendation-institution']}>{rec.institution_name || 'Institution not specified'}</p>
                      <p className={styles['recommendation-department']}>{rec.department_name || rec.department || 'Department not specified'}</p>
                    </div>
                  </div>
                  <div className={styles['recommendation-card-body']}>
                    <div className={styles['recommendation-match-badge']} data-strength={
                      ['shared_keyword', 'keyword_to_publication', 'publication_to_keyword'].includes(rec.recommendation_type) ? 'high' : 'base'
                    }>
                      <span className={styles['match-pulse']} />
                      <span className={styles['match-badge-text']}>{rec.recommendation_text}</span>
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
              <p>No recommendations available yet.</p>
              <p className={styles['dashboard-empty-hint']}>
                Add research keywords to your profile to get personalized recommendations.
              </p>
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
