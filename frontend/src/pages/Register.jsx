import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register, login, getMe } from '../api/client';
import { useAuthStore } from '../store/auth';

const DEFAULT_INTERESTS = ['Large Language Models', 'AI Agents', 'RAG Systems', 'Prompt Engineering'];

export default function Register() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    email: '', password: '', name: '', title: '',
    background: '', interests: [...DEFAULT_INTERESTS], expertise_level: 'Intermediate',
  });
  const [newInterest, setNewInterest] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setAuth, setUser } = useAuthStore();
  const navigate = useNavigate();

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const addInterest = (e) => {
    if ((e.key === 'Enter' || e.key === ',') && newInterest.trim()) {
      e.preventDefault();
      if (!form.interests.includes(newInterest.trim())) {
        set('interests', [...form.interests, newInterest.trim()]);
      }
      setNewInterest('');
    }
  };
  const removeInterest = (i) => set('interests', form.interests.filter((_, idx) => idx !== i));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (step === 1) { setStep(2); return; }
    setError(''); setLoading(true);
    try {
      await register(form);
      const { data } = await login(form.email, form.password);
      setAuth(data.access_token, null);
      const me = await getMe();
      setUser(me.data);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ maxWidth: 480 }}>
        <div className="auth-logo" style={{ display: 'flex', alignItems: 'center', gap: 12, justifyContent: 'center' }}>
          <div className="auth-logo-svg" style={{ display: 'flex', alignItems: 'center' }}>
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="registerLogoGrad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="var(--primary)" />
                  <stop offset="100%" stopColor="var(--accent)" />
                </linearGradient>
              </defs>
              <circle cx="12" cy="12" r="9" stroke="url(#registerLogoGrad)" strokeWidth="1.5" strokeDasharray="3 3" />
              <circle cx="12" cy="12" r="3" fill="url(#registerLogoGrad)" />
              <circle cx="6" cy="12" r="1.5" fill="url(#registerLogoGrad)" />
              <circle cx="18" cy="12" r="1.5" fill="url(#registerLogoGrad)" />
              <circle cx="12" cy="6" r="1.5" fill="url(#registerLogoGrad)" />
              <circle cx="12" cy="18" r="1.5" fill="url(#registerLogoGrad)" />
              <line x1="8.5" y1="12" x2="9.5" y2="12" stroke="url(#registerLogoGrad)" strokeWidth="1" />
              <line x1="14.5" y1="12" x2="15.5" y2="12" stroke="url(#registerLogoGrad)" strokeWidth="1" />
              <line x1="12" y1="8.5" x2="12" y2="9.5" stroke="url(#registerLogoGrad)" strokeWidth="1" />
              <line x1="12" y1="14.5" x2="12" y2="15.5" stroke="url(#registerLogoGrad)" strokeWidth="1" />
            </svg>
          </div>
          <span className="auth-logo-text" style={{ fontSize: 18, fontWeight: 800 }}>AI News Curator</span>
        </div>
        <h1 className="auth-title">{step === 1 ? 'Create account' : 'Set your interests'}</h1>
        <p className="auth-subtitle">
          {step === 1 ? 'Start receiving personalized AI news' : 'Help us curate content just for you'}
        </p>

        {/* Progress */}
        <div style={{ display: 'flex', gap: 6, marginBottom: 24 }}>
          {[1,2].map(s => (
            <div key={s} style={{
              flex: 1, height: 3, borderRadius: 2,
              background: s <= step ? 'var(--primary)' : 'var(--border)',
              transition: 'background 0.3s'
            }} />
          ))}
        </div>

        {error && <div className="error-msg">{error}</div>}

        <form onSubmit={handleSubmit}>
          {step === 1 ? (
            <>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input className="form-input" placeholder="Alex Smith" value={form.name}
                  onChange={e => set('name', e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Email</label>
                <input className="form-input" type="email" placeholder="you@example.com"
                  value={form.email} onChange={e => set('email', e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input className="form-input" type="password" placeholder="Min 8 characters"
                  value={form.password} onChange={e => set('password', e.target.value)} required minLength={8} />
              </div>
            </>
          ) : (
            <>
              <div className="form-group">
                <label className="form-label">Job Title (optional)</label>
                <input className="form-input" placeholder="ML Engineer, Researcher..." value={form.title}
                  onChange={e => set('title', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Background / Context</label>
                <textarea className="form-input" placeholder="Tell us about your work and what you're building..."
                  value={form.background} onChange={e => set('background', e.target.value)} rows={3} />
              </div>
              <div className="form-group">
                <label className="form-label">AI Interests (press Enter to add)</label>
                <div className="tag-container">
                  {form.interests.map((t, i) => (
                    <span className="tag" key={t}>
                      {t}<button type="button" onClick={() => removeInterest(i)}>×</button>
                    </span>
                  ))}
                  <input className="tag-input" placeholder="Add interest..."
                    value={newInterest} onChange={e => setNewInterest(e.target.value)} onKeyDown={addInterest} />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Expertise Level</label>
                <select className="form-input" value={form.expertise_level}
                  onChange={e => set('expertise_level', e.target.value)}>
                  {['Beginner','Intermediate','Advanced','Expert'].map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>
            </>
          )}

          <div style={{ display: 'flex', gap: 10 }}>
            {step === 2 && (
              <button type="button" className="btn btn-ghost" onClick={() => setStep(1)} style={{ flex: 1 }}>
                ← Back
              </button>
            )}
            <button type="submit" className="btn btn-primary" disabled={loading}
              style={{ flex: 1, justifyContent: 'center' }}>
              {loading ? <><span className="spinner" /> Creating...</> :
               step === 1 ? 'Continue →' : 'Create Account →'}
            </button>
          </div>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
