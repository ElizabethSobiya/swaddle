import { themeIcons, themeLabels, useTheme } from '../lib/theme';

export function ThemeToggle({ className = '' }: { className?: string }) {
  const { theme, resolvedTheme, cycleTheme } = useTheme();
  const description =
    theme === 'system' ? `System (${resolvedTheme})` : themeLabels[theme];

  return (
    <button
      type="button"
      onClick={cycleTheme}
      title={`Theme: ${description}`}
      aria-label={`Theme: ${description}. Activate to change.`}
      className={`flex shrink-0 items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 py-2 text-xs font-bold text-slate-600 transition hover:bg-stone-50 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-white ${className}`}
    >
      <span aria-hidden="true" className="text-sm leading-none">
        {themeIcons[theme]}
      </span>
      {themeLabels[theme]}
    </button>
  );
}
