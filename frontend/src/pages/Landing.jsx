import { Link } from 'react-router-dom';
import { Zap, Brain, Clock, Rss, Star, Shield } from 'lucide-react';

const FEATURES = [
  { icon: '🤖', color: 'rgba(124,58,237,0.2)',  title: 'GPT-4.1 Curation',     desc: 'Every article is scored and ranked by GPT-4.1 based on your exact interests and background.' },
  { icon: '⚡', color: 'rgba(6,182,212,0.2)',   title: 'Auto-Delivery',        desc: 'Set your preferred time — daily or weekly — and receive your digest automatically in your inbox.' },
  { icon: '🎯', color: 'rgba(16,185,129,0.2)',  title: 'Personalized Profile', desc: 'Configure your AI interests, expertise level, and preferences. The more context, the better the curation.' },
  { icon: '📡', color: 'rgba(245,158,11,0.2)',  title: 'Custom Sources',       desc: 'Add your own YouTube channels and RSS feeds on top of our curated defaults like OpenAI, Anthropic and more.' },
  { icon: '📰', color: 'rgba(239,68,68,0.2)',   title: 'Multi-Source',         desc: 'We monitor YouTube, OpenAI blog, Anthropic research, Hacker News, arXiv and Reddit all in one place.' },
  { icon: '🔒', color: 'rgba(99,102,241,0.2)',  title: 'Private & Secure',     desc: 'Your profile and digest history are private. We never share your data with third parties.' },
];

export default function Landing() {
  return (
    <div className="landing">
      <nav className="landing-nav">
        <div className="landing-logo">
          <div className="landing-logo-icon">⚡</div>
          <span className="landing-logo-text">AI Digest</span>
        </div>
        <div className="landing-nav-actions">
          <Link to="/login"><button className="btn btn-ghost">Sign In</button></Link>
          <Link to="/register"><button className="btn btn-primary">Get Started Free</button></Link>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-badge">
          <span>✨</span> Powered by GPT-4.1
        </div>
        <h1 className="hero-title">
          Your personal<br />
          <span className="gradient-text">AI News Curator</span>
        </h1>
        <p className="hero-sub">
          Stay ahead in AI without the noise. We scan dozens of sources daily, rank the most relevant articles for <em>your</em> interests, and deliver a curated digest straight to your inbox.
        </p>
        <div className="hero-actions">
          <Link to="/register">
            <button className="btn btn-primary" style={{ padding: '13px 28px', fontSize: 15 }}>
              Start for Free →
            </button>
          </Link>
          <Link to="/login">
            <button className="btn btn-ghost" style={{ padding: '13px 28px', fontSize: 15 }}>
              Sign In
            </button>
          </Link>
        </div>
      </section>

      <section className="features">
        {FEATURES.map((f) => (
          <div className="feature-card" key={f.title}>
            <div className="feature-icon" style={{ background: f.color }}>
              {f.icon}
            </div>
            <div className="feature-title">{f.title}</div>
            <div className="feature-desc">{f.desc}</div>
          </div>
        ))}
      </section>
    </div>
  );
}
