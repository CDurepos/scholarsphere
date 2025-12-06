import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Faculty from './pages/Search/Faculty';
import FacultyProfile from './pages/FacultyProfile';
import Equipment from './pages/Search/Equipment';
import Grants from './pages/Search/Grants';
import Institutions from './pages/Search/Institutions';
import { isAuthenticated as checkAuth } from './services/api';
import './App.css';

/**
 * Main App component with routing
 *
 * Routes:
 * - / : Landing page (always accessible, even when logged in)
 * - /login : Login page (redirects to dashboard if already logged in)
 * - /signup : Multi-step signup flow (redirects to dashboard if already logged in)
 * - /dashboard : Main dashboard (protected route)
 */
function App() {
  const ProtectedRoute = ({ children }) => {
    const [isAuth, setIsAuth] = useState(null);
    
    useEffect(() => {
      const verifyAuth = async () => {
        const authenticated = await checkAuth();
        setIsAuth(authenticated);
      };
      verifyAuth();
    }, []);
    
    if (isAuth === null) {
      return <div>Loading...</div>;
    }
    return isAuth ? children : <Navigate to="/login" replace />;
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* Landing page - always accessible */}
        <Route path="/" element={<Landing />} />
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
          path="/search/faculty"
          element={
            <ProtectedRoute>
              <Faculty />
            </ProtectedRoute>
          }
        />
        <Route
          path="/faculty/:facultyId"
          element={
            <ProtectedRoute>
              <FacultyProfile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/search/equipment"
          element={
            <ProtectedRoute>
              <Equipment />
            </ProtectedRoute>
          }
        />
        <Route
          path="/search/grants"
          element={
            <ProtectedRoute>
              <Grants />
            </ProtectedRoute>
          }
        />
        <Route
          path="/search/institutions"
          element={
            <ProtectedRoute>
              <Institutions />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
