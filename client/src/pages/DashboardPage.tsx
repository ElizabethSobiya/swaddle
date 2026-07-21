import type { BabyProfile } from '@babycare/types';
import type { PageName } from '../components/AppShell';
import { PageHeader } from '../components/UI';

const actions: {
  page: PageName;
  title: string;
  copy: string;
  color: string;
}[] = [
  {
    page: 'Symptom Check',
    title: 'Check symptoms',
    copy: 'Get careful, non-diagnostic guidance',
    color: 'bg-rose-50 text-rose-700',
  },
  {
    page: 'Prescriptions',
    title: 'Scan prescription',
    copy: 'Extract text for professional review',
    color: 'bg-amber-50 text-amber-700',
  },
  {
    page: 'Consult',
    title: 'Book a consult',
    copy: 'Choose an available pediatrician slot',
    color: 'bg-sky-50 text-sky-700',
  },
];

export function DashboardPage({
  baby,
  ageMonths,
  onNavigate,
}: {
  baby: BabyProfile;
  ageMonths: number;
  onNavigate: (page: PageName) => void;
}) {
  return (
    <>
      <PageHeader
        eyebrow="Today’s care overview"
        title={`Good morning, ${baby.name}’s family`}
      >
        A calm place for everyday care, learning, and trusted next steps.
      </PageHeader>
      <section className="overflow-hidden rounded-[2rem] bg-gradient-to-br from-teal-700 to-teal-500 p-7 text-white shadow-lg shadow-teal-900/10 sm:flex sm:items-center sm:justify-between sm:p-9">
        <div>
          <p className="text-sm font-semibold text-teal-100">Baby profile</p>
          <h2 className="font-display mt-2 text-4xl font-bold">{baby.name}</h2>
          <p className="mt-2 text-teal-50 capitalize">
            {baby.sex} · Born {new Date(baby.birthDate).toLocaleDateString()}
          </p>
        </div>
        <div className="mt-6 rounded-3xl bg-white/15 p-5 backdrop-blur sm:mt-0 sm:text-right">
          <p className="text-sm text-teal-100">Current age</p>
          <p className="font-display text-3xl font-bold">{ageMonths} months</p>
          <p className="text-xs text-teal-100">
            Content and products adapt to this age
          </p>
        </div>
      </section>
      <h2 className="font-display mb-4 mt-9 text-xl font-bold">
        What would you like to do?
      </h2>
      <div className="grid gap-4 md:grid-cols-3">
        {actions.map((action) => (
          <button
            key={action.page}
            onClick={() => onNavigate(action.page)}
            className="rounded-3xl border border-stone-200 bg-white p-6 text-left shadow-sm transition hover:-translate-y-1 hover:shadow-md"
          >
            <span
              className={`inline-block rounded-xl px-3 py-1 text-xs font-bold ${action.color}`}
            >
              {action.page}
            </span>
            <h3 className="mt-5 text-lg font-bold">{action.title}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              {action.copy}
            </p>
            <span className="mt-5 block text-teal-600">Explore →</span>
          </button>
        ))}
      </div>
    </>
  );
}
