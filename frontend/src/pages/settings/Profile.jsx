import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMe, updateProfile } from '../../api/client';
import { Layout } from '../../components/Layout';
import { Save } from 'lucide-react';

export default function ProfileSettings() {
  const qc = useQueryClient();
  const { data: me, isLoading } = useQuery({ queryKey: ['me'], queryFn: () => getMe().then(r => r.data) });

  const [form, setForm] = useState({ name: '', title: '', background: '', interests: [], expertise_level: 'Intermediate' });
  const [newInterest, setNewInterest] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (me?.profile) {
      setForm({
        name: me.profile.name || '',
        title: me.profile.title || '',
        background: me.profile.background || '',
        interests: me.profile.interests || [],
        expertise_level: me.profile.expertise_level || 'Intermediate',
      });
    }
  }, [me]);

  const mutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['me'] });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    },
  });

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

  const handleSubmit = (e) => { e.preventDefault(); mutation.mutate(form); };

  if (isLoading) return <Layout><div className="page-loading"><span className="spinner" /></div></Layout>;

  return (
    <Layout>
      <div className="page-header">
        <h1 className="page-title">Profile Settings</h1>
        <p className="page-subtitle">Customize your AI curation profile</p>
      </div>

      {saved && <div className="alert alert-success">✓ Profile saved successfully!</div>}
      {mutation.isError && <div className="alert alert-error">Failed to save. Please try again.</div>}

      <div className="card" style={{ maxWidth: 640 }}>
        <form onSubmit={handleSubmit}>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input className="form-input" value={form.name} onChange={e => set('name', e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Job Title</label>
              <input className="form-input" placeholder="ML Engineer, Researcher..." value={form.title}
                onChange={e => set('title', e.target.value)} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Background & Context</label>
            <textarea className="form-input" rows={4}
              placeholder="Describe your work, what you're building, or what you need AI news for..."
              value={form.background} onChange={e => set('background', e.target.value)} />
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

          <div className="form-group">
            <label className="form-label">AI Interests (press Enter to add)</label>
            <div className="tag-container">
              {form.interests.map((t, i) => (
                <span className="tag" key={t}>
                  {t}
                  <button type="button" onClick={() => set('interests', form.interests.filter((_, idx) => idx !== i))}>×</button>
                </span>
              ))}
              <input className="tag-input" placeholder="e.g. LLMs, Agents, LoRA..."
                value={newInterest} onChange={e => setNewInterest(e.target.value)} onKeyDown={addInterest} />
            </div>
            <p className="text-muted" style={{ marginTop: 6 }}>These drive how GPT-4.1 ranks articles for you.</p>
          </div>

          <button type="submit" className="btn btn-primary" disabled={mutation.isPending}>
            {mutation.isPending ? <><span className="spinner" /> Saving...</> : <><Save size={15} /> Save Profile</>}
          </button>
        </form>
      </div>
    </Layout>
  );
}
