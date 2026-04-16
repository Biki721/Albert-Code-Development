/**
 * Dark / light theme state management
 */
import { create } from 'zustand';

const applyTheme = (theme) => {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
  try {
    localStorage.setItem('albert_theme', theme);
  } catch {
    // ignore
  }
};

const getInitialTheme = () => {
  if (typeof window === 'undefined') return 'light';

  try {
    const stored = localStorage.getItem('albert_theme');
    if (stored === 'light' || stored === 'dark') return stored;
  } catch {
    // ignore
  }

  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  return prefersDark ? 'dark' : 'light';
};

export const useThemeStore = create((set) => ({
  theme: 'light',

  initTheme: () => {
    const initial = getInitialTheme();
    applyTheme(initial);
    set({ theme: initial });
  },

  setTheme: (theme) => {
    applyTheme(theme);
    set({ theme });
  },

  toggleTheme: () => set((state) => {
    const next = state.theme === 'light' ? 'dark' : 'light';
    applyTheme(next);
    return { theme: next };
  }),
}));
