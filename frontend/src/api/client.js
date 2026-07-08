import axios from 'axios';
import { useAuthStore } from '../store/auth';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({ baseURL: API_BASE });

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(err);
  }
);

// ── Auth ─────────────────────────────────────────────────────
export const register = (data) => api.post('/auth/register', data);
export const login = (email, password) =>
  api.post('/auth/login', new URLSearchParams({ username: email, password }));

// ── User ─────────────────────────────────────────────────────
export const getMe = () => api.get('/users/me');
export const updateProfile = (data) => api.put('/users/me/profile', data);
export const updateEmailSettings = (data) => api.put('/users/me/settings', data);

// ── Sources ──────────────────────────────────────────────────
export const getSources = () => api.get('/sources');
export const addSource = (data) => api.post('/sources', data);
export const deleteSource = (id) => api.delete(`/sources/${id}`);

// ── Digests ──────────────────────────────────────────────────
export const getDigests = (limit = 50) => api.get('/digests', { params: { limit } });

// ── Pipeline ─────────────────────────────────────────────────
export const triggerPipeline = () => api.post('/pipeline/run');
export const reschedulePipeline = () => api.post('/pipeline/reschedule');
