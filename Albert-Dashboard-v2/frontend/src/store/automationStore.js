/**
 * Automation state management
 */
import { create } from 'zustand';
import { automationAPI, resourcesAPI } from '../services/api';

export const useAutomationStore = create((set, get) => ({
  // Resources
  languages: [],
  accounts: [],
  modules: null,
  
  // Jobs
  jobs: [],
  runningJob: null,
  systemStatus: null,
  
  // Loading states
  isLoadingResources: false,
  isLoadingJobs: false,
  
  // Polling interval
  pollingInterval: null,

  // Load languages
  loadLanguages: async () => {
    try {
      const data = await resourcesAPI.getLanguages();
      set({ languages: data.languages || [] });
    } catch (error) {
      console.error('Failed to load languages:', error);
    }
  },

  // Load accounts
  loadAccounts: async (language = null) => {
    set({ isLoadingResources: true });
    try {
      const accounts = await resourcesAPI.getAccounts(language);
      set({ accounts, isLoadingResources: false });
    } catch (error) {
      console.error('Failed to load accounts:', error);
      set({ isLoadingResources: false });
    }
  },

  // Load modules
  loadModules: async () => {
    try {
      const modules = await resourcesAPI.getModules();
      set({ modules });
    } catch (error) {
      console.error('Failed to load modules:', error);
    }
  },

  // Submit automation job
  submitJob: async (request) => {
    try {
      const response = await automationAPI.runAutomation(request);
      await get().loadJobs();
      return { success: true, data: response };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || error.response?.data?.detail || 'Failed to submit job',
      };
    }
  },

  // Load all jobs
  loadJobs: async () => {
    set({ isLoadingJobs: true });
    try {
      const jobs = await automationAPI.getJobs();
      set({ jobs, isLoadingJobs: false });
    } catch (error) {
      console.error('Failed to load jobs:', error);
      set({ isLoadingJobs: false });
    }
  },

  // Get running job
  loadRunningJob: async () => {
    try {
      const runningJob = await automationAPI.getRunningJob();
      set({ runningJob });
    } catch (error) {
      console.error('Failed to load running job:', error);
    }
  },

  // Load system status
  loadSystemStatus: async () => {
    try {
      const systemStatus = await automationAPI.getSystemStatus();
      set({ systemStatus });
    } catch (error) {
      console.error('Failed to load system status:', error);
    }
  },

  // Stop automation
  stopAutomation: async (jobId = null) => {
    try {
      await automationAPI.stopAutomation(jobId);
      await get().loadJobs();
      await get().loadRunningJob();
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to stop automation',
      };
    }
  },

  // Start polling for updates
  startPolling: () => {
    const interval = setInterval(async () => {
      await get().loadRunningJob();
      await get().loadSystemStatus();
      await get().loadJobs();
    }, 5000); // Poll every 5 seconds
    
    set({ pollingInterval: interval });
  },

  // Stop polling
  stopPolling: () => {
    const { pollingInterval } = get();
    if (pollingInterval) {
      clearInterval(pollingInterval);
      set({ pollingInterval: null });
    }
  },
}));
