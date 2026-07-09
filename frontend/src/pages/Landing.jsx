import { Link } from 'react-router-dom';

const FEATURES = [
  { icon: '🤖', color: 'rgba(217, 119, 6, 0.1)',  title: 'Multi-Agent AI', desc: 'Specialized AI agents work together to summarize, evaluate, and curate the most relevant news for you.' },
  { icon: '🎯', color: 'rgba(16, 185, 129, 0.1)',  title: 'Personalized Curation', desc: 'Our system learns your interests and delivers only the news that matters to you.' },
  { icon: '✉️', color: 'rgba(163, 230, 53, 0.1)',   title: 'Daily Email Digest', desc: 'Get a clean, concise, and personalized digest delivered to your inbox every day.' },
  { icon: '📊', color: 'rgba(99, 102, 241, 0.1)',  title: 'Web Dashboard', desc: 'Manage your preferences, view history, and explore curated news anytime.' },
];

export default function Landing() {
  return (
    <div className="landing-container" style={{ position: 'relative', minHeight: '100vh', overflow: 'hidden' }}>
      
      {/* ── Background Video with Dark Overlay ──────────────────── */}
      <div style={{
        position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
        zIndex: -2, overflow: 'hidden', background: '#0c0c0e'
      }}>
        <video
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: 1 }}
        >
          <source src="/bg-video.mp4" type="video/mp4" />
        </video>
      </div>
      <div style={{
        position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
        zIndex: -1,
        background: 'linear-gradient(to bottom, rgba(12, 12, 14, 0.45) 0%, rgba(12, 12, 14, 0.85) 60%, #0c0c0e 100%)'
      }} />

      {/* ── Navbar ────────────────────────────────────────────── */}
      <nav className="landing-nav" style={{ background: 'rgba(12, 12, 14, 0.65)' }}>
        <div className="landing-logo" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="landing-logo-svg" style={{ display: 'flex', alignItems: 'center' }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="navLogoGrad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="var(--primary)" />
                  <stop offset="100%" stopColor="var(--accent)" />
                </linearGradient>
              </defs>
              {/* Outer connected rings */}
              <circle cx="12" cy="12" r="9" stroke="url(#navLogoGrad)" strokeWidth="1.5" strokeDasharray="3 3" />
              {/* Inner core nodes */}
              <circle cx="12" cy="12" r="3" fill="url(#navLogoGrad)" />
              <circle cx="6" cy="12" r="1.5" fill="url(#navLogoGrad)" />
              <circle cx="18" cy="12" r="1.5" fill="url(#navLogoGrad)" />
              <circle cx="12" cy="6" r="1.5" fill="url(#navLogoGrad)" />
              <circle cx="12" cy="18" r="1.5" fill="url(#navLogoGrad)" />
              {/* Connecting lines */}
              <line x1="8.5" y1="12" x2="9.5" y2="12" stroke="url(#navLogoGrad)" strokeWidth="1" />
              <line x1="14.5" y1="12" x2="15.5" y2="12" stroke="url(#navLogoGrad)" strokeWidth="1" />
              <line x1="12" y1="8.5" x2="12" y2="9.5" stroke="url(#navLogoGrad)" strokeWidth="1" />
              <line x1="12" y1="14.5" x2="12" y2="15.5" stroke="url(#navLogoGrad)" strokeWidth="1" />
            </svg>
          </div>
          <div className="flex-col" style={{ display: 'flex', flexDirection: 'column' }}>
            <span className="landing-logo-text" style={{ fontSize: 15, fontWeight: 700, letterSpacing: '0.02em', lineHeight: 1.1 }}>Multi-Agent AI</span>
            <span style={{ fontSize: 10, color: 'var(--text-secondary)', letterSpacing: '0.04em' }}>News Curation System</span>
          </div>
        </div>
        
        {/* Center navigation links removed */}
        
        <div className="landing-nav-actions">
          <Link to="/login"><button className="btn btn-ghost" style={{ fontSize: 13, border: 'none' }}>Log In</button></Link>
          <Link to="/register"><button className="btn btn-primary btn-sm">Get Started</button></Link>
        </div>
      </nav>

      {/* ── Hero Content Layout (Split Left and Right) ───────────── */}
      <section style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(320px, 1.2fr) minmax(300px, 1fr)',
        gap: 40,
        maxWidth: 1200,
        margin: '0 auto',
        padding: '120px 24px 60px',
        zIndex: 1,
        position: 'relative',
        alignItems: 'center'
      }} className="grid-2">
        
        {/* Left Column: Headline and CTAs */}
        <div>
          <div className="hero-badge" style={{
            background: 'rgba(124, 58, 237, 0.08)',
            border: '1px solid rgba(124, 58, 237, 0.25)',
            backdropFilter: 'blur(8px)',
            marginBottom: 20
          }}>
            <span style={{ color: 'var(--primary-light)' }}>AI-Powered News. Personalized for You.</span>
          </div>

          <h1 className="hero-title" style={{
            fontSize: 'clamp(36px, 5.5vw, 56px)',
            fontWeight: 800,
            letterSpacing: '-0.02em',
            lineHeight: 1.1,
            marginBottom: 20,
            textAlign: 'left'
          }}>
            Multi-Agent AI<br />
            <span className="gradient-text" style={{
              background: 'linear-gradient(135deg, #fff 0%, var(--primary-light) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>News Curation System</span>
          </h1>

          <p className="hero-sub" style={{
            fontSize: 'clamp(14px, 2.2vw, 15.5px)',
            lineHeight: 1.6,
            color: 'var(--text-secondary)',
            marginBottom: 36,
            textAlign: 'left'
          }}>
            We collect the latest AI news from top sources, summarize with advanced AI, personalize based on your interests, and deliver a handpicked digest straight to your inbox.
          </p>

          <div className="hero-actions" style={{ justifyContent: 'flex-start', marginBottom: 32 }}>
            <Link to="/register">
              <button className="btn btn-primary" style={{ padding: '12px 28px', fontSize: 13.5 }}>
                Get Your Personalized Digest →
              </button>
            </Link>
            <Link to="/login">
              <button className="btn btn-ghost" style={{ padding: '12px 24px', fontSize: 13.5 }}>
                Explore Dashboard
              </button>
            </Link>
          </div>

          {/* Bullet Checkmarks */}
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', fontSize: 13, color: 'var(--text-secondary)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ color: 'var(--primary-light)' }}>✓</span> AI-Powered Summaries
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ color: 'var(--primary-light)' }}>✓</span> Personalized For You
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ color: 'var(--primary-light)' }}>✓</span> Daily Email Digests
            </div>
          </div>
        </div>

        {/* Right Column: Visual Diagram Card (How It Works) */}
        <div id="how-it-works" className="card" style={{
          background: 'rgba(20, 20, 22, 0.65)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          borderRadius: 'var(--radius-lg)',
          padding: 28,
          display: 'flex',
          flexDirection: 'column',
          gap: 20
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border)', paddingBottom: 12 }}>
            <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>Sources</span>
            <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>Multi-Agent Pipeline</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr 1fr', gap: 16, alignItems: 'center', fontSize: 12 }} className="grid-3">
            {/* Sources column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ background: 'var(--bg-elevated)', padding: 10, borderRadius: 6, border: '1px solid var(--border)', textAlign: 'center' }}>
                <div style={{ color: '#ef4444', fontSize: 18, marginBottom: 2 }}>▶</div>
                <div style={{ fontWeight: 600, fontSize: 10 }}>YouTube</div>
              </div>
              <div style={{ background: 'var(--bg-elevated)', padding: 10, borderRadius: 6, border: '1px solid var(--border)', textAlign: 'center' }}>
                <div style={{ color: '#f59e0b', fontSize: 18, marginBottom: 2 }}>📡</div>
                <div style={{ fontWeight: 600, fontSize: 10 }}>RSS Feeds</div>
              </div>
              <div style={{ background: 'var(--bg-elevated)', padding: 10, borderRadius: 6, border: '1px solid var(--border)', textAlign: 'center' }}>
                <div style={{ color: '#3b82f6', fontSize: 18, marginBottom: 2 }}>🌐</div>
                <div style={{ fontWeight: 600, fontSize: 10 }}>AI Blogs</div>
              </div>
            </div>

            {/* Pipeline column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ background: 'var(--bg-elevated)', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 700, color: 'var(--primary-light)', fontSize: 10 }}>Digest Agent</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: 9 }}>Summarizes content</div>
              </div>
              <div style={{ background: 'var(--bg-elevated)', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 700, color: '#10b981', fontSize: 10 }}>Curator Agent</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: 9 }}>Ranks by relevance</div>
              </div>
              <div style={{ background: 'var(--bg-elevated)', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border)' }}>
                <div style={{ fontWeight: 700, color: '#3b82f6', fontSize: 10 }}>Email Agent</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: 9 }}>Crafts newsletter</div>
              </div>
            </div>

            {/* User target column */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
              <div style={{ fontSize: 24 }}>👤</div>
              <div style={{
                background: 'rgba(217, 119, 6, 0.1)',
                border: '1px solid var(--border-active)',
                padding: '10px 8px',
                borderRadius: 6,
                textAlign: 'center',
                fontSize: 9,
                fontWeight: 700,
                color: 'var(--primary-light)'
              }}>
                ✉️ Personalized Digest
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features Section ───────────────────────────────────── */}
      <section id="features" style={{
        position: 'relative',
        zIndex: 1,
        padding: '40px 24px 100px',
        maxWidth: 1200,
        margin: '0 auto'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
          gap: 20
        }}>
          {FEATURES.map((f) => (
            <div className="feature-card" key={f.title} style={{
              background: 'rgba(20, 20, 22, 0.55)',
              border: '1px solid rgba(255, 255, 255, 0.04)',
              backdropFilter: 'blur(16px)',
              borderRadius: 'var(--radius-lg)'
            }}>
              <div className="feature-icon" style={{ background: f.color, fontSize: 20 }}>
                {f.icon}
              </div>
              <div className="feature-title" style={{ fontSize: 15, fontWeight: 700, marginBottom: 8 }}>
                {f.title}
              </div>
              <div className="feature-desc" style={{ color: 'var(--text-secondary)', fontSize: 13, lineHeight: 1.6 }}>
                {f.desc}
              </div>
            </div>
          ))}
        </div>
      </section>

    </div>
  );
}
