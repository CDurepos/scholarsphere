import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Search from './pages/Search';
import './App.css';

/**
 * Main App component with routing
 *
 * Routes:
 * - / : Landing page (Login/Signup choice) or redirect to dashboard if logged in
 * - /login : Login page
 * - /signup : Multi-step signup flow
 * - /dashboard : Main dashboard (protected route)
 */
function App() {
  // Check if user is logged in
  const isAuthenticated = () => {
    const facultyId = localStorage.getItem('faculty_id');
    return !!facultyId;
  };

  // Protected route wrapper
  const ProtectedRoute = ({ children }) => {
    return isAuthenticated() ? children : <Navigate to="/" replace />;
  };

  function RootRedirect() {
    const auth = isAuthenticated();
    return auth ? <Navigate to="/dashboard" replace /> : <Landing />;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<RootRedirect />}
        />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/search"
          element={
            <ProtectedRoute>
              <Search />
            </ProtectedRoute>
          }
        />
        {/* Catch all - redirect to landing */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
