import { Link } from 'react-router-dom';
import { FaSearch, FaHandshake, FaBookOpen, FaGlobe, FaLightbulb, FaChartBar } from 'react-icons/fa';
import ConnectionParticles from '../components/ConnectionParticles';
import logo from '../assets/logo.png';
import umoLogo from '../assets/umo-logo.png';
import usmLogo from '../assets/usm-logo.png';
import umfLogo from '../assets/umf-logo.png';
import umaLogo from '../assets/uma-logo.png';
import styles from './Landing.module.css';

const LANDING_PARTICLE_COLORS = ['#ffffff', '#dfe8ff'];
const LANDING_PARTICLE_LINK_COLOR = '#c6d6ff';
const LANDING_PARTICLE_QUANTITY = 70;

function Landing() {
  return (
    <div className={styles['landing-container']}>
      {/* Top Navigation Bar */}
      <header className={styles['landing-nav']}>
        <div className={styles['landing-nav-left']}>
          <img src={logo} alt="ScholarSphere" className={styles['landing-nav-logo']} />
          <span className={styles['landing-nav-brand']}>ScholarSphere</span>
        </div>
        <div className={styles['landing-nav-right']}>
          <a href="#features" className={styles['landing-nav-link']}>
            Features
          </a>
          <a href="#how-it-works" className={styles['landing-nav-link']}>
            How it works
          </a>
          <Link to="/login" className={styles['landing-nav-button-secondary']}>
            Sign in
          </Link>
          <Link to="/signup" className={styles['landing-nav-button-primary']}>
            GET STARTED
          </Link>
        </div>
      </header>

      <main className={styles['landing-main']}>
        {/* Hero Section with particle background */}
        <section className={styles['landing-hero']}>
          <ConnectionParticles
            className={styles['landing-hero-particles']}
            colors={LANDING_PARTICLE_COLORS}
            linkColor={LANDING_PARTICLE_LINK_COLOR}
            quantity={LANDING_PARTICLE_QUANTITY}
          />
          <div className={styles['landing-hero-inner']}>
            <div className={styles['landing-hero-copy']}>
              <div className={styles['landing-hero-pill']}>
                <span className={styles['landing-hero-pill-dot']} />
                Built for researchers at Maine&apos;s universities
              </div>

              <h1 className={styles['landing-headline']}>
                Your single, statewide directory for
                <span className={styles['landing-headline-highlight']}>
                  {' '}finding collaborative faculty.
                </span>
              </h1>

              <p className={styles['landing-subheadline']}>
                ScholarSphere is a research-focused directory for Maine. Create a profile that
                highlights your interests, expertise, and current work so others can quickly see
                where you fit and reach out when their projects align.
              </p>

              <div className={styles['landing-cta-row']}>
                <Link to="/signup" className={styles['landing-cta-primary']}>
                  Create your profile
                </Link>
                <a href="#features" className={styles['landing-cta-secondary']}>
                  Explore features
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Connected Maine Universities Banner */}
        <section
          className={styles['landing-universities-row']}
          aria-label="Connected Maine universities"
        >
          <div className={styles['landing-universities-inner']}>
            <p className={styles['landing-universities-label']}>
              Connecting researchers across Maine&apos;s universities
            </p>
            <div className={styles['landing-universities-container']}>
              <div className={styles['landing-university-logo-item']}>
                <img
                  src={umoLogo}
                  alt="University of Maine"
                  className={styles['landing-university-logo']}
                />
              </div>
              <div className={styles['landing-university-logo-item']}>
                <img
                  src={usmLogo}
                  alt="University of Southern Maine"
                  className={styles['landing-university-logo']}
                />
              </div>
              <div className={styles['landing-university-logo-item']}>
                <img
                  src={umfLogo}
                  alt="University of Maine at Farmington"
                  className={styles['landing-university-logo']}
                />
              </div>
              <div className={styles['landing-university-logo-item']}>
                <img
                  src={umaLogo}
                  alt="University of Maine at Augusta"
                  className={styles['landing-university-logo']}
                />
              </div>
            </div>
          </div>

          <p className={styles['landing-universities-disclaimer']}>
            ScholarSphere is an independent project and is not officially affiliated with, 
            sponsored by, or endorsed by the institutions shown. Faculty information is 
            collected from publicly available sources.
          </p>
        </section>

        {/* Features Section */}
        <section className={styles['landing-features']} id="features">
          <div className={styles['landing-features-container']}>
            <p className={styles['landing-section-label']}>Features</p>
            <h2 className={styles['landing-features-title']}>
              Unlock the full potential of Maine's research community.
            </h2>
            <div className={styles['landing-features-grid']}>
              <div className={styles['landing-feature-card']}>
                <div className={styles['landing-feature-icon']}>
                  <FaSearch />
                </div>
                <h3 className={styles['landing-feature-card-title']}>Search by research interests</h3>
                <p className={styles['landing-feature-card-description']}>
                  Search across Maine by topic, keywords, or areas of expertise to see who is
                  working on related problems—whether they&apos;re in your department or at
                  another institution.
                </p>
              </div>

              <div className={styles['landing-feature-card']}>
                <div className={styles['landing-feature-icon']}>
                  <FaHandshake />
                </div>
                <h3 className={styles['landing-feature-card-title']}>Grow your research network</h3>
                <p className={styles['landing-feature-card-description']}>
                  Discover researchers you may not already know and connect around projects,
                  grants, workshops, or student opportunities without relying only on existing
                  personal networks.
                </p>
              </div>

              <div className={styles['landing-feature-card']}>
                <div className={styles['landing-feature-icon']}>
                  <FaBookOpen />
                </div>
                <h3 className={styles['landing-feature-card-title']}>Show your research identity</h3>
                <p className={styles['landing-feature-card-description']}>
                  Summarize what you work on, your expertise, and the types of collaborations
                  you&apos;re interested in so potential partners quickly understand how you fit.
                </p>
              </div>

              <div className={styles['landing-feature-card']}>
                <div className={styles['landing-feature-icon']}>
                  <FaGlobe />
                </div>
                <h3 className={styles['landing-feature-card-title']}>See the Maine research landscape</h3>
                <p className={styles['landing-feature-card-description']}>
                  Look beyond a single campus directory. ScholarSphere brings together
                  researchers across Maine&apos;s universities into one place, centered on
                  research connections.
                </p>
              </div>

              <div className={styles['landing-feature-card']}>
                <div className={styles['landing-feature-icon']}>
                  <FaLightbulb />
                </div>
                <h3 className={styles['landing-feature-card-title']}>Spark new collaborations</h3>
                <p className={styles['landing-feature-card-description']}>
                  Use overlapping interests and complementary expertise to start new projects,
                  explore emerging topics, or co-develop courses and initiatives.
                </p>
              </div>

              <div className={styles['landing-feature-card']}>
                <div className={styles['landing-feature-icon']}>
                  <FaChartBar />
                </div>
                <h3 className={styles['landing-feature-card-title']}>Build stronger project teams</h3>
                <p className={styles['landing-feature-card-description']}>
                  Quickly spot people whose skills and experience round out your team when
                  you&apos;re planning research projects, programs, or future proposals.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section (simple, text-only) */}
        <section className={styles['landing-how-it-works']} id="how-it-works">
          <div className={styles['landing-how-it-works-container']}>
            <p className={styles['landing-section-label']}>How it works</p>
            <h2 className={styles['landing-how-it-works-title']}>
              Build your profile. Find your partners. Start collaborating.
            </h2>
            <div className={styles['landing-steps']}>
              <div className={styles['landing-step']}>
                <div className={styles['landing-step-number']}>1</div>
                <h3 className={styles['landing-step-title']}>Share your research focus</h3>
                <p className={styles['landing-step-description']}>
                  Sign up with your institution email and add your main areas of interest,
                  expertise, and a short overview of what you&apos;re working on. You control
                  what&apos;s visible.
                </p>
              </div>
              <div className={styles['landing-step']}>
                <div className={styles['landing-step-number']}>2</div>
                <h3 className={styles['landing-step-title']}>Explore researchers in Maine</h3>
                <p className={styles['landing-step-description']}>
                  Search by topic or keywords to discover colleagues whose work aligns with
                  yours, whether they&apos;re nearby or at another university in the state.
                </p>
              </div>
              <div className={styles['landing-step']}>
                <div className={styles['landing-step-number']}>3</div>
                <h3 className={styles['landing-step-title']}>Start meaningful collaborations</h3>
                <p className={styles['landing-step-description']}>
                  Reach out when you see a natural fit, build new partnerships over time, and
                  return to ScholarSphere whenever you&apos;re planning a project or looking for
                  new people to involve.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA Section */}
        <section className={styles['landing-final-cta']} id="get-started">
          <div className={styles['landing-final-cta-container']}>
            <p className={styles['landing-section-label']}>Get started</p>
            <h2 className={styles['landing-final-cta-title']}>
            Start connecting across Maine today.
            </h2>
            <p className={styles['landing-final-cta-description']}>
              Create your ScholarSphere profile and make it easier for researchers across Maine
              to understand what you focus on, see where interests overlap, and start new
              collaborations.
            </p>
            <Link
              to="/signup"
              className={`${styles['landing-cta-primary']} ${styles['landing-final-cta-button']}`}
            >
              Create your profile
            </Link>
            <p className={styles['landing-final-cta-login']}>
              Already have an account?{' '}
              <Link to="/login" className={styles['landing-link']}>
                Sign in
              </Link>
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Landing;
