/**
 * API service for Albert Dashboard
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Authentication API
// ============================================================================

export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/api/auth/logout');
    return response.data;
  },

  getStatus: async () => {
    const response = await api.get('/api/auth/status');
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

// ============================================================================
// Accounts and Modules API
// ============================================================================

export const resourcesAPI = {
  getLanguages: async () => {
    const response = await api.get('/api/languages');
    return response.data;
  },

  getAccounts: async (language = null) => {
    const params = language ? { language } : {};
    const response = await api.get('/api/accounts', { params });
    return response.data;
  },

  getModules: async () => {
    const response = await api.get('/api/modules');
    return response.data;
  },
};

// ============================================================================
// Automation API
// ============================================================================

export const automationAPI = {
  runAutomation: async (request) => {
    const response = await api.post('/api/automation/run', request);
    return response.data;
  },

  getJobs: async () => {
    const response = await api.get('/api/automation/jobs');
    return response.data;
  },

  getJob: async (jobId) => {
    const response = await api.get(`/api/automation/job/${jobId}`);
    return response.data;
  },

  getRunningJob: async () => {
    const response = await api.get('/api/automation/running');
    return response.data;
  },

  stopAutomation: async (jobId = null) => {
    const response = await api.post('/api/automation/stop', { job_id: jobId });
    return response.data;
  },

  getSystemStatus: async () => {
    const response = await api.get('/api/system/status');
    return response.data;
  },
};

// ============================================================================
// Fixers and Adhoc Word Table API
// ============================================================================

export const fixersAPI = {
  getWorkbook: async () => {
    const response = await api.get('/api/fixers');
    return response.data;
  },

  saveWorkbook: async (workbook) => {
    const response = await api.post('/api/fixers', workbook);
    return response.data;
  },
};

export const adhocWordsAPI = {
  getTable: async () => {
    const response = await api.get('/api/adhoc/words');
    return response.data;
  },

  saveTable: async (table) => {
    const response = await api.post('/api/adhoc/words', table);
    return response.data;
  },
};

export const adhocLinksAPI = {
  getTable: async () => {
    const response = await api.get('/api/adhoc/links');
    return response.data;
  },

  saveTable: async (table) => {
    const response = await api.post('/api/adhoc/links', table);
    return response.data;
  },
};

export default api;
