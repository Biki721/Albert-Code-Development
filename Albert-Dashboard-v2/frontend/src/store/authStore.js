/**
 * Authentication state management
 */
import { create } from 'zustand';
import { authAPI } from '../services/api';

export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('auth_token'),
  isAuthenticated: false,
  isLoading: false,
  lockStatus: null,

  // Initialize auth state
  initialize: async () => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      try {
        const user = await authAPI.getMe();
        set({ user, token, isAuthenticated: true });
      } catch (error) {
        localStorage.removeItem('auth_token');
        set({ user: null, token: null, isAuthenticated: false });
      }
    }
  },

  // Login action
  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const data = await authAPI.login(email, password);
      localStorage.setItem('auth_token', data.access_token);
      set({
        token: data.access_token,
        user: { email },
        isAuthenticated: true,
        isLoading: false,
      });
      return { success: true };
    } catch (error) {
      set({ isLoading: false });
      return {
        success: false,
        error: error.response?.data?.error || error.response?.data?.detail || 'Login failed',
      };
    }
  },

  // Logout action
  logout: async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      });
    }
  },

  // Check lock status
  checkLockStatus: async () => {
    try {
      const status = await authAPI.getStatus();
      set({ lockStatus: status });
      return status;
    } catch (error) {
      console.error('Failed to check lock status:', error);
      return null;
    }
  },
}));
