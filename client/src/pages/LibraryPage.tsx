import { useCallback, useEffect, useState } from 'react';
import type { ContentItem, ContentType } from '@swaddle/types';
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/UI';
import { getContent } from '../lib/api';

const filters: { label: string; value?: ContentType }[] = [
  { label: 'All' },
  { label: 'Rhymes', value: 'rhyme' },
  { label: 'Videos', value: 'video' },
  { label: 'Sounds', value: 'sound' },
  { label: 'Activities', value: 'activity' },
];
export function LibraryPage({ ageMonths }: { ageMonths: number }) {
  const [type, setType] = useState<ContentType | undefined>();
  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setItems(await getContent(ageMonths, type));
    } catch (r) {
      setError(r instanceof Error ? r.message : 'Could not load the library.');
    } finally {
      setLoading(false);
    }
  }, [ageMonths, type]);
  useEffect(() => {
    void load();
  }, [load]);
  return (
    <>
      <PageHeader eyebrow="Play and learn" title="Content library">
        Age-filtered songs, sounds, videos, and simple activities.
      </PageHeader>
      <div className="mb-6 flex flex-wrap gap-2">
        {filters.map((filter) => (
          <button
            key={filter.label}
            onClick={() => setType(filter.value)}
            className={`rounded-full px-4 py-2 text-sm font-bold ${type === filter.value ? 'bg-teal-600 text-white' : 'border border-stone-200 bg-white text-slate-600'}`}
          >
            {filter.label}
          </button>
        ))}
      </div>
      {loading ? (
        <LoadingState label="Opening the library…" />
      ) : error ? (
        <ErrorState message={error} retry={() => void load()} />
      ) : items.length === 0 ? (
        <EmptyState>No content matches this age and filter.</EmptyState>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {items.map((item) => (
            <ContentCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </>
  );
}
function ContentCard({ item }: { item: ContentItem }) {
  const icon = { rhyme: '♫', video: '▶', sound: '♪', activity: '✦' }[item.type];
  return (
    <article className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm">
      <div className="grid h-12 w-12 place-items-center rounded-2xl bg-teal-50 text-xl text-teal-700">
        {icon}
      </div>
      <p className="mt-5 text-xs font-bold uppercase tracking-widest text-teal-600">
        {item.type}
      </p>
      <h2 className="font-display mt-1 text-xl font-bold">{item.title}</h2>
      <p className="mt-2 text-sm text-slate-500">
        Ages {item.ageMinMonths}–{item.ageMaxMonths} months
      </p>
      {item.type === 'activity' && (
        <p className="mt-4 rounded-xl bg-amber-50 p-3 text-sm text-amber-900">
          {String(item.config?.instructions ?? 'Interactive activity')}
        </p>
      )}
      <a
        href={
          item.type === 'video'
            ? `https://www.youtube.com/watch?v=${item.url}`
            : item.url
        }
        target="_blank"
        rel="noreferrer"
        className="mt-5 inline-block text-sm font-bold text-teal-700"
      >
        {item.type === 'activity' ? 'View game config' : 'Open content'} →
      </a>
    </article>
  );
}
