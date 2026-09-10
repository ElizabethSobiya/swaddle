import { createContext, useContext } from 'react';

/** What the user picked. `system` follows the OS setting and keeps following it. */
export type ThemePreference = 'light' | 'dark' | 'system';
/** What is actually painted once `system` has been resolved. */
export type ResolvedTheme = 'light' | 'dark';

export const THEME_STORAGE_KEY = 'swaddle-theme';

export const themeOrder: ThemePreference[] = ['light', 'dark', 'system'];

export const themeLabels: Record<ThemePreference, string> = {
  light: 'Light',
  dark: 'Dark',
  system: 'System',
};

export const themeIcons: Record<ThemePreference, string> = {
  light: '☀',
  dark: '☾',
  system: '◐',
};

export function isThemePreference(value: unknown): value is ThemePreference {
  return value === 'light' || value === 'dark' || value === 'system';
}

/** Reads the stored preference, falling back to `system` for a first visit. */
export function readStoredTheme(): ThemePreference {
  try {
    const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
    return isThemePreference(stored) ? stored : 'system';
  } catch {
    // Private-mode or blocked storage: fall back to following the OS.
    return 'system';
  }
}

export function systemTheme(): ResolvedTheme {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
}

export function resolveTheme(preference: ThemePreference): ResolvedTheme {
  return preference === 'system' ? systemTheme() : preference;
}

/**
 * Paints the resolved theme. Kept free of React so the inline boot script in
 * index.html and the provider stay in agreement about what "dark" means.
 */
export function applyTheme(resolved: ResolvedTheme) {
  const root = document.documentElement;
  root.classList.toggle('dark', resolved === 'dark');
  root.style.colorScheme = resolved;
}

export type ThemeContextValue = {
  /** The user's choice, including `system`. */
  theme: ThemePreference;
  /** The theme currently painted. */
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: ThemePreference) => void;
  /** Advances light → dark → system → light. */
  cycleTheme: () => void;
};

export const ThemeContext = createContext<ThemeContextValue | null>(null);

export function useTheme(): ThemeContextValue {
  const value = useContext(ThemeContext);
  if (!value) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return value;
}
