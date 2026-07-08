import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSources, addSource, deleteSource } from '../../api/client';
import { Layout } from '../../components/Layout';
import { Plus, Trash2 } from 'lucide-react';

const SOURCE_TYPES = [
  { value: 'youtube', label: 'YouTube Channel', icon: '▶', placeholder: 'UCbfYPyITQ-7l4upoX8nvctg' },
  { value: 'rss',     label: 'RSS Feed',        icon: '📡', placeholder: 'https://example.com/feed.xml' },
];

export default function Sources() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ source_type: 'youtube', name: '', url: '' });
  const [error, setError] = useState('');

  const { data: sources = [], isLoading } = useQuery({
    queryKey: ['sources'],
    queryFn: () => getSources().then(r => r.data),
  });

  const add = useMutation({
    mutationFn: addSource,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sources'] });
      setForm({ source_type: 'youtube', name: '', url: '' });
      setShowForm(false); setError('');
    },
    onError: (e) => setError(e.response?.data?.detail || 'Failed to add source.'),
  });

  const remove = useMutation({
    mutationFn: deleteSource,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sources'] }),
  });

  const handleAdd = (e) => { e.preventDefault(); setError(''); add.mutate(form); };

  const placeholder = SOURCE_TYPES.find(t => t.value === form.source_type)?.placeholder || '';

  return (
    <Layout>
      <div className="page-header" style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
        <div>
          <h1 className="page-title">News Sources</h1>
          <p className="page-subtitle">Manage your YouTube channels and RSS feeds</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(s => !s)}>
          <Plus size={15} /> {showForm ? 'Cancel' : 'Add Source'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ maxWidth: 520, marginBottom: 24 }}>
          <h3 style={{ fontWeight:700, fontSize:15, marginBottom:16 }}>Add New Source</h3>
          {error && <div className="error-msg">{error}</div>}
          <form onSubmit={handleAdd}>
            <div className="form-group">
              <label className="form-label">Source Type</label>
              <select className="form-input" value={form.source_type}
                onChange={e => setForm(f => ({ ...f, source_type: e.target.value }))}>
                {SOURCE_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Display Name</label>
              <input className="form-input" placeholder="e.g. Andrej Karpathy" value={form.name}
                onChange={e => setForm(f => ({ ...f, name: e.target.value }))} required />
            </div>
            <div className="form-group">
              <label className="form-label">{form.source_type === 'youtube' ? 'YouTube Channel ID' : 'Feed URL'}</label>
              <input className="form-input" placeholder={placeholder} value={form.url}
                onChange={e => setForm(f => ({ ...f, url: e.target.value }))} required />
              {form.source_type === 'youtube' && (
                <p className="text-muted" style={{ marginTop: 6 }}>
                  Find channel ID in the channel's URL: youtube.com/channel/<strong>CHANNEL_ID</strong>
                </p>
              )}
            </div>
            <button type="submit" className="btn btn-primary" disabled={add.isPending}>
              {add.isPending ? <><span className="spinner" /> Adding...</> : 'Add Source'}
            </button>
          </form>
        </div>
      )}

      {isLoading ? (
        <div className="page-loading"><span className="spinner" /></div>
      ) : sources.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📡</div>
          <p style={{ fontWeight:600, marginBottom:6 }}>No custom sources yet</p>
          <p>Add YouTube channels or RSS feeds to personalize your digest beyond the defaults.</p>
        </div>
      ) : (
        <div className="source-list">
          {sources.map((s) => (
            <div className="source-item" key={s.id}>
              <div className="source-info">
                <div className={`source-icon ${s.source_type}`}>
                  {s.source_type === 'youtube' ? '▶' : '📡'}
                </div>
                <div>
                  <div className="source-name">{s.name}</div>
                  <div className="source-url">{s.url}</div>
                </div>
              </div>
              <div style={{ display:'flex', gap:8, alignItems:'center' }}>
                <span className={`badge badge-${s.source_type === 'youtube' ? 'youtube' : 'rss'}`}>
                  {s.source_type}
                </span>
                <button className="btn btn-danger btn-sm"
                  onClick={() => remove.mutate(s.id)}
                  disabled={remove.isPending}>
                  <Trash2 size={13} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
