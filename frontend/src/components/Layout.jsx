import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Newspaper, Settings, Rss, LogOut, Zap, User } from 'lucide-react';
import { useAuthStore } from '../store/auth';

const NAV = [
  { to: '/dashboard', icon: <LayoutDashboard />, label: 'Dashboard' },
  { to: '/digests',   icon: <Newspaper />,       label: 'My Digests' },
];
const SETTINGS_NAV = [
  { to: '/settings/profile', icon: <User />,     label: 'Profile' },
  { to: '/settings/sources', icon: <Rss />,      label: 'Sources' },
  { to: '/settings/email',   icon: <Settings />, label: 'Email' },
];

export function Layout({ children }) {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">⚡</div>
          <span className="sidebar-logo-text">AI Digest</span>
        </div>

        <nav className="sidebar-nav">
          {NAV.map(({ to, icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
              {icon}{label}
            </NavLink>
          ))}

          <div className="nav-section-title" style={{ marginTop: 20 }}>Settings</div>
          {SETTINGS_NAV.map(({ to, icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
              {icon}{label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          {user && (
            <div style={{ padding: '0 12px 12px', fontSize: 12, color: 'var(--text-muted)' }}>
              {user.email}
            </div>
          )}
          <button className="nav-item" style={{ width: '100%' }} onClick={handleLogout}>
            <LogOut size={18} />Logout
          </button>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
