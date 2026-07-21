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
  const [showVideo, setShowVideo] = useState(false);
  const [videoLoading, setVideoLoading] = useState(false);
  const icon = { rhyme: '♫', video: '▶', sound: '♪', activity: '✦' }[item.type];

  function playGeneratedSound() {
    const context = new AudioContext();
    const rawCues = item.config?.cues;
    const frequencies = Array.isArray(rawCues)
      ? rawCues
          .map((cue) =>
            typeof cue === 'number'
              ? cue
              : typeof cue === 'object' &&
                  cue !== null &&
                  'frequency_hz' in cue &&
                  typeof cue.frequency_hz === 'number'
                ? cue.frequency_hz
                : null,
          )
          .filter((frequency): frequency is number => frequency !== null)
      : typeof item.config?.frequency_hz === 'number'
        ? [item.config.frequency_hz]
        : [392];
    const duration =
      typeof item.config?.duration_ms === 'number'
        ? item.config.duration_ms / 1000
        : 0.4;
    const gainValue =
      typeof item.config?.gain === 'number' ? item.config.gain : 0.1;

    frequencies.forEach((frequency, index) => {
      const start = context.currentTime + index * (duration + 0.15);
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = 'sine';
      oscillator.frequency.value = frequency;
      gain.gain.setValueAtTime(0, start);
      gain.gain.linearRampToValueAtTime(gainValue, start + 0.03);
      gain.gain.linearRampToValueAtTime(0, start + duration);
      oscillator.connect(gain).connect(context.destination);
      oscillator.start(start);
      oscillator.stop(start + duration);
    });
    window.setTimeout(
      () => void context.close(),
      (frequencies.length * (duration + 0.15) + 0.2) * 1000,
    );
  }

  return (
    <article className="flex h-full flex-col rounded-3xl border border-stone-200 bg-white p-6 shadow-sm">
      <div className="grid h-12 w-12 place-items-center rounded-2xl bg-teal-50 text-xl text-teal-700">
        {icon}
      </div>
      <p className="mt-5 text-xs font-bold uppercase tracking-widest text-teal-600">
        {item.type}
      </p>
      <h2 className="font-display mt-1 min-h-14 text-xl font-bold">
        {item.title}
      </h2>
      <p className="mt-2 text-sm text-slate-500">
        Ages {item.ageMinMonths}–{item.ageMaxMonths} months
      </p>
      {item.type === 'activity' && (
        <p className="mt-4 rounded-xl bg-amber-50 p-3 text-sm text-amber-900">
          {String(item.config?.instructions ?? 'Interactive activity')}
        </p>
      )}
      {item.type === 'video' && !showVideo && (
        <button
          type="button"
          onClick={() => {
            setVideoLoading(true);
            setShowVideo(true);
          }}
          className="mt-5 rounded-xl bg-teal-600 px-4 py-2.5 text-sm font-bold text-white"
        >
          Load video
        </button>
      )}
      {item.type === 'video' && showVideo && (
        <div className="relative mt-5 aspect-video overflow-hidden rounded-2xl bg-slate-100">
          {videoLoading && (
            <div className="absolute inset-0 grid place-items-center text-sm text-slate-500">
              Loading video…
            </div>
          )}
          <iframe
            src={`https://www.youtube-nocookie.com/embed/${item.url}`}
            title={item.title}
            loading="lazy"
            allow="accelerometer; autoplay; encrypted-media; picture-in-picture"
            allowFullScreen
            onLoad={() => setVideoLoading(false)}
            className="absolute inset-0 h-full w-full"
          />
        </div>
      )}
      {item.type === 'rhyme' && (
        <audio controls preload="none" className="mt-5 w-full">
          <source src={item.url} type="audio/ogg" />
        </audio>
      )}
      {item.type === 'sound' && (
        <div className="flex flex-1 flex-col">
          <p className="mt-4 rounded-xl bg-sky-50 p-3 text-sm text-sky-900">
            {String(item.config?.description ?? 'A short listening activity.')}
          </p>
          <div className="mt-auto pt-4">
            <button
              type="button"
              onClick={playGeneratedSound}
              className="rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-bold text-white"
            >
              Play sound cue
            </button>
          </div>
        </div>
      )}
    </article>
  );
}
