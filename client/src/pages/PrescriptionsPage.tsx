import { useState, type FormEvent } from 'react';
import type {
  BabyProfile,
  PrescriptionExtraction,
  PrescriptionStatus,
} from '@swaddle/types';
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
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          setFile(event.dataTransfer.files?.[0] ?? null);
        }}
        className="rounded-3xl border-2 border-dashed border-stone-300 bg-white p-8 text-center"
      >
        <span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-teal-50 text-teal-700">
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            className="h-7 w-7"
          >
            <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5" />
            <path d="M5 13v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5" />
          </svg>
        </span>
        <p className="mt-4 font-bold">Drop in a prescription image or PDF</p>
        <p className="mt-1 text-sm text-slate-500">
          The result always requires pharmacist or doctor review.
        </p>
        <input
          id="prescription-file"
          required
          type="file"
          accept="image/*,.pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="sr-only"
        />
        <label
          htmlFor="prescription-file"
          className="mt-5 inline-flex cursor-pointer items-center gap-2 rounded-xl border border-teal-200 bg-teal-50 px-5 py-3 text-sm font-bold text-teal-800 transition hover:border-teal-300 hover:bg-teal-100 focus-within:ring-2 focus-within:ring-teal-200"
        >
          <span aria-hidden="true">＋</span>
          {file ? 'Browse another file' : 'Browse files'}
        </label>
        {file && (
          <div className="mx-auto mt-4 flex max-w-md items-center justify-between gap-3 rounded-xl bg-stone-50 px-4 py-3 text-left">
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-slate-700">
                {file.name}
              </p>
              <p className="text-xs text-slate-400">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              type="button"
              onClick={() => setFile(null)}
              aria-label="Remove selected file"
              className="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-slate-400 hover:bg-white hover:text-rose-600"
            >
              ×
            </button>
          </div>
        )}
        <button
          disabled={!file || loading}
          className="mx-auto mt-7 block rounded-xl bg-teal-600 px-5 py-3 text-sm font-bold text-white disabled:opacity-40"
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
