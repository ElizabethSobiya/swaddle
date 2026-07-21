export interface BabyProfile {
  id: string;
  name: string;
  birthDate: string;
}

export interface CareEntry {
  id: string;
  babyId: string;
  category: 'feeding' | 'sleep' | 'diaper' | 'note';
  occurredAt: string;
  notes?: string;
}

export type ContentType = 'rhyme' | 'video' | 'sound' | 'activity';

export interface ContentItem {
  id: number;
  type: ContentType;
  title: string;
  url: string;
  ageMinMonths: number;
  ageMaxMonths: number;
  config?: Record<string, unknown> | null;
}
