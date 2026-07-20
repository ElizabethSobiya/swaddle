import type { BabyProfile } from '@babycare/types';

const exampleProfile: BabyProfile = {
  id: 'demo',
  name: 'Your little one',
  birthDate: '2026-01-01',
};

export function App() {
  return (
    <main className="grid min-h-screen place-items-center bg-slate-50 p-6">
      <section className="max-w-xl rounded-3xl bg-white p-10 text-center shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-widest text-teal-600">
          BabyCare AI
        </p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-900">
          Care guidance, thoughtfully organized.
        </h1>
        <p className="mt-4 text-slate-600">
          The platform is ready for {exampleProfile.name}.
        </p>
      </section>
    </main>
  );
}

