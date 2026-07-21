import { useState } from 'react';

import type { BabyProfile } from '@babycare/types';

import { AppShell, type PageName } from './components/AppShell';
import { ConsultPage } from './pages/ConsultPage';
import { DashboardPage } from './pages/DashboardPage';
import { LibraryPage } from './pages/LibraryPage';
import { PrescriptionsPage } from './pages/PrescriptionsPage';
import { ShopPage } from './pages/ShopPage';
import { SymptomCheckPage } from './pages/SymptomCheckPage';

const baby: BabyProfile = {
  id: 1,
  name: 'Maya',
  birthDate: '2026-01-18',
  sex: 'female',
};

export function App() {
  const [page, setPage] = useState<PageName>('Dashboard');
  const ageMonths = Math.max(
    0,
    Math.floor(
      (Date.now() - new Date(baby.birthDate).getTime()) / 2_629_746_000,
    ),
  );
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
      {pages[page]}
    </AppShell>
  );
}
