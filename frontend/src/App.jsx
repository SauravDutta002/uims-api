import { useState, useEffect } from 'react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { API_BASE_URL } from './config';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState(null);
  const [data, setData] = useState(null);
  const [uid, setUid] = useState('');
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const autoLogin = async () => {
      const savedUid = localStorage.getItem('cuims_uid');
      const savedPwd = localStorage.getItem('cuims_pwd');
      
      if (!savedUid || !savedPwd) {
        setIsInitializing(false);
        return;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: savedUid, password: savedPwd }),
        });

        const result = await response.json();

        if (response.ok && result.success) {
          setToken(result.token);
          setData(result.data);
          setUid(savedUid);
          setIsLoggedIn(true);
        } else {
          // Credentials might be invalid now, clear them
          localStorage.removeItem('cuims_uid');
          localStorage.removeItem('cuims_pwd');
        }
      } catch (err) {
        console.error('Auto login failed', err);
      } finally {
        setIsInitializing(false);
      }
    };

    autoLogin();
  }, []);

  const handleLoginSuccess = (sessionToken, cuimsData, userUid, password) => {
    // Save to local storage for auto-relogin
    localStorage.setItem('cuims_uid', userUid);
    localStorage.setItem('cuims_pwd', password);

    setToken(sessionToken);
    setData(cuimsData);
    setUid(userUid);
    setIsLoggedIn(true);
  };

  const handleLogout = async () => {
    // Clear auto-relogin data
    localStorage.removeItem('cuims_uid');
    localStorage.removeItem('cuims_pwd');

    if (token) {
      try {
        await fetch(`${API_BASE_URL}/api/logout`, {
          method: 'POST',
          headers: { 'x-session-token': token },
        });
      } catch {
        // Ignore logout errors
      }
    }
    setIsLoggedIn(false);
    setToken(null);
    setData(null);
    setUid('');
  };

  if (isInitializing) {
    return (
      <div className="login-wrapper">
        <div className="login-card" style={{ textAlign: 'center' }}>
          <div className="logo" style={{ animation: 'bounce 1s infinite' }}>🎓</div>
          <h2>Restoring Session...</h2>
          <p className="subtitle" style={{ marginTop: '1rem' }}>
            Logging you back into CUIMS automatically.
          </p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return <Dashboard data={data} uid={uid} onLogout={handleLogout} />;
}
