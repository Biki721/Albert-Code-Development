import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Dashboard form state (mode, selections, schedule)
export const useDashboardFormStore = create(
  persist(
    (set) => ({
      // Core mode
      mode: 'REG', // 'REG' or 'ADH'

      // Regular mode selections
      selectedLanguages: [],
      selectedAccounts: [],
      selectedDomains: [],
      selectedModules: [],

      // Adhoc
      adhocType: '',

      // Options
      sharepointUpload: false,

      // Schedule
      scheduleDate: '', // YYYY-MM-DD
      scheduleTime: '', // HH:MM
      scheduleMode: 'now', // 'now' or 'later'

      // Setters
      setMode: (mode) => set({ mode }),
      setSelectedLanguages: (selectedLanguages) => set({ selectedLanguages }),
      setSelectedAccounts: (selectedAccounts) => set({ selectedAccounts }),
      setSelectedDomains: (selectedDomains) => set({ selectedDomains }),
      setSelectedModules: (selectedModules) => set({ selectedModules }),
      setAdhocType: (adhocType) => set({ adhocType }),
      setSharepointUpload: (sharepointUpload) => set({ sharepointUpload }),
      setScheduleDate: (scheduleDate) => set({ scheduleDate }),
      setScheduleTime: (scheduleTime) => set({ scheduleTime }),
      setScheduleMode: (scheduleMode) => set({ scheduleMode }),

      // Reset fields typically cleared after a run
      resetAfterRun: () =>
        set((state) => ({
          // Keep mode and languages so re-run is easy
          selectedAccounts: [],
          selectedDomains: [],
          selectedModules: [],
          adhocType: '',
          scheduleDate: '',
          scheduleTime: '',
          // Keep sharepointUpload and scheduleMode as-is
          sharepointUpload: state.sharepointUpload,
          scheduleMode: state.scheduleMode,
        })),
    }),
    {
      name: 'albert_dashboard_form',
    },
  ),
);
