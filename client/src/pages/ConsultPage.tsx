import { useCallback, useEffect, useState } from 'react';
import type { BookingConfirmation, ConsultationSlot } from '@babycare/types';
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/UI';
import { bookSlot, getSlots } from '../lib/api';

export function ConsultPage() {
  const [slots, setSlots] = useState<ConsultationSlot[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [confirmation, setConfirmation] = useState<BookingConfirmation | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setSlots(await getSlots());
    } catch (r) {
      setError(r instanceof Error ? r.message : 'Could not load slots.');
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    void load();
  }, [load]);
  async function book() {
    if (selected === null) return;
    setBooking(true);
    setError('');
    try {
      const result = await bookSlot(selected);
      setConfirmation(result);
      setSlots((current) =>
        current.map((slot) =>
          slot.id === selected ? { ...slot, status: 'booked' } : slot,
        ),
      );
    } catch (r) {
      setError(r instanceof Error ? r.message : 'Could not book this slot.');
    } finally {
      setBooking(false);
    }
  }
  return (
    <>
      <PageHeader eyebrow="Scheduled care" title="Book a consultation">
        Choose an available pediatrician time. Live video is not included in
        this demo.
      </PageHeader>
      {confirmation ? (
        <section className="mx-auto max-w-xl rounded-[2rem] border border-emerald-200 bg-emerald-50 p-8 text-center">
          <span className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-emerald-600 text-2xl text-white">
            ✓
          </span>
          <h2 className="font-display mt-5 text-2xl font-bold text-emerald-950">
            Booking confirmed
          </h2>
          <p className="mt-2 text-emerald-800">
            {confirmation.pediatricianName}
          </p>
          <p className="font-bold text-emerald-900">
            {new Date(confirmation.slotTime).toLocaleString()}
          </p>
          <p className="mt-4 text-xs font-bold tracking-widest text-emerald-700">
            {confirmation.confirmationId}
          </p>
          <button
            onClick={() => {
              setConfirmation(null);
              setSelected(null);
            }}
            className="mt-6 text-sm font-bold text-emerald-800 underline"
          >
            Book another slot
          </button>
        </section>
      ) : loading ? (
        <LoadingState label="Checking available times…" />
      ) : error && slots.length === 0 ? (
        <ErrorState message={error} retry={() => void load()} />
      ) : slots.length === 0 ? (
        <EmptyState>No consultation slots have been scheduled.</EmptyState>
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {slots.map((slot) => (
              <button
                key={slot.id}
                disabled={slot.status === 'booked'}
                onClick={() => setSelected(slot.id)}
                className={`rounded-2xl border p-5 text-left transition disabled:cursor-not-allowed disabled:opacity-45 ${selected === slot.id ? 'border-teal-500 bg-teal-50 ring-2 ring-teal-100' : 'border-stone-200 bg-white'}`}
              >
                <p className="font-bold">{slot.pediatricianName}</p>
                <p className="mt-2 text-sm text-slate-500">
                  {new Date(slot.slotTime).toLocaleString()}
                </p>
                <span
                  className={`mt-3 inline-block rounded-full px-2 py-1 text-xs font-bold ${slot.status === 'available' ? 'bg-emerald-100 text-emerald-700' : 'bg-stone-100 text-slate-500'}`}
                >
                  {slot.status}
                </span>
              </button>
            ))}
          </div>
          {error && (
            <div className="mt-5">
              <ErrorState message={error} />
            </div>
          )}
          <div className="mt-6 flex justify-end">
            <button
              disabled={selected === null || booking}
              onClick={() => void book()}
              className="rounded-xl bg-teal-600 px-6 py-3 text-sm font-bold text-white disabled:opacity-40"
            >
              {booking ? 'Booking…' : 'Confirm booking'}
            </button>
          </div>
        </>
      )}
    </>
  );
}
