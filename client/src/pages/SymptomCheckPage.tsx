import { useState, type FormEvent } from 'react';
import type { BabyProfile, SymptomCheckResult } from '@babycare/types';
import { ErrorState, LoadingState, PageHeader } from '../components/UI';
import { checkSymptoms } from '../lib/api';

const alertStyles = {
  low: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  medium: 'bg-amber-50 text-amber-800 border-amber-200',
  high: 'bg-rose-50 text-rose-800 border-rose-200',
};

export function SymptomCheckPage({
  baby,
  ageMonths,
}: {
  baby: BabyProfile;
  ageMonths: number;
}) {
  const [symptoms, setSymptoms] = useState('');
  const [result, setResult] = useState<SymptomCheckResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      setResult(await checkSymptoms(baby.id, ageMonths, symptoms));
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : 'Unable to check symptoms.',
      );
    } finally {
      setLoading(false);
    }
  }
  return (
    <>
      <PageHeader eyebrow="AI care assistant" title="Symptom check">
        Describe what you notice. This tool supports—not replaces—professional
        medical care.
      </PageHeader>
      <form
        onSubmit={submit}
        className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm"
      >
        <label htmlFor="symptoms" className="text-sm font-bold">
          What symptoms is {baby.name} experiencing?
        </label>
        <textarea
          id="symptoms"
          required
          minLength={3}
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          placeholder="For example: mild cough since yesterday, feeding normally…"
          className="mt-3 min-h-36 w-full rounded-2xl border border-stone-200 bg-stone-50 p-4 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
        />
        <div className="mt-4 flex items-center justify-between gap-4">
          <p className="text-xs text-slate-400">
            Age supplied: {ageMonths} months
          </p>
          <button
            disabled={loading}
            className="rounded-xl bg-teal-600 px-5 py-3 text-sm font-bold text-white disabled:opacity-50"
          >
            Check symptoms
          </button>
        </div>
      </form>
      <div className="mt-6">
        {loading && <LoadingState label="Reviewing symptoms carefully…" />}
        {error && <ErrorState message={error} />}{' '}
        {result && (
          <div className="space-y-4">
            <div
              className={`rounded-2xl border p-5 ${alertStyles[result.alertLevel]}`}
            >
              <p className="text-xs font-bold uppercase tracking-widest">
                {result.alertLevel} alert level
              </p>
              <p className="mt-1 text-sm">{result.disclaimer}</p>
            </div>
            <div className="grid gap-4 lg:grid-cols-3">
              <ResponseCard
                title="Possible general causes"
                items={result.possibleCauses}
              />
              <ResponseCard title="Home care" items={result.homeCare} />
              <ResponseCard
                title="See a doctor now if…"
                items={result.redFlags}
              />
            </div>
          </div>
        )}
      </div>
    </>
  );
}

function ResponseCard({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="rounded-3xl border border-stone-200 bg-white p-6">
      <h2 className="font-display text-lg font-bold">{title}</h2>
      <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="text-teal-500">•</span>
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}
