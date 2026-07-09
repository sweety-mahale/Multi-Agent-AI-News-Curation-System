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
        <div className="sidebar-logo" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="sidebar-logo-svg" style={{ display: 'flex', alignItems: 'center' }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="sidebarLogoGrad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="var(--primary)" />
                  <stop offset="100%" stopColor="var(--accent)" />
                </linearGradient>
              </defs>
              <circle cx="12" cy="12" r="9" stroke="url(#sidebarLogoGrad)" strokeWidth="1.5" strokeDasharray="3 3" />
              <circle cx="12" cy="12" r="3" fill="url(#sidebarLogoGrad)" />
              <circle cx="6" cy="12" r="1.5" fill="url(#sidebarLogoGrad)" />
              <circle cx="18" cy="12" r="1.5" fill="url(#sidebarLogoGrad)" />
              <circle cx="12" cy="6" r="1.5" fill="url(#sidebarLogoGrad)" />
              <circle cx="12" cy="18" r="1.5" fill="url(#sidebarLogoGrad)" />
              <line x1="8.5" y1="12" x2="9.5" y2="12" stroke="url(#sidebarLogoGrad)" strokeWidth="1" />
              <line x1="14.5" y1="12" x2="15.5" y2="12" stroke="url(#sidebarLogoGrad)" strokeWidth="1" />
              <line x1="12" y1="8.5" x2="12" y2="9.5" stroke="url(#sidebarLogoGrad)" strokeWidth="1" />
              <line x1="12" y1="14.5" x2="12" y2="15.5" stroke="url(#sidebarLogoGrad)" strokeWidth="1" />
            </svg>
          </div>
          <span className="sidebar-logo-text" style={{ fontSize: 13, whiteSpace: 'nowrap' }}>AI News Curator</span>
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
