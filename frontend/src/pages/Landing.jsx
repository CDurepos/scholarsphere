import { Link } from 'react-router-dom';
import { FaSearch, FaHandshake, FaBookOpen, FaGlobe, FaLightbulb, FaChartBar } from 'react-icons/fa';
import ConnectionParticles from '../components/ConnectionParticles';
import logo from '../assets/logo.png';
import umoLogo from '../assets/umo-logo.png';
import usmLogo from '../assets/usm-logo.png';
import umfLogo from '../assets/umf-logo.png';
import umaLogo from '../assets/uma-logo.png';
import './Landing.css';

const LANDING_PARTICLE_COLORS = ['#ffffff', '#dfe8ff'];
const LANDING_PARTICLE_LINK_COLOR = '#c6d6ff';
const LANDING_PARTICLE_QUANTITY = 70;

function Landing() {
  return (
    <div className="landing-container">
      {/* Top Navigation Bar */}
      <header className="landing-nav">
        <div className="landing-nav-left">
          <img src={logo} alt="ScholarSphere" className="landing-nav-logo" />
          <span className="landing-nav-brand">ScholarSphere</span>
        </div>
        <div className="landing-nav-right">
          <a href="#features" className="landing-nav-link">
            Features
          </a>
          <a href="#how-it-works" className="landing-nav-link">
            How it works
          </a>
          <Link to="/login" className="landing-nav-link">
            Sign in
          </Link>
          <Link to="/signup" className="landing-nav-button-primary">
            GET STARTED
          </Link>
        </div>
      </header>

      <main className="landing-main">
        {/* Hero Section with particle background */}
        <section className="landing-hero">
          <ConnectionParticles
            className="landing-hero-particles"
            colors={LANDING_PARTICLE_COLORS}
            linkColor={LANDING_PARTICLE_LINK_COLOR}
            quantity={LANDING_PARTICLE_QUANTITY}
          />
          <div className="landing-hero-inner">
            <div className="landing-hero-copy">
              <div className="landing-hero-pill">
                <span className="landing-hero-pill-dot" />
                Built for researchers at Maine&apos;s universities
              </div>

              <h1 className="landing-headline">
                Your single, statewide directory for
                <span className="landing-headline-highlight">
                  {' '}finding collaborative faculty.
                </span>
              </h1>

              <p className="landing-subheadline">
                ScholarSphere is a research-focused directory for Maine. Create a profile that
                highlights your interests, expertise, and current work so others can quickly see
                where you fit and reach out when their projects align.
              </p>

              <div className="landing-cta-row">
                <Link to="/signup" className="landing-cta-primary">
                  Create your profile
                </Link>
                <a href="#features" className="landing-cta-secondary">
                  Explore features
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Connected Maine Universities Banner */}
        <section
          className="landing-universities-row"
          aria-label="Connected Maine universities"
        >
          <div className="landing-universities-inner">
            <p className="landing-universities-label">
              Connecting researchers across Maine&apos;s universities
            </p>
            <div className="landing-universities-container">
              <div className="landing-university-logo-item">
                <img
                  src={umoLogo}
                  alt="University of Maine"
                  className="landing-university-logo"
                />
              </div>
              <div className="landing-university-logo-item">
                <img
                  src={usmLogo}
                  alt="University of Southern Maine"
                  className="landing-university-logo"
                />
              </div>
              <div className="landing-university-logo-item">
                <img
                  src={umfLogo}
                  alt="University of Maine at Farmington"
                  className="landing-university-logo"
                />
              </div>
              <div className="landing-university-logo-item">
                <img
                  src={umaLogo}
                  alt="University of Maine at Augusta"
                  className="landing-university-logo"
                />
              </div>
            </div>
          </div>

          <p className="landing-universities-disclaimer">
            ScholarSphere is an independent project and is not officially affiliated with, 
            sponsored by, or endorsed by the institutions shown. Faculty information is 
            collected from publicly available sources.
          </p>
        </section>

        {/* Features Section */}
        <section className="landing-features" id="features">
          <div className="landing-features-container">
            <p className="landing-section-label">Features</p>
            <h2 className="landing-features-title">
              Unlock the full potential of Maine's research community.
            </h2>
            <div className="landing-features-grid">
              <div className="landing-feature-card">
                <div className="landing-feature-icon">
                  <FaSearch />
                </div>
                <h3 className="landing-feature-card-title">Search by research interests</h3>
                <p className="landing-feature-card-description">
                  Search across Maine by topic, keywords, or areas of expertise to see who is
                  working on related problems—whether they&apos;re in your department or at
                  another institution.
                </p>
              </div>

              <div className="landing-feature-card">
                <div className="landing-feature-icon">
                  <FaHandshake />
                </div>
                <h3 className="landing-feature-card-title">Grow your research network</h3>
                <p className="landing-feature-card-description">
                  Discover researchers you may not already know and connect around projects,
                  grants, workshops, or student opportunities without relying only on existing
                  personal networks.
                </p>
              </div>

              <div className="landing-feature-card">
                <div className="landing-feature-icon">
                  <FaBookOpen />
                </div>
                <h3 className="landing-feature-card-title">Show your research identity</h3>
                <p className="landing-feature-card-description">
                  Summarize what you work on, your expertise, and the types of collaborations
                  you&apos;re interested in so potential partners quickly understand how you fit.
                </p>
              </div>

              <div className="landing-feature-card">
                <div className="landing-feature-icon">
                  <FaGlobe />
                </div>
                <h3 className="landing-feature-card-title">See the Maine research landscape</h3>
                <p className="landing-feature-card-description">
                  Look beyond a single campus directory. ScholarSphere brings together
                  researchers across Maine&apos;s universities into one place, centered on
                  research connections.
                </p>
              </div>

              <div className="landing-feature-card">
                <div className="landing-feature-icon">
                  <FaLightbulb />
                </div>
                <h3 className="landing-feature-card-title">Spark new collaborations</h3>
                <p className="landing-feature-card-description">
                  Use overlapping interests and complementary expertise to start new projects,
                  explore emerging topics, or co-develop courses and initiatives.
                </p>
              </div>

              <div className="landing-feature-card">
                <div className="landing-feature-icon">
                  <FaChartBar />
                </div>
                <h3 className="landing-feature-card-title">Build stronger project teams</h3>
                <p className="landing-feature-card-description">
                  Quickly spot people whose skills and experience round out your team when
                  you&apos;re planning research projects, programs, or future proposals.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section (simple, text-only) */}
        <section className="landing-how-it-works" id="how-it-works">
          <div className="landing-how-it-works-container">
            <p className="landing-section-label">How it works</p>
            <h2 className="landing-how-it-works-title">
              Build your profile. Find your partners. Start collaborating.
            </h2>
            <div className="landing-steps">
              <div className="landing-step">
                <div className="landing-step-number">1</div>
                <h3 className="landing-step-title">Share your research focus</h3>
                <p className="landing-step-description">
                  Sign up with your institution email and add your main areas of interest,
                  expertise, and a short overview of what you&apos;re working on. You control
                  what&apos;s visible.
                </p>
              </div>
              <div className="landing-step">
                <div className="landing-step-number">2</div>
                <h3 className="landing-step-title">Explore researchers in Maine</h3>
                <p className="landing-step-description">
                  Search by topic or keywords to discover colleagues whose work aligns with
                  yours, whether they&apos;re nearby or at another university in the state.
                </p>
              </div>
              <div className="landing-step">
                <div className="landing-step-number">3</div>
                <h3 className="landing-step-title">Start meaningful collaborations</h3>
                <p className="landing-step-description">
                  Reach out when you see a natural fit, build new partnerships over time, and
                  return to ScholarSphere whenever you&apos;re planning a project or looking for
                  new people to involve.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA Section */}
        <section className="landing-final-cta" id="get-started">
          <div className="landing-final-cta-container">
            <p className="landing-section-label">Get started</p>
            <h2 className="landing-final-cta-title">
            Start connecting across Maine today.
            </h2>
            <p className="landing-final-cta-description">
              Create your ScholarSphere profile and make it easier for researchers across Maine
              to understand what you focus on, see where interests overlap, and start new
              collaborations.
            </p>
            <Link
              to="/signup"
              className="landing-cta-primary landing-final-cta-button"
            >
              Create your profile
            </Link>
            <p className="landing-final-cta-login">
              Already have an account?{' '}
              <Link to="/login" className="landing-link">
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
