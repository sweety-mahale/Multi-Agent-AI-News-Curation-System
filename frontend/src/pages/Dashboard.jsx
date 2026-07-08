import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMe, getDigests, triggerPipeline } from '../api/client';
import { Layout } from '../components/Layout';
import { Play, Clock, Newspaper, Star, Zap } from 'lucide-react';

function StatCard({ icon, label, value, sub, color }) {
  return (
    <div className="stat-card">
      <div className="stat-icon" style={{ background: color }}>{icon}</div>
      <div className="card-title">{label}</div>
      <div className="card-value">{value}</div>
      {sub && <div className="card-sub">{sub}</div>}
    </div>
  );
}

function Badge({ type }) {
  return <span className={`badge badge-${type}`}>{type}</span>;
}

export default function Dashboard() {
  const qc = useQueryClient();
  const [triggered, setTriggered] = useState(false);

  const { data: me } = useQuery({ queryKey: ['me'], queryFn: () => getMe().then(r => r.data) });
  const { data: digests = [] } = useQuery({ queryKey: ['digests'], queryFn: () => getDigests(5).then(r => r.data) });

  const trigger = useMutation({
    mutationFn: triggerPipeline,
    onSuccess: () => { setTriggered(true); setTimeout(() => setTriggered(false), 5000); },
  });

  const profile = me?.profile;
  const settings = me?.email_settings;
  const nextSend = settings
    ? `${settings.frequency === 'weekly' ? settings.delivery_day + ' at' : 'Daily at'} ${settings.delivery_hour}:00 UTC`
    : '—';

  return (
    <Layout>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">
            {profile ? `Hey, ${profile.name.split(' ')[0]} 👋` : 'Dashboard'}
          </h1>
          <p className="page-subtitle">Here's your AI news overview</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => trigger.mutate()}
          disabled={trigger.isPending || triggered}
        >
          {triggered ? '✓ Digest sent!' :
           trigger.isPending ? <><span className="spinner" /> Running...</> :
           <><Play size={15} /> Run Now</>}
        </button>
      </div>

      {triggered && (
        <div className="alert alert-success" style={{ marginBottom: 20 }}>
          🚀 Pipeline triggered! Check your inbox in a few minutes.
        </div>
      )}

      <div className="stats-grid">
        <StatCard icon="📰" color="rgba(124,58,237,0.2)" label="Total Digests" value={digests.length || 0} sub="articles sent" />
        <StatCard icon="⏰" color="rgba(6,182,212,0.2)"  label="Next Delivery" value={settings?.frequency || '—'} sub={nextSend} />
        <StatCard icon="🎯" color="rgba(16,185,129,0.2)" label="Interests"     value={profile?.interests?.length || 0} sub="topics tracked" />
        <StatCard icon="⚡" color="rgba(245,158,11,0.2)" label="Expertise"     value={profile?.expertise_level || '—'} sub="curation level" />
      </div>

      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: 16, fontWeight: 700 }}>Recent Articles</h2>
        <a href="/digests" style={{ fontSize: 13, color: 'var(--primary-light)' }}>View all →</a>
      </div>

      <div className="digest-list">
        {digests.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p style={{ fontWeight: 600, marginBottom: 6 }}>No digests yet</p>
            <p>Click "Run Now" above to generate your first digest!</p>
          </div>
        ) : digests.slice(0, 5).map((item) => (
          <a key={item.summary_id} href={item.url} target="_blank" rel="noreferrer">
            <div className="digest-item">
              <div className="digest-meta">
                <Badge type={item.article_type} />
                <span className="text-muted">
                  {new Date(item.sent_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              </div>
              <div className="digest-title">{item.title}</div>
              <div className="digest-summary">{item.summary}</div>
              <div className="digest-footer">
                <span className="digest-rank">Rank #{item.rank}</span>
                <span className="digest-score">⭐ {item.relevance_score?.toFixed(1)}/10</span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </Layout>
  );
}
