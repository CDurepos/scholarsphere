import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Faculty from './pages/Search/Faculty';
import Equipment from './pages/Search/Equipment';
import Grants from './pages/Search/Grants';
import Institutions from './pages/Search/Institutions';
import { isAuthenticated as checkAuth } from './services/api';
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
  const [authStatus, setAuthStatus] = useState(null);

  useEffect(() => {
    const checkAuthStatus = async () => {
      const authenticated = await checkAuth();
      setAuthStatus(authenticated);
    };
    checkAuthStatus();
  }, []);

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
    return isAuth ? children : <Navigate to="/" replace />;
  };

  function RootRedirect() {
    if (authStatus === null) {
      return <div>Loading...</div>;
    }
    return authStatus ? <Navigate to="/dashboard" replace /> : <Landing />;
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
          path="/search/faculty"
          element={
            <ProtectedRoute>
              <Faculty />
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
