import { useState, type FormEvent } from 'react';
import type {
  BabyProfile,
  PrescriptionExtraction,
  PrescriptionStatus,
} from '@babycare/types';
import { ErrorState, LoadingState, PageHeader } from '../components/UI';
import { extractPrescription, reviewPrescription } from '../lib/api';

const badge: Record<PrescriptionStatus, string> = {
  pending_review: 'bg-amber-100 text-amber-800',
  reviewed: 'bg-emerald-100 text-emerald-800',
  flagged: 'bg-rose-100 text-rose-800',
};
export function PrescriptionsPage({ baby }: { baby: BabyProfile }) {
  const [file, setFile] = useState<File | null>(null);
  const [item, setItem] = useState<PrescriptionExtraction | null>(null);
  const [reviewer, setReviewer] = useState(false);
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  async function upload(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      setItem(await extractPrescription(baby.id, file));
    } catch (r) {
      setError(r instanceof Error ? r.message : 'Upload failed.');
    } finally {
      setLoading(false);
    }
  }
  async function review(status: 'reviewed' | 'flagged') {
    if (!item) return;
    setLoading(true);
    setError('');
    try {
      await reviewPrescription(item.id, 2, status, note);
      setItem({ ...item, status });
    } catch (r) {
      setError(r instanceof Error ? r.message : 'Review failed.');
    } finally {
      setLoading(false);
    }
  }
  return (
    <>
      <PageHeader eyebrow="Document assistant" title="Prescriptions">
        Upload an image or PDF for text extraction and professional review.
      </PageHeader>
      <div className="mb-5 flex justify-end">
        <label className="flex items-center gap-3 text-sm font-semibold">
          <span>Reviewer view</span>
          <input
            type="checkbox"
            checked={reviewer}
            onChange={(e) => setReviewer(e.target.checked)}
            className="h-5 w-5 accent-teal-600"
          />
        </label>
      </div>
      <form
        onSubmit={upload}
        className="rounded-3xl border-2 border-dashed border-stone-300 bg-white p-8 text-center"
      >
        <p className="font-bold">Drop in a prescription image or PDF</p>
        <p className="mt-1 text-sm text-slate-500">
          The result always requires pharmacist or doctor review.
        </p>
        <input
          required
          type="file"
          accept="image/*,.pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="mx-auto mt-5 block max-w-full text-sm"
        />
        <button
          disabled={!file || loading}
          className="mt-5 rounded-xl bg-teal-600 px-5 py-3 text-sm font-bold text-white disabled:opacity-40"
        >
          Extract text
        </button>
      </form>
      <div className="mt-6">
        {loading && <LoadingState label="Processing prescription…" />}
        {error && <ErrorState message={error} />}{' '}
        {item && (
          <section className="rounded-3xl border border-stone-200 bg-white p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="font-display text-xl font-bold">
                Extraction #{item.id}
              </h2>
              <span
                className={`rounded-full px-3 py-1 text-xs font-bold ${badge[item.status]}`}
              >
                {item.status.replace('_', ' ')}
              </span>
            </div>
            <p className="mt-3 rounded-xl bg-amber-50 p-3 text-xs text-amber-900">
              {item.aiDisclaimer}
            </p>
            <div className="mt-5 grid gap-5 sm:grid-cols-3">
              <ExtractList title="Medicine names" items={item.medicineNames} />
              <ExtractList title="Dosage text" items={item.dosageText} />
              <ExtractList title="Frequency text" items={item.frequencyText} />
            </div>
            {reviewer && item.status === 'pending_review' && (
              <div className="mt-6 border-t pt-5">
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="Required reviewer note"
                  className="w-full rounded-xl border p-3"
                />
                <div className="mt-3 flex gap-3">
                  <button
                    disabled={!note}
                    type="button"
                    onClick={() => review('reviewed')}
                    className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white disabled:opacity-40"
                  >
                    Mark reviewed
                  </button>
                  <button
                    disabled={!note}
                    type="button"
                    onClick={() => review('flagged')}
                    className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-bold text-white disabled:opacity-40"
                  >
                    Flag
                  </button>
                </div>
              </div>
            )}
          </section>
        )}
      </div>
    </>
  );
}
function ExtractList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3 className="text-sm font-bold">{title}</h3>
      <ul className="mt-2 space-y-1 text-sm text-slate-600">
        {items.length ? (
          items.map((x) => <li key={x}>{x}</li>)
        ) : (
          <li>None detected</li>
        )}
      </ul>
    </div>
  );
}
