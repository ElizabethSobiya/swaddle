import type { ReactNode } from 'react';

import { ThemeToggle } from './ThemeToggle';

export type PageName =
  | 'Dashboard'
  | 'Symptom Check'
  | 'Prescriptions'
  | 'Shop'
  | 'Library'
  | 'Consult';

const pages: { name: PageName; icon: string }[] = [
  { name: 'Dashboard', icon: '⌂' },
  { name: 'Symptom Check', icon: '♡' },
  { name: 'Prescriptions', icon: '▤' },
  { name: 'Shop', icon: '◇' },
  { name: 'Library', icon: '▦' },
  { name: 'Consult', icon: '◷' },
];

export function AppShell({
  page,
  onNavigate,
  children,
}: {
  page: PageName;
  onNavigate: (page: PageName) => void;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-stone-50 text-slate-800 dark:bg-slate-950 dark:text-slate-200">
      <aside className="border-b border-stone-200 bg-white lg:fixed lg:inset-y-0 lg:left-0 lg:z-20 lg:h-screen lg:w-64 lg:overflow-y-auto lg:border-b-0 lg:border-r dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center gap-3 px-6 py-5">
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-teal-600 text-xl text-white dark:bg-teal-500 dark:text-slate-950">
            ♡
          </span>
          <div>
            <p className="font-display text-xl font-bold text-slate-900 dark:text-slate-50">
              Swaddle
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              AI care companion
            </p>
          </div>
          <ThemeToggle className="ml-auto lg:hidden" />
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3 lg:block lg:space-y-1">
          {pages.map(({ name, icon }) => (
            <button
              key={name}
              onClick={() => onNavigate(name)}
              className={`flex shrink-0 items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition lg:w-full ${page === name ? 'bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300' : 'text-slate-500 hover:bg-stone-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100'}`}
            >
              <span className="text-lg">{icon}</span>
              {name}
            </button>
          ))}
        </nav>
        <div className="hidden px-3 pb-5 lg:block">
          <ThemeToggle className="w-full justify-center" />
        </div>
      </aside>
      <main className="min-w-0 p-5 sm:p-8 lg:ml-64 lg:p-10">{children}</main>
    </div>
  );
}
