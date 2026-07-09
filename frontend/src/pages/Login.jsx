import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login, getMe } from '../api/client';
import { useAuthStore } from '../store/auth';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setAuth, setUser } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const { data } = await login(email, password);
      setAuth(data.access_token, null);
      const me = await getMe();
      setUser(me.data);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo" style={{ display: 'flex', alignItems: 'center', gap: 12, justifyContent: 'center' }}>
          <div className="auth-logo-svg" style={{ display: 'flex', alignItems: 'center' }}>
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="authLogoGrad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="var(--primary)" />
                  <stop offset="100%" stopColor="var(--accent)" />
                </linearGradient>
              </defs>
              <circle cx="12" cy="12" r="9" stroke="url(#authLogoGrad)" strokeWidth="1.5" strokeDasharray="3 3" />
              <circle cx="12" cy="12" r="3" fill="url(#authLogoGrad)" />
              <circle cx="6" cy="12" r="1.5" fill="url(#authLogoGrad)" />
              <circle cx="18" cy="12" r="1.5" fill="url(#authLogoGrad)" />
              <circle cx="12" cy="6" r="1.5" fill="url(#authLogoGrad)" />
              <circle cx="12" cy="18" r="1.5" fill="url(#authLogoGrad)" />
              <line x1="8.5" y1="12" x2="9.5" y2="12" stroke="url(#authLogoGrad)" strokeWidth="1" />
              <line x1="14.5" y1="12" x2="15.5" y2="12" stroke="url(#authLogoGrad)" strokeWidth="1" />
              <line x1="12" y1="8.5" x2="12" y2="9.5" stroke="url(#authLogoGrad)" strokeWidth="1" />
              <line x1="12" y1="14.5" x2="12" y2="15.5" stroke="url(#authLogoGrad)" strokeWidth="1" />
            </svg>
          </div>
          <span className="auth-logo-text" style={{ fontSize: 18, fontWeight: 800 }}>AI News Curator</span>
        </div>
        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Sign in to your account</p>

        {error && <div className="error-msg">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-input" type="email" placeholder="you@example.com"
              value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className="form-input" type="password" placeholder="••••••••"
              value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? <><span className="spinner" /> Signing in...</> : 'Sign In →'}
          </button>
        </form>

        <div className="auth-footer">
          Don't have an account? <Link to="/register">Create one free</Link>
        </div>
      </div>
    </div>
  );
}
