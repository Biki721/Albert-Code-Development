import { Sun, MoonStar } from 'lucide-react';
import { useThemeStore } from '../store/themeStore';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useThemeStore();
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-gray-300 dark:border-slate-700 bg-white/80 dark:bg-slate-900/80 text-xs font-medium text-gray-700 dark:text-slate-200 shadow-sm hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
      aria-label="Toggle dark mode"
    >
      {isDark ? (
        <>
          <Sun className="w-4 h-4 text-yellow-400" />
          <span>Light mode</span>
        </>
      ) : (
        <>
          <MoonStar className="w-4 h-4 text-slate-700" />
          <span>Dark mode</span>
        </>
      )}
    </button>
  );
}
