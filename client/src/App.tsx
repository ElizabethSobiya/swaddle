import { useState } from 'react';

import type { BabyProfile } from '@swaddle/types';

import { AppShell, type PageName } from './components/AppShell';
import { ConsultPage } from './pages/ConsultPage';
import { DashboardPage } from './pages/DashboardPage';
import { LibraryPage } from './pages/LibraryPage';
import { PrescriptionsPage } from './pages/PrescriptionsPage';
import { ShopPage } from './pages/ShopPage';
import { SymptomCheckPage } from './pages/SymptomCheckPage';

type DemoBaby = BabyProfile & { ageMonths: number };

function birthDateMonthsAgo(months: number) {
  const date = new Date();
  date.setMonth(date.getMonth() - months);
  return date.toISOString().slice(0, 10);
}

const babies: DemoBaby[] = [
  {
    id: 1,
    name: 'Aarav',
    birthDate: birthDateMonthsAgo(2),
    sex: 'male',
    ageMonths: 2,
  },
  {
    id: 2,
    name: 'Maya',
    birthDate: birthDateMonthsAgo(8),
    sex: 'female',
    ageMonths: 8,
  },
  {
    id: 3,
    name: 'Noah',
    birthDate: birthDateMonthsAgo(18),
    sex: 'male',
    ageMonths: 18,
  },
];

export function App() {
  const [page, setPage] = useState<PageName>('Dashboard');
  const [babyId, setBabyId] = useState(babies[0].id);
  const baby = babies.find((profile) => profile.id === babyId) ?? babies[0];
  const ageMonths = baby.ageMonths;
  const pages = {
    Dashboard: (
      <DashboardPage baby={baby} ageMonths={ageMonths} onNavigate={setPage} />
    ),
    'Symptom Check': <SymptomCheckPage baby={baby} ageMonths={ageMonths} />,
    Prescriptions: <PrescriptionsPage baby={baby} />,
    Shop: <ShopPage baby={baby} />,
    Library: <LibraryPage ageMonths={ageMonths} />,
    Consult: <ConsultPage />,
  } satisfies Record<PageName, React.ReactNode>;

  return (
    <AppShell page={page} onNavigate={setPage}>
      <section className="mb-7 flex flex-wrap items-center gap-3 rounded-2xl border border-stone-200 bg-white p-3 shadow-sm">
        <p className="px-2 text-xs font-bold uppercase tracking-widest text-slate-500">
          Demo baby
        </p>
        {babies.map((profile) => (
          <button
            key={profile.id}
            type="button"
            onClick={() => setBabyId(profile.id)}
            className={`rounded-xl px-4 py-2 text-left text-sm transition ${profile.id === baby.id ? 'bg-teal-600 text-white shadow-sm' : 'bg-stone-50 text-slate-600 hover:bg-teal-50 hover:text-teal-700'}`}
          >
            <span className="font-bold">{profile.name}</span>
            <span className="ml-2 opacity-80">{profile.ageMonths} months</span>
          </button>
        ))}
        <p className="ml-auto hidden text-xs text-slate-500 md:block">
          Shop and Library adapt to the selected age
        </p>
      </section>
      {pages[page]}
    </AppShell>
  );
}
