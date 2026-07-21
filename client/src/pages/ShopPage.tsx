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
    badge: 'bg-emerald-100 text-emerald-800',
    accent: 'border-t-emerald-400',
  },
  toy: {
    badge: 'bg-fuchsia-100 text-fuchsia-800',
    accent: 'border-t-fuchsia-400',
  },
  supplies: {
    badge: 'bg-sky-100 text-sky-800',
    accent: 'border-t-sky-400',
  },
  feeding: {
    badge: 'bg-orange-100 text-orange-800',
    accent: 'border-t-orange-400',
  },
  sleep: {
    badge: 'bg-indigo-100 text-indigo-800',
    accent: 'border-t-indigo-400',
  },
  diapering: {
    badge: 'bg-cyan-100 text-cyan-800',
    accent: 'border-t-cyan-400',
  },
  bath: {
    badge: 'bg-sky-100 text-sky-800',
    accent: 'border-t-sky-400',
  },
  teething: {
    badge: 'bg-rose-100 text-rose-800',
    accent: 'border-t-rose-400',
  },
  health: {
    badge: 'bg-emerald-100 text-emerald-800',
    accent: 'border-t-emerald-400',
  },
  grooming: {
    badge: 'bg-violet-100 text-violet-800',
    accent: 'border-t-violet-400',
  },
  play: {
    badge: 'bg-fuchsia-100 text-fuchsia-800',
    accent: 'border-t-fuchsia-400',
  },
  safety: {
    badge: 'bg-red-100 text-red-800',
    accent: 'border-t-red-400',
  },
  learning: {
    badge: 'bg-amber-100 text-amber-800',
    accent: 'border-t-amber-400',
  },
  travel: {
    badge: 'bg-lime-100 text-lime-800',
    accent: 'border-t-lime-400',
  },
};

const defaultCategoryStyle = {
  badge: 'bg-slate-100 text-slate-700',
  accent: 'border-t-slate-400',
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
                className={`flex flex-col rounded-3xl border border-t-4 border-stone-200 bg-white p-6 shadow-sm ${colors.accent}`}
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
                    <span key={tag} className="text-xs text-teal-700">
                      #{tag}
                    </span>
                  ))}
                </div>
                {(product.explanation || product.matchedTags.length > 0) && (
                  <p className="mt-5 flex-1 rounded-2xl bg-teal-50 p-4 text-sm leading-6 text-teal-900">
                    {product.explanation ??
                      `Matches: ${product.matchedTags.join(', ')}.`}
                  </p>
                )}
                <p className="mt-4 text-xs text-slate-400">
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
