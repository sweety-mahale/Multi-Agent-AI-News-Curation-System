import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMe, updateEmailSettings, reschedulePipeline } from '../../api/client';
import { Layout } from '../../components/Layout';
import { Save, Clock, Mail } from 'lucide-react';

const DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
const HOURS = Array.from({ length: 24 }, (_, i) => ({
  value: i, label: `${String(i).padStart(2,'0')}:00 UTC`
}));

export default function EmailSettings() {
  const qc = useQueryClient();
  const { data: me, isLoading } = useQuery({ queryKey: ['me'], queryFn: () => getMe().then(r => r.data) });

  const [form, setForm] = useState({
    email_address: '', frequency: 'daily', delivery_hour: 8, delivery_day: 'monday', top_n: 10
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (me?.email_settings) {
      const s = me.email_settings;
      setForm({
        email_address: s.email_address || '',
        frequency: s.frequency || 'daily',
        delivery_hour: s.delivery_hour ?? 8,
        delivery_day: s.delivery_day || 'monday',
        top_n: s.top_n ?? 10,
      });
    }
  }, [me]);

  const mutation = useMutation({
    mutationFn: async (data) => {
      await updateEmailSettings(data);
      await reschedulePipeline();
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['me'] });
      setSaved(true); setTimeout(() => setSaved(false), 3000);
    },
  });

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));
  const handleSubmit = (e) => { e.preventDefault(); mutation.mutate(form); };

  if (isLoading) return <Layout><div className="page-loading"><span className="spinner" /></div></Layout>;

  return (
    <Layout>
      <div className="page-header">
        <h1 className="page-title">Email Settings</h1>
        <p className="page-subtitle">Configure when and how you receive your digest</p>
      </div>

      {saved && <div className="alert alert-success">✓ Settings saved and schedule updated!</div>}
      {mutation.isError && <div className="alert alert-error">Failed to save. Please try again.</div>}

      <div className="card" style={{ maxWidth: 560 }}>
        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label className="form-label"><Mail size={13} style={{ marginRight:5 }} />Delivery Email</label>
            <input className="form-input" type="email" value={form.email_address}
              onChange={e => set('email_address', e.target.value)} required />
          </div>

          <hr className="divider" />

          <div className="form-group">
            <label className="form-label"><Clock size={13} style={{ marginRight:5 }} />Delivery Frequency</label>
            <div style={{ display:'flex', gap:10 }}>
              {['daily','weekly'].map(f => (
                <button key={f} type="button"
                  style={{
                    flex:1, padding:'11px 0', borderRadius:'var(--radius-sm)',
                    border: `1px solid ${form.frequency === f ? 'var(--primary)' : 'var(--border)'}`,
                    background: form.frequency === f ? 'var(--primary-glow)' : 'var(--bg-elevated)',
                    color: form.frequency === f ? 'var(--primary-light)' : 'var(--text-secondary)',
                    fontWeight: 600, fontSize:14, cursor:'pointer', transition:'all 0.15s'
                  }}
                  onClick={() => set('frequency', f)}>
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {form.frequency === 'weekly' && (
            <div className="form-group">
              <label className="form-label">Delivery Day</label>
              <select className="form-input" value={form.delivery_day}
                onChange={e => set('delivery_day', e.target.value.toLowerCase())}>
                {DAYS.map(d => <option key={d} value={d.toLowerCase()}>{d}</option>)}
              </select>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Delivery Time (UTC)</label>
            <select className="form-input" value={form.delivery_hour}
              onChange={e => set('delivery_hour', parseInt(e.target.value))}>
              {HOURS.map(h => <option key={h.value} value={h.value}>{h.label}</option>)}
            </select>
            <p className="text-muted" style={{ marginTop:6 }}>
              Your local time: {new Date(new Date().setUTCHours(form.delivery_hour, 0, 0, 0)).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })}
            </p>
          </div>

          <div className="form-group">
            <label className="form-label">Articles per Digest</label>
            <div style={{ display:'flex', alignItems:'center', gap:14 }}>
              <input type="range" min={5} max={20} step={1} value={form.top_n}
                onChange={e => set('top_n', parseInt(e.target.value))}
                style={{ flex:1, accentColor:'var(--primary)' }} />
              <span style={{ minWidth:40, textAlign:'center', fontWeight:700, color:'var(--primary-light)' }}>
                {form.top_n}
              </span>
            </div>
            <p className="text-muted" style={{ marginTop:6 }}>Top {form.top_n} articles ranked by relevance</p>
          </div>

          <button type="submit" className="btn btn-primary" disabled={mutation.isPending}>
            {mutation.isPending ? <><span className="spinner" /> Saving...</> : <><Save size={15} /> Save & Apply</>}
          </button>
        </form>
      </div>
    </Layout>
  );
}
