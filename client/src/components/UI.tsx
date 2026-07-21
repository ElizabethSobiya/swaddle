import type { ReactNode } from 'react';

export function PageHeader({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <header className="mb-8">
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-600">
        {eyebrow}
      </p>
      <h1 className="font-display mt-2 text-3xl font-bold text-slate-900 sm:text-4xl">
        {title}
      </h1>
      <p className="mt-2 max-w-2xl text-slate-500">{children}</p>
    </header>
  );
}

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="grid min-h-48 place-items-center rounded-3xl border border-stone-200 bg-white">
      <div className="text-center">
        <span className="mx-auto block h-8 w-8 animate-spin rounded-full border-4 border-teal-100 border-t-teal-600" />
        <p className="mt-3 text-sm text-slate-500">{label}</p>
      </div>
    </div>
  );
}

export function ErrorState({
  message,
  retry,
}: {
  message: string;
  retry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="rounded-2xl border border-rose-200 bg-rose-50 p-5 text-rose-800"
    >
      <p className="font-semibold">Something went wrong</p>
      <p className="mt-1 text-sm">{message}</p>
      {retry && (
        <button onClick={retry} className="mt-3 text-sm font-bold underline">
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-3xl border border-dashed border-stone-300 bg-white p-10 text-center text-sm text-slate-500">
      {children}
    </div>
  );
}
