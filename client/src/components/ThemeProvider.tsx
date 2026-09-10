import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

import {
  applyTheme,
  readStoredTheme,
  resolveTheme,
  systemTheme,
  ThemeContext,
  THEME_STORAGE_KEY,
  themeOrder,
  type ResolvedTheme,
  type ThemePreference,
} from '../lib/theme';

export function ThemeProvider({ children }: { children: ReactNode }) {
  // The inline boot script in index.html has already painted this value, so
  // seeding from the same source keeps the first render flash-free.
  const [theme, setThemeState] = useState<ThemePreference>(readStoredTheme);
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>(() =>
    resolveTheme(readStoredTheme()),
  );

  useEffect(() => {
    const resolved = resolveTheme(theme);
    setResolvedTheme(resolved);
    applyTheme(resolved);
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
      // Storage is unavailable; the theme still applies for this session.
    }
  }, [theme]);

  // Only `system` tracks the OS, so an explicit choice is never overridden.
  useEffect(() => {
    if (theme !== 'system') return;
    const query = window.matchMedia('(prefers-color-scheme: dark)');
    const sync = () => {
      const resolved = systemTheme();
      setResolvedTheme(resolved);
      applyTheme(resolved);
    };
    query.addEventListener('change', sync);
    return () => query.removeEventListener('change', sync);
  }, [theme]);

  const cycleTheme = useCallback(() => {
    setThemeState((current) => {
      const next = themeOrder.indexOf(current) + 1;
      return themeOrder[next % themeOrder.length];
    });
  }, []);

  const value = useMemo(
    () => ({ theme, resolvedTheme, setTheme: setThemeState, cycleTheme }),
    [theme, resolvedTheme, cycleTheme],
  );

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}
