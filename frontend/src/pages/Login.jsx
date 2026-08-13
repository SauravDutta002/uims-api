import { useState } from 'react';
import { API_BASE_URL } from '../config';

export default function Login({ onLoginSuccess }) {
  const [uid, setUid] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!uid.trim() || !password.trim()) return;

    setLoading(true);
    setError('');
    setStatus('Connecting to CUIMS...');

    try {
      // Short delay to show the connecting message
      await new Promise((r) => setTimeout(r, 300));
      setStatus('Solving captcha & logging in...');

      const response = await fetch(`${API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid: uid.trim(), password }),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.error || 'Login failed');
      }

      setStatus('Loading dashboard...');
      await new Promise((r) => setTimeout(r, 200));

      onLoginSuccess(result.token, result.data, uid.trim(), password);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
      setLoading(false);
      setStatus('');
    }
  };

  return (
    <div className="login-wrapper">
      <form className="login-card" onSubmit={handleSubmit}>
        <div className="logo">🎓</div>
        <h1>CUIMS Dashboard</h1>
        <p className="subtitle">
          Login once — we handle the captcha for you
        </p>

        {error && <div className="login-error">{error}</div>}

        <div className="form-group">
          <label htmlFor="uid">University ID</label>
          <input
            id="uid"
            type="text"
            placeholder="e.g. 24BCS10029"
            value={uid}
            onChange={(e) => setUid(e.target.value)}
            disabled={loading}
            autoComplete="username"
            autoFocus
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            placeholder="Enter your CUIMS password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
            autoComplete="current-password"
          />
        </div>

        <button type="submit" className="login-btn" disabled={loading}>
          {loading ? 'Please wait...' : 'Login'}
        </button>

        {status && (
          <div className="login-status">
            <span className="spinner" />
            {status}
          </div>
        )}
      </form>
    </div>
  );
}
