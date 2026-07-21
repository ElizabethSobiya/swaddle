import type { ReactNode } from 'react';

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
    <div className="min-h-screen bg-stone-50 text-slate-800">
      <aside className="border-b border-stone-200 bg-white lg:fixed lg:inset-y-0 lg:left-0 lg:z-20 lg:h-screen lg:w-64 lg:overflow-y-auto lg:border-b-0 lg:border-r">
        <div className="flex items-center gap-3 px-6 py-5">
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-teal-600 text-xl text-white">
            ♡
          </span>
          <div>
            <p className="font-display text-xl font-bold text-slate-900">
              Swaddle
            </p>
            <p className="text-xs text-slate-500">AI care companion</p>
          </div>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3 lg:block lg:space-y-1">
          {pages.map(({ name, icon }) => (
            <button
              key={name}
              onClick={() => onNavigate(name)}
              className={`flex shrink-0 items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition lg:w-full ${page === name ? 'bg-teal-50 text-teal-700' : 'text-slate-500 hover:bg-stone-50 hover:text-slate-900'}`}
            >
              <span className="text-lg">{icon}</span>
              {name}
            </button>
          ))}
        </nav>
      </aside>
      <main className="min-w-0 p-5 sm:p-8 lg:ml-64 lg:p-10">{children}</main>
    </div>
  );
}
