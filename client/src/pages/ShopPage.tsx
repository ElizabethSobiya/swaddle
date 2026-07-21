import { useCallback, useEffect, useState } from 'react';
import type { BabyProfile, ProductRecommendation } from '@babycare/types';
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/UI';
import { getProducts } from '../lib/api';

export function ShopPage({ baby }: { baby: BabyProfile }) {
  const [items, setItems] = useState<ProductRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setItems(await getProducts(baby.id));
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
          {items.map((product) => (
            <article
              key={product.id}
              className="flex flex-col rounded-3xl border border-stone-200 bg-white p-6 shadow-sm"
            >
              <div className="flex items-start justify-between gap-3">
                <span className="rounded-full bg-stone-100 px-3 py-1 text-xs font-bold capitalize text-slate-600">
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
              <p className="mt-5 flex-1 rounded-2xl bg-teal-50 p-4 text-sm leading-6 text-teal-900">
                {product.explanation ??
                  (product.matchedTags.length
                    ? `Matches: ${product.matchedTags.join(', ')}.`
                    : 'Recommended for the current age range.')}
              </p>
              <p className="mt-4 text-xs text-slate-400">
                Ages {product.ageMinMonths}–{product.ageMaxMonths} months
              </p>
            </article>
          ))}
        </div>
      )}
    </>
  );
}
