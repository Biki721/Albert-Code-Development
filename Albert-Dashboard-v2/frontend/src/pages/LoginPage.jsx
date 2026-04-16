import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, AlertCircle, Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import ThemeToggle from '../components/ThemeToggle';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const { login, isLoading, checkLockStatus } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    // Check lock status on mount
    checkLockStatus();
  }, [checkLockStatus]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }

    const result = await login(email, password);
    
    if (result.success) {
      toast.success('Login successful!');
      navigate('/dashboard');
    } else {
      setError(result.error);
      toast.error(result.error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 dark:from-slate-950 dark:via-black dark:to-slate-950 p-4">
      <div className="w-full max-w-md">
        {/* Top bar with HPE logo + theme toggle */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            {/* Simple HPE-style logo */}
            <div className="flex items-center justify-center">
              <div className="h-5 w-14 border-4 border-hpe-green rounded-sm bg-transparent" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold tracking-wide text-slate-100">
                Hewlett Packard Enterprise
              </span>
              <span className="text-xs text-slate-300">
                Albert Automation Dashboard
              </span>
            </div>
          </div>
          <ThemeToggle />
        </div>

        {/* Hero / Title */}
        <div className="text-left mb-6">
          <h1 className="text-3xl font-bold text-slate-50 mb-1">
            Sign in to Albert
          </h1>
          <p className="text-slate-300 text-sm">
            Secure access to the automation control plane.
          </p>
        </div>

        {/* Login Card */}
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field pl-10"
                  placeholder="your.email@hpe.com"
                  disabled={isLoading}
                  autoFocus
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field pl-10"
                  placeholder="••••••••"
                  disabled={isLoading}
                />
              </div>
            </div>

            {error && (
              <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Logging in...
                </>
              ) : (
                'Login'
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Note: Only one user can access the dashboard at a time.
              <br />
              Default credentials: admin@hpe.com / Admin@123
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-gray-600 mt-6">
          HPE Internal Tool - Confidential
        </p>
      </div>
    </div>
  );
}
