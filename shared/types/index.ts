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

