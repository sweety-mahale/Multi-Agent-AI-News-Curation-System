import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getDigests } from '../api/client';
import { Layout } from '../components/Layout';
import { ExternalLink } from 'lucide-react';

function Badge({ type }) {
  return <span className={`badge badge-${type}`}>{type}</span>;
}

const FILTERS = ['all', 'youtube', 'openai', 'anthropic'];

export default function Digests() {
  const [filter, setFilter] = useState('all');
  const { data: digests = [], isLoading } = useQuery({
    queryKey: ['digests', 200],
    queryFn: () => getDigests(200).then(r => r.data),
  });

  const filtered = filter === 'all' ? digests : digests.filter(d => d.article_type === filter);

  return (
    <Layout>
      <div className="page-header">
        <h1 className="page-title">My Digests</h1>
        <p className="page-subtitle">All articles sent to your inbox</p>
      </div>

      <div className="settings-tabs" style={{ marginBottom: 24 }}>
        {FILTERS.map(f => (
          <button key={f} className={`settings-tab${filter === f ? ' active' : ''}`}
            onClick={() => setFilter(f)}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="page-loading"><span className="spinner" /></div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <p style={{ fontWeight: 600, marginBottom: 6 }}>No digests yet</p>
          <p>Go to the Dashboard and hit "Run Now" to get your first digest.</p>
        </div>
      ) : (
        <div className="digest-list">
          {filtered.map((item) => (
            <a key={item.summary_id} href={item.url} target="_blank" rel="noreferrer" style={{ display: 'block' }}>
              <div className="digest-item">
                <div className="digest-meta">
                  <Badge type={item.article_type} />
                  <span className="text-muted">
                    {new Date(item.sent_at).toLocaleDateString('en-US', { weekday:'short', month:'short', day:'numeric' })}
                  </span>
                  {item.rank && <span className="text-muted">Rank #{item.rank}</span>}
                </div>
                <div className="digest-title">{item.title}</div>
                <div className="digest-summary">{item.summary}</div>
                <div className="digest-footer">
                  <span style={{ fontSize: 12, color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <ExternalLink size={12} /> Read article
                  </span>
                  {item.relevance_score && (
                    <span className="digest-score">⭐ {item.relevance_score.toFixed(1)}/10</span>
                  )}
                </div>
              </div>
            </a>
          ))}
        </div>
      )}
    </Layout>
  );
}
