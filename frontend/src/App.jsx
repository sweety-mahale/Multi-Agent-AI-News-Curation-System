import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProtectedRoute } from './components/ProtectedRoute';
import Landing  from './pages/Landing';
import Login    from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Digests  from './pages/Digests';
import Profile  from './pages/settings/Profile';
import Sources  from './pages/settings/Sources';
import Email    from './pages/settings/Email';

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 1000 * 60, retry: 1 } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/"         element={<Landing />} />
          <Route path="/login"    element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected */}
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/digests"   element={<ProtectedRoute><Digests /></ProtectedRoute>} />
          <Route path="/settings/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/settings/sources" element={<ProtectedRoute><Sources /></ProtectedRoute>} />
          <Route path="/settings/email"   element={<ProtectedRoute><Email /></ProtectedRoute>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
