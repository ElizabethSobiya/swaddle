import { useCallback, useEffect, useState } from 'react';
import type { BabyProfile, ProductRecommendation } from '@swaddle/types';
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/UI';
import { getProducts } from '../lib/api';

const categoryStyles: Record<string, { badge: string; accent: string }> = {
  pharmacy: {
    badge:
      'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-200',
    accent: 'border-t-emerald-400 dark:border-t-emerald-500',
  },
  toy: {
    badge:
      'bg-fuchsia-100 text-fuchsia-800 dark:bg-fuchsia-950/60 dark:text-fuchsia-200',
    accent: 'border-t-fuchsia-400 dark:border-t-fuchsia-500',
  },
  supplies: {
    badge: 'bg-sky-100 text-sky-800 dark:bg-sky-950/60 dark:text-sky-200',
    accent: 'border-t-sky-400 dark:border-t-sky-500',
  },
  feeding: {
    badge:
      'bg-orange-100 text-orange-800 dark:bg-orange-950/60 dark:text-orange-200',
    accent: 'border-t-orange-400 dark:border-t-orange-500',
  },
  sleep: {
    badge:
      'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-200',
    accent: 'border-t-indigo-400 dark:border-t-indigo-500',
  },
  diapering: {
    badge: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-950/60 dark:text-cyan-200',
    accent: 'border-t-cyan-400 dark:border-t-cyan-500',
  },
  bath: {
    badge: 'bg-sky-100 text-sky-800 dark:bg-sky-950/60 dark:text-sky-200',
    accent: 'border-t-sky-400 dark:border-t-sky-500',
  },
  teething: {
    badge: 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-200',
    accent: 'border-t-rose-400 dark:border-t-rose-500',
  },
  health: {
    badge:
      'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-200',
    accent: 'border-t-emerald-400 dark:border-t-emerald-500',
  },
  grooming: {
    badge:
      'bg-violet-100 text-violet-800 dark:bg-violet-950/60 dark:text-violet-200',
    accent: 'border-t-violet-400 dark:border-t-violet-500',
  },
  play: {
    badge:
      'bg-fuchsia-100 text-fuchsia-800 dark:bg-fuchsia-950/60 dark:text-fuchsia-200',
    accent: 'border-t-fuchsia-400 dark:border-t-fuchsia-500',
  },
  safety: {
    badge: 'bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-200',
    accent: 'border-t-red-400 dark:border-t-red-500',
  },
  learning: {
    badge:
      'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-200',
    accent: 'border-t-amber-400 dark:border-t-amber-500',
  },
  travel: {
    badge: 'bg-lime-100 text-lime-800 dark:bg-lime-950/60 dark:text-lime-200',
    accent: 'border-t-lime-400 dark:border-t-lime-500',
  },
};

const defaultCategoryStyle = {
  badge: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200',
  accent: 'border-t-slate-400 dark:border-t-slate-500',
};

export function ShopPage({ baby }: { baby: BabyProfile }) {
  const [items, setItems] = useState<ProductRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      // Load the deterministic ranking immediately. AI re-ranking remains an
      // explicit API demo option and must not block the product grid.
      setItems(await getProducts(baby.id, false));
    } catch (r) {
      setError(
        r instanceof Error ? r.message : 'Could not load recommendations.',
      );
    } finally {
      setLoading(false);
    }
  }, [baby.id]);
  useEffect(() => {
    void load();
  }, [load]);
  return (
    <>
      <PageHeader eyebrow="Age-aware picks" title={`Shop for ${baby.name}`}>
        Recommendations combine age fit with relevant recent care context.
      </PageHeader>
      {loading ? (
        <LoadingState label="Finding suitable products…" />
      ) : error ? (
        <ErrorState message={error} retry={() => void load()} />
      ) : items.length === 0 ? (
        <EmptyState>No age-matched products are available yet.</EmptyState>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {items.map((product) => {
            const colors =
              categoryStyles[product.category.toLowerCase()] ??
              defaultCategoryStyle;
            return (
              <article
                key={product.id}
                className={`flex flex-col rounded-3xl border border-t-4 border-stone-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900 ${colors.accent}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-bold capitalize ${colors.badge}`}
                  >
                    {product.category}
                  </span>
                  <span className="font-display text-lg font-bold">
                    ${Number(product.price).toFixed(2)}
                  </span>
                </div>
                <h2 className="font-display mt-5 text-xl font-bold">
                  {product.name}
                </h2>
                <div className="mt-3 flex flex-wrap gap-2">
                  {product.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs text-teal-700 dark:text-teal-400"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
                {(product.explanation || product.matchedTags.length > 0) && (
                  <p className="mt-5 flex-1 rounded-2xl bg-teal-50 p-4 text-sm leading-6 text-teal-900 dark:bg-teal-950/50 dark:text-teal-100">
                    {product.explanation ??
                      `Matches: ${product.matchedTags.join(', ')}.`}
                  </p>
                )}
                <p className="mt-4 text-xs text-slate-400 dark:text-slate-500">
                  Ages {product.ageMinMonths}–{product.ageMaxMonths} months
                </p>
              </article>
            );
          })}
        </div>
      )}
    </>
  );
}
